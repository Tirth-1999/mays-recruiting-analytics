"""
Machine learning models module for predictive analytics.
Contains forecasting, optimization, and recommendation components.
"""

import pandas as pd
import numpy as np
import logging
from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime
import sqlite3
import joblib
import os
from pathlib import Path
from utils.validation import BoundsChecker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clear_model_cache(cache_dir: str = '.cache/models') -> int:
    """
    Clear all cached models. Useful when new data is added to the database.
    
    Args:
        cache_dir: Directory containing cached models (default: '.cache/models')
        
    Returns:
        Number of cache files deleted
    """
    cache_path = Path(cache_dir)
    
    if not cache_path.exists():
        logger.info(f"Cache directory '{cache_dir}' does not exist")
        return 0
    
    deleted_count = 0
    for cache_file in cache_path.glob('*.pkl'):
        try:
            cache_file.unlink()
            deleted_count += 1
            logger.debug(f"Deleted cache file: {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to delete cache file {cache_file}: {e}")
    
    logger.info(f"Cleared {deleted_count} cached models from '{cache_dir}'")
    return deleted_count


def get_cache_info(cache_dir: str = '.cache/models') -> Dict[str, Any]:
    """
    Get information about cached models.
    
    Args:
        cache_dir: Directory containing cached models (default: '.cache/models')
        
    Returns:
        Dictionary with cache statistics:
        - total_files: Number of cached model files
        - total_size_mb: Total size of cache in MB
        - oldest_file: Path to oldest cached file
        - newest_file: Path to newest cached file
    """
    cache_path = Path(cache_dir)
    
    if not cache_path.exists():
        return {
            'total_files': 0,
            'total_size_mb': 0.0,
            'oldest_file': None,
            'newest_file': None
        }
    
    cache_files = list(cache_path.glob('*.pkl'))
    
    if not cache_files:
        return {
            'total_files': 0,
            'total_size_mb': 0.0,
            'oldest_file': None,
            'newest_file': None
        }
    
    # Calculate total size
    total_size_bytes = sum(f.stat().st_size for f in cache_files)
    total_size_mb = total_size_bytes / (1024 * 1024)
    
    # Find oldest and newest files
    files_with_mtime = [(f, f.stat().st_mtime) for f in cache_files]
    oldest_file = min(files_with_mtime, key=lambda x: x[1])[0]
    newest_file = max(files_with_mtime, key=lambda x: x[1])[0]
    
    return {
        'total_files': len(cache_files),
        'total_size_mb': round(total_size_mb, 2),
        'oldest_file': str(oldest_file),
        'newest_file': str(newest_file)
    }


