"""
Cohort-Aware Forecasting System
Understands academic cohort cycles and seasonal patterns for more realistic predictions.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import sqlite3
from utils.ml_models import TimeSeriesForecaster

logger = logging.getLogger(__name__)


class CohortAwareForecaster:
    """
    Forecasting system that understands academic cohort progression patterns.
    
    Key Concepts:
    - Each cohort has its own lifecycle (Oct/Jan start → July end)
    - Cohorts follow similar growth patterns but at different scales
    - Seasonality is cohort-relative, not calendar-relative
    """
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.cohort_patterns = {}
        self.baseline_growth_rates = {}
        
    def analyze_cohort_patterns(self, program: str, metric: str) -> Dict[str, any]:
        """
        Analyze historical cohort patterns to understand:
        1. Starting values for each cohort
        2. Growth patterns within cohort lifecycle
        3. Month-to-month progression rates
        4. Seasonal factors within academic year
        """
        logger.info(f"Analyzing cohort patterns for {program} - {metric}")
        
        # Get historical cohort data
        data = pd.read_sql("""
            SELECT cohort_year, report_date, metric_value
            FROM admissions_metrics
            WHERE program = ? AND metric_name = ? AND cohort_season = 'fall'
            ORDER BY cohort_year, report_date
        """, self.conn, params=[program, metric])
        
        if data.empty:
            return {'error': 'No historical data available'}
        
        data['report_date'] = pd.to_datetime(data['report_date'])
        
        cohort_analysis = {}
        
        for cohort_year in data['cohort_year'].unique():
            cohort_data = data[data['cohort_year'] == cohort_year].copy()
            cohort_data = cohort_data.sort_values('report_date')
            
            if len(cohort_data) < 2:
                continue
                
            # Calculate cohort-relative months (0 = start, 1 = month 1, etc.)
            cohort_data['cohort_month'] = range(len(cohort_data))
            
            # Calculate month-to-month growth rates
            cohort_data['growth_rate'] = cohort_data['metric_value'].pct_change()
            
            # Calculate cumulative growth from start
            start_value = cohort_data['metric_value'].iloc[0]
            cohort_data['cumulative_growth'] = (cohort_data['metric_value'] / start_value) - 1
            
            cohort_analysis[cohort_year] = {
                'start_value': start_value,
                'end_value': cohort_data['metric_value'].iloc[-1],
                'total_growth': (cohort_data['metric_value'].iloc[-1] / start_value) - 1,
                'monthly_data': cohort_data[['cohort_month', 'metric_value', 'growth_rate', 'cumulative_growth']].to_dict('records'),
                'avg_monthly_growth': cohort_data['growth_rate'].mean(),
                'lifecycle_months': len(cohort_data)
            }
        
        # Calculate baseline patterns across cohorts
        baseline_pattern = self._calculate_baseline_pattern(cohort_analysis)
        
        return {
            'cohort_analysis': cohort_analysis,
            'baseline_pattern': baseline_pattern,
            'available_cohorts': list(cohort_analysis.keys())
        }
    
    def _calculate_baseline_pattern(self, cohort_analysis: Dict) -> Dict:
        """Calculate average growth patterns across all cohorts including volatility analysis"""
        if not cohort_analysis:
            return {}
        
        # Find the maximum lifecycle length
        max_months = max([info['lifecycle_months'] for info in cohort_analysis.values()])
        
        # Calculate average growth rates by cohort month
        monthly_growth_rates = {}
        monthly_cumulative_growth = {}
        monthly_volatility = {}
        
        for month in range(max_months):
            growth_rates = []
            cumulative_growths = []
            
            for cohort_info in cohort_analysis.values():
                monthly_data = cohort_info['monthly_data']
                if month < len(monthly_data):
                    if not pd.isna(monthly_data[month]['growth_rate']):
                        growth_rates.append(monthly_data[month]['growth_rate'])
                    cumulative_growths.append(monthly_data[month]['cumulative_growth'])
            
            if growth_rates:
                monthly_growth_rates[month] = np.mean(growth_rates)
                monthly_volatility[month] = np.std(growth_rates)  # Capture volatility
            if cumulative_growths:
                monthly_cumulative_growth[month] = np.mean(cumulative_growths)
        
        # Calculate average starting values and total growth
        start_values = [info['start_value'] for info in cohort_analysis.values()]
        total_growths = [info['total_growth'] for info in cohort_analysis.values()]
        
        # Analyze fluctuation patterns
        fluctuation_analysis = self._analyze_fluctuation_patterns(cohort_analysis)
        
        return {
            'avg_start_value': np.mean(start_values),
            'avg_total_growth': np.mean(total_growths),
            'monthly_growth_rates': monthly_growth_rates,
            'monthly_cumulative_growth': monthly_cumulative_growth,
            'monthly_volatility': monthly_volatility,
            'start_value_range': (min(start_values), max(start_values)),
            'total_growth_range': (min(total_growths), max(total_growths)),
            'fluctuation_patterns': fluctuation_analysis
        }
    
    def _analyze_fluctuation_patterns(self, cohort_analysis: Dict) -> Dict:
        """
        Analyze historical fluctuation patterns to understand natural ups and downs.
        
        Returns patterns like:
        - Which months typically see increases vs decreases
        - Average magnitude of fluctuations
        - Seasonal volatility patterns
        """
        all_changes = []
        monthly_change_patterns = {}
        
        for cohort_year, cohort_info in cohort_analysis.items():
            monthly_data = cohort_info['monthly_data']
            
            for i, month_data in enumerate(monthly_data):
                if not pd.isna(month_data['growth_rate']):
                    change_pct = month_data['growth_rate'] * 100
                    all_changes.append(change_pct)
                    
                    # Track patterns by cohort month
                    cohort_month = month_data['cohort_month']
                    if cohort_month not in monthly_change_patterns:
                        monthly_change_patterns[cohort_month] = []
                    monthly_change_patterns[cohort_month].append(change_pct)
        
        # Calculate statistics
        if all_changes:
            avg_change = np.mean(all_changes)
            volatility = np.std(all_changes)
            positive_changes = len([c for c in all_changes if c > 0])
            negative_changes = len([c for c in all_changes if c < 0])
            
            # Calculate monthly patterns
            monthly_patterns = {}
            for month, changes in monthly_change_patterns.items():
                monthly_patterns[month] = {
                    'avg_change': np.mean(changes),
                    'volatility': np.std(changes),
                    'positive_ratio': len([c for c in changes if c > 0]) / len(changes)
                }
        else:
            avg_change = 5.0  # Default 5% growth
            volatility = 3.0   # Default 3% volatility
            positive_changes = 7
            negative_changes = 1
            monthly_patterns = {}
        
        return {
            'avg_monthly_change_pct': avg_change,
            'monthly_volatility_pct': volatility,
            'positive_change_ratio': positive_changes / (positive_changes + negative_changes),
            'monthly_patterns': monthly_patterns,
            'total_data_points': len(all_changes)
        }
    
    def predict_new_cohort(
        self, 
        program: str, 
        metric: str, 
        target_cohort: int,
        prediction_months: int = 8,
        confidence_level: float = 0.95
    ) -> Dict[str, any]:
        """
        Predict values for a new cohort based on historical cohort patterns.
        
        This method:
        1. Analyzes historical cohort patterns
        2. Estimates a realistic starting value for the new cohort
        3. Applies learned growth patterns to predict progression
        4. Accounts for trend changes between cohorts
        5. CORRECTLY predicts the cohort's lifecycle timeline, not extension beyond it
        """
        logger.info(f"Predicting new cohort {target_cohort} for {program} - {metric}")
        
        # Analyze historical patterns
        pattern_analysis = self.analyze_cohort_patterns(program, metric)
        
        if 'error' in pattern_analysis:
            return pattern_analysis
        
        cohort_analysis = pattern_analysis['cohort_analysis']
        baseline_pattern = pattern_analysis['baseline_pattern']
        
        if not cohort_analysis:
            return {'error': 'No cohort patterns found'}
        
        # Estimate starting value for new cohort
        predicted_start_value = self._estimate_cohort_start_value(
            cohort_analysis, target_cohort, baseline_pattern
        )
        
        # CRITICAL FIX: Determine the correct timeline for the target cohort
        prediction_start_date = self._get_cohort_start_date(target_cohort, cohort_analysis)
        
        # Generate month-by-month predictions
        predictions = self._generate_cohort_predictions(
            predicted_start_value,
            baseline_pattern,
            prediction_months,
            confidence_level
        )
        
        # Create prediction dates starting from the cohort's actual lifecycle start
        prediction_dates = [prediction_start_date + pd.DateOffset(months=i) for i in range(prediction_months)]
        
        # Format results
        result_df = pd.DataFrame({
            'date': prediction_dates,
            'predicted_value': predictions['values'],
            'lower_bound': predictions['lower_bounds'],
            'upper_bound': predictions['upper_bounds'],
            'cohort_month': range(prediction_months)
        })
        
        return {
            'success': True,
            'predictions': result_df,
            'predicted_start_value': predicted_start_value,
            'prediction_start_date': prediction_start_date,
            'methodology': 'cohort_aware_forecasting',
            'pattern_analysis': pattern_analysis,
            'confidence_level': confidence_level
        }
    
    def _get_cohort_start_date(self, target_cohort: int, cohort_analysis: Dict) -> pd.Timestamp:
        """
        Dynamically determine the correct start date for a target cohort's lifecycle
        based on actual historical data patterns, not hardcoded formulas.
        """
        # First, try to get actual start date if we have data for this cohort
        if str(target_cohort) in cohort_analysis:
            cohort_info = cohort_analysis[str(target_cohort)]
            monthly_data = cohort_info.get('monthly_data', [])
            if monthly_data:
                # We have actual data - find the earliest date
                first_month_data = monthly_data[0]  # Should be cohort_month 0
                # Calculate actual start date from the data
                # This is the most accurate method
                return pd.Timestamp(first_month_data.get('date', f'{target_cohort-3}-10-01'))
        
        # If no actual data, analyze historical patterns to predict start date
        historical_starts = {}
        
        # Analyze all available historical cohorts to find the pattern
        for cohort_year_str, cohort_info in cohort_analysis.items():
            try:
                cohort_year = int(cohort_year_str)
                monthly_data = cohort_info.get('monthly_data', [])
                if monthly_data and len(monthly_data) > 0:
                    # Get the first data point to infer start date
                    first_data = monthly_data[0]
                    if 'date' in first_data:
                        start_date = pd.to_datetime(first_data['date'])
                        historical_starts[cohort_year] = start_date
                        logger.info(f"Historical pattern: Class {cohort_year} started {start_date.strftime('%B %Y')}")
            except (ValueError, KeyError) as e:
                continue
        
        # If we have historical patterns, use them to predict
        if len(historical_starts) >= 2:
            # Analyze the pattern between cohorts
            sorted_cohorts = sorted(historical_starts.keys())
            
            # Calculate the typical gap between cohort starts
            gaps = []
            for i in range(1, len(sorted_cohorts)):
                prev_cohort = sorted_cohorts[i-1]
                curr_cohort = sorted_cohorts[i]
                prev_start = historical_starts[prev_cohort]
                curr_start = historical_starts[curr_cohort]
                
                # Calculate months between starts
                months_diff = (curr_start.year - prev_start.year) * 12 + (curr_start.month - prev_start.month)
                gaps.append(months_diff)
                logger.info(f"Gap between Class {prev_cohort} and {curr_cohort}: {months_diff} months")
            
            if gaps:
                # Use the most recent gap pattern
                avg_gap = int(np.mean(gaps))
                logger.info(f"Average gap between cohort starts: {avg_gap} months")
                
                # Find the most recent cohort we have data for
                latest_cohort = max(historical_starts.keys())
                latest_start = historical_starts[latest_cohort]
                
                # Calculate how many cohorts ahead the target is
                cohorts_ahead = target_cohort - latest_cohort
                
                # Predict start date
                predicted_start = latest_start + pd.DateOffset(months=avg_gap * cohorts_ahead)
                logger.info(f"Predicted start for Class {target_cohort}: {predicted_start.strftime('%B %Y')} (based on {cohorts_ahead} cohorts ahead of Class {latest_cohort})")
                
                return predicted_start
        
        # Fallback: Use database query to get actual start dates
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT cohort_year, MIN(report_date) as start_date
                FROM admissions_metrics 
                WHERE cohort_year IN (2026, 2027, 2028)
                GROUP BY cohort_year
                ORDER BY cohort_year
            """)
            
            db_starts = {}
            for cohort_year, start_date in cursor.fetchall():
                if start_date:
                    db_starts[cohort_year] = pd.to_datetime(start_date)
                    logger.info(f"Database: Class {cohort_year} started {pd.to_datetime(start_date).strftime('%B %Y')}")
            
            # If we have the target cohort in database, use it
            if target_cohort in db_starts:
                logger.info(f"Using actual database start date for Class {target_cohort}")
                return db_starts[target_cohort]
            
            # Otherwise, predict based on database pattern
            if len(db_starts) >= 2:
                sorted_db_cohorts = sorted(db_starts.keys())
                latest_db_cohort = max(db_starts.keys())
                latest_db_start = db_starts[latest_db_cohort]
                
                # Calculate average gap from database
                db_gaps = []
                for i in range(1, len(sorted_db_cohorts)):
                    prev_cohort = sorted_db_cohorts[i-1]
                    curr_cohort = sorted_db_cohorts[i]
                    prev_start = db_starts[prev_cohort]
                    curr_start = db_starts[curr_cohort]
                    months_diff = (curr_start.year - prev_start.year) * 12 + (curr_start.month - prev_start.month)
                    db_gaps.append(months_diff)
                
                if db_gaps:
                    avg_db_gap = int(np.mean(db_gaps))
                    cohorts_ahead = target_cohort - latest_db_cohort
                    predicted_start = latest_db_start + pd.DateOffset(months=avg_db_gap * cohorts_ahead)
                    logger.info(f"Database-based prediction for Class {target_cohort}: {predicted_start.strftime('%B %Y')}")
                    return predicted_start
                    
        except Exception as e:
            logger.warning(f"Could not query database for cohort start dates: {e}")
        
        # Final fallback: Use the most recent known pattern
        # From actual data: Class 2028 starts October 2025
        if target_cohort == 2028:
            return pd.Timestamp('2025-10-01')
        elif target_cohort == 2029:
            # Assume similar pattern: ~12 months after Class 2028
            return pd.Timestamp('2026-10-01')
        else:
            # Generic fallback
            estimated_year = target_cohort - 3
            return pd.Timestamp(f'{estimated_year}-10-01')
    
    def predict_historical_cohort(
        self,
        program: str,
        metric: str,
        target_cohort: int,
        training_cohorts: List[int],
        prediction_months: int = 8,
        confidence_level: float = 0.95
    ) -> Dict[str, any]:
        """
        Predict a historical cohort's lifecycle for validation purposes.
        
        This is used when you want to:
        - Train on Class 2026
        - Predict Class 2027's FULL LIFECYCLE (Nov 2024 → June 2025)
        - Compare predictions against actual Class 2027 data for validation
        
        Args:
            target_cohort: The cohort to predict (e.g., 2027)
            training_cohorts: Cohorts to train on (e.g., [2026])
        """
        logger.info(f"Predicting historical cohort {target_cohort} using training cohorts {training_cohorts}")
        
        # Get all cohort data
        all_data = pd.read_sql("""
            SELECT cohort_year, report_date, metric_value
            FROM admissions_metrics
            WHERE program = ? AND metric_name = ? AND cohort_season = 'fall'
            ORDER BY cohort_year, report_date
        """, self.conn, params=[program, metric])
        
        if all_data.empty:
            return {'error': 'No historical data available'}
        
        all_data['report_date'] = pd.to_datetime(all_data['report_date'])
        
        # Separate training and target data
        training_data = all_data[all_data['cohort_year'].isin(training_cohorts)]
        target_actual_data = all_data[all_data['cohort_year'] == target_cohort]
        
        if training_data.empty:
            return {'error': f'No training data available for cohorts {training_cohorts}'}
        
        if target_actual_data.empty:
            return {'error': f'No actual data available for target cohort {target_cohort}'}
        
        # Analyze patterns from training cohorts only
        training_analysis = {}
        for cohort in training_cohorts:
            cohort_data = training_data[training_data['cohort_year'] == cohort].copy()
            if not cohort_data.empty:
                cohort_data = cohort_data.sort_values('report_date')
                cohort_data['cohort_month'] = range(len(cohort_data))
                cohort_data['growth_rate'] = cohort_data['metric_value'].pct_change()
                
                start_value = cohort_data['metric_value'].iloc[0]
                cohort_data['cumulative_growth'] = (cohort_data['metric_value'] / start_value) - 1
                
                training_analysis[cohort] = {
                    'start_value': start_value,
                    'end_value': cohort_data['metric_value'].iloc[-1],
                    'total_growth': (cohort_data['metric_value'].iloc[-1] / start_value) - 1,
                    'monthly_data': cohort_data[['cohort_month', 'metric_value', 'growth_rate', 'cumulative_growth']].to_dict('records'),
                    'avg_monthly_growth': cohort_data['growth_rate'].mean(),
                    'lifecycle_months': len(cohort_data)
                }
        
        # Calculate baseline pattern from training data
        baseline_pattern = self._calculate_baseline_pattern(training_analysis)
        
        # Estimate starting value for target cohort
        predicted_start_value = self._estimate_cohort_start_value(
            training_analysis, target_cohort, baseline_pattern
        )
        
        # Get the actual start date of the target cohort
        target_start_date = target_actual_data['report_date'].min()
        target_lifecycle_months = len(target_actual_data)
        
        # CRITICAL FIX: Use user-requested prediction_months instead of limiting to actual data length
        # This allows predicting the full requested period (e.g., 8 months) even if only 3 months of actual data exist
        actual_prediction_months = max(prediction_months, target_lifecycle_months)
        
        logger.info(f"Predicting {actual_prediction_months} months for Class {target_cohort} (requested: {prediction_months}, actual data: {target_lifecycle_months})")
        
        # Generate predictions for the user-requested timeline
        predictions = self._generate_cohort_predictions(
            predicted_start_value,
            baseline_pattern,
            actual_prediction_months,  # Use requested prediction period
            confidence_level
        )
        
        # Create prediction dates for the full requested period
        prediction_dates = [target_start_date + pd.DateOffset(months=i) for i in range(actual_prediction_months)]
        
        # Format results
        result_df = pd.DataFrame({
            'date': prediction_dates,
            'predicted_value': predictions['values'],
            'lower_bound': predictions['lower_bounds'],
            'upper_bound': predictions['upper_bounds'],
            'cohort_month': range(actual_prediction_months)
        })
        
        # Add actual values for comparison (pad with NaN for months beyond actual data)
        actual_values = target_actual_data.sort_values('report_date')['metric_value'].tolist()
        
        # Extend actual values with NaN for months beyond available data
        while len(actual_values) < actual_prediction_months:
            actual_values.append(np.nan)
        
        result_df['actual_value'] = actual_values[:actual_prediction_months]
        
        # Calculate validation metrics only for months where we have actual data
        predicted_values = predictions['values'][:target_lifecycle_months]
        actual_values_for_validation = actual_values[:target_lifecycle_months]
        mape = np.mean(np.abs((np.array(actual_values_for_validation) - np.array(predicted_values)) / np.array(actual_values_for_validation))) * 100
        mae = np.mean(np.abs(np.array(actual_values_for_validation) - np.array(predicted_values)))
        rmse = np.sqrt(np.mean((np.array(actual_values_for_validation) - np.array(predicted_values)) ** 2))
        
        return {
            'success': True,
            'predictions': result_df,
            'predicted_start_value': predicted_start_value,
            'actual_start_value': actual_values_for_validation[0] if actual_values_for_validation else None,
            'target_start_date': target_start_date,
            'methodology': 'historical_cohort_prediction',
            'training_cohorts': training_cohorts,
            'target_cohort': target_cohort,
            'validation_metrics': {
                'mape': mape,
                'mae': mae,
                'rmse': rmse
            },
            'confidence_level': confidence_level
        }
    
    def _estimate_cohort_start_value(
        self, 
        cohort_analysis: Dict, 
        target_cohort: int, 
        baseline_pattern: Dict
    ) -> float:
        """
        Estimate the starting value for a new cohort based on:
        1. Historical starting values
        2. Trend in starting values across cohorts
        3. Overall program growth
        """
        cohort_years = sorted(cohort_analysis.keys())
        start_values = [cohort_analysis[year]['start_value'] for year in cohort_years]
        
        if len(start_values) == 1:
            # Only one historical cohort - use baseline with small growth
            return start_values[0] * 1.1  # Assume 10% growth
        
        # Calculate trend in starting values
        if len(start_values) >= 2:
            # Linear trend in starting values
            years_diff = cohort_years[-1] - cohort_years[0]
            value_diff = start_values[-1] - start_values[0]
            
            if years_diff > 0:
                annual_start_growth = value_diff / years_diff
                years_to_target = target_cohort - cohort_years[-1]
                
                # Project starting value
                projected_start = start_values[-1] + (annual_start_growth * years_to_target)
                
                # Apply bounds checking (don't let it go below 50% or above 200% of recent values)
                recent_avg = np.mean(start_values[-2:]) if len(start_values) >= 2 else start_values[-1]
                projected_start = max(recent_avg * 0.5, min(projected_start, recent_avg * 2.0))
                
                return projected_start
        
        # Fallback: use average starting value with slight growth
        return baseline_pattern['avg_start_value'] * 1.05
    
    def _generate_cohort_predictions(
        self,
        start_value: float,
        baseline_pattern: Dict,
        prediction_months: int,
        confidence_level: float
    ) -> Dict[str, List[float]]:
        """
        Generate month-by-month predictions for a cohort lifecycle with realistic fluctuations.
        
        This enhanced version includes:
        - Natural ups and downs based on academic marketing cycles
        - Seasonal effects (holiday dips, application rushes)
        - Campaign-driven variations
        - Market volatility patterns
        """
        predictions = []
        lower_bounds = []
        upper_bounds = []
        
        current_value = start_value
        
        # Define realistic fluctuation patterns for academic marketing
        # Start with default patterns, then override with historical data if available
        monthly_volatility_factors = {
            0: 1.0,    # January - Starting point
            1: 1.15,   # February - Post-holiday campaign boost
            2: 0.95,   # March - Mid-semester dip
            3: 1.25,   # April - Spring campaign push
            4: 1.10,   # May - Steady growth
            5: 0.90,   # June - Summer slowdown
            6: 1.05,   # July - Final push before deadline
            7: 0.85,   # August - Post-deadline drop (if extending)
        }
        
        # Override with historical patterns if available
        if 'fluctuation_patterns' in baseline_pattern:
            fluctuation_data = baseline_pattern['fluctuation_patterns']
            monthly_patterns = fluctuation_data.get('monthly_patterns', {})
            
            for month, pattern in monthly_patterns.items():
                if month < prediction_months:
                    # Use historical volatility but ensure some variation
                    base_factor = 1.0 + (pattern['avg_change'] / 100)  # Convert percentage to factor
                    volatility = pattern['volatility'] / 100
                    
                    # Add some controlled randomness based on historical volatility
                    random_adjustment = np.random.normal(0, volatility)
                    monthly_volatility_factors[month] = max(0.8, min(1.3, base_factor + random_adjustment))
        
        # Add some randomness to make it more realistic
        np.random.seed(42)  # For reproducible results
        base_volatility = baseline_pattern.get('fluctuation_patterns', {}).get('monthly_volatility_pct', 5.0) / 100
        random_factors = np.random.normal(1.0, base_volatility, prediction_months)  # Historical volatility
        
        for month in range(prediction_months):
            if month == 0:
                # First month is the starting value
                predicted_value = start_value
            else:
                # Base growth from historical patterns
                if month in baseline_pattern['monthly_cumulative_growth']:
                    # Use learned cumulative growth pattern
                    base_cumulative_growth = baseline_pattern['monthly_cumulative_growth'][month]
                    base_predicted_value = start_value * (1 + base_cumulative_growth)
                else:
                    # Extrapolate using average growth rate
                    avg_monthly_growth = baseline_pattern.get('avg_total_growth', 0.5) / 8  # Spread over 8 months
                    base_predicted_value = current_value * (1 + avg_monthly_growth)
                
                # Apply volatility factor for realistic fluctuations
                volatility_factor = monthly_volatility_factors.get(month, 1.0)
                random_factor = random_factors[month]
                
                # Combine base growth with volatility
                predicted_value = base_predicted_value * volatility_factor * random_factor
                
                # Ensure we don't go below previous month by more than 15% (realistic constraint)
                min_allowed = current_value * 0.85
                predicted_value = max(predicted_value, min_allowed)
                
                # Also ensure overall upward trend (cohorts generally grow over time)
                if month > 2:  # After first few months, enforce minimum growth
                    min_growth_value = start_value * (1 + (month * 0.05))  # Minimum 5% growth per month
                    predicted_value = max(predicted_value, min_growth_value)
            
            # Calculate confidence intervals with realistic uncertainty
            # Academic marketing has higher uncertainty than other domains
            cv = 0.20  # 20% coefficient of variation (higher than before for realism)
            std_error = predicted_value * cv
            
            # Calculate bounds using normal distribution approximation
            z_score = 1.96 if confidence_level == 0.95 else 2.58  # 95% or 99%
            margin_error = z_score * std_error
            
            lower_bound = max(0, predicted_value - margin_error)  # Don't go below 0
            upper_bound = predicted_value + margin_error
            
            predictions.append(predicted_value)
            lower_bounds.append(lower_bound)
            upper_bounds.append(upper_bound)
            
            current_value = predicted_value
        
        return {
            'values': predictions,
            'lower_bounds': lower_bounds,
            'upper_bounds': upper_bounds
        }
    
    def compare_forecasting_methods(
        self,
        program: str,
        metric: str,
        target_cohort: int,
        prediction_months: int = 8
    ) -> Dict[str, any]:
        """
        Compare cohort-aware forecasting with traditional time series forecasting.
        """
        logger.info(f"Comparing forecasting methods for {program} - {metric}")
        
        # Method 1: Cohort-aware forecasting
        cohort_result = self.predict_new_cohort(
            program, metric, target_cohort, prediction_months
        )
        
        # Method 2: Traditional time series forecasting
        # Get all historical data as continuous time series
        data = pd.read_sql("""
            SELECT report_date, metric_value
            FROM admissions_metrics
            WHERE program = ? AND metric_name = ? AND cohort_season = 'fall'
            ORDER BY report_date
        """, self.conn, params=[program, metric])
        
        if not data.empty:
            data['report_date'] = pd.to_datetime(data['report_date'])
            data = data.rename(columns={'report_date': 'date'})
            
            # Traditional forecasting
            traditional_forecaster = TimeSeriesForecaster(data, metric)
            traditional_forecaster.fit(model_type='auto')
            traditional_predictions = traditional_forecaster.predict(periods=prediction_months)
            
            traditional_result = {
                'success': True,
                'predictions': traditional_predictions,
                'methodology': 'traditional_time_series'
            }
        else:
            traditional_result = {'error': 'No data for traditional forecasting'}
        
        return {
            'cohort_aware': cohort_result,
            'traditional': traditional_result,
            'comparison_summary': self._create_comparison_summary(cohort_result, traditional_result)
        }
    
    def _create_comparison_summary(self, cohort_result: Dict, traditional_result: Dict) -> Dict:
        """Create a summary comparing the two forecasting approaches."""
        if 'error' in cohort_result or 'error' in traditional_result:
            return {'error': 'Cannot compare due to missing data'}
        
        cohort_preds = cohort_result['predictions']['predicted_value'].tolist()
        traditional_preds = traditional_result['predictions']['forecast'].tolist()
        
        # Compare starting values
        cohort_start = cohort_preds[0]
        traditional_start = traditional_preds[0]
        
        # Compare ending values
        cohort_end = cohort_preds[-1]
        traditional_end = traditional_preds[-1]
        
        # Compare growth patterns
        cohort_growth = (cohort_end / cohort_start - 1) * 100
        traditional_growth = (traditional_end / traditional_start - 1) * 100
        
        return {
            'starting_values': {
                'cohort_aware': cohort_start,
                'traditional': traditional_start,
                'difference_pct': ((cohort_start / traditional_start - 1) * 100) if traditional_start > 0 else 0
            },
            'ending_values': {
                'cohort_aware': cohort_end,
                'traditional': traditional_end,
                'difference_pct': ((cohort_end / traditional_end - 1) * 100) if traditional_end > 0 else 0
            },
            'growth_patterns': {
                'cohort_aware_growth_pct': cohort_growth,
                'traditional_growth_pct': traditional_growth
            },
            'recommendation': self._get_method_recommendation(cohort_growth, traditional_growth, cohort_start, traditional_start)
        }
    
    def _get_method_recommendation(self, cohort_growth: float, traditional_growth: float, cohort_start: float, traditional_start: float) -> str:
        """Provide recommendation on which method to use."""
        
        # Cohort-aware is generally better for academic programs because:
        # 1. It respects cohort lifecycle patterns
        # 2. It starts with realistic baseline values
        # 3. It accounts for academic seasonality
        
        if cohort_start < traditional_start * 0.5:
            return "Cohort-aware recommended: More realistic starting values for new cohort lifecycle"
        elif abs(cohort_growth - 50) < abs(traditional_growth - 50):  # 50% is typical academic growth
            return "Cohort-aware recommended: Growth pattern more aligned with academic cycles"
        else:
            return "Both methods viable: Consider using cohort-aware for new cohorts, traditional for trend analysis"