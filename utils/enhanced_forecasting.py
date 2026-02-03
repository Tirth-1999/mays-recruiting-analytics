"""
Enhanced Forecasting Module for Cohort-Based Predictions
Implements professor's requirements for Class 26/27 training → Class 28 prediction
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import sqlite3
from pathlib import Path
import joblib
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CohortForecaster:
    """
    Enhanced forecasting system that trains on historical cohorts to predict future cohorts.
    Implements the professor's requirement for Class 26/27 → Class 28 predictions.
    """
    
    def __init__(self, db_connection: sqlite3.Connection):
        """
        Initialize the cohort forecaster.
        
        Args:
            db_connection: SQLite database connection
        """
        self.conn = db_connection
        self.models = {}
        self.validation_results = {}
        self.training_cohorts = []
        self.target_cohort = None
        
        logger.info("Initialized CohortForecaster")
    
    def load_cohort_data(self, cohorts: List[int], programs: List[str] = None) -> pd.DataFrame:
        """
        Load admissions data for specified cohorts.
        
        Args:
            cohorts: List of cohort years (e.g., [2026, 2027])
            programs: List of programs to include (if None, include all)
            
        Returns:
            DataFrame with cohort admissions data
        """
        logger.info(f"Loading data for cohorts: {cohorts}")
        
        # Build query
        cohort_placeholders = ','.join(['?' for _ in cohorts])
        query = f"""
            SELECT 
                report_date,
                program,
                cohort_year,
                cohort_season,
                metric_name,
                metric_value
            FROM admissions_metrics
            WHERE cohort_year IN ({cohort_placeholders})
                AND cohort_season = 'fall'
        """
        
        params = cohorts
        
        if programs:
            program_placeholders = ','.join(['?' for _ in programs])
            query += f" AND program IN ({program_placeholders})"
            params.extend(programs)
        
        query += " ORDER BY cohort_year, program, report_date"
        
        df = pd.read_sql_query(query, self.conn, params=params)
        
        if df.empty:
            logger.warning(f"No data found for cohorts {cohorts}")
            return df
        
        # Convert date column
        df['report_date'] = pd.to_datetime(df['report_date'])
        
        # Create cohort identifier
        df['cohort'] = df['cohort_year'].astype(str)
        
        logger.info(f"Loaded {len(df)} records for {len(cohorts)} cohorts")
        return df
    
    def prepare_training_data(self, data: pd.DataFrame, target_metrics: List[str]) -> Dict[str, pd.DataFrame]:
        """
        Prepare training data by organizing it by program and metric.
        
        Args:
            data: Raw cohort data
            target_metrics: List of metrics to forecast
            
        Returns:
            Dictionary with structure: {program: {metric: DataFrame}}
        """
        logger.info(f"Preparing training data for {len(target_metrics)} metrics")
        
        training_data = {}
        
        for program in data['program'].unique():
            program_data = data[data['program'] == program].copy()
            training_data[program] = {}
            
            for metric in target_metrics:
                metric_data = program_data[program_data['metric_name'] == metric].copy()
                
                if not metric_data.empty:
                    # Create time series format
                    # Group by cohort and report_date to handle multiple entries
                    ts_data = metric_data.groupby(['cohort', 'report_date']).agg({
                        'metric_value': 'sum'
                    }).reset_index()
                    
                    # Pivot to have cohorts as columns
                    pivot_data = ts_data.pivot(
                        index='report_date', 
                        columns='cohort', 
                        values='metric_value'
                    ).fillna(0)
                    
                    training_data[program][metric] = pivot_data
                    
                    logger.debug(f"Prepared {program} - {metric}: {pivot_data.shape}")
        
        logger.info(f"Training data prepared for {len(training_data)} programs")
        return training_data
    
    def train_cohort_models(
        self, 
        training_data: Dict[str, pd.DataFrame], 
        training_cohorts: List[str],
        model_type: str = 'arima'
    ) -> Dict[str, Any]:
        """
        Train forecasting models on specified cohorts.
        
        Args:
            training_data: Prepared training data
            training_cohorts: List of cohort years to train on (e.g., ['2026', '2027'])
            model_type: Type of model to use ('arima', 'prophet', 'linear')
            
        Returns:
            Dictionary of trained models
        """
        logger.info(f"Training {model_type} models on cohorts: {training_cohorts}")
        
        self.training_cohorts = training_cohorts
        trained_models = {}
        
        for program, program_data in training_data.items():
            trained_models[program] = {}
            
            for metric, metric_data in program_data.items():
                logger.info(f"Training model for {program} - {metric}")
                
                try:
                    # Extract training data for specified cohorts
                    available_cohorts = [c for c in training_cohorts if c in metric_data.columns]
                    
                    if not available_cohorts:
                        logger.warning(f"No training data available for {program} - {metric}")
                        continue
                    
                    # Combine data from training cohorts
                    combined_data = []
                    for cohort in available_cohorts:
                        cohort_series = metric_data[cohort].dropna()
                        if not cohort_series.empty:
                            cohort_df = pd.DataFrame({
                                'date': cohort_series.index,
                                'value': cohort_series.values,
                                'cohort': cohort
                            })
                            combined_data.append(cohort_df)
                    
                    if not combined_data:
                        logger.warning(f"No valid training data for {program} - {metric}")
                        continue
                    
                    # Combine all cohort data
                    training_df = pd.concat(combined_data, ignore_index=True)
                    training_df = training_df.sort_values('date')
                    
                    # Train model based on type
                    if model_type == 'arima':
                        model = self._train_arima_model(training_df)
                    elif model_type == 'prophet':
                        model = self._train_prophet_model(training_df)
                    else:  # linear
                        model = self._train_linear_model(training_df)
                    
                    if model is not None:
                        trained_models[program][metric] = {
                            'model': model,
                            'model_type': model_type,
                            'training_cohorts': available_cohorts,
                            'training_data_points': len(training_df),
                            'last_training_date': training_df['date'].max()
                        }
                        
                        logger.info(f"Successfully trained {model_type} model for {program} - {metric}")
                    
                except Exception as e:
                    logger.error(f"Error training model for {program} - {metric}: {e}")
                    continue
        
        self.models = trained_models
        logger.info(f"Training complete. Models trained for {len(trained_models)} programs")
        return trained_models
    
    def _train_arima_model(self, data: pd.DataFrame) -> Any:
        """Train ARIMA model on combined cohort data."""
        try:
            from statsmodels.tsa.arima.model import ARIMA
            from statsmodels.tsa.stattools import adfuller
            
            # Prepare time series
            ts_data = data.groupby('date')['value'].sum().sort_index()
            
            if len(ts_data) < 10:
                logger.warning("Insufficient data for ARIMA model (need at least 10 points)")
                return None
            
            # Check for stationarity
            adf_result = adfuller(ts_data.dropna())
            is_stationary = adf_result[1] <= 0.05
            
            # Determine differencing order
            d = 0 if is_stationary else 1
            
            # Use simple ARIMA(1,d,1) configuration
            # In production, you might want to use auto_arima for optimal parameters
            order = (1, d, 1)
            
            model = ARIMA(ts_data, order=order)
            fitted_model = model.fit()
            
            return fitted_model
            
        except Exception as e:
            logger.error(f"Error training ARIMA model: {e}")
            return None
    
    def _train_prophet_model(self, data: pd.DataFrame) -> Any:
        """Train Prophet model on combined cohort data."""
        try:
            from prophet import Prophet
            
            # Prepare Prophet format
            prophet_data = data.groupby('date')['value'].sum().reset_index()
            prophet_data.columns = ['ds', 'y']
            
            if len(prophet_data) < 10:
                logger.warning("Insufficient data for Prophet model (need at least 10 points)")
                return None
            
            # Configure Prophet
            model = Prophet(
                yearly_seasonality=False,
                weekly_seasonality=False,
                daily_seasonality=False,
                interval_width=0.95
            )
            
            # Add monthly seasonality if enough data
            if len(prophet_data) >= 24:
                model.add_seasonality(
                    name='monthly',
                    period=30.5,
                    fourier_order=3
                )
            
            model.fit(prophet_data)
            return model
            
        except Exception as e:
            logger.error(f"Error training Prophet model: {e}")
            return None
    
    def _train_linear_model(self, data: pd.DataFrame) -> Any:
        """Train linear regression model on combined cohort data."""
        try:
            from sklearn.linear_model import LinearRegression
            
            # Prepare time series
            ts_data = data.groupby('date')['value'].sum().sort_index()
            
            if len(ts_data) < 5:
                logger.warning("Insufficient data for linear model (need at least 5 points)")
                return None
            
            # Create time index
            X = np.arange(len(ts_data)).reshape(-1, 1)
            y = ts_data.values
            
            model = LinearRegression()
            model.fit(X, y)
            
            return {
                'model': model,
                'start_date': ts_data.index[0],
                'data_length': len(ts_data)
            }
            
        except Exception as e:
            logger.error(f"Error training linear model: {e}")
            return None
    
    def validate_on_holdout_cohort(
        self, 
        validation_data: Dict[str, pd.DataFrame], 
        holdout_cohort: str
    ) -> Dict[str, Dict[str, float]]:
        """
        Validate trained models on a holdout cohort (e.g., Class 27 when trained on Class 26).
        
        Args:
            validation_data: Prepared validation data
            holdout_cohort: Cohort to validate on (e.g., '2027')
            
        Returns:
            Dictionary with validation metrics for each program-metric combination
        """
        logger.info(f"Validating models on holdout cohort: {holdout_cohort}")
        
        validation_results = {}
        
        for program, program_models in self.models.items():
            validation_results[program] = {}
            
            for metric, model_info in program_models.items():
                logger.info(f"Validating {program} - {metric}")
                
                try:
                    # Get actual data for holdout cohort
                    if program not in validation_data or metric not in validation_data[program]:
                        logger.warning(f"No validation data for {program} - {metric}")
                        continue
                    
                    metric_data = validation_data[program][metric]
                    
                    if holdout_cohort not in metric_data.columns:
                        logger.warning(f"Holdout cohort {holdout_cohort} not found in {program} - {metric}")
                        continue
                    
                    actual_values = metric_data[holdout_cohort].dropna()
                    
                    if actual_values.empty:
                        logger.warning(f"No actual values for {program} - {metric} - {holdout_cohort}")
                        continue
                    
                    # Generate predictions for the same time period
                    predictions = self._predict_for_dates(
                        model_info, 
                        actual_values.index.tolist()
                    )
                    
                    if predictions is None or len(predictions) == 0:
                        logger.warning(f"Could not generate predictions for {program} - {metric}")
                        continue
                    
                    # Align predictions with actual values
                    aligned_actual = []
                    aligned_predicted = []
                    
                    for date in actual_values.index:
                        if date in predictions.index:
                            aligned_actual.append(actual_values[date])
                            aligned_predicted.append(predictions[date])
                    
                    if len(aligned_actual) == 0:
                        logger.warning(f"No aligned data points for {program} - {metric}")
                        continue
                    
                    # Calculate validation metrics
                    actual_array = np.array(aligned_actual)
                    predicted_array = np.array(aligned_predicted)
                    
                    metrics = self._calculate_validation_metrics(actual_array, predicted_array)
                    metrics['data_points'] = len(aligned_actual)
                    metrics['holdout_cohort'] = holdout_cohort
                    
                    validation_results[program][metric] = metrics
                    
                    logger.info(f"Validation complete for {program} - {metric}: MAPE = {metrics['mape']:.2f}%")
                    
                except Exception as e:
                    logger.error(f"Error validating {program} - {metric}: {e}")
                    continue
        
        self.validation_results = validation_results
        logger.info(f"Validation complete for {len(validation_results)} programs")
        return validation_results
    
    def _predict_for_dates(self, model_info: Dict, target_dates: List) -> pd.Series:
        """Generate predictions for specific dates using trained model."""
        try:
            model = model_info['model']
            model_type = model_info['model_type']
            
            if model_type == 'arima':
                return self._predict_arima_for_dates(model, target_dates, model_info)
            elif model_type == 'prophet':
                return self._predict_prophet_for_dates(model, target_dates)
            else:  # linear
                return self._predict_linear_for_dates(model, target_dates, model_info)
                
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            return None
    
    def _predict_arima_for_dates(self, model: Any, target_dates: List, model_info: Dict) -> pd.Series:
        """Generate ARIMA predictions for specific dates."""
        try:
            # Calculate number of steps from last training date
            last_date = model_info['last_training_date']
            target_dates_dt = pd.to_datetime(target_dates)
            
            # Generate predictions
            predictions = {}
            
            for target_date in target_dates_dt:
                # Calculate steps from last training date
                if target_date <= last_date:
                    # For dates within training period, use fitted values
                    # This is a simplification - in practice you'd need more sophisticated handling
                    steps = 1
                else:
                    # Calculate months difference
                    months_diff = (target_date.year - last_date.year) * 12 + (target_date.month - last_date.month)
                    steps = max(1, months_diff)
                
                try:
                    forecast = model.forecast(steps=steps)
                    if hasattr(forecast, '__iter__'):
                        predictions[target_date] = forecast[-1]  # Take last prediction
                    else:
                        predictions[target_date] = forecast
                except:
                    # Fallback to mean if forecast fails
                    predictions[target_date] = model.fittedvalues.mean()
            
            return pd.Series(predictions)
            
        except Exception as e:
            logger.error(f"Error in ARIMA prediction: {e}")
            return pd.Series()
    
    def _predict_prophet_for_dates(self, model: Any, target_dates: List) -> pd.Series:
        """Generate Prophet predictions for specific dates."""
        try:
            # Create future dataframe
            future_df = pd.DataFrame({'ds': pd.to_datetime(target_dates)})
            
            # Generate predictions
            forecast = model.predict(future_df)
            
            # Return as series
            predictions = pd.Series(
                forecast['yhat'].values,
                index=pd.to_datetime(target_dates)
            )
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error in Prophet prediction: {e}")
            return pd.Series()
    
    def _predict_linear_for_dates(self, model_dict: Dict, target_dates: List, model_info: Dict) -> pd.Series:
        """Generate linear model predictions for specific dates."""
        try:
            model = model_dict['model']
            start_date = model_dict['start_date']
            
            predictions = {}
            
            for target_date in pd.to_datetime(target_dates):
                # Calculate time index from start date
                days_diff = (target_date - start_date).days
                months_diff = days_diff / 30.44  # Average days per month
                
                X = np.array([[months_diff]])
                prediction = model.predict(X)[0]
                predictions[target_date] = max(0, prediction)  # Ensure non-negative
            
            return pd.Series(predictions)
            
        except Exception as e:
            logger.error(f"Error in linear prediction: {e}")
            return pd.Series()
    
    def _calculate_validation_metrics(self, actual: np.ndarray, predicted: np.ndarray) -> Dict[str, float]:
        """Calculate validation metrics."""
        # Mean Absolute Error
        mae = np.mean(np.abs(actual - predicted))
        
        # Root Mean Squared Error
        rmse = np.sqrt(np.mean((actual - predicted) ** 2))
        
        # Mean Absolute Percentage Error
        mask = actual != 0
        if mask.any():
            mape = np.mean(np.abs((actual[mask] - predicted[mask]) / actual[mask])) * 100
        else:
            mape = 0.0
        
        # R-squared
        ss_res = np.sum((actual - predicted) ** 2)
        ss_tot = np.sum((actual - np.mean(actual)) ** 2)
        r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        return {
            'mae': float(mae),
            'rmse': float(rmse),
            'mape': float(mape),
            'r2': float(r2)
        }
    
    def predict_future_cohort(
        self, 
        target_cohort: str, 
        prediction_months: int = 12
    ) -> Dict[str, pd.DataFrame]:
        """
        Predict metrics for a future cohort (e.g., Class 28).
        
        Args:
            target_cohort: Cohort to predict (e.g., '2028')
            prediction_months: Number of months to predict
            
        Returns:
            Dictionary with predictions for each program-metric combination
        """
        logger.info(f"Generating predictions for cohort {target_cohort} ({prediction_months} months)")
        
        self.target_cohort = target_cohort
        predictions = {}
        
        # Generate prediction dates (assuming academic year starts in August)
        start_date = pd.Timestamp(f"{target_cohort}-08-01")
        prediction_dates = pd.date_range(
            start=start_date,
            periods=prediction_months,
            freq='MS'  # Month start
        )
        
        for program, program_models in self.models.items():
            predictions[program] = {}
            
            for metric, model_info in program_models.items():
                logger.info(f"Predicting {program} - {metric} for cohort {target_cohort}")
                
                try:
                    # Generate predictions
                    pred_series = self._predict_for_dates(model_info, prediction_dates.tolist())
                    
                    if pred_series is not None and not pred_series.empty:
                        # Create prediction DataFrame with confidence intervals
                        pred_df = pd.DataFrame({
                            'date': pred_series.index,
                            'predicted_value': pred_series.values,
                            'cohort': target_cohort,
                            'program': program,
                            'metric': metric,
                            'model_type': model_info['model_type']
                        })
                        
                        # Add simple confidence intervals (±20% for demonstration)
                        pred_df['lower_bound'] = pred_df['predicted_value'] * 0.8
                        pred_df['upper_bound'] = pred_df['predicted_value'] * 1.2
                        
                        # Ensure non-negative values for count metrics
                        count_metrics = [
                            'inquiries_received', 'total_applications', 'applications_complete',
                            'admissions_offered', 'admissions_accepted', 'anticipated_cohort_size'
                        ]
                        
                        if metric in count_metrics:
                            pred_df['predicted_value'] = pred_df['predicted_value'].clip(lower=0)
                            pred_df['lower_bound'] = pred_df['lower_bound'].clip(lower=0)
                            pred_df['upper_bound'] = pred_df['upper_bound'].clip(lower=0)
                            
                            # Round to integers
                            pred_df['predicted_value'] = pred_df['predicted_value'].round().astype(int)
                            pred_df['lower_bound'] = pred_df['lower_bound'].round().astype(int)
                            pred_df['upper_bound'] = pred_df['upper_bound'].round().astype(int)
                        
                        predictions[program][metric] = pred_df
                        
                        logger.info(f"Generated {len(pred_df)} predictions for {program} - {metric}")
                    
                except Exception as e:
                    logger.error(f"Error predicting {program} - {metric}: {e}")
                    continue
        
        logger.info(f"Prediction complete for cohort {target_cohort}")
        return predictions
    
    def generate_case_study_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive case study report showing model performance.
        
        Returns:
            Dictionary with case study results and analysis
        """
        logger.info("Generating case study report")
        
        if not self.validation_results:
            logger.warning("No validation results available. Run validation first.")
            return {}
        
        # Aggregate validation metrics
        all_mapes = []
        all_r2s = []
        program_summaries = {}
        
        for program, metrics in self.validation_results.items():
            program_mapes = []
            program_r2s = []
            metric_details = {}
            
            for metric, results in metrics.items():
                mape = results['mape']
                r2 = results['r2']
                
                all_mapes.append(mape)
                all_r2s.append(r2)
                program_mapes.append(mape)
                program_r2s.append(r2)
                
                # Classify performance
                if mape <= 15:
                    performance = "Excellent"
                elif mape <= 25:
                    performance = "Good"
                elif mape <= 40:
                    performance = "Fair"
                else:
                    performance = "Poor"
                
                metric_details[metric] = {
                    'mape': mape,
                    'r2': r2,
                    'performance': performance,
                    'data_points': results['data_points']
                }
            
            program_summaries[program] = {
                'avg_mape': np.mean(program_mapes) if program_mapes else 0,
                'avg_r2': np.mean(program_r2s) if program_r2s else 0,
                'metrics_count': len(metric_details),
                'metric_details': metric_details
            }
        
        # Overall summary
        overall_summary = {
            'avg_mape': np.mean(all_mapes) if all_mapes else 0,
            'avg_r2': np.mean(all_r2s) if all_r2s else 0,
            'total_models': len(all_mapes),
            'excellent_models': sum(1 for mape in all_mapes if mape <= 15),
            'good_models': sum(1 for mape in all_mapes if 15 < mape <= 25),
            'fair_models': sum(1 for mape in all_mapes if 25 < mape <= 40),
            'poor_models': sum(1 for mape in all_mapes if mape > 40)
        }
        
        # Generate insights
        insights = []
        
        if overall_summary['avg_mape'] <= 20:
            insights.append("✅ Overall model performance is strong with low prediction errors")
        elif overall_summary['avg_mape'] <= 35:
            insights.append("⚠️ Model performance is moderate - consider additional training data")
        else:
            insights.append("❌ Model performance needs improvement - review data quality and model selection")
        
        if overall_summary['avg_r2'] >= 0.7:
            insights.append("✅ Models explain a high proportion of variance in the data")
        elif overall_summary['avg_r2'] >= 0.5:
            insights.append("⚠️ Models have moderate explanatory power")
        else:
            insights.append("❌ Models have low explanatory power - consider feature engineering")
        
        # Best and worst performing models
        best_model = None
        worst_model = None
        best_mape = float('inf')
        worst_mape = 0
        
        for program, metrics in self.validation_results.items():
            for metric, results in metrics.items():
                if results['mape'] < best_mape:
                    best_mape = results['mape']
                    best_model = f"{program} - {metric}"
                
                if results['mape'] > worst_mape:
                    worst_mape = results['mape']
                    worst_model = f"{program} - {metric}"
        
        case_study = {
            'training_cohorts': self.training_cohorts,
            'validation_cohort': list(self.validation_results.values())[0] if self.validation_results else None,
            'overall_summary': overall_summary,
            'program_summaries': program_summaries,
            'insights': insights,
            'best_model': {'name': best_model, 'mape': best_mape},
            'worst_model': {'name': worst_model, 'mape': worst_mape},
            'generated_at': datetime.now().isoformat()
        }
        
        logger.info(f"Case study report generated with {overall_summary['total_models']} models")
        return case_study
    
    def save_predictions_to_db(self, predictions: Dict[str, pd.DataFrame]) -> int:
        """
        Save predictions to the model_predictions table.
        
        Args:
            predictions: Dictionary of prediction DataFrames
            
        Returns:
            Number of predictions saved
        """
        logger.info("Saving predictions to database")
        
        saved_count = 0
        prediction_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            cursor = self.conn.cursor()
            
            for program, program_predictions in predictions.items():
                for metric, pred_df in program_predictions.items():
                    for _, row in pred_df.iterrows():
                        cursor.execute("""
                            INSERT OR REPLACE INTO model_predictions (
                                model_type, program, cohort, prediction_date, forecast_date,
                                metric, predicted_value, lower_bound, upper_bound
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            row['model_type'],
                            program,
                            row['cohort'],
                            prediction_date,
                            row['date'].strftime('%Y-%m-%d'),
                            metric,
                            float(row['predicted_value']),
                            float(row['lower_bound']),
                            float(row['upper_bound'])
                        ))
                        saved_count += 1
            
            self.conn.commit()
            logger.info(f"Saved {saved_count} predictions to database")
            
        except Exception as e:
            logger.error(f"Error saving predictions: {e}")
            self.conn.rollback()
            raise
        
        return saved_count


def run_cohort_forecasting_pipeline(
    db_path: str = 'edulytix.db',
    training_cohorts: List[int] = [2026, 2027],
    validation_cohort: int = 2027,
    prediction_cohort: int = 2028,
    target_metrics: List[str] = None
) -> Dict[str, Any]:
    """
    Run the complete cohort forecasting pipeline as requested by the professor.
    
    Args:
        db_path: Path to SQLite database
        training_cohorts: Cohorts to train on (default: [2026, 2027])
        validation_cohort: Cohort to validate on (default: 2027)
        prediction_cohort: Cohort to predict (default: 2028)
        target_metrics: Metrics to forecast (if None, use key metrics)
        
    Returns:
        Dictionary with pipeline results
    """
    logger.info("🚀 Starting Cohort Forecasting Pipeline")
    
    # Default target metrics
    if target_metrics is None:
        target_metrics = [
            'inquiries_received',
            'total_applications',
            'applications_complete',
            'admissions_offered',
            'admissions_accepted',
            'anticipated_cohort_size'
        ]
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    
    try:
        # Initialize forecaster
        forecaster = CohortForecaster(conn)
        
        # Step 1: Load and prepare data
        logger.info("📊 Loading cohort data...")
        all_cohorts = training_cohorts + [validation_cohort] if validation_cohort not in training_cohorts else training_cohorts
        raw_data = forecaster.load_cohort_data(all_cohorts)
        
        if raw_data.empty:
            raise ValueError("No data available for specified cohorts")
        
        training_data = forecaster.prepare_training_data(raw_data, target_metrics)
        
        # Step 2: Train models on training cohorts
        logger.info("🤖 Training forecasting models...")
        models = forecaster.train_cohort_models(
            training_data, 
            [str(c) for c in training_cohorts],
            model_type='arima'  # Use ARIMA as requested by professor
        )
        
        # Step 3: Validate on holdout cohort (Case Study)
        logger.info("📈 Validating models on holdout cohort...")
        validation_results = forecaster.validate_on_holdout_cohort(
            training_data, 
            str(validation_cohort)
        )
        
        # Step 4: Generate case study report
        logger.info("📋 Generating case study report...")
        case_study = forecaster.generate_case_study_report()
        
        # Step 5: Predict future cohort
        logger.info("🔮 Predicting future cohort...")
        future_predictions = forecaster.predict_future_cohort(
            str(prediction_cohort),
            prediction_months=12
        )
        
        # Compile results
        results = {
            'pipeline_status': 'success',
            'training_cohorts': training_cohorts,
            'validation_cohort': validation_cohort,
            'prediction_cohort': prediction_cohort,
            'target_metrics': target_metrics,
            'models_trained': len([m for p in models.values() for m in p.values()]),
            'validation_results': validation_results,
            'case_study': case_study,
            'future_predictions': future_predictions,
            'completed_at': datetime.now().isoformat()
        }
        
        logger.info("✅ Cohort Forecasting Pipeline completed successfully!")
        return results
        
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        return {
            'pipeline_status': 'failed',
            'error': str(e),
            'completed_at': datetime.now().isoformat()
        }
        
    finally:
        conn.close()


if __name__ == "__main__":
    # Run the pipeline with professor's requirements
    results = run_cohort_forecasting_pipeline()
    
    if results['pipeline_status'] == 'success':
        print("🎉 Cohort Forecasting Pipeline completed successfully!")
        print(f"📊 Models trained: {results['models_trained']}")
        
        # Print case study summary
        case_study = results['case_study']
        if case_study:
            print(f"\n📋 Case Study Summary:")
            print(f"   Average MAPE: {case_study['overall_summary']['avg_mape']:.2f}%")
            print(f"   Average R²: {case_study['overall_summary']['avg_r2']:.3f}")
            print(f"   Total Models: {case_study['overall_summary']['total_models']}")
    else:
        print(f"❌ Pipeline failed: {results['error']}")