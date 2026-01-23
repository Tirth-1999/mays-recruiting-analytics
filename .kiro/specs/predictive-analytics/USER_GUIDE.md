# Predictive Analytics & Machine Learning - User Guide

## Overview

The Predictive Analytics & Machine Learning module provides data-driven forecasting, optimization, and recommendation capabilities to support enrollment planning and marketing strategy for Texas A&M Mays Business School's Flex Online Programs.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Forecasting](#forecasting)
3. [Channel Optimization](#channel-optimization)
4. [Timing Analysis](#timing-analysis)
5. [Budget Allocation](#budget-allocation)
6. [Model Performance](#model-performance)
7. [Interpreting Results](#interpreting-results)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

- Ensure the ETL pipeline has been run to populate the database with historical data
- At least 6 months of historical data is recommended for basic forecasting
- 12+ months of data is recommended for seasonal pattern detection
- 24+ months of data enables advanced forecasting models

### Accessing the Page

1. Navigate to the Edulytix dashboard
2. Select "Predictive Analytics & Machine Learning" from the sidebar
3. The page will load with five main sections accessible via tabs

---

## Forecasting

### Purpose

Generate predictions for future inquiries, applications, and enrollments with confidence intervals to support enrollment planning and resource allocation.

### How to Use

1. **Select Program**: Choose the program you want to forecast (e.g., MBA, MS ACCT)
2. **Select Cohort** (Optional): Choose a specific cohort year or leave blank for all cohorts
3. **Select Metric**: Choose what to forecast:
   - Inquiries Received
   - Applications Received
   - Applications Complete
   - Admissions Offered
   - Admissions Accepted
   - Anticipated Cohort Size
4. **Select Forecast Horizon**: Choose how many months ahead to predict (1-12 months)
5. **Click "Generate Forecast"**

### Understanding the Results

**Forecast Chart**:
- **Blue dashed line**: Point estimate (most likely value)
- **Maroon solid line**: Historical data
- **Shaded blue region**: 95% confidence interval (range where actual value is likely to fall)

**Model Information**:
- **Model Type**: The forecasting algorithm used (Prophet, ARIMA, or Linear)
- **MAPE**: Mean Absolute Percentage Error - lower is better (< 15% is good)
- **Data Points Used**: Number of historical observations used for training

**Interpretation Tips**:
- Wider confidence intervals indicate more uncertainty
- MAPE < 10%: Excellent accuracy
- MAPE 10-15%: Good accuracy
- MAPE > 15%: Consider collecting more data or reviewing model

### Common Issues

**"Insufficient data" warning**:
- Need at least 6 months of historical data
- Solution: Wait for more data to accumulate or use simpler forecasting methods

**Very wide confidence intervals**:
- Indicates high uncertainty in predictions
- Causes: Limited data, high variability, or seasonal patterns
- Solution: Collect more data or review historical trends

---

## Channel Optimization

### Purpose

Identify the most effective marketing channels for each program based on historical ROI and conversion rates.

### How to Use

1. **Select Program**: Choose the program to analyze
2. **Click "Analyze Channels"**

### Understanding the Results

**Channel Recommendations**:
- Channels are ranked by effectiveness score (0-100)
- Top 3 channels are displayed with detailed metrics

**Metrics Explained**:
- **ROI (Return on Investment)**: (Revenue - Cost) / Cost
  - ROI > 2.0: Excellent (green indicator)
  - ROI 1.0-2.0: Good (yellow indicator)
  - ROI < 1.0: Needs improvement (red indicator)
- **Average Monthly Spend**: Historical average investment in this channel
- **Average Monthly Conversions**: Historical average admissions from this channel
- **Effectiveness Score**: Composite score combining ROI, conversion rate, consistency, and data confidence

**Performance History Chart**:
- Shows monthly spend, conversions, and ROI trends over time
- Helps identify seasonal patterns and performance changes

### Interpretation Tips

- Focus budget on channels with high effectiveness scores
- Consider consistency - channels with stable performance are lower risk
- Review performance history to understand trends
- Low data confidence indicates limited historical data - proceed with caution

### Common Issues

**"Insufficient data" for a channel**:
- Not enough historical spend/conversion data for that channel
- Solution: Collect baseline data before making decisions

**Negative ROI**:
- Channel is not generating enough admissions to justify the cost
- Solution: Review targeting, messaging, or consider reallocating budget

---

## Timing Analysis

### Purpose

Identify optimal months for marketing investments based on historical conversion patterns and seasonal trends.

### How to Use

1. **Select Program**: Choose the program to analyze
2. **Click "Analyze Timing"**

### Understanding the Results

**Seasonal Heatmap**:
- **X-axis**: Months (January - December)
- **Y-axis**: Years
- **Color intensity**: Conversion rate (darker = higher conversion)
- Helps visualize seasonal patterns across multiple years

**Timing Recommendations**:
- Months are ranked by effectiveness score
- Top months show highest historical conversion rates
- Consistency score indicates reliability of the pattern

**Metrics Explained**:
- **Average Conversion Rate**: Inquiries → Applications conversion for that month
- **Effectiveness Score**: Combines conversion rate and consistency
- **Consistency Score**: How stable the pattern is across years (0-1, higher is better)

### Interpretation Tips

- Strong seasonal patterns (consistency > 0.7) are reliable for planning
- Invest more heavily in high-conversion months
- Consider lead time - marketing in month M affects outcomes in months M+1 to M+3
- Account for program-specific enrollment cycles and application deadlines

### Common Issues

**No clear seasonal pattern**:
- Program may not have strong seasonality
- Solution: Focus on other optimization factors (channels, budget)

**Limited history**:
- Need multiple years of data to detect reliable patterns
- Solution: Use with caution until more data is available

---

## Budget Allocation

### Purpose

Receive data-driven recommendations for distributing marketing budget across programs and channels to maximize ROI and enrollments.

### How to Use

1. **Enter Total Budget**: Specify your total marketing budget
2. **Select Programs**: Choose which programs to include in the allocation
3. **Adjust Constraints** (Optional):
   - Minimum budget per program
   - Maximum budget per channel
4. **Click "Generate Allocation"**

### Understanding the Results

**Allocation Table**:
- Shows recommended budget distribution by program and channel
- Includes expected outcomes for each allocation

**Expected Outcomes**:
- **Expected Inquiries**: Predicted number of inquiries from this allocation
- **Expected Applications**: Predicted number of applications
- **Expected Enrollments**: Predicted number of enrollments
- **Expected ROI**: Predicted return on investment

**Sensitivity Analysis**:
- Shows how outcomes change with ±20% budget adjustments
- Helps understand budget flexibility and risk

**Allocation Chart**:
- Visual representation of budget distribution
- Color-coded by program or channel

### Interpretation Tips

- Allocations are optimized for maximum ROI by default
- Higher-ROI programs/channels receive more budget
- Constraints ensure minimum investment in all programs
- Sensitivity analysis helps with scenario planning

### Common Issues

**"Budget too small" error**:
- Total budget is insufficient to meet minimum constraints
- Solution: Increase budget or reduce minimum allocations

**Unexpected allocation**:
- Algorithm optimizes for ROI, which may differ from intuition
- Solution: Review historical performance data to understand recommendations

---

## Model Performance

### Purpose

Track prediction accuracy over time and monitor model health to ensure recommendations remain reliable.

### How to Use

1. Navigate to the "Model Performance" tab
2. Review accuracy metrics and trends
3. Check for warnings about model degradation

### Understanding the Results

**Accuracy Metrics**:
- **MAPE (Mean Absolute Percentage Error)**: Average prediction error as percentage
  - < 10%: Excellent
  - 10-15%: Good
  - > 15%: Needs attention
- **RMSE (Root Mean Squared Error)**: Penalizes large errors more heavily
- **MAE (Mean Absolute Error)**: Average absolute difference between predicted and actual

**Model Health Status**:
- **Healthy** (Green): MAPE < 15%, model performing well
- **Warning** (Yellow): MAPE 15-20%, monitor closely
- **Needs Retraining** (Red): MAPE > 20%, model should be retrained

**Accuracy Trends**:
- Line chart showing how accuracy changes over time
- Helps identify if model performance is degrading

### Interpretation Tips

- Regular monitoring ensures reliable predictions
- Degrading accuracy may indicate changing patterns or data quality issues
- Retrain models when performance drops below acceptable thresholds
- Compare multiple models to identify best performer

### Common Issues

**Model performance degrading**:
- Patterns may have changed (e.g., new marketing strategy, market conditions)
- Solution: Retrain model with recent data

**High error for specific program**:
- Program may have unique patterns or limited data
- Solution: Collect more data or use program-specific models

---

## Interpreting Results

### Confidence Intervals

All forecasts include 95% confidence intervals, meaning:
- There's a 95% probability the actual value will fall within the shaded region
- Wider intervals = more uncertainty
- Narrower intervals = more confidence in the prediction

### ROI Calculations

ROI is calculated as:
```
ROI = (Admissions Value - Marketing Spend) / Marketing Spend
```

Where:
- Admissions Value = Number of admissions × Estimated tuition per student
- Marketing Spend = Total spend on channel for program in time period

### Effectiveness Scores

Composite scores (0-100) combining multiple factors:
- **Channel Effectiveness**: ROI (40%) + Conversion Rate (30%) + Consistency (20%) + Data Confidence (10%)
- **Timing Effectiveness**: Conversion Rate (60%) + Consistency (40%)

### Time Lags

Marketing effects are not immediate. The system accounts for:
- 1-3 month lag between marketing spend and admissions outcomes
- Configurable lag parameter in channel optimization
- Consider lead time when planning campaigns

---

## Troubleshooting

### Common Error Messages

**"Insufficient data for forecasting"**
- **Cause**: Less than 6 months of historical data
- **Solution**: Wait for more data to accumulate or use alternative planning methods

**"Database connection failed"**
- **Cause**: Cannot connect to SQLite database
- **Solution**: Ensure database file exists and is accessible, check file permissions

**"Invalid program code"**
- **Cause**: Selected program not found in database
- **Solution**: Verify program code spelling, check available programs in dropdown

**"Forecast horizon too long"**
- **Cause**: Requesting predictions beyond available data
- **Solution**: Reduce forecast horizon or collect more historical data

**"Model training failed"**
- **Cause**: Data quality issues or insufficient observations
- **Solution**: Review data quality, check for missing values or outliers

### Data Quality Issues

**Missing values**:
- System automatically fills gaps ≤ 1 month using forward-fill
- Gaps > 1 month are interpolated
- Check data quality warnings in logs

**Outliers**:
- Values > 3 standard deviations are flagged
- System logs warnings but includes data
- Review flagged outliers to ensure they're legitimate

**Negative values**:
- Count metrics (inquiries, applications) cannot be negative
- System replaces negative values with 0 and logs warning
- Review data source if this occurs frequently

### Performance Issues

**Slow forecast generation**:
- **Cause**: Large dataset or complex model
- **Solution**: Normal for first run, subsequent runs use cached models

**Cache errors**:
- **Cause**: Corrupted cache files
- **Solution**: Clear cache directory (.cache/models/) and regenerate

### Getting Help

If you encounter persistent issues:

1. **Check the logs**: Detailed error information is logged for debugging
2. **Review data quality**: Many issues stem from data problems
3. **Verify prerequisites**: Ensure ETL pipeline has run successfully
4. **Contact support**: Provide error message, program/cohort details, and steps to reproduce

---

## Best Practices

### Data Management

- Run ETL pipeline regularly to keep data current
- Validate data quality before making decisions
- Maintain at least 12 months of historical data for reliable forecasting

### Forecasting

- Use longer forecast horizons (6-12 months) for strategic planning
- Use shorter horizons (1-3 months) for tactical decisions
- Review and update forecasts monthly as new data becomes available
- Consider multiple scenarios (optimistic, realistic, pessimistic)

### Optimization

- Review channel performance quarterly
- Test new channels with small budgets before scaling
- Monitor ROI trends to identify changes in effectiveness
- Combine channel and timing insights for maximum impact

### Budget Planning

- Use sensitivity analysis for scenario planning
- Set realistic constraints based on program needs
- Review allocations with stakeholders before implementation
- Track actual outcomes vs. predictions to validate recommendations

### Model Maintenance

- Monitor model performance monthly
- Retrain models when MAPE exceeds 15%
- Compare multiple models to identify best performer
- Document any changes to data collection or business processes that may affect models

---

## Appendix: Technical Details

### Forecasting Models

**Prophet**:
- Used when ≥ 24 months of data available
- Handles seasonality and trends automatically
- Robust to missing data and outliers

**ARIMA**:
- Fallback when Prophet fails
- Good for time series with trends
- Requires stationary data

**Linear Regression**:
- Used when < 24 months of data
- Simple trend-based forecasting
- Less accurate but more stable with limited data

### Model Selection Logic

```
if data_points >= 24:
    use Prophet (with seasonal components)
elif data_points >= 12:
    use ARIMA or Linear Regression
else:
    use Simple Moving Average (with warning)
```

### Validation Strategy

- Last 20% of data held out for validation
- MAPE calculated on holdout set
- Cross-validation with expanding window for time series

### Cache Management

- Trained models cached using joblib
- Cache key based on training parameters
- Cache invalidated when new data added
- Cache directory: `.cache/models/`

---

## Glossary

- **MAPE**: Mean Absolute Percentage Error - average prediction error as percentage
- **ROI**: Return on Investment - (gain - cost) / cost
- **Confidence Interval**: Range where actual value is likely to fall (95% probability)
- **Cohort**: Group of students expected to graduate in the same year
- **Forecast Horizon**: Number of periods ahead to predict
- **Effectiveness Score**: Composite metric combining multiple performance factors
- **Seasonality**: Recurring patterns at regular intervals (e.g., monthly, yearly)
- **Time Lag**: Delay between marketing spend and admissions outcomes
- **Conversion Rate**: Percentage of inquiries that become applications

---

## Version History

- **v1.0** (January 2026): Initial release with forecasting, optimization, and budget allocation features
