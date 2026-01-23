"""
Validation and error handling module for Predictive Analytics & Machine Learning.
Provides input validation, bounds checking, and error logging utilities.
"""

import pandas as pd
import numpy as np
import logging
import sqlite3
from typing import Optional, List, Tuple, Any, Dict
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Valid program codes
VALID_PROGRAMS = [
    'MBA', 'ACCT', 'MS ACCT', 'HRM', 'MS HRM', 
    'MISY', 'MS MISY', 'MKTG', 'MS MKTG', 
    'ENLD', 'MS ENLD', 'SPBA', 'MS SPBA'
]

# Valid metrics
VALID_METRICS = [
    'inquiries_received', 'applications_received', 'applications_complete',
    'admissions_offered', 'admissions_accepted', 'anticipated_cohort_size'
]

# Valid marketing channels
VALID_CHANNELS = [
    'Search', 'Display', 'LinkedIn', 'Meta', 'YouTube', 'OOH'
]


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class InputValidator:
    """
    Validates user inputs for predictive analytics operations.
    Provides clear error messages for invalid inputs.
    """
    
    @staticmethod
    def validate_program(program: str) -> Tuple[bool, Optional[str]]:
        """
        Validate program code.
        
        Args:
            program: Program code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not program:
            return False, "Program code cannot be empty"
        
        if program not in VALID_PROGRAMS:
            return False, (
                f"Invalid program code '{program}'. "
                f"Valid programs are: {', '.join(VALID_PROGRAMS)}"
            )
        
        return True, None
    
    @staticmethod
    def validate_cohort(cohort: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate cohort year.
        
        Args:
            cohort: Cohort year to validate (int or string)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if cohort is None:
            # Cohort is optional in some contexts
            return True, None
        
        try:
            # Convert to int if string
            if isinstance(cohort, str):
                # Handle "Class of YYYY" format
                if cohort.startswith("Class of "):
                    cohort_year = int(cohort.replace("Class of ", ""))
                else:
                    cohort_year = int(cohort)
            else:
                cohort_year = int(cohort)
            
            # Validate year range (reasonable range: 2020-2035)
            current_year = datetime.now().year
            if cohort_year < 2020 or cohort_year > current_year + 10:
                return False, (
                    f"Cohort year {cohort_year} is outside valid range (2020-{current_year + 10})"
                )
            
            return True, None
            
        except (ValueError, TypeError):
            return False, f"Invalid cohort format '{cohort}'. Expected year (e.g., 2026) or 'Class of YYYY'"
    
    @staticmethod
    def validate_date_range(
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate date range.
        
        Args:
            start_date: Start date in ISO format (YYYY-MM-DD) or None
            end_date: End date in ISO format (YYYY-MM-DD) or None
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if start_date is None and end_date is None:
            # Both None is valid (no filtering)
            return True, None
        
        try:
            if start_date:
                start_dt = pd.to_datetime(start_date)
                
                # Check if date is not too far in the past
                if start_dt.year < 2020:
                    return False, f"Start date {start_date} is before 2020 (no data available)"
            
            if end_date:
                end_dt = pd.to_datetime(end_date)
                
                # Check if date is not in the future
                if end_dt > pd.Timestamp.now():
                    return False, f"End date {end_date} is in the future"
            
            # If both provided, check that start <= end
            if start_date and end_date:
                if start_dt > end_dt:
                    return False, f"Start date {start_date} is after end date {end_date}"
            
            return True, None
            
        except (ValueError, TypeError) as e:
            return False, f"Invalid date format. Expected ISO format (YYYY-MM-DD): {str(e)}"
    
    @staticmethod
    def validate_budget(budget: float) -> Tuple[bool, Optional[str]]:
        """
        Validate budget amount.
        
        Args:
            budget: Budget amount to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if budget is None:
            return False, "Budget amount cannot be None"
        
        try:
            budget_float = float(budget)
            
            if budget_float <= 0:
                return False, f"Budget must be positive, got ${budget_float:,.2f}"
            
            # Check for unreasonably large budgets (> $10M)
            if budget_float > 10_000_000:
                return False, (
                    f"Budget ${budget_float:,.2f} exceeds reasonable maximum ($10,000,000). "
                    "Please verify the amount."
                )
            
            # Check for unreasonably small budgets (< $100)
            if budget_float < 100:
                return False, (
                    f"Budget ${budget_float:,.2f} is below minimum ($100). "
                    "Please specify a larger budget."
                )
            
            return True, None
            
        except (ValueError, TypeError):
            return False, f"Invalid budget format '{budget}'. Expected numeric value."
    
    @staticmethod
    def validate_forecast_horizon(
        horizon: int,
        available_data_points: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate forecast horizon against available data.
        
        Args:
            horizon: Number of periods to forecast
            available_data_points: Number of historical data points available
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if horizon is None:
            return False, "Forecast horizon cannot be None"
        
        try:
            horizon_int = int(horizon)
            
            if horizon_int <= 0:
                return False, f"Forecast horizon must be positive, got {horizon_int}"
            
            # Check maximum forecast horizon (24 months)
            if horizon_int > 24:
                return False, (
                    f"Forecast horizon {horizon_int} months exceeds maximum (24 months). "
                    "Long-term forecasts become increasingly unreliable."
                )
            
            # Check if horizon exceeds available data
            # Rule of thumb: don't forecast more than 50% of available data length
            max_recommended_horizon = max(3, available_data_points // 2)
            
            if horizon_int > max_recommended_horizon:
                return False, (
                    f"Forecast horizon {horizon_int} months exceeds recommended maximum "
                    f"({max_recommended_horizon} months) based on available data "
                    f"({available_data_points} months). "
                    "Forecasts may be unreliable with limited historical data."
                )
            
            # Warn if insufficient data for reliable forecasting
            if available_data_points < 6:
                return False, (
                    f"Insufficient historical data ({available_data_points} months). "
                    "Need at least 6 months of data for reliable forecasting."
                )
            
            return True, None
            
        except (ValueError, TypeError):
            return False, f"Invalid forecast horizon '{horizon}'. Expected integer value."
    
    @staticmethod
    def validate_metric(metric: str) -> Tuple[bool, Optional[str]]:
        """
        Validate metric name.
        
        Args:
            metric: Metric name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not metric:
            return False, "Metric name cannot be empty"
        
        if metric not in VALID_METRICS:
            return False, (
                f"Invalid metric '{metric}'. "
                f"Valid metrics are: {', '.join(VALID_METRICS)}"
            )
        
        return True, None
    
    @staticmethod
    def validate_channel(channel: str) -> Tuple[bool, Optional[str]]:
        """
        Validate marketing channel name.
        
        Args:
            channel: Channel name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not channel:
            return False, "Channel name cannot be empty"
        
        if channel not in VALID_CHANNELS:
            return False, (
                f"Invalid channel '{channel}'. "
                f"Valid channels are: {', '.join(VALID_CHANNELS)}"
            )
        
        return True, None
    
    @staticmethod
    def validate_top_n(top_n: int, max_value: int = 10) -> Tuple[bool, Optional[str]]:
        """
        Validate top_n parameter for recommendations.
        
        Args:
            top_n: Number of top items to return
            max_value: Maximum allowed value (default 10)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if top_n is None:
            return False, "top_n cannot be None"
        
        try:
            top_n_int = int(top_n)
            
            if top_n_int <= 0:
                return False, f"top_n must be positive, got {top_n_int}"
            
            if top_n_int > max_value:
                return False, f"top_n {top_n_int} exceeds maximum ({max_value})"
            
            return True, None
            
        except (ValueError, TypeError):
            return False, f"Invalid top_n value '{top_n}'. Expected integer."
    
    @staticmethod
    def validate_confidence_level(confidence_level: float) -> Tuple[bool, Optional[str]]:
        """
        Validate confidence level for predictions.
        
        Args:
            confidence_level: Confidence level (e.g., 0.95 for 95%)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if confidence_level is None:
            return False, "Confidence level cannot be None"
        
        try:
            conf_float = float(confidence_level)
            
            if conf_float <= 0 or conf_float >= 1:
                return False, (
                    f"Confidence level must be between 0 and 1, got {conf_float}. "
                    "Example: 0.95 for 95% confidence."
                )
            
            # Warn about unusual confidence levels
            if conf_float < 0.80 or conf_float > 0.99:
                logger.warning(
                    f"Unusual confidence level {conf_float}. "
                    "Typical values are 0.90 (90%), 0.95 (95%), or 0.99 (99%)."
                )
            
            return True, None
            
        except (ValueError, TypeError):
            return False, f"Invalid confidence level '{confidence_level}'. Expected float between 0 and 1."
    
    @staticmethod
    def validate_lag_months(lag_months: int) -> Tuple[bool, Optional[str]]:
        """
        Validate lag months for marketing attribution.
        
        Args:
            lag_months: Number of months to lag marketing data
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if lag_months is None:
            return False, "lag_months cannot be None"
        
        try:
            lag_int = int(lag_months)
            
            if lag_int < 1 or lag_int > 3:
                return False, (
                    f"lag_months must be between 1 and 3, got {lag_int}. "
                    "Marketing effects typically manifest within 1-3 months."
                )
            
            return True, None
            
        except (ValueError, TypeError):
            return False, f"Invalid lag_months value '{lag_months}'. Expected integer between 1 and 3."


class BoundsChecker:
    """
    Checks if predictions are within realistic bounds.
    Applies bounds and displays warnings when violations detected.
    """
    
    @staticmethod
    def check_prediction_bounds(
        predictions: pd.DataFrame,
        historical_data: pd.DataFrame,
        metric: str
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Check if predictions are within realistic bounds.
        
        Args:
            predictions: DataFrame with forecast, lower_bound, upper_bound columns
            historical_data: Historical data for the metric
            metric: Metric name
            
        Returns:
            Tuple of (bounded_predictions, warnings_list)
        """
        warnings = []
        bounded_df = predictions.copy()
        
        if predictions.empty or historical_data.empty:
            return bounded_df, warnings
        
        # Extract historical values
        if 'metric_value' in historical_data.columns:
            historical_values = historical_data['metric_value'].values
        elif metric in historical_data.columns:
            historical_values = historical_data[metric].values
        else:
            logger.warning(f"Cannot find metric '{metric}' in historical data for bounds checking")
            return bounded_df, warnings
        
        # Remove NaN values
        historical_values = historical_values[~np.isnan(historical_values)]
        
        if len(historical_values) == 0:
            warnings.append("No historical data available for bounds checking")
            return bounded_df, warnings
        
        # Calculate historical statistics
        historical_max = np.max(historical_values)
        historical_min = np.min(historical_values)
        historical_mean = np.mean(historical_values)
        historical_std = np.std(historical_values)
        
        # Define bounds
        # Upper bound: 300% of historical maximum
        upper_limit = historical_max * 3.0
        
        # Lower bound: 0 for count metrics, or historical_min - 3*std for others
        count_metrics = [
            'inquiries_received', 'applications_received', 'applications_complete',
            'admissions_offered', 'admissions_accepted', 'anticipated_cohort_size'
        ]
        
        if metric in count_metrics:
            lower_limit = 0
        else:
            lower_limit = max(0, historical_min - 3 * historical_std)
        
        # Check for violations
        forecast_violations = (
            (bounded_df['forecast'] < lower_limit) | 
            (bounded_df['forecast'] > upper_limit)
        )
        
        if forecast_violations.any():
            num_violations = forecast_violations.sum()
            warnings.append(
                f"Warning: {num_violations} forecast values are outside realistic bounds "
                f"(historical range: {historical_min:.1f} - {historical_max:.1f}, "
                f"allowed range: {lower_limit:.1f} - {upper_limit:.1f})"
            )
            
            # Apply bounds to forecasts
            bounded_df.loc[bounded_df['forecast'] < lower_limit, 'forecast'] = lower_limit
            bounded_df.loc[bounded_df['forecast'] > upper_limit, 'forecast'] = upper_limit
            
            logger.warning(f"Applied bounds to {num_violations} forecast values")
        
        # Check for negative predictions (should not happen for count metrics)
        if metric in count_metrics:
            negative_forecasts = bounded_df['forecast'] < 0
            if negative_forecasts.any():
                warnings.append(
                    f"Warning: {negative_forecasts.sum()} negative forecasts detected for count metric '{metric}'. "
                    "Setting to 0."
                )
                bounded_df.loc[negative_forecasts, 'forecast'] = 0
        
        # Check confidence intervals
        if 'lower_bound' in bounded_df.columns and 'upper_bound' in bounded_df.columns:
            # Ensure lower_bound <= forecast <= upper_bound
            invalid_intervals = (
                (bounded_df['lower_bound'] > bounded_df['forecast']) |
                (bounded_df['upper_bound'] < bounded_df['forecast'])
            )
            
            if invalid_intervals.any():
                warnings.append(
                    f"Warning: {invalid_intervals.sum()} predictions have invalid confidence intervals. "
                    "Adjusting intervals."
                )
                
                # Fix invalid intervals
                bounded_df.loc[bounded_df['lower_bound'] > bounded_df['forecast'], 'lower_bound'] = (
                    bounded_df.loc[bounded_df['lower_bound'] > bounded_df['forecast'], 'forecast'] * 0.9
                )
                bounded_df.loc[bounded_df['upper_bound'] < bounded_df['forecast'], 'upper_bound'] = (
                    bounded_df.loc[bounded_df['upper_bound'] < bounded_df['forecast'], 'forecast'] * 1.1
                )
            
            # Apply bounds to confidence intervals
            bounded_df['lower_bound'] = bounded_df['lower_bound'].clip(lower=lower_limit, upper=upper_limit)
            bounded_df['upper_bound'] = bounded_df['upper_bound'].clip(lower=lower_limit, upper=upper_limit)
        
        # Check for unrealistic growth rates
        if len(historical_values) > 0:
            last_historical_value = historical_values[-1]
            
            if last_historical_value > 0:
                for idx, row in bounded_df.iterrows():
                    growth_rate = (row['forecast'] - last_historical_value) / last_historical_value
                    
                    # Warn if growth exceeds 200% or decline exceeds 80%
                    if growth_rate > 2.0:
                        warnings.append(
                            f"Warning: Forecast for period {idx} shows {growth_rate*100:.0f}% growth "
                            f"from last historical value. This may be unrealistic."
                        )
                    elif growth_rate < -0.8:
                        warnings.append(
                            f"Warning: Forecast for period {idx} shows {abs(growth_rate)*100:.0f}% decline "
                            f"from last historical value. This may be unrealistic."
                        )
        
        return bounded_df, warnings
    
    @staticmethod
    def check_roi_bounds(roi: float) -> Tuple[float, Optional[str]]:
        """
        Check if ROI is within reasonable bounds.
        
        Args:
            roi: ROI value to check
            
        Returns:
            Tuple of (bounded_roi, warning_message)
        """
        warning = None
        bounded_roi = roi
        
        # Check for extremely high ROI (> 10.0 or 1000%)
        if roi > 10.0:
            warning = (
                f"Warning: ROI of {roi:.2f} ({roi*100:.0f}%) is extremely high. "
                "Please verify data accuracy."
            )
            # Don't cap ROI, but warn user
        
        # Check for extremely negative ROI (< -1.0 or -100%)
        if roi < -1.0:
            warning = (
                f"Warning: ROI of {roi:.2f} ({roi*100:.0f}%) indicates total loss exceeding investment. "
                "Please verify data accuracy."
            )
        
        return bounded_roi, warning
    
    @staticmethod
    def check_conversion_rate_bounds(conversion_rate: float) -> Tuple[float, Optional[str]]:
        """
        Check if conversion rate is within valid bounds (0-1).
        
        Args:
            conversion_rate: Conversion rate to check
            
        Returns:
            Tuple of (bounded_rate, warning_message)
        """
        warning = None
        bounded_rate = conversion_rate
        
        if conversion_rate < 0:
            warning = f"Warning: Negative conversion rate {conversion_rate:.2%} detected. Setting to 0."
            bounded_rate = 0.0
        elif conversion_rate > 1.0:
            warning = (
                f"Warning: Conversion rate {conversion_rate:.2%} exceeds 100%. "
                "This indicates data quality issues. Capping at 100%."
            )
            bounded_rate = 1.0
        
        return bounded_rate, warning


def validate_and_raise(is_valid: bool, error_message: Optional[str]) -> None:
    """
    Helper function to raise ValidationError if validation fails.
    
    Args:
        is_valid: Validation result
        error_message: Error message if validation failed
        
    Raises:
        ValidationError: If validation failed
    """
    if not is_valid:
        raise ValidationError(error_message)



class ErrorHandler:
    """
    Handles errors with detailed logging and user-friendly messaging.
    Wraps exceptions to provide clear feedback without exposing technical details.
    """
    
    @staticmethod
    def handle_database_error(error: Exception, operation: str) -> str:
        """
        Handle database-related errors.
        
        Args:
            error: The exception that occurred
            operation: Description of the operation being performed
            
        Returns:
            User-friendly error message
        """
        # Log detailed error for debugging
        logger.error(f"Database error during {operation}: {type(error).__name__}: {str(error)}")
        
        # Return user-friendly message
        if "no such table" in str(error).lower():
            return (
                f"Database error: Required table not found. "
                f"Please ensure the database is properly initialized."
            )
        elif "locked" in str(error).lower():
            return (
                f"Database is currently locked by another process. "
                f"Please try again in a moment."
            )
        elif "connection" in str(error).lower():
            return (
                f"Unable to connect to database. "
                f"Please check that the database file exists and is accessible."
            )
        else:
            return (
                f"A database error occurred while {operation}. "
                f"Please contact support if the problem persists."
            )
    
    @staticmethod
    def handle_insufficient_data_error(
        data_type: str,
        required: int,
        available: int
    ) -> str:
        """
        Handle insufficient data errors.
        
        Args:
            data_type: Type of data (e.g., "historical observations", "training samples")
            required: Minimum required data points
            available: Available data points
            
        Returns:
            User-friendly error message
        """
        logger.warning(
            f"Insufficient data: {data_type} - required: {required}, available: {available}"
        )
        
        return (
            f"Insufficient {data_type} for this operation. "
            f"Required: at least {required}, Available: {available}. "
            f"Please collect more data or select a different time period."
        )
    
    @staticmethod
    def handle_model_training_error(error: Exception, model_type: str) -> str:
        """
        Handle model training errors.
        
        Args:
            error: The exception that occurred
            model_type: Type of model being trained
            
        Returns:
            User-friendly error message
        """
        # Log detailed error
        logger.error(f"Model training error ({model_type}): {type(error).__name__}: {str(error)}")
        
        # Check for common issues
        if "convergence" in str(error).lower():
            return (
                f"The {model_type} model failed to converge. "
                f"This may be due to insufficient or noisy data. "
                f"Try using a simpler model or collecting more data."
            )
        elif "singular" in str(error).lower() or "invertible" in str(error).lower():
            return (
                f"The {model_type} model encountered a mathematical issue with the data. "
                f"This often occurs with highly correlated or constant values. "
                f"Please check your data quality."
            )
        elif "memory" in str(error).lower():
            return (
                f"Insufficient memory to train {model_type} model. "
                f"Try reducing the amount of data or using a simpler model."
            )
        else:
            return (
                f"Unable to train {model_type} model. "
                f"This may be due to data quality issues. "
                f"Please verify your data and try again."
            )
    
    @staticmethod
    def handle_prediction_error(error: Exception, context: str = "") -> str:
        """
        Handle prediction generation errors.
        
        Args:
            error: The exception that occurred
            context: Additional context about the prediction
            
        Returns:
            User-friendly error message
        """
        # Log detailed error
        logger.error(f"Prediction error {context}: {type(error).__name__}: {str(error)}")
        
        if "not fitted" in str(error).lower() or "no model" in str(error).lower():
            return (
                "Model has not been trained yet. "
                "Please train the model before generating predictions."
            )
        elif "invalid" in str(error).lower():
            return (
                f"Invalid input for prediction{' ' + context if context else ''}. "
                f"Please check your parameters and try again."
            )
        else:
            return (
                f"Unable to generate predictions{' ' + context if context else ''}. "
                f"Please verify your inputs and try again."
            )
    
    @staticmethod
    def handle_optimization_error(error: Exception, optimization_type: str) -> str:
        """
        Handle optimization errors.
        
        Args:
            error: The exception that occurred
            optimization_type: Type of optimization (e.g., "budget allocation", "channel selection")
            
        Returns:
            User-friendly error message
        """
        # Log detailed error
        logger.error(f"Optimization error ({optimization_type}): {type(error).__name__}: {str(error)}")
        
        if "infeasible" in str(error).lower() or "no solution" in str(error).lower():
            return (
                f"Unable to find a valid {optimization_type} solution with the given constraints. "
                f"Try relaxing your constraints or increasing the budget."
            )
        elif "empty" in str(error).lower() or "no data" in str(error).lower():
            return (
                f"Insufficient data for {optimization_type}. "
                f"Please ensure you have historical performance data available."
            )
        else:
            return (
                f"An error occurred during {optimization_type}. "
                f"Please check your inputs and try again."
            )
    
    @staticmethod
    def handle_validation_error(error: ValidationError) -> str:
        """
        Handle validation errors (already user-friendly).
        
        Args:
            error: ValidationError exception
            
        Returns:
            User-friendly error message
        """
        # Validation errors are already user-friendly, just log and return
        logger.warning(f"Validation error: {str(error)}")
        return str(error)
    
    @staticmethod
    def handle_generic_error(error: Exception, operation: str) -> str:
        """
        Handle generic/unexpected errors.
        
        Args:
            error: The exception that occurred
            operation: Description of the operation being performed
            
        Returns:
            User-friendly error message
        """
        # Log detailed error
        logger.error(
            f"Unexpected error during {operation}: {type(error).__name__}: {str(error)}",
            exc_info=True
        )
        
        return (
            f"An unexpected error occurred while {operation}. "
            f"Please try again or contact support if the problem persists."
        )
    
    @staticmethod
    def wrap_operation(operation_name: str):
        """
        Decorator to wrap operations with error handling.
        
        Args:
            operation_name: Name of the operation for error messages
            
        Returns:
            Decorator function
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except ValidationError as e:
                    error_msg = ErrorHandler.handle_validation_error(e)
                    raise ValidationError(error_msg)
                except sqlite3.Error as e:
                    error_msg = ErrorHandler.handle_database_error(e, operation_name)
                    raise RuntimeError(error_msg)
                except ValueError as e:
                    if "insufficient" in str(e).lower() or "not enough" in str(e).lower():
                        error_msg = str(e)  # Already user-friendly
                    else:
                        error_msg = ErrorHandler.handle_generic_error(e, operation_name)
                    raise ValueError(error_msg)
                except Exception as e:
                    error_msg = ErrorHandler.handle_generic_error(e, operation_name)
                    raise RuntimeError(error_msg)
            
            return wrapper
        return decorator


def configure_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> None:
    """
    Configure Python logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to
        log_format: Optional custom log format string
    """
    if log_format is None:
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),  # Console output
        ]
    )
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)
        
        logger.info(f"Logging configured: level={log_level}, file={log_file}")
    else:
        logger.info(f"Logging configured: level={log_level}")


def get_user_friendly_error_message(error: Exception, context: str = "") -> str:
    """
    Convert any exception to a user-friendly error message.
    
    Args:
        error: The exception that occurred
        context: Optional context about what was being done
        
    Returns:
        User-friendly error message
    """
    if isinstance(error, ValidationError):
        return ErrorHandler.handle_validation_error(error)
    elif isinstance(error, sqlite3.Error):
        return ErrorHandler.handle_database_error(error, context)
    elif isinstance(error, ValueError):
        return str(error)  # ValueError messages are usually clear
    elif isinstance(error, RuntimeError):
        return str(error)  # RuntimeError messages are usually clear
    else:
        return ErrorHandler.handle_generic_error(error, context)
