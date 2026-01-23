# Comparison Tool

[← Back to Documentation](README.md)

---

## Overview

The Comparison Tool provides dedicated year-over-year analysis for comparing cohort performance with statistical rigor.

## Features

### Filter Configuration
- **Primary Cohort**: Select the main cohort for analysis (2028, 2027, or 2026)
- **Comparison Cohort**: Choose the cohort to compare against
- **Program Filter**: Focus on specific program or view all programs

### Smart Data Handling
- **Automatic Filtering**: Excludes metrics where both cohorts have zero values
- **Excluded Metrics Note**: Yellow info box shows which metrics were filtered out
- **N/A for No Base**: Shows "N/A" for % Change when comparison cohort has no data
- **Descriptive Indicators**: Clear performance labels with context

### Statistical Analysis
- **Variance Calculation**: `((Primary - Mean)² + (Comparison - Mean)²) / 2`
- **Standard Deviation**: `√Variance` for measuring spread
- **Coefficient of Variation**: `(Std Dev / Mean) × 100` for relative variability
- **Performance Indicators**: Based on % change thresholds with special handling for edge cases

### Visualization Components

1. **Time Series Comparison**: Side-by-side charts for each metric with toggle buttons
2. **Percentage Change Analysis**: Full-width bar chart showing growth/decline
3. **Comprehensive Table**: All metrics with variance analysis and performance indicators
4. **Export Options**: Three download buttons (comparison table, primary data, comparison data)

## How to Use

1. **Select Primary Cohort**: Main cohort for analysis
2. **Select Comparison Cohort**: Cohort to compare against
3. **Select Program Filter**: Focus on specific program or view all
4. **Explore Metrics**:
   - Use metric selector to choose which to visualize
   - Click "Show Data Table" for program breakdowns
   - Review percentage change chart
5. **Export Data**: Download tables for further analysis

## Statistical Metrics

### Variance
Measures the spread between the two cohorts:
```
Variance = ((Primary - Mean)² + (Comparison - Mean)²) / 2
```

### Standard Deviation
Square root of variance, in same units as original data:
```
Std Deviation = √Variance
```

### Coefficient of Variation
Relative variability as a percentage:
```
Coefficient of Variation = (Std Dev / Mean) × 100
```

## Performance Indicators

- **Strong Growth**: % Change > 15%
- **Moderate Growth**: % Change 5-15%
- **Stable**: % Change -5% to 5%
- **Decline**: % Change < -5%
- **New Metric**: Comparison cohort has no data

## Tips

- Use time series to identify trend differences
- Review percentage change for quick insights
- Check variance metrics for consistency
- Export data for stakeholder presentations

---

[← Back to Documentation](README.md)
