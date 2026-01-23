# Predictive Analytics

[← Back to Documentation](README.md)

---

## Overview

The Predictive Analytics page provides data-driven forecasting, optimization, and recommendations for enrollment planning using advanced machine learning models.

## Features

### Five ML Tabs

#### 1. Forecasting Tab
- **Time Series Predictions**: Forecast inquiries, applications, enrollments
- **Confidence Intervals**: 95% confidence ranges
- **Model Selection**: Automatic best model selection (Prophet, ARIMA, Linear)
- **Accuracy Metrics**: MAPE, RMSE, MAE tracking

#### 2. Channel Optimization Tab
- **ROI Analysis**: Identify most effective channels
- **Effectiveness Scores**: Composite performance metrics
- **Performance History**: Track channel performance over time
- **Recommendations**: Top channels ranked by effectiveness

#### 3. Timing Analysis Tab
- **Seasonal Patterns**: Identify optimal months for marketing
- **Conversion Heatmap**: Visualize patterns across years
- **Timing Recommendations**: Ranked months by effectiveness
- **Consistency Scores**: Reliability of seasonal patterns

#### 4. Budget Allocation Tab
- **Optimization**: Data-driven budget distribution
- **Expected Outcomes**: Predicted inquiries, applications, enrollments
- **Sensitivity Analysis**: Impact of budget changes
- **Constraint Management**: Minimum/maximum allocations

#### 5. Model Performance Tab
- **Accuracy Tracking**: Monitor prediction accuracy over time
- **Model Health**: Status indicators (Healthy, Warning, Needs Retraining)
- **Trend Analysis**: Identify performance degradation
- **Comparison**: Multiple model evaluation

## How to Use

### Forecasting
1. Select Program to forecast
2. Select Cohort year (optional)
3. Select Metric to forecast
4. Select Horizon (3-24 months)
5. Generate Forecast and view predictions with confidence intervals

### Channel Optimization
1. Select Program to analyze
2. Analyze top performing channels
3. Review ROI and effectiveness scores
4. Apply insights to budget allocation

### Timing Analysis
1. Select Program to analyze
2. Analyze seasonal patterns
3. Review conversion heatmap
4. Plan campaigns in high-conversion months

### Budget Allocation
1. Enter Total Budget
2. Select Programs to include
3. Set Constraints (optional)
4. Generate Allocation and review recommendations
5. Review Sensitivity analysis

## ML Models

### Prophet Model
- **Best for**: 24+ months of data
- **Features**: Automatic seasonality detection, holiday effects
- **Accuracy**: Highest for long-term forecasts

### ARIMA Model
- **Best for**: 12-24 months of data
- **Features**: Statistical forecasting, trend analysis
- **Accuracy**: Good for medium-term forecasts

### Linear Regression
- **Best for**: <12 months of data
- **Features**: Trend-based forecasting
- **Accuracy**: Basic but reliable for short-term

## Accuracy Metrics

- **MAPE < 10%**: Excellent
- **MAPE 10-15%**: Good
- **MAPE > 15%**: Needs attention

## Tips

- Use 12+ months of data for reliable forecasts
- Review model performance regularly
- Combine channel and timing insights
- Test budget scenarios with sensitivity analysis
- Monitor accuracy metrics monthly

---

[← Back to Documentation](README.md)