class TimeSeriesForecaster:
    """
    Generate forecasts for admissions metrics with confidence intervals.
    Automatically selects appropriate model based on data characteristics.
    """
    
    def __init__(self, data: pd.DataFrame, metric: str):
        """
        Initialize forecaster with historical data.
        
        Args:
            data: DataFrame with columns [date, program, cohort, metric_value]
            metric: Name of metric to forecast (e.g., 'inquiries_received')
        """
        self.data = data.copy()
        self.metric = metric
        self.model = None
        self.model_type = None
        self.data_points = len(data)
        self.has_seasonality = False
        self.validation_metrics = {}
        self.holdout_size = 0
        
        # Ensure data is sorted by date
        if 'date' in self.data.columns:
            self.data['date'] = pd.to_datetime(self.data['date'])
            self.data = self.data.sort_values('date').reset_index(drop=True)
        
        logger.info(f"Initialized TimeSeriesForecaster for metric '{metric}' with {self.data_points} data points")
    
    def fit(self, model_type: str = 'auto') -> None:
        """
        Train forecasting model on historical data.
        
        Args:
            model_type: 'auto', 'prophet', 'arima', or 'linear'
        """
        if model_type == 'auto':
            self.model_type = self._select_model()
        else:
            self.model_type = model_type
        
        logger.info(f"Training {self.model_type} model")
        
        # Detect seasonality
        self.has_seasonality = self._detect_seasonality()
        
        # Check for cached model
        cache_key = self._get_cache_key()
        cached_model = self._load_cached_model(cache_key)
        
        if cached_model is not None:
            logger.info("Using cached model")
            self.model = cached_model
            # Still validate to get metrics
            self.validation_metrics = self._validate_model()
            return
        
        # Train new model
        try:
            if self.model_type == 'prophet':
                self._fit_prophet()
            elif self.model_type == 'arima':
                self._fit_arima()
            else:  # linear
                self._fit_linear()
            
            # Validate model and calculate accuracy metrics
            self.validation_metrics = self._validate_model()
            
            # Cache the trained model
            self._cache_model(cache_key)
            
            logger.info(f"Successfully trained {self.model_type} model")
            
        except Exception as e:
            logger.error(f"Error training {self.model_type} model: {e}")
            
            # Fallback logic
            if self.model_type == 'prophet':
                logger.info("Falling back to ARIMA model")
                self.model_type = 'arima'
                try:
                    self._fit_arima()
                    self.validation_metrics = self._validate_model()
                except Exception as e2:
                    logger.error(f"ARIMA fallback failed: {e2}")
                    logger.info("Falling back to linear model")
                    self.model_type = 'linear'
                    self._fit_linear()
                    self.validation_metrics = self._validate_model()
            elif self.model_type == 'arima':
                logger.info("Falling back to linear model")
                self.model_type = 'linear'
                self._fit_linear()
                self.validation_metrics = self._validate_model()
            else:
                raise Exception(f"Failed to train any model: {e}")
    
    def _fit_prophet(self) -> None:
        """Fit Prophet model with seasonal components."""
        from prophet import Prophet
        
        # Prepare data in Prophet format (ds, y)
        df = self._prepare_prophet_data()
        
        # Configure Prophet with monthly seasonality
        model = Prophet(
            yearly_seasonality=self.has_seasonality,
            weekly_seasonality=False,
            daily_seasonality=False,
            interval_width=0.95
        )
        
        # Add monthly seasonality with 12-month period
        if self.has_seasonality:
            model.add_seasonality(
                name='monthly',
                period=30.5,
                fourier_order=5
            )
        
        # Fit the model
        model.fit(df)
        self.model = model
        
        logger.info("Prophet model fitted successfully")
    
    def _fit_arima(self) -> None:
        """Fit ARIMA model."""
        from statsmodels.tsa.arima.model import ARIMA
        
        # Extract values
        values = self._extract_values()
        
        # Fit ARIMA model with auto order selection
        # Using simple (1,1,1) as default
        model = ARIMA(values, order=(1, 1, 1))
        fitted_model = model.fit()
        
        self.model = fitted_model
        logger.info("ARIMA model fitted successfully")
    
    def _fit_linear(self) -> None:
        """Fit simple linear regression model."""
        from sklearn.linear_model import LinearRegression
        
        # Extract values
        values = self._extract_values()
        
        # Create time index
        X = np.arange(len(values)).reshape(-1, 1)
        y = values
        
        # Fit linear model
        model = LinearRegression()
        model.fit(X, y)
        
        self.model = model
        logger.info("Linear model fitted successfully")
    
    def _prepare_prophet_data(self) -> pd.DataFrame:
        """Prepare data in Prophet format (ds, y)."""
        df = self.data.copy()
        
        # Ensure date column exists
        if 'date' not in df.columns:
            raise ValueError("Data must have 'date' column for Prophet")
        
        # Extract metric values
        if 'metric_value' in df.columns:
            y_col = 'metric_value'
        elif self.metric in df.columns:
            y_col = self.metric
        else:
            raise ValueError(f"Metric '{self.metric}' not found in data")
        
        # Create Prophet dataframe
        prophet_df = pd.DataFrame({
            'ds': pd.to_datetime(df['date']),
            'y': df[y_col]
        })
        
        return prophet_df
    
    def _extract_values(self) -> np.ndarray:
        """Extract metric values as numpy array."""
        if 'metric_value' in self.data.columns:
            values = self.data['metric_value'].values
        elif self.metric in self.data.columns:
            values = self.data[self.metric].values
        else:
            raise ValueError(f"Metric '{self.metric}' not found in data")
        
        return values
    
    def _get_cache_key(self) -> str:
        """
        Generate cache key based on data and parameters.
        
        The cache key includes:
        - Model type
        - Metric name
        - Hash of training data (dates and values)
        - Data size
        
        This ensures cache is invalidated when:
        - Different model type is used
        - Different metric is forecasted
        - Training data changes (new data added or values modified)
        """
        # Create hash of data and parameters
        data_hash = hash(tuple(self.data['date'].astype(str)) + tuple(self._extract_values()))
        data_size = len(self.data)
        cache_key = f"{self.model_type}_{self.metric}_{abs(data_hash)}_{data_size}"
        return cache_key
    
    def _load_cached_model(self, cache_key: str) -> Any:
        """Load cached model if available."""
        cache_dir = Path('.cache/models')
        cache_file = cache_dir / f"{cache_key}.pkl"
        
        if cache_file.exists():
            try:
                model = joblib.load(cache_file)
                logger.info(f"Loaded cached model from {cache_file}")
                return model
            except Exception as e:
                logger.warning(f"Failed to load cached model: {e}")
                return None
        
        return None
    
    def _cache_model(self, cache_key: str) -> None:
        """Cache the trained model."""
        cache_dir = Path('.cache/models')
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / f"{cache_key}.pkl"
        
        try:
            joblib.dump(self.model, cache_file)
            logger.info(f"Cached model to {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to cache model: {e}")
    
    def predict(
        self, 
        periods: int,
        confidence_level: float = 0.95
    ) -> pd.DataFrame:
        """
        Generate forecasts for specified number of periods.
        
        Args:
            periods: Number of months to forecast
            confidence_level: Confidence level for intervals (default 0.95)
            
        Returns:
            DataFrame with columns [date, forecast, lower_bound, upper_bound]
        """
        if self.model is None:
            raise ValueError("Model must be fitted before making predictions. Call fit() first.")
        
        logger.info(f"Generating {periods}-period forecast with {confidence_level} confidence")
        
        try:
            if self.model_type == 'prophet':
                result = self._predict_prophet(periods)
            elif self.model_type == 'arima':
                result = self._predict_arima(periods, confidence_level)
            else:  # linear
                result = self._predict_linear(periods, confidence_level)
            
            # Apply bounds checking for count metrics and unrealistic predictions
            result, warnings = BoundsChecker.check_prediction_bounds(
                predictions=result,
                historical_data=self.data,
                metric=self.metric
            )
            
            # Log warnings
            for warning in warnings:
                logger.warning(warning)
            
            # Apply non-negative bounds for count metrics (additional safety check)
            result = self._apply_bounds_checking(result)
            
            # Round count-based predictions to integers
            result = self._round_count_predictions(result)
            
            logger.info(f"Successfully generated {len(result)} predictions")
            return result
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            raise
    
    def _predict_prophet(self, periods: int) -> pd.DataFrame:
        """Generate predictions using Prophet model."""
        # Create future dataframe
        future = self.model.make_future_dataframe(periods=periods, freq='MS')
        
        # Generate forecast
        forecast = self.model.predict(future)
        
        # Extract only future predictions (not historical)
        forecast = forecast.tail(periods)
        
        # Format output
        result = pd.DataFrame({
            'date': forecast['ds'],
            'forecast': forecast['yhat'],
            'lower_bound': forecast['yhat_lower'],
            'upper_bound': forecast['yhat_upper']
        })
        
        return result.reset_index(drop=True)
    
    def _predict_arima(self, periods: int, confidence_level: float) -> pd.DataFrame:
        """Generate predictions using ARIMA model."""
        # Generate forecast
        forecast_result = self.model.forecast(steps=periods)
        
        # Get confidence intervals
        forecast_df = self.model.get_forecast(steps=periods)
        conf_int = forecast_df.conf_int(alpha=1-confidence_level)
        
        # Get last date from training data
        if 'date' in self.data.columns:
            last_date = pd.to_datetime(self.data['date'].iloc[-1])
        else:
            last_date = pd.Timestamp.now()
        
        # Generate future dates
        future_dates = pd.date_range(
            start=last_date + pd.DateOffset(months=1),
            periods=periods,
            freq='MS'
        )
        
        # Handle conf_int as either DataFrame or ndarray
        if isinstance(conf_int, pd.DataFrame):
            lower_bound = conf_int.iloc[:, 0].values
            upper_bound = conf_int.iloc[:, 1].values
        else:
            # conf_int is a numpy array
            lower_bound = conf_int[:, 0]
            upper_bound = conf_int[:, 1]
        
        # Format output
        result = pd.DataFrame({
            'date': future_dates,
            'forecast': forecast_result,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound
        })
        
        return result.reset_index(drop=True)
    
    def _predict_linear(self, periods: int, confidence_level: float) -> pd.DataFrame:
        """Generate predictions using linear regression model."""
        # Get last date from training data
        if 'date' in self.data.columns:
            last_date = pd.to_datetime(self.data['date'].iloc[-1])
        else:
            last_date = pd.Timestamp.now()
        
        # Generate future dates
        future_dates = pd.date_range(
            start=last_date + pd.DateOffset(months=1),
            periods=periods,
            freq='MS'
        )
        
        # Create future time indices
        last_index = len(self.data) - 1
        future_indices = np.arange(last_index + 1, last_index + 1 + periods).reshape(-1, 1)
        
        # Generate predictions
        predictions = self.model.predict(future_indices)
        
        # Calculate simple confidence intervals based on historical variance
        values = self._extract_values()
        std_error = np.std(values) * 1.96  # 95% CI approximation
        
        # Format output
        result = pd.DataFrame({
            'date': future_dates,
            'forecast': predictions,
            'lower_bound': predictions - std_error,
            'upper_bound': predictions + std_error
        })
        
        return result.reset_index(drop=True)
    
    def _apply_bounds_checking(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply bounds checking to ensure non-negative values for count metrics."""
        # Count metrics should be non-negative
        count_metrics = [
            'inquiries_received', 'applications_received', 'applications_complete',
            'admissions_offered', 'admissions_accepted', 'anticipated_cohort_size'
        ]
        
        if self.metric in count_metrics:
            # Ensure all values are non-negative
            df['forecast'] = df['forecast'].clip(lower=0)
            df['lower_bound'] = df['lower_bound'].clip(lower=0)
            df['upper_bound'] = df['upper_bound'].clip(lower=0)
            
            logger.info("Applied non-negative bounds checking for count metric")
        
        return df
    
    def _round_count_predictions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Round count-based predictions to integers."""
        # Count metrics should be integers
        count_metrics = [
            'inquiries_received', 'applications_received', 'applications_complete',
            'admissions_offered', 'admissions_accepted', 'anticipated_cohort_size'
        ]
        
        if self.metric in count_metrics:
            df['forecast'] = df['forecast'].round().astype(int)
            df['lower_bound'] = df['lower_bound'].round().astype(int)
            df['upper_bound'] = df['upper_bound'].round().astype(int)
            
            logger.info("Rounded count predictions to integers")
        
        return df
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Return information about the selected model and its parameters.
        
        Returns:
            Dictionary with model_type, parameters, and data_points_used
        """
        info = {
            'model_type': self.model_type,
            'data_points_used': self.data_points - self.holdout_size,
            'metric': self.metric,
            'has_seasonality': self.has_seasonality,
            'validation_metrics': self.validation_metrics
        }
        
        # Add model-specific parameters
        if self.model_type == 'prophet' and self.model is not None:
            info['parameters'] = {
                'yearly_seasonality': self.has_seasonality,
                'interval_width': 0.95
            }
        elif self.model_type == 'arima' and self.model is not None:
            info['parameters'] = {
                'order': getattr(self.model, 'model_orders', {}).get('order', (1, 1, 1))
            }
        elif self.model_type == 'linear':
            info['parameters'] = {
                'model': 'LinearRegression'
            }
        
        return info
    
    def _validate_model(self) -> Dict[str, float]:
        """
        Validate model using holdout set (last 20% of data).
        Calculate MAPE, RMSE, MAE on holdout set.
        
        Returns:
            Dictionary with validation metrics
        """
        if self.data_points < 10:
            logger.warning("Insufficient data for validation (need at least 10 points)")
            return {'mape': None, 'rmse': None, 'mae': None}
        
        # Calculate holdout size (20% of data, minimum 2 points)
        self.holdout_size = max(2, int(self.data_points * 0.2))
        
        # Split data into train and holdout
        train_data = self.data.iloc[:-self.holdout_size].copy()
        holdout_data = self.data.iloc[-self.holdout_size:].copy()
        
        # Extract actual values from holdout
        if 'metric_value' in holdout_data.columns:
            actual_values = holdout_data['metric_value'].values
        elif self.metric in holdout_data.columns:
            actual_values = holdout_data[self.metric].values
        else:
            logger.warning(f"Cannot validate: metric '{self.metric}' not found")
            return {'mape': None, 'rmse': None, 'mae': None}
        
        # Create temporary forecaster with training data only
        temp_forecaster = TimeSeriesForecaster(train_data, self.metric)
        temp_forecaster.fit(model_type=self.model_type)
        
        # Generate predictions for holdout period
        try:
            predictions_df = temp_forecaster.predict(periods=self.holdout_size)
            predicted_values = predictions_df['forecast'].values
            
            # Calculate metrics
            mape = self._calculate_mape(actual_values, predicted_values)
            rmse = self._calculate_rmse(actual_values, predicted_values)
            mae = self._calculate_mae(actual_values, predicted_values)
            
            metrics = {
                'mape': mape,
                'rmse': rmse,
                'mae': mae,
                'holdout_size': self.holdout_size
            }
            
            logger.info(f"Validation metrics - MAPE: {mape:.2f}%, RMSE: {rmse:.2f}, MAE: {mae:.2f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error during validation: {e}")
            return {'mape': None, 'rmse': None, 'mae': None}
    
    def _calculate_mape(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """Calculate Mean Absolute Percentage Error."""
        # Avoid division by zero
        mask = actual != 0
        if not mask.any():
            return 0.0
        
        mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
        return float(mape)
    
    def _calculate_rmse(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """Calculate Root Mean Squared Error."""
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        return float(rmse)
    
    def _calculate_mae(self, actual: np.ndarray, predicted: np.ndarray) -> float:
        """Calculate Mean Absolute Error."""
        mae = np.mean(np.abs(actual - predicted))
        return float(mae)
    
    def _select_model(self) -> str:
        """
        Select appropriate model based on data characteristics.
        
        Returns:
            Model type string: 'prophet', 'arima', or 'linear'
        """
        if self.data_points >= 24:
            logger.info(f"Sufficient data ({self.data_points} points) - selecting Prophet model")
            return 'prophet'
        elif self.data_points >= 12:
            logger.info(f"Moderate data ({self.data_points} points) - selecting ARIMA model")
            return 'arima'
        else:
            logger.warning(f"Limited data ({self.data_points} points) - using simple linear model")
            return 'linear'
    
    def _detect_seasonality(self) -> bool:
        """
        Detect seasonality using autocorrelation analysis.
        
        Returns:
            True if strong seasonality detected (autocorrelation > 0.6 at 12-month lag), False otherwise
        """
        if self.data_points < 24:
            logger.info("Insufficient data for seasonality detection (need at least 24 points)")
            return False
        
        try:
            # Extract the metric values
            if 'metric_value' in self.data.columns:
                values = self.data['metric_value'].values
            elif self.metric in self.data.columns:
                values = self.data[self.metric].values
            else:
                logger.warning(f"Metric column '{self.metric}' not found in data")
                return False
            
            # Remove NaN values
            values = values[~np.isnan(values)]
            
            if len(values) < 24:
                return False
            
            # Calculate autocorrelation at 12-month lag
            from statsmodels.tsa.stattools import acf
            
            # Calculate autocorrelation with enough lags
            max_lags = min(len(values) - 1, 13)
            autocorr = acf(values, nlags=max_lags, fft=True)
            
            # Check if 12-month lag exists and has strong correlation
            if len(autocorr) > 12:
                seasonal_corr = autocorr[12]
                logger.info(f"12-month autocorrelation: {seasonal_corr:.3f}")
                
                if seasonal_corr > 0.6:
                    logger.info("Strong seasonality detected")
                    return True
                else:
                    logger.info("No strong seasonality detected")
                    return False
            else:
                logger.info("Insufficient lags for 12-month seasonality check")
                return False
                
        except Exception as e:
            logger.warning(f"Error detecting seasonality: {e}")
            return False


class ChannelOptimizer:
    """
    Analyze marketing channel effectiveness and provide recommendations.
    """
    
    # Program-specific tuition estimates for admissions value calculation
    TUITION_ESTIMATES = {
        'MBA': 60000,
        'ACCT': 45000,
        'MS ACCT': 45000,
        'HRM': 45000,
        'MS HRM': 45000,
        'MISY': 45000,
        'MS MISY': 45000,
        'MKTG': 45000,
        'MS MKTG': 45000,
        'ENLD': 50000,
        'MS ENLD': 50000,
        'SPBA': 50000,
        'MS SPBA': 50000
    }
    
    def __init__(self, admissions_data: pd.DataFrame, marketing_data: pd.DataFrame):
        """
        Initialize optimizer with admissions and marketing data.
        
        Args:
            admissions_data: Historical admissions metrics
            marketing_data: Historical marketing spend by channel
        """
        self.admissions_data = admissions_data.copy()
        self.marketing_data = marketing_data.copy()
        
        # Ensure date columns are datetime
        if 'report_date' in self.admissions_data.columns:
            self.admissions_data['report_date'] = pd.to_datetime(self.admissions_data['report_date'])
        if 'spend_date' in self.marketing_data.columns:
            self.marketing_data['spend_date'] = pd.to_datetime(self.marketing_data['spend_date'])
        
        logger.info("Initialized ChannelOptimizer")
    
    def calculate_roi(
        self,
        program: str,
        lag_months: int = 2
    ) -> pd.DataFrame:
        """
        Calculate ROI for each marketing channel for a program.
        
        Args:
            program: Program code (e.g., 'MBA', 'ACCT')
            lag_months: Time lag between spend and conversions (default 2)
            
        Returns:
            DataFrame with columns [channel, spend, conversions, roi, effectiveness_score]
        """
        logger.info(f"Calculating ROI for program '{program}' with {lag_months}-month lag")
        
        if not 1 <= lag_months <= 3:
            raise ValueError(f"lag_months must be between 1 and 3, got {lag_months}")
        
        # Filter data for the specified program
        program_admissions = self.admissions_data[
            self.admissions_data['program'] == program
        ].copy()
        
        program_marketing = self.marketing_data[
            self.marketing_data['program'] == program
        ].copy()
        
        if program_admissions.empty or program_marketing.empty:
            logger.warning(f"No data available for program '{program}'")
            return pd.DataFrame(columns=['channel', 'spend', 'conversions', 'roi', 'effectiveness_score'])
        
        # Create month_year columns for joining
        program_admissions['month_year'] = program_admissions['report_date'].dt.to_period('M')
        program_marketing['month_year'] = program_marketing['spend_date'].dt.to_period('M')
        
        # Apply lag to marketing data
        program_marketing['month_year_lagged'] = program_marketing['month_year'] + lag_months
        
        # Get admissions_accepted metric (conversions)
        conversions_data = program_admissions[
            program_admissions['metric_name'] == 'admissions_accepted'
        ].copy()
        
        if conversions_data.empty:
            logger.warning(f"No admissions_accepted data for program '{program}'")
            return pd.DataFrame(columns=['channel', 'spend', 'conversions', 'roi', 'effectiveness_score'])
        
        # Aggregate conversions by month
        conversions_by_month = conversions_data.groupby('month_year').agg({
            'metric_value': 'sum'
        }).reset_index()
        conversions_by_month.columns = ['month_year', 'conversions']
        
        # Aggregate marketing spend by channel and lagged month
        spend_by_channel = program_marketing.groupby(
            ['channel', 'month_year_lagged']
        ).agg({
            'amount': 'sum'
        }).reset_index()
        spend_by_channel.columns = ['channel', 'month_year', 'spend']
        
        # Join spend with conversions
        channel_performance = spend_by_channel.merge(
            conversions_by_month,
            on='month_year',
            how='left'
        )
        
        # Fill missing conversions with 0
        channel_performance['conversions'] = channel_performance['conversions'].fillna(0)
        
        # Aggregate by channel
        channel_summary = channel_performance.groupby('channel').agg({
            'spend': 'sum',
            'conversions': 'sum'
        }).reset_index()
        
        # Get tuition estimate for this program
        tuition_estimate = self.TUITION_ESTIMATES.get(program, 50000)
        
        # Calculate ROI for each channel
        channel_summary['admissions_value'] = channel_summary['conversions'] * tuition_estimate
        channel_summary['roi'] = (
            (channel_summary['admissions_value'] - channel_summary['spend']) / 
            channel_summary['spend']
        ).replace([np.inf, -np.inf], 0)  # Handle division by zero
        
        # Calculate effectiveness score (will be implemented in next subtask)
        channel_summary['effectiveness_score'] = 0.0
        
        # Select and order columns
        result = channel_summary[['channel', 'spend', 'conversions', 'roi', 'effectiveness_score']]
        
        logger.info(f"Calculated ROI for {len(result)} channels")
        
        return result
    
    def _calculate_effectiveness_score(
        self,
        channel_data: pd.DataFrame,
        program: str
    ) -> pd.DataFrame:
        """
        Calculate effectiveness score combining multiple factors.
        
        Score components:
        - ROI (40% weight)
        - Conversion rate (30% weight)
        - Consistency (20% weight)
        - Data confidence (10% weight)
        
        Args:
            channel_data: DataFrame with channel performance metrics
            program: Program code
            
        Returns:
            DataFrame with effectiveness_score column added
        """
        df = channel_data.copy()
        
        if df.empty:
            return df
        
        # Get detailed monthly data for consistency calculation
        program_admissions = self.admissions_data[
            self.admissions_data['program'] == program
        ].copy()
        
        program_marketing = self.marketing_data[
            self.marketing_data['program'] == program
        ].copy()
        
        # Calculate conversion rate (inquiries to admissions)
        inquiries_data = program_admissions[
            program_admissions['metric_name'] == 'inquiries_received'
        ]
        
        if not inquiries_data.empty:
            total_inquiries = inquiries_data['metric_value'].sum()
            if total_inquiries > 0:
                df['conversion_rate'] = df['conversions'] / total_inquiries
            else:
                df['conversion_rate'] = 0.0
        else:
            df['conversion_rate'] = 0.0
        
        # Calculate consistency score (based on variance of monthly performance)
        consistency_scores = []
        for channel in df['channel']:
            channel_monthly = program_marketing[
                program_marketing['channel'] == channel
            ].groupby(program_marketing['spend_date'].dt.to_period('M')).agg({
                'amount': 'sum'
            })
            
            if len(channel_monthly) >= 3:
                # Calculate coefficient of variation (lower is more consistent)
                cv = channel_monthly['amount'].std() / channel_monthly['amount'].mean() if channel_monthly['amount'].mean() > 0 else 1.0
                # Convert to consistency score (0-1, higher is better)
                consistency = max(0, 1 - cv)
            else:
                consistency = 0.5  # Default for insufficient data
            
            consistency_scores.append(consistency)
        
        df['consistency'] = consistency_scores
        
        # Calculate data confidence (based on number of data points)
        data_confidence_scores = []
        for channel in df['channel']:
            channel_months = len(program_marketing[
                program_marketing['channel'] == channel
            ]['spend_date'].dt.to_period('M').unique())
            
            # Confidence increases with more months of data (max at 12+ months)
            confidence = min(1.0, channel_months / 12.0)
            data_confidence_scores.append(confidence)
        
        df['data_confidence'] = data_confidence_scores
        
        # Normalize ROI to 0-1 scale for scoring
        # Use sigmoid-like transformation to handle negative ROI
        df['roi_normalized'] = df['roi'].apply(lambda x: 1 / (1 + np.exp(-x)))
        
        # Calculate weighted effectiveness score
        df['effectiveness_score'] = (
            df['roi_normalized'] * 0.4 +
            df['conversion_rate'] * 0.3 +
            df['consistency'] * 0.2 +
            df['data_confidence'] * 0.1
        ) * 100  # Scale to 0-100
        
        # Drop intermediate columns
        df = df.drop(columns=['roi_normalized', 'conversion_rate', 'consistency', 'data_confidence'])
        
        return df
    
    def recommend_channels(
        self,
        program: str,
        top_n: int = 3
    ) -> List[Tuple[str, float, float]]:
        """
        Recommend top marketing channels for a program.
        
        Args:
            program: Program code
            top_n: Number of top channels to recommend
            
        Returns:
            List of tuples (channel, effectiveness_score, roi)
        """
        logger.info(f"Generating top {top_n} channel recommendations for '{program}'")
        
        # Calculate ROI for all channels
        channel_data = self.calculate_roi(program)
        
        if channel_data.empty:
            logger.warning(f"No channel data available for program '{program}'")
            return []
        
        # Calculate effectiveness scores
        channel_data = self._calculate_effectiveness_score(channel_data, program)
        
        # Filter out channels with insufficient data (less than 3 months)
        program_marketing = self.marketing_data[
            self.marketing_data['program'] == program
        ]
        
        sufficient_data_channels = []
        for channel in channel_data['channel']:
            channel_months = len(program_marketing[
                program_marketing['channel'] == channel
            ]['spend_date'].dt.to_period('M').unique())
            
            if channel_months >= 3:
                sufficient_data_channels.append(channel)
        
        # Filter to channels with sufficient data
        channel_data = channel_data[channel_data['channel'].isin(sufficient_data_channels)]
        
        if channel_data.empty:
            logger.warning(f"No channels with sufficient data (>= 3 months) for program '{program}'")
            return []
        
        # Sort by effectiveness score
        channel_data = channel_data.sort_values('effectiveness_score', ascending=False)
        
        # Get top N channels
        top_channels = channel_data.head(top_n)
        
        # Convert to list of tuples
        recommendations = [
            (row['channel'], row['effectiveness_score'], row['roi'])
            for _, row in top_channels.iterrows()
        ]
        
        logger.info(f"Generated {len(recommendations)} channel recommendations")
        
        return recommendations
    
    def get_channel_performance_history(
        self,
        program: str,
        channel: str
    ) -> pd.DataFrame:
        """
        Get historical performance data for a program-channel combination.
        
        Args:
            program: Program code
            channel: Marketing channel name
            
        Returns:
            DataFrame with columns [month_year, spend, conversions, roi]
        """
        logger.info(f"Getting performance history for {program} - {channel}")
        
        # Filter data for the specified program and channel
        program_admissions = self.admissions_data[
            self.admissions_data['program'] == program
        ].copy()
        
        program_marketing = self.marketing_data[
            (self.marketing_data['program'] == program) &
            (self.marketing_data['channel'] == channel)
        ].copy()
        
        if program_admissions.empty or program_marketing.empty:
            logger.warning(f"No data available for {program} - {channel}")
            return pd.DataFrame(columns=['month_year', 'spend', 'conversions', 'roi'])
        
        # Create month_year columns
        program_admissions['month_year'] = program_admissions['report_date'].dt.to_period('M')
        program_marketing['month_year'] = program_marketing['spend_date'].dt.to_period('M')
        
        # Apply default 2-month lag
        lag_months = 2
        program_marketing['month_year_lagged'] = program_marketing['month_year'] + lag_months
        
        # Get admissions_accepted metric (conversions)
        conversions_data = program_admissions[
            program_admissions['metric_name'] == 'admissions_accepted'
        ].copy()
        
        # Aggregate conversions by month
        conversions_by_month = conversions_data.groupby('month_year').agg({
            'metric_value': 'sum'
        }).reset_index()
        conversions_by_month.columns = ['month_year', 'conversions']
        
        # Aggregate spend by lagged month
        spend_by_month = program_marketing.groupby('month_year_lagged').agg({
            'amount': 'sum'
        }).reset_index()
        spend_by_month.columns = ['month_year', 'spend']
        
        # Join spend with conversions
        performance_history = spend_by_month.merge(
            conversions_by_month,
            on='month_year',
            how='left'
        )
        
        # Fill missing conversions with 0
        performance_history['conversions'] = performance_history['conversions'].fillna(0)
        
        # Get tuition estimate for ROI calculation
        tuition_estimate = self.TUITION_ESTIMATES.get(program, 50000)
        
        # Calculate ROI for each month
        performance_history['admissions_value'] = performance_history['conversions'] * tuition_estimate
        performance_history['roi'] = (
            (performance_history['admissions_value'] - performance_history['spend']) / 
            performance_history['spend']
        ).replace([np.inf, -np.inf], 0)
        
        # Convert month_year to string for display
        performance_history['month_year'] = performance_history['month_year'].astype(str)
        
        # Select and order columns
        result = performance_history[['month_year', 'spend', 'conversions', 'roi']]
        
        # Sort by month_year
        result = result.sort_values('month_year')
        
        logger.info(f"Retrieved {len(result)} months of performance history")
        
        return result


class TimingOptimizer:
    """
    Identify optimal months for marketing investments based on historical patterns.
    """
    
    def __init__(self, admissions_data: pd.DataFrame):
        """
        Initialize timing optimizer with historical admissions data.
        
        Args:
            admissions_data: Historical admissions metrics with monthly granularity
        """
        self.admissions_data = admissions_data.copy()
        
        # Ensure date columns are datetime
        if 'report_date' in self.admissions_data.columns:
            self.admissions_data['report_date'] = pd.to_datetime(self.admissions_data['report_date'])
        
        logger.info("Initialized TimingOptimizer")
    
    def analyze_seasonal_patterns(self, program: str) -> pd.DataFrame:
        """
        Analyze seasonal patterns in conversion rates.
        
        Args:
            program: Program code
            
        Returns:
            DataFrame with columns [month, avg_conversion_rate, consistency_score]
        """
        logger.info(f"Analyzing seasonal patterns for '{program}'")
        
        # Filter data for the specified program
        program_data = self.admissions_data[
            self.admissions_data['program'] == program
        ].copy()
        
        if program_data.empty:
            logger.warning(f"No data available for program '{program}'")
            return pd.DataFrame(columns=['month', 'avg_conversion_rate', 'consistency_score'])
        
        # Extract inquiries and applications data
        inquiries_data = program_data[
            program_data['metric_name'] == 'inquiries_received'
        ].copy()
        
        applications_data = program_data[
            program_data['metric_name'] == 'applications_received'
        ].copy()
        
        if inquiries_data.empty or applications_data.empty:
            logger.warning(f"Insufficient data for conversion rate calculation for '{program}'")
            return pd.DataFrame(columns=['month', 'avg_conversion_rate', 'consistency_score'])
        
        # Add month column
        inquiries_data['month'] = inquiries_data['report_date'].dt.month
        inquiries_data['year'] = inquiries_data['report_date'].dt.year
        applications_data['month'] = applications_data['report_date'].dt.month
        applications_data['year'] = applications_data['report_date'].dt.year
        
        # Aggregate by month and year
        inquiries_monthly = inquiries_data.groupby(['year', 'month']).agg({
            'metric_value': 'sum'
        }).reset_index()
        inquiries_monthly.columns = ['year', 'month', 'inquiries']
        
        applications_monthly = applications_data.groupby(['year', 'month']).agg({
            'metric_value': 'sum'
        }).reset_index()
        applications_monthly.columns = ['year', 'month', 'applications']
        
        # Join inquiries and applications
        monthly_data = inquiries_monthly.merge(
            applications_monthly,
            on=['year', 'month'],
            how='inner'
        )
        
        # Calculate conversion rate for each month-year combination
        monthly_data['conversion_rate'] = np.where(
            monthly_data['inquiries'] > 0,
            monthly_data['applications'] / monthly_data['inquiries'],
            0.0
        )
        
        # Calculate average conversion rate by month (across all years)
        monthly_avg = monthly_data.groupby('month').agg({
            'conversion_rate': 'mean'
        }).reset_index()
        monthly_avg.columns = ['month', 'avg_conversion_rate']
        
        # Calculate consistency score based on variance across years
        consistency_scores = []
        for month in monthly_avg['month']:
            month_rates = monthly_data[monthly_data['month'] == month]['conversion_rate']
            
            if len(month_rates) >= 2:
                # Calculate coefficient of variation (lower is more consistent)
                mean_rate = month_rates.mean()
                std_rate = month_rates.std()
                
                if mean_rate > 0:
                    cv = std_rate / mean_rate
                    # Convert to consistency score (0-1, higher is better)
                    consistency = max(0, 1 - cv)
                else:
                    consistency = 0.5
            else:
                # Only one year of data - default consistency
                consistency = 0.5
            
            consistency_scores.append(consistency)
        
        monthly_avg['consistency_score'] = consistency_scores
        
        # Sort by month
        monthly_avg = monthly_avg.sort_values('month')
        
        logger.info(f"Analyzed seasonal patterns for {len(monthly_avg)} months")
        
        return monthly_avg
    
    def recommend_timing(
        self,
        program: str,
        top_n: int = 3
    ) -> List[Tuple[str, float, float]]:
        """
        Recommend optimal months for marketing investment.
        
        Args:
            program: Program code
            top_n: Number of top months to recommend
            
        Returns:
            List of tuples (month, effectiveness_score, avg_conversion_rate)
        """
        logger.info(f"Generating top {top_n} timing recommendations for '{program}'")
        
        # Get seasonal patterns
        seasonal_data = self.analyze_seasonal_patterns(program)
        
        if seasonal_data.empty:
            logger.warning(f"No seasonal data available for program '{program}'")
            return []
        
        # Detect strong seasonal patterns using autocorrelation
        has_strong_seasonality = self._detect_strong_seasonality(program)
        
        # Calculate effectiveness scores based on conversion rates and consistency
        # Effectiveness = (conversion_rate * 0.7) + (consistency_score * 0.3)
        seasonal_data['effectiveness_score'] = (
            seasonal_data['avg_conversion_rate'] * 0.7 +
            seasonal_data['consistency_score'] * 0.3
        )
        
        # If strong seasonality detected, boost effectiveness scores
        if has_strong_seasonality:
            logger.info("Strong seasonal patterns detected - highlighting in recommendations")
            seasonal_data['has_strong_seasonality'] = True
        else:
            seasonal_data['has_strong_seasonality'] = False
        
        # Sort by effectiveness score
        seasonal_data = seasonal_data.sort_values('effectiveness_score', ascending=False)
        
        # Get top N months
        top_months = seasonal_data.head(top_n)
        
        # Convert month numbers to month names
        month_names = {
            1: 'January', 2: 'February', 3: 'March', 4: 'April',
            5: 'May', 6: 'June', 7: 'July', 8: 'August',
            9: 'September', 10: 'October', 11: 'November', 12: 'December'
        }
        
        # Convert to list of tuples
        recommendations = [
            (month_names[row['month']], row['effectiveness_score'], row['avg_conversion_rate'])
            for _, row in top_months.iterrows()
        ]
        
        logger.info(f"Generated {len(recommendations)} timing recommendations")
        
        return recommendations
    
    def _detect_strong_seasonality(self, program: str) -> bool:
        """
        Detect strong seasonal patterns using autocorrelation (threshold > 0.6).
        
        Args:
            program: Program code
            
        Returns:
            True if strong seasonality detected, False otherwise
        """
        # Filter data for the specified program
        program_data = self.admissions_data[
            self.admissions_data['program'] == program
        ].copy()
        
        if program_data.empty:
            return False
        
        # Get conversion rate time series
        inquiries_data = program_data[
            program_data['metric_name'] == 'inquiries_received'
        ].copy()
        
        applications_data = program_data[
            program_data['metric_name'] == 'applications_received'
        ].copy()
        
        if inquiries_data.empty or applications_data.empty:
            return False
        
        # Sort by date
        inquiries_data = inquiries_data.sort_values('report_date')
        applications_data = applications_data.sort_values('report_date')
        
        # Create monthly time series
        inquiries_data['month_year'] = inquiries_data['report_date'].dt.to_period('M')
        applications_data['month_year'] = applications_data['report_date'].dt.to_period('M')
        
        inquiries_monthly = inquiries_data.groupby('month_year').agg({
            'metric_value': 'sum'
        }).reset_index()
        
        applications_monthly = applications_data.groupby('month_year').agg({
            'metric_value': 'sum'
        }).reset_index()
        
        # Join and calculate conversion rates
        monthly_data = inquiries_monthly.merge(
            applications_monthly,
            on='month_year',
            how='inner',
            suffixes=('_inquiries', '_applications')
        )
        
        if len(monthly_data) < 24:
            logger.info("Insufficient data for seasonality detection (need at least 24 months)")
            return False
        
        # Calculate conversion rates
        monthly_data['conversion_rate'] = np.where(
            monthly_data['metric_value_inquiries'] > 0,
            monthly_data['metric_value_applications'] / monthly_data['metric_value_inquiries'],
            0.0
        )
        
        # Remove NaN values
        conversion_rates = monthly_data['conversion_rate'].values
        conversion_rates = conversion_rates[~np.isnan(conversion_rates)]
        
        if len(conversion_rates) < 24:
            return False
        
        try:
            # Calculate autocorrelation at 12-month lag
            from statsmodels.tsa.stattools import acf
            
            max_lags = min(len(conversion_rates) - 1, 13)
            autocorr = acf(conversion_rates, nlags=max_lags, fft=True)
            
            # Check if 12-month lag exists and has strong correlation
            if len(autocorr) > 12:
                seasonal_corr = autocorr[12]
                logger.info(f"12-month autocorrelation for conversion rates: {seasonal_corr:.3f}")
                
                if seasonal_corr > 0.6:
                    logger.info("Strong seasonality detected (autocorrelation > 0.6)")
                    return True
                else:
                    logger.info("No strong seasonality detected")
                    return False
            else:
                return False
                
        except Exception as e:
            logger.warning(f"Error detecting seasonality: {e}")
            return False
    
    def visualize_seasonal_heatmap(self, program: str):
        """
        Create heatmap visualization of seasonal patterns.
        
        Args:
            program: Program code
            
        Returns:
            Plotly figure object for rendering in Streamlit
        """
        import plotly.graph_objects as go
        
        logger.info(f"Creating seasonal heatmap for '{program}'")
        
        # Filter data for the specified program
        program_data = self.admissions_data[
            self.admissions_data['program'] == program
        ].copy()
        
        if program_data.empty:
            logger.warning(f"No data available for program '{program}'")
            # Return empty figure
            fig = go.Figure()
            fig.add_annotation(
                text=f"No data available for program '{program}'",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14)
            )
            return fig
        
        # Extract inquiries and applications data
        inquiries_data = program_data[
            program_data['metric_name'] == 'inquiries_received'
        ].copy()
        
        applications_data = program_data[
            program_data['metric_name'] == 'applications_received'
        ].copy()
        
        if inquiries_data.empty or applications_data.empty:
            logger.warning(f"Insufficient data for heatmap for '{program}'")
            fig = go.Figure()
            fig.add_annotation(
                text=f"Insufficient data for conversion rate heatmap",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=14)
            )
            return fig
        
        # Add month and year columns
        inquiries_data['month'] = inquiries_data['report_date'].dt.month
        inquiries_data['year'] = inquiries_data['report_date'].dt.year
        applications_data['month'] = applications_data['report_date'].dt.month
        applications_data['year'] = applications_data['report_date'].dt.year
        
        # Aggregate by month and year
        inquiries_monthly = inquiries_data.groupby(['year', 'month']).agg({
            'metric_value': 'sum'
        }).reset_index()
        inquiries_monthly.columns = ['year', 'month', 'inquiries']
        
        applications_monthly = applications_data.groupby(['year', 'month']).agg({
            'metric_value': 'sum'
        }).reset_index()
        applications_monthly.columns = ['year', 'month', 'applications']
        
        # Join inquiries and applications
        monthly_data = inquiries_monthly.merge(
            applications_monthly,
            on=['year', 'month'],
            how='inner'
        )
        
        # Calculate conversion rate
        monthly_data['conversion_rate'] = np.where(
            monthly_data['inquiries'] > 0,
            monthly_data['applications'] / monthly_data['inquiries'],
            0.0
        )
        
        # Pivot data for heatmap (months as columns, years as rows)
        heatmap_data = monthly_data.pivot(
            index='year',
            columns='month',
            values='conversion_rate'
        )
        
        # Month names for x-axis
        month_names = [
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ]
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=[month_names[m-1] for m in heatmap_data.columns],
            y=heatmap_data.index.astype(str),
            colorscale='RdYlGn',
            text=np.round(heatmap_data.values, 3),
            texttemplate='%{text:.1%}',
            textfont={"size": 10},
            colorbar=dict(
                title="Conversion<br>Rate",
                tickformat='.0%'
            ),
            hoverongaps=False,
            hovertemplate='Month: %{x}<br>Year: %{y}<br>Conversion Rate: %{z:.1%}<extra></extra>'
        ))
        
        # Update layout
        fig.update_layout(
            title=f'Seasonal Conversion Rate Patterns - {program}',
            xaxis_title='Month',
            yaxis_title='Year',
            height=400,
            margin=dict(l=80, r=80, t=80, b=80)
        )
        
        logger.info(f"Created seasonal heatmap with {len(heatmap_data)} years of data")
        
        return fig


class BudgetAllocator:
    """
    Provide data-driven budget allocation recommendations.
    """
    
    def __init__(
        self,
        channel_optimizer: ChannelOptimizer,
        forecaster: TimeSeriesForecaster
    ):
        """
        Initialize budget allocator with optimizer and forecaster.
        
        Args:
            channel_optimizer: Trained ChannelOptimizer instance
            forecaster: Trained TimeSeriesForecaster instance
        """
        self.channel_optimizer = channel_optimizer
        self.forecaster = forecaster
        
        logger.info("Initialized BudgetAllocator")
    
    def allocate_budget(
        self,
        total_budget: float,
        programs: List[str],
        constraints: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Allocate budget across programs and channels to maximize ROI.
        
        Args:
            total_budget: Total available marketing budget
            programs: List of program codes to include
            constraints: Optional dict with min/max allocations per program
                - 'min_per_program': Minimum budget per program (default: 0)
                - 'max_per_channel': Maximum budget per channel (default: total_budget * 0.5)
            
        Returns:
            DataFrame with columns [program, channel, allocated_budget, 
                                   expected_inquiries, expected_applications, 
                                   expected_enrollments, expected_roi, allocation_percentage]
        """
        logger.info(f"Allocating ${total_budget:,.2f} across {len(programs)} programs")
        
        if total_budget <= 0:
            raise ValueError("total_budget must be positive")
        
        if not programs:
            raise ValueError("programs list cannot be empty")
        
        # Set default constraints
        if constraints is None:
            constraints = {}
        
        min_per_program = constraints.get('min_per_program', 0)
        max_per_channel = constraints.get('max_per_channel', total_budget * 0.5)
        
        # Validate constraints
        if min_per_program < 0:
            raise ValueError("min_per_program must be non-negative")
        
        if max_per_channel <= 0:
            raise ValueError("max_per_channel must be positive")
        
        # Check if budget is too small for constraints
        if min_per_program > 0 and min_per_program * len(programs) > total_budget:
            raise ValueError(
                f"Budget too small: minimum per program (${min_per_program:,.2f}) "
                f"* {len(programs)} programs = ${min_per_program * len(programs):,.2f} "
                f"exceeds total budget ${total_budget:,.2f}"
            )
        
        # Collect all program-channel combinations with their ROI and effectiveness
        program_channel_combos = []
        
        for program in programs:
            # Get channel recommendations for this program
            channel_data = self.channel_optimizer.calculate_roi(program)
            
            if channel_data.empty:
                logger.warning(f"No channel data for program '{program}', skipping")
                continue
            
            # Calculate effectiveness scores
            channel_data = self.channel_optimizer._calculate_effectiveness_score(
                channel_data, program
            )
            
            # Add program column
            channel_data['program'] = program
            
            # Store combinations
            for _, row in channel_data.iterrows():
                program_channel_combos.append({
                    'program': program,
                    'channel': row['channel'],
                    'roi': row['roi'],
                    'effectiveness_score': row['effectiveness_score'],
                    'historical_spend': row['spend'],
                    'historical_conversions': row['conversions']
                })
        
        if not program_channel_combos:
            logger.warning("No valid program-channel combinations found")
            return pd.DataFrame(columns=[
                'program', 'channel', 'allocated_budget', 'expected_inquiries',
                'expected_applications', 'expected_enrollments', 'expected_roi',
                'allocation_percentage'
            ])
        
        # Convert to DataFrame for easier manipulation
        combos_df = pd.DataFrame(program_channel_combos)
        
        # Rank by effectiveness score (primary) and ROI (secondary)
        combos_df = combos_df.sort_values(
            ['effectiveness_score', 'roi'],
            ascending=[False, False]
        ).reset_index(drop=True)
        
        # Allocate budget iteratively to highest-ranked combinations
        allocations = []
        remaining_budget = total_budget
        program_allocations = {program: 0 for program in programs}
        channel_allocations = {}
        
        # First pass: ensure minimum per program if specified
        if min_per_program > 0:
            for program in programs:
                # Find best channel for this program
                program_combos = combos_df[combos_df['program'] == program]
                
                if not program_combos.empty:
                    best_combo = program_combos.iloc[0]
                    channel = best_combo['channel']
                    
                    # Allocate minimum budget
                    allocation_amount = min(min_per_program, remaining_budget)
                    
                    if allocation_amount > 0:
                        allocations.append({
                            'program': program,
                            'channel': channel,
                            'allocated_budget': allocation_amount,
                            'roi': best_combo['roi'],
                            'effectiveness_score': best_combo['effectiveness_score']
                        })
                        
                        remaining_budget -= allocation_amount
                        program_allocations[program] += allocation_amount
                        channel_allocations[channel] = channel_allocations.get(channel, 0) + allocation_amount
        
        # Second pass: allocate remaining budget to highest-ranked combinations
        for _, combo in combos_df.iterrows():
            if remaining_budget <= 0:
                break
            
            program = combo['program']
            channel = combo['channel']
            
            # Check if channel has reached max allocation
            current_channel_allocation = channel_allocations.get(channel, 0)
            if current_channel_allocation >= max_per_channel:
                continue
            
            # Calculate how much we can allocate to this combination
            # Use historical spend as a guide for allocation size
            max_additional_for_channel = max_per_channel - current_channel_allocation
            
            suggested_allocation = min(
                combo['historical_spend'] * 1.2,  # 20% increase over historical
                remaining_budget,
                max_additional_for_channel  # Don't exceed channel max
            )
            
            # Minimum allocation of $1000 per combination (or remaining budget if less)
            min_allocation = min(1000, remaining_budget)
            
            if suggested_allocation >= min_allocation:
                # Check if this program-channel combo already has an allocation
                existing_allocation = next(
                    (a for a in allocations if a['program'] == program and a['channel'] == channel),
                    None
                )
                
                if existing_allocation:
                    # Add to existing allocation (respecting channel max)
                    current_combo_allocation = existing_allocation['allocated_budget']
                    current_channel_total = channel_allocations.get(channel, 0)
                    
                    # Calculate how much more we can add
                    max_additional = min(
                        suggested_allocation,
                        remaining_budget,
                        max_per_channel - current_channel_total
                    )
                    
                    if max_additional > 0:
                        existing_allocation['allocated_budget'] += max_additional
                        remaining_budget -= max_additional
                        program_allocations[program] += max_additional
                        channel_allocations[channel] += max_additional
                else:
                    # Create new allocation
                    allocation_amount = min(suggested_allocation, remaining_budget, max_additional_for_channel)
                    
                    if allocation_amount > 0:
                        allocations.append({
                            'program': program,
                            'channel': channel,
                            'allocated_budget': allocation_amount,
                            'roi': combo['roi'],
                            'effectiveness_score': combo['effectiveness_score']
                        })
                        
                        remaining_budget -= allocation_amount
                        program_allocations[program] += allocation_amount
                        channel_allocations[channel] = channel_allocations.get(channel, 0) + allocation_amount
        
        # If there's still remaining budget, distribute proportionally to existing allocations
        # while respecting channel constraints
        if remaining_budget > 0 and allocations:
            total_allocated = sum(a['allocated_budget'] for a in allocations)
            
            # Try to distribute remaining budget proportionally
            for allocation in allocations:
                channel = allocation['channel']
                current_channel_total = channel_allocations.get(channel, 0)
                
                # Check if channel can accept more budget
                if current_channel_total < max_per_channel:
                    proportion = allocation['allocated_budget'] / total_allocated
                    additional = min(
                        remaining_budget * proportion,
                        max_per_channel - current_channel_total
                    )
                    
                    if additional > 0:
                        allocation['allocated_budget'] += additional
                        channel_allocations[channel] += additional
                        remaining_budget -= additional
                        
                        if remaining_budget <= 0:
                            break
        
        # Convert to DataFrame
        if not allocations:
            logger.warning("No allocations could be made with given constraints")
            return pd.DataFrame(columns=[
                'program', 'channel', 'allocated_budget', 'expected_inquiries',
                'expected_applications', 'expected_enrollments', 'expected_roi',
                'allocation_percentage'
            ])
        
        result_df = pd.DataFrame(allocations)
        
        # Validate budget constraint: total allocation should equal specified budget (within 1% tolerance)
        total_allocated = result_df['allocated_budget'].sum()
        budget_diff = abs(total_allocated - total_budget)
        budget_diff_pct = (budget_diff / total_budget) * 100
        
        if budget_diff_pct > 1.0:
            logger.warning(
                f"Budget allocation differs from target by {budget_diff_pct:.2f}% "
                f"(allocated: ${total_allocated:,.2f}, target: ${total_budget:,.2f})"
            )
            
            # Only adjust if we're under-allocated (not over-allocated due to constraints)
            if total_allocated < total_budget:
                # Adjust allocations proportionally to meet budget constraint
                # But respect channel constraints
                adjustment_needed = total_budget - total_allocated
                
                # Try to distribute the remaining budget
                for idx, row in result_df.iterrows():
                    if adjustment_needed <= 0:
                        break
                    
                    channel = row['channel']
                    current_channel_total = result_df[result_df['channel'] == channel]['allocated_budget'].sum()
                    
                    # Check if channel can accept more budget
                    if current_channel_total < max_per_channel:
                        max_additional = max_per_channel - current_channel_total
                        additional = min(adjustment_needed, max_additional)
                        
                        if additional > 0:
                            result_df.at[idx, 'allocated_budget'] += additional
                            adjustment_needed -= additional
                
                logger.info(f"Adjusted allocations to meet budget constraint")
        
        # Validate minimum per program constraint
        if min_per_program > 0:
            program_totals = result_df.groupby('program')['allocated_budget'].sum()
            
            for program in programs:
                if program in program_totals.index:
                    if program_totals[program] < min_per_program * 0.95:  # 5% tolerance
                        logger.warning(
                            f"Program '{program}' allocation ${program_totals[program]:,.2f} "
                            f"is below minimum ${min_per_program:,.2f}"
                        )
        
        # Validate maximum per channel constraint
        channel_totals = result_df.groupby('channel')['allocated_budget'].sum()
        for channel, total in channel_totals.items():
            if total > max_per_channel * 1.01:  # 1% tolerance
                logger.warning(
                    f"Channel '{channel}' allocation ${total:,.2f} "
                    f"exceeds maximum ${max_per_channel:,.2f}"
                )
                
                # This shouldn't happen with proper allocation logic
                # But if it does, cap it
                excess = total - max_per_channel
                channel_rows = result_df[result_df['channel'] == channel]
                
                # Reduce allocations proportionally
                for idx in channel_rows.index:
                    reduction = (result_df.at[idx, 'allocated_budget'] / total) * excess
                    result_df.at[idx, 'allocated_budget'] -= reduction
        
        # Calculate allocation percentages
        result_df['allocation_percentage'] = (
            result_df['allocated_budget'] / total_budget * 100
        )
        
        # Calculate expected outcomes using historical conversion rates and forecasting
        expected_outcomes = []
        
        for _, row in result_df.iterrows():
            program = row['program']
            channel = row['channel']
            allocated = row['allocated_budget']
            
            # Get historical performance for this program-channel combination
            historical_data = self.channel_optimizer.get_channel_performance_history(
                program, channel
            )
            
            if not historical_data.empty and historical_data['spend'].sum() > 0:
                # Calculate average conversion metrics from historical data
                total_historical_spend = historical_data['spend'].sum()
                total_historical_conversions = historical_data['conversions'].sum()
                
                # Calculate conversion rate (admissions per dollar spent)
                conversion_rate = total_historical_conversions / total_historical_spend if total_historical_spend > 0 else 0
                
                # Estimate expected enrollments based on allocated budget
                expected_enrollments = int(allocated * conversion_rate)
                
                # Get program admissions data to calculate inquiry and application rates
                program_admissions = self.channel_optimizer.admissions_data[
                    self.channel_optimizer.admissions_data['program'] == program
                ]
                
                if not program_admissions.empty:
                    # Calculate historical ratios
                    inquiries = program_admissions[
                        program_admissions['metric_name'] == 'inquiries_received'
                    ]['metric_value'].sum()
                    
                    applications = program_admissions[
                        program_admissions['metric_name'] == 'applications_received'
                    ]['metric_value'].sum()
                    
                    admissions = program_admissions[
                        program_admissions['metric_name'] == 'admissions_accepted'
                    ]['metric_value'].sum()
                    
                    # Calculate ratios (with defaults if data is missing)
                    if admissions > 0:
                        inquiry_to_admission_ratio = inquiries / admissions if inquiries > 0 else 10
                        application_to_admission_ratio = applications / admissions if applications > 0 else 3
                    else:
                        inquiry_to_admission_ratio = 10
                        application_to_admission_ratio = 3
                    
                    # Estimate inquiries and applications based on expected enrollments
                    expected_inquiries = int(expected_enrollments * inquiry_to_admission_ratio)
                    expected_applications = int(expected_enrollments * application_to_admission_ratio)
                else:
                    # Use default multipliers if no historical data
                    expected_inquiries = expected_enrollments * 10
                    expected_applications = expected_enrollments * 3
                
                # Calculate expected ROI
                tuition_estimate = self.channel_optimizer.TUITION_ESTIMATES.get(program, 50000)
                expected_value = expected_enrollments * tuition_estimate
                expected_roi = (expected_value - allocated) / allocated if allocated > 0 else 0
                
            else:
                # No historical data - use conservative estimates
                expected_inquiries = 0
                expected_applications = 0
                expected_enrollments = 0
                expected_roi = row['roi']  # Use historical ROI from channel data
            
            expected_outcomes.append({
                'expected_inquiries': expected_inquiries,
                'expected_applications': expected_applications,
                'expected_enrollments': expected_enrollments,
                'expected_roi': expected_roi
            })
        
        # Add expected outcomes to result DataFrame
        outcomes_df = pd.DataFrame(expected_outcomes)
        result_df['expected_inquiries'] = outcomes_df['expected_inquiries']
        result_df['expected_applications'] = outcomes_df['expected_applications']
        result_df['expected_enrollments'] = outcomes_df['expected_enrollments']
        result_df['expected_roi'] = outcomes_df['expected_roi']
        
        # Select and order columns
        result_df = result_df[[
            'program', 'channel', 'allocated_budget', 'expected_inquiries',
            'expected_applications', 'expected_enrollments', 'expected_roi',
            'allocation_percentage'
        ]]
        
        # Sort by allocated budget descending
        result_df = result_df.sort_values('allocated_budget', ascending=False).reset_index(drop=True)
        
        logger.info(f"Created {len(result_df)} budget allocations totaling ${result_df['allocated_budget'].sum():,.2f}")
        
        return result_df
    
    def sensitivity_analysis(
        self,
        base_allocation: pd.DataFrame,
        adjustment_pct: float = 0.2
    ) -> Dict[str, Any]:
        """
        Perform sensitivity analysis on budget allocation.
        
        Args:
            base_allocation: Base budget allocation from allocate_budget()
            adjustment_pct: Percentage adjustment for sensitivity (default ±20%)
            
        Returns:
            Dictionary with scenarios and expected outcomes:
            {
                'scenarios': {
                    'low': {'budget': float, 'allocations': DataFrame, 'outcomes': dict},
                    'base': {'budget': float, 'allocations': DataFrame, 'outcomes': dict},
                    'high': {'budget': float, 'allocations': DataFrame, 'outcomes': dict}
                },
                'summary': {
                    'budget_range': tuple,
                    'inquiries_range': tuple,
                    'applications_range': tuple,
                    'enrollments_range': tuple,
                    'roi_range': tuple
                }
            }
        """
        logger.info(f"Performing sensitivity analysis with ±{adjustment_pct*100}% adjustment")
        
        if base_allocation.empty:
            logger.warning("Empty base allocation provided")
            return {
                'scenarios': {},
                'summary': {}
            }
        
        # Calculate base budget
        base_budget = base_allocation['allocated_budget'].sum()
        
        # Extract programs from base allocation
        programs = base_allocation['program'].unique().tolist()
        
        # Extract constraints if any (approximate from base allocation)
        constraints = {}
        
        # Generate three scenarios: -20%, base, +20%
        scenarios = {}
        
        # Low scenario (-20%)
        low_budget = base_budget * (1 - adjustment_pct)
        logger.info(f"Generating low scenario with budget ${low_budget:,.2f}")
        
        try:
            low_allocation = self.allocate_budget(
                total_budget=low_budget,
                programs=programs,
                constraints=constraints
            )
            
            low_outcomes = {
                'total_inquiries': int(low_allocation['expected_inquiries'].sum()),
                'total_applications': int(low_allocation['expected_applications'].sum()),
                'total_enrollments': int(low_allocation['expected_enrollments'].sum()),
                'weighted_avg_roi': float(
                    (low_allocation['expected_roi'] * low_allocation['allocated_budget']).sum() / 
                    low_allocation['allocated_budget'].sum()
                ) if not low_allocation.empty else 0.0
            }
            
            scenarios['low'] = {
                'budget': low_budget,
                'allocations': low_allocation,
                'outcomes': low_outcomes
            }
        except Exception as e:
            logger.error(f"Error generating low scenario: {e}")
            scenarios['low'] = {
                'budget': low_budget,
                'allocations': pd.DataFrame(),
                'outcomes': {
                    'total_inquiries': 0,
                    'total_applications': 0,
                    'total_enrollments': 0,
                    'weighted_avg_roi': 0.0
                }
            }
        
        # Base scenario (current allocation)
        base_outcomes = {
            'total_inquiries': int(base_allocation['expected_inquiries'].sum()),
            'total_applications': int(base_allocation['expected_applications'].sum()),
            'total_enrollments': int(base_allocation['expected_enrollments'].sum()),
            'weighted_avg_roi': float(
                (base_allocation['expected_roi'] * base_allocation['allocated_budget']).sum() / 
                base_allocation['allocated_budget'].sum()
            ) if not base_allocation.empty else 0.0
        }
        
        scenarios['base'] = {
            'budget': base_budget,
            'allocations': base_allocation,
            'outcomes': base_outcomes
        }
        
        # High scenario (+20%)
        high_budget = base_budget * (1 + adjustment_pct)
        logger.info(f"Generating high scenario with budget ${high_budget:,.2f}")
        
        try:
            high_allocation = self.allocate_budget(
                total_budget=high_budget,
                programs=programs,
                constraints=constraints
            )
            
            high_outcomes = {
                'total_inquiries': int(high_allocation['expected_inquiries'].sum()),
                'total_applications': int(high_allocation['expected_applications'].sum()),
                'total_enrollments': int(high_allocation['expected_enrollments'].sum()),
                'weighted_avg_roi': float(
                    (high_allocation['expected_roi'] * high_allocation['allocated_budget']).sum() / 
                    high_allocation['allocated_budget'].sum()
                ) if not high_allocation.empty else 0.0
            }
            
            scenarios['high'] = {
                'budget': high_budget,
                'allocations': high_allocation,
                'outcomes': high_outcomes
            }
        except Exception as e:
            logger.error(f"Error generating high scenario: {e}")
            scenarios['high'] = {
                'budget': high_budget,
                'allocations': pd.DataFrame(),
                'outcomes': {
                    'total_inquiries': 0,
                    'total_applications': 0,
                    'total_enrollments': 0,
                    'weighted_avg_roi': 0.0
                }
            }
        
        # Create summary with ranges
        summary = {
            'budget_range': (low_budget, base_budget, high_budget),
            'inquiries_range': (
                scenarios['low']['outcomes']['total_inquiries'],
                scenarios['base']['outcomes']['total_inquiries'],
                scenarios['high']['outcomes']['total_inquiries']
            ),
            'applications_range': (
                scenarios['low']['outcomes']['total_applications'],
                scenarios['base']['outcomes']['total_applications'],
                scenarios['high']['outcomes']['total_applications']
            ),
            'enrollments_range': (
                scenarios['low']['outcomes']['total_enrollments'],
                scenarios['base']['outcomes']['total_enrollments'],
                scenarios['high']['outcomes']['total_enrollments']
            ),
            'roi_range': (
                scenarios['low']['outcomes']['weighted_avg_roi'],
                scenarios['base']['outcomes']['weighted_avg_roi'],
                scenarios['high']['outcomes']['weighted_avg_roi']
            )
        }
        
        logger.info(
            f"Sensitivity analysis complete: "
            f"Enrollments range {summary['enrollments_range'][0]}-{summary['enrollments_range'][2]}, "
            f"ROI range {summary['roi_range'][0]:.2f}-{summary['roi_range'][2]:.2f}"
        )
        
        return {
            'scenarios': scenarios,
            'summary': summary
        }


class ModelValidator:
    """
    Track model performance and validate predictions against actual outcomes.
    """
    
    def __init__(self, db_connection: sqlite3.Connection):
        """
        Initialize validator with database connection.
        
        Args:
            db_connection: SQLite database connection
        """
        self.conn = db_connection
        
        logger.info("Initialized ModelValidator")
    
    def store_prediction(
        self,
        model_type: str,
        program: str,
        cohort: str,
        prediction_date: str,
        forecast_date: str,
        metric: str,
        predicted_value: float,
        lower_bound: float,
        upper_bound: float
    ) -> None:
        """
        Store prediction in database for future validation.
        
        Args:
            model_type: Type of model used (e.g., 'prophet', 'arima', 'linear')
            program: Program code (e.g., 'MBA', 'ACCT')
            cohort: Cohort identifier (e.g., 'Class of 2026')
            prediction_date: Date when prediction was made (ISO format)
            forecast_date: Date being forecasted (ISO format)
            metric: Metric being predicted (e.g., 'inquiries_received')
            predicted_value: Point estimate prediction
            lower_bound: Lower bound of confidence interval
            upper_bound: Upper bound of confidence interval
        """
        logger.info(f"Storing prediction for {program} - {metric} on {forecast_date}")
        
        try:
            cursor = self.conn.cursor()
            
            insert_sql = """
            INSERT INTO model_predictions (
                model_type, program, cohort, prediction_date, forecast_date,
                metric, predicted_value, lower_bound, upper_bound
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(insert_sql, (
                model_type, program, cohort, prediction_date, forecast_date,
                metric, predicted_value, lower_bound, upper_bound
            ))
            
            self.conn.commit()
            logger.info(f"Successfully stored prediction (ID: {cursor.lastrowid})")
            
        except Exception as e:
            logger.error(f"Error storing prediction: {e}")
            self.conn.rollback()
            raise
    
    def validate_predictions(
        self,
        model_type: str,
        metric: str
    ) -> pd.DataFrame:
        """
        Validate stored predictions against actual outcomes.
        
        Args:
            model_type: Type of model to validate
            metric: Metric to validate
            
        Returns:
            DataFrame with columns [prediction_date, forecast_date, predicted, actual, error, pct_error]
        """
        logger.info(f"Validating {model_type} predictions for {metric}")
        
        try:
            # Query predictions with actual values
            query = """
            SELECT 
                p.id,
                p.model_type,
                p.program,
                p.cohort,
                p.prediction_date,
                p.forecast_date,
                p.metric,
                p.predicted_value,
                p.lower_bound,
                p.upper_bound,
                p.actual_value
            FROM model_predictions p
            WHERE p.model_type = ?
                AND p.metric = ?
                AND p.actual_value IS NOT NULL
            ORDER BY p.forecast_date
            """
            
            df = pd.read_sql_query(query, self.conn, params=(model_type, metric))
            
            if df.empty:
                logger.warning(f"No predictions with actual values found for {model_type} - {metric}")
                return pd.DataFrame(columns=[
                    'prediction_date', 'forecast_date', 'predicted', 'actual', 'error', 'pct_error'
                ])
            
            # Calculate errors
            df['error'] = df['actual_value'] - df['predicted_value']
            
            # Calculate percentage error (avoid division by zero)
            df['pct_error'] = np.where(
                df['actual_value'] != 0,
                (df['error'] / df['actual_value']) * 100,
                0.0
            )
            
            # Select and rename columns for output
            result = df[[
                'prediction_date', 'forecast_date', 'predicted_value', 
                'actual_value', 'error', 'pct_error'
            ]].copy()
            
            result.columns = [
                'prediction_date', 'forecast_date', 'predicted', 
                'actual', 'error', 'pct_error'
            ]
            
            logger.info(f"Validated {len(result)} predictions")
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating predictions: {e}")
            raise
    
    def calculate_accuracy_metrics(
        self,
        predictions: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Calculate accuracy metrics for predictions.
        
        Args:
            predictions: DataFrame with 'predicted' and 'actual' columns
            
        Returns:
            Dictionary with MAPE, RMSE, MAE, and accuracy_score
        """
        if predictions.empty:
            logger.warning("No predictions provided for accuracy calculation")
            return {
                'mape': None,
                'rmse': None,
                'mae': None,
                'accuracy_score': None,
                'predictions_count': 0
            }
        
        if 'predicted' not in predictions.columns or 'actual' not in predictions.columns:
            raise ValueError("predictions DataFrame must have 'predicted' and 'actual' columns")
        
        predicted = predictions['predicted'].values
        actual = predictions['actual'].values
        
        # Calculate MAE (Mean Absolute Error)
        mae = np.mean(np.abs(actual - predicted))
        
        # Calculate RMSE (Root Mean Squared Error)
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        
        # Calculate MAPE (Mean Absolute Percentage Error)
        # Avoid division by zero
        mask = actual != 0
        if mask.any():
            mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
        else:
            mape = 0.0
        
        # Calculate accuracy score as (1 - MAPE/100) * 100
        accuracy_score = max(0, (1 - mape / 100) * 100)
        
        metrics = {
            'mape': float(mape),
            'rmse': float(rmse),
            'mae': float(mae),
            'accuracy_score': float(accuracy_score),
            'predictions_count': len(predictions)
        }
        
        logger.info(f"Calculated accuracy metrics: MAPE={mape:.2f}%, RMSE={rmse:.2f}, MAE={mae:.2f}")
        
        return metrics
    
    def check_model_health(
        self,
        model_type: str,
        threshold_mape: float = 15.0
    ) -> Dict[str, Any]:
        """
        Check if model performance is within acceptable thresholds.
        
        Args:
            model_type: Type of model to check
            threshold_mape: MAPE threshold for acceptable performance (default 15%)
            
        Returns:
            Dictionary with status ('healthy', 'warning', 'needs_retraining'), 
            current_mape, and recommendation
        """
        logger.info(f"Checking health of {model_type} model (threshold: {threshold_mape}%)")
        
        try:
            # Get all metrics for this model type
            query = """
            SELECT DISTINCT metric
            FROM model_predictions
            WHERE model_type = ?
                AND actual_value IS NOT NULL
            """
            
            cursor = self.conn.cursor()
            cursor.execute(query, (model_type,))
            metrics = [row[0] for row in cursor.fetchall()]
            
            if not metrics:
                logger.warning(f"No validated predictions found for {model_type}")
                return {
                    'status': 'unknown',
                    'current_mape': None,
                    'recommendation': 'No validated predictions available. Generate predictions and wait for actual outcomes.',
                    'metrics_checked': []
                }
            
            # Calculate MAPE for each metric
            metric_mapes = {}
            for metric in metrics:
                predictions_df = self.validate_predictions(model_type, metric)
                if not predictions_df.empty:
                    accuracy_metrics = self.calculate_accuracy_metrics(predictions_df)
                    metric_mapes[metric] = accuracy_metrics['mape']
            
            if not metric_mapes:
                return {
                    'status': 'unknown',
                    'current_mape': None,
                    'recommendation': 'Unable to calculate MAPE. Check prediction data.',
                    'metrics_checked': metrics
                }
            
            # Calculate average MAPE across all metrics
            avg_mape = np.mean(list(metric_mapes.values()))
            
            # Determine status based on threshold
            if avg_mape <= threshold_mape:
                status = 'healthy'
                recommendation = f'Model performance is good (MAPE: {avg_mape:.2f}%). Continue monitoring.'
            elif avg_mape <= threshold_mape * 1.5:  # 1.5x threshold (22.5% for default)
                status = 'warning'
                recommendation = f'Model performance is degrading (MAPE: {avg_mape:.2f}%). Consider retraining soon.'
            else:
                status = 'needs_retraining'
                recommendation = f'Model performance is poor (MAPE: {avg_mape:.2f}%). Retraining recommended.'
            
            result = {
                'status': status,
                'current_mape': float(avg_mape),
                'threshold_mape': float(threshold_mape),
                'recommendation': recommendation,
                'metrics_checked': metrics,
                'metric_mapes': {k: float(v) for k, v in metric_mapes.items()}
            }
            
            logger.info(f"Model health check complete: {status} (MAPE: {avg_mape:.2f}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error checking model health: {e}")
            raise
    
    def compare_models(
        self,
        metric: str,
        model_types: List[str] = None
    ) -> pd.DataFrame:
        """
        Compare performance of multiple models for a specific metric.
        
        Args:
            metric: Metric to compare models for
            model_types: List of model types to compare (if None, compare all available)
            
        Returns:
            DataFrame with columns [model_type, mape, rmse, mae, accuracy_score, predictions_count]
            sorted by MAPE (best performing first)
        """
        logger.info(f"Comparing models for metric '{metric}'")
        
        try:
            # Get all model types if not specified
            if model_types is None:
                query = """
                SELECT DISTINCT model_type
                FROM model_predictions
                WHERE metric = ?
                    AND actual_value IS NOT NULL
                """
                cursor = self.conn.cursor()
                cursor.execute(query, (metric,))
                model_types = [row[0] for row in cursor.fetchall()]
            
            if not model_types:
                logger.warning(f"No models found for metric '{metric}'")
                return pd.DataFrame(columns=[
                    'model_type', 'mape', 'rmse', 'mae', 'accuracy_score', 'predictions_count'
                ])
            
            # Calculate metrics for each model
            comparison_results = []
            for model_type in model_types:
                predictions_df = self.validate_predictions(model_type, metric)
                
                if not predictions_df.empty:
                    accuracy_metrics = self.calculate_accuracy_metrics(predictions_df)
                    
                    comparison_results.append({
                        'model_type': model_type,
                        'mape': accuracy_metrics['mape'],
                        'rmse': accuracy_metrics['rmse'],
                        'mae': accuracy_metrics['mae'],
                        'accuracy_score': accuracy_metrics['accuracy_score'],
                        'predictions_count': accuracy_metrics['predictions_count']
                    })
            
            if not comparison_results:
                logger.warning(f"No validated predictions found for any model")
                return pd.DataFrame(columns=[
                    'model_type', 'mape', 'rmse', 'mae', 'accuracy_score', 'predictions_count'
                ])
            
            # Create DataFrame and sort by MAPE (lower is better)
            result_df = pd.DataFrame(comparison_results)
            result_df = result_df.sort_values('mape').reset_index(drop=True)
            
            logger.info(f"Compared {len(result_df)} models for metric '{metric}'")
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error comparing models: {e}")
            raise
    
    def get_best_model(
        self,
        metric: str,
        model_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Identify the best-performing model for a specific metric based on lowest MAPE.
        
        Args:
            metric: Metric to find best model for
            model_types: List of model types to consider (if None, consider all available)
            
        Returns:
            Dictionary with best_model_type, mape, and other performance metrics
        """
        logger.info(f"Finding best model for metric '{metric}'")
        
        comparison_df = self.compare_models(metric, model_types)
        
        if comparison_df.empty:
            logger.warning(f"No models available for comparison")
            return {
                'best_model_type': None,
                'mape': None,
                'rmse': None,
                'mae': None,
                'accuracy_score': None,
                'predictions_count': 0
            }
        
        # Best model is the one with lowest MAPE (first row after sorting)
        best_model = comparison_df.iloc[0].to_dict()
        best_model['best_model_type'] = best_model.pop('model_type')
        
        logger.info(f"Best model for '{metric}': {best_model['best_model_type']} (MAPE: {best_model['mape']:.2f}%)")
        
        return best_model
