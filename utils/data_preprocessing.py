"""
Data preprocessing module for Predictive Analytics & Machine Learning
Handles data extraction, cleaning, validation, and preparation for ML models
"""
import pandas as pd
import numpy as np
import sqlite3
import logging
from typing import Optional, Tuple
from utils.database import get_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    Handles data extraction, cleaning, and preparation for ML models.
    Integrates with existing Edulytix database infrastructure.
    """
    
    def __init__(self, db_connection: Optional[sqlite3.Connection] = None):
        """
        Initialize preprocessor with database connection.
        
        Args:
            db_connection: SQLite database connection. If None, uses get_connection()
        """
        self.conn = db_connection if db_connection is not None else get_connection()
        logger.info("DataPreprocessor initialized with database connection")
    
    def extract_admissions_data(
        self, 
        program: Optional[str] = None,
        cohort: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Extract admissions data from database with optional filters.
        
        Args:
            program: Optional program code filter (e.g., 'MBA', 'MS ACCT')
            cohort: Optional cohort year filter (e.g., 2026, 2027)
            
        Returns:
            DataFrame with columns [report_date, program, cohort_year, metric_name, metric_value]
        """
        query = """
            SELECT 
                report_date,
                program,
                cohort_year,
                metric_name,
                metric_value
            FROM admissions_metrics
            WHERE 1=1
        """
        params = []
        
        if program is not None:
            query += " AND program = ?"
            params.append(program)
        
        if cohort is not None:
            query += " AND cohort_year = ?"
            params.append(cohort)
        
        query += " ORDER BY report_date, program, cohort_year, metric_name"
        
        try:
            df = pd.read_sql(query, self.conn, params=params)
            logger.info(f"Extracted {len(df)} admissions records (program={program}, cohort={cohort})")
            
            # Convert report_date to datetime
            if not df.empty:
                df['report_date'] = pd.to_datetime(df['report_date'])
            
            return df
        except Exception as e:
            logger.error(f"Error extracting admissions data: {e}")
            raise
    
    def extract_marketing_data(
        self,
        program: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Extract marketing spend data from database.
        
        Args:
            program: Optional program code filter
            
        Returns:
            DataFrame with columns [spend_date, program, channel, amount, cohort_year]
        """
        query = """
            SELECT 
                month_date as spend_date,
                program,
                channel,
                spend_amount as amount,
                NULL as cohort_year
            FROM marketing_spend
            WHERE 1=1
        """
        params = []
        
        if program is not None:
            query += " AND program = ?"
            params.append(program)
        
        query += " ORDER BY month_date, program, channel"
        
        try:
            df = pd.read_sql(query, self.conn, params=params)
            logger.info(f"Extracted {len(df)} marketing spend records (program={program})")
            
            # Convert spend_date to datetime
            if not df.empty:
                df['spend_date'] = pd.to_datetime(df['spend_date'])
            
            return df
        except Exception as e:
            logger.error(f"Error extracting marketing data: {e}")
            raise

    def handle_missing_values(
        self,
        data: pd.DataFrame,
        method: str = 'forward_fill'
    ) -> pd.DataFrame:
        """
        Handle missing values in time series data.
        Uses forward-fill for gaps <= 1 month as specified in requirements.
        
        Args:
            data: DataFrame with time series data
            method: 'forward_fill', 'interpolate', or 'drop'
            
        Returns:
            DataFrame with missing values handled
        """
        if data.empty:
            return data
        
        df = data.copy()
        
        if method == 'forward_fill':
            # Forward fill with limit of 1 (for gaps <= 1 month)
            # Use ffill() instead of deprecated fillna(method='ffill')
            df = df.ffill(limit=1)
            
            # Log remaining missing values
            missing_count = df.isnull().sum().sum()
            if missing_count > 0:
                logger.warning(f"After forward-fill, {missing_count} missing values remain (gaps > 1 month)")
        
        elif method == 'interpolate':
            # Linear interpolation for numeric columns
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].interpolate(method='linear', limit_direction='forward')
        
        elif method == 'drop':
            df = df.dropna()
            logger.info(f"Dropped rows with missing values, {len(df)} rows remaining")
        
        else:
            raise ValueError(f"Unknown method: {method}. Use 'forward_fill', 'interpolate', or 'drop'")
        
        return df
    
    def detect_outliers(
        self,
        data: pd.DataFrame,
        threshold: float = 3.0
    ) -> pd.DataFrame:
        """
        Detect and flag outliers using z-score method.
        
        Args:
            data: DataFrame with numeric data
            threshold: Z-score threshold (default 3.0 standard deviations)
            
        Returns:
            DataFrame with outlier_flag column added (True for outliers)
        """
        if data.empty:
            return data
        
        df = data.copy()
        
        # Identify numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        # Initialize outlier flag
        df['outlier_flag'] = False
        
        for col in numeric_cols:
            if col == 'outlier_flag':
                continue
            
            # Calculate z-scores
            mean = df[col].mean()
            std = df[col].std()
            
            if std > 0:  # Avoid division by zero
                z_scores = np.abs((df[col] - mean) / std)
                outliers = z_scores > threshold
                
                # Update outlier flag
                df.loc[outliers, 'outlier_flag'] = True
                
                # Log outliers
                outlier_count = outliers.sum()
                if outlier_count > 0:
                    logger.warning(
                        f"Detected {outlier_count} outliers in column '{col}' "
                        f"(threshold={threshold} std dev)"
                    )
        
        return df
    
    def prepare_time_series(
        self,
        data: pd.DataFrame,
        metric: str,
        freq: str = 'M'
    ) -> pd.DataFrame:
        """
        Prepare time series data for forecasting.
        Converts to datetime-indexed DataFrame with specified frequency.
        
        Args:
            data: Raw data from database
            metric: Metric column to use as target variable
            freq: Frequency ('M' for monthly, 'W' for weekly, 'D' for daily)
            
        Returns:
            DataFrame with datetime index and cleaned values
        """
        if data.empty:
            logger.warning("Empty dataset provided to prepare_time_series")
            return pd.DataFrame()
        
        df = data.copy()
        
        # Determine date column
        date_col = None
        for col in ['report_date', 'spend_date', 'date']:
            if col in df.columns:
                date_col = col
                break
        
        if date_col is None:
            raise ValueError("No date column found in data. Expected 'report_date', 'spend_date', or 'date'")
        
        # Ensure date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
            df[date_col] = pd.to_datetime(df[date_col])
        
        # Set date as index
        df = df.set_index(date_col)
        
        # Sort by date
        df = df.sort_index()
        
        # If metric column exists, ensure it's numeric
        if metric in df.columns:
            df[metric] = pd.to_numeric(df[metric], errors='coerce')
        
        # Resample to specified frequency if needed
        if freq and metric in df.columns:
            # Group by frequency and aggregate
            df = df.resample(freq)[metric].sum().to_frame()
        
        logger.info(f"Prepared time series with {len(df)} periods at frequency '{freq}'")
        
        return df

    def join_admissions_marketing(
        self,
        admissions: pd.DataFrame,
        marketing: pd.DataFrame,
        lag_months: int = 2
    ) -> pd.DataFrame:
        """
        Join admissions and marketing data with time lag.
        Marketing spend in month M is associated with admissions outcomes in month M+lag.
        
        Args:
            admissions: Admissions data with report_date
            marketing: Marketing spend data with spend_date
            lag_months: Number of months to lag marketing data (1-3 months, default 2)
            
        Returns:
            Joined DataFrame with marketing spend lagged appropriately
        """
        if admissions.empty or marketing.empty:
            logger.warning("Empty dataset provided to join_admissions_marketing")
            return pd.DataFrame()
        
        if not 1 <= lag_months <= 3:
            raise ValueError(f"lag_months must be between 1 and 3, got {lag_months}")
        
        # Make copies to avoid modifying originals
        adm_df = admissions.copy()
        mkt_df = marketing.copy()
        
        # Ensure date columns are datetime
        if 'report_date' in adm_df.columns:
            adm_df['report_date'] = pd.to_datetime(adm_df['report_date'])
        if 'spend_date' in mkt_df.columns:
            mkt_df['spend_date'] = pd.to_datetime(mkt_df['spend_date'])
        
        # Create month_year column for joining (YYYY-MM format)
        adm_df['month_year'] = adm_df['report_date'].dt.to_period('M')
        mkt_df['month_year'] = mkt_df['spend_date'].dt.to_period('M')
        
        # Apply lag to marketing data
        # Marketing spend in month M should match admissions in month M+lag
        mkt_df['month_year_lagged'] = mkt_df['month_year'] + lag_months
        
        # Aggregate marketing data by program, cohort, channel, and lagged month
        mkt_agg = mkt_df.groupby(
            ['program', 'cohort_year', 'channel', 'month_year_lagged'],
            dropna=False
        ).agg({
            'amount': 'sum'
        }).reset_index()
        
        # Rename for joining
        mkt_agg = mkt_agg.rename(columns={
            'month_year_lagged': 'month_year',
            'amount': 'marketing_spend'
        })
        
        # Join on program, cohort_year, and month_year
        # Use outer join to preserve all admissions records
        joined = adm_df.merge(
            mkt_agg,
            on=['program', 'cohort_year', 'month_year'],
            how='left'
        )
        
        # Fill missing marketing spend with 0
        joined['marketing_spend'] = joined['marketing_spend'].fillna(0)
        
        logger.info(
            f"Joined {len(adm_df)} admissions records with {len(mkt_agg)} marketing records "
            f"(lag={lag_months} months), resulting in {len(joined)} records"
        )
        
        return joined
