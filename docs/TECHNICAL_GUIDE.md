# Technical Guide

[← Back to Documentation](README.md)

---

## Database Schema

### Admissions Tables

#### programs
- program_code (TEXT, PRIMARY KEY)
- program_name (TEXT)
- is_active (INTEGER)

#### admissions_metrics
- id (INTEGER, PRIMARY KEY)
- report_date (TEXT)
- program (TEXT)
- cohort_year (INTEGER)
- metric_name (TEXT)
- metric_value (REAL)
- created_at (TIMESTAMP)
- UNIQUE constraint on (report_date, program, cohort_year, metric_name)

### Marketing Tables

#### marketing_spend
- spend_id (INTEGER, PRIMARY KEY)
- spend_date (TEXT)
- program (TEXT)
- channel (TEXT) - Search, Display, LinkedIn, Meta, etc.
- amount (REAL)
- fiscal_year (TEXT)
- currency (TEXT)

#### marketing_metrics
- metric_id (INTEGER, PRIMARY KEY)
- report_date (TEXT)
- program (TEXT)
- channel (TEXT)
- spend (REAL)
- is_active (INTEGER) - 1 = active, 0 = inactive
- impressions, clicks, inquiries, applications (for future use)

#### marketing_campaigns
Ready for future data:
- campaign_id, campaign_name, campaign_type, start_date, end_date, etc.

#### inquiry_sources
Ready for future data:
- inquiry_id, inquiry_date, source, campaign_id, converted_to_application, etc.

### System Tables

#### metadata
- key (TEXT, PRIMARY KEY)
- value (TEXT)
- updated_at (TIMESTAMP)

Tracks:
- `last_data_update` - When admissions data was last loaded
- `last_marketing_update` - When marketing data was last loaded

#### model_predictions
- prediction_id (INTEGER, PRIMARY KEY)
- model_name (TEXT)
- program (TEXT)
- cohort_year (INTEGER)
- metric_name (TEXT)
- prediction_date (TEXT)
- predicted_value (REAL)
- lower_bound (REAL)
- upper_bound (REAL)
- actual_value (REAL)
- mape (REAL)
- created_at (TIMESTAMP)

---

## Configuration

### Database Setup

```bash
# Initialize database
python3 etl_pipeline.py          # Admissions data
python3 marketing_etl.py         # Marketing data

# Database location
edulytix.db                      # SQLite database file

# Schema files
marketing_schema.sql             # Marketing tables schema
```

### Environment Variables

```bash
# Optional configuration
STREAMLIT_SERVER_PORT=8501       # Default port
STREAMLIT_SERVER_ADDRESS=localhost
```

### Data Sources

```
Dataset/
├── MBS-Flex-Online-Admissions-2024-04-30.xlsx
├── MBS-Flex-Online-Admissions-2024-05-31.xlsx
├── MBS-Flex-Online-Admissions-2024-07-31.xlsx
├── MBS-Flex-Online-Admissions-2025-07-31.xlsx
├── MBS-Flex-Online-Admissions-2025-10-31.xlsx
├── MBS-Flex-Online-Admissions-2025-11-30.xlsx
├── MBS-Flex-Online-Admissions-2025-12-31.xlsx
└── Mays Flex Online Ad Spend Year 1.xlsx
```

### Version Management

```python
# Update version in ONE file
version.py

# Version format
VERSION_MAJOR = 4
VERSION_MINOR = 0
VERSION_PATCH = 0
VERSION_FULL = f"v{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"

# Automatically propagates to:
- Sidebar footer
- Help page footer
- Troubleshooting section
```

### Customization

#### Colors
```python
# Mays Business School brand colors
maroon = '#500000'
gold = '#C5A572'
dark_maroon = '#700000'
light_maroon = '#B00000'
```

#### Filters
```python
# Cohort options
cohort_options = [2028, 2027, 2026]

# Program options
program_options = ['All Programs', 'MBA', 'MS ACCT', 
                   'MS ENLD', 'MS HRM', 'MS MISY', 
                   'MS MKTG', 'MS SPBA']
```

---

## Troubleshooting

### Common Issues

#### Database Errors

**"No data available"**
```bash
# Solution: Run ETL pipeline
python3 etl_pipeline.py
python3 marketing_etl.py
```

**"Database connection failed"**
```bash
# Check database file exists
ls -la edulytix.db

# Check permissions
chmod 644 edulytix.db
```

#### Display Issues

**"Charts not rendering"**
```bash
# Clear Streamlit cache
streamlit cache clear

# Restart application
streamlit run main_app.py
```

**"Filters not working"**
```bash
# Reset session state
# Refresh browser (Ctrl+R or Cmd+R)
```

#### Performance Issues

**"Slow loading"**
```bash
# Check database size
du -h edulytix.db

# Filter data before exporting
# Close unused browser tabs
```

**"Memory errors"**
```bash
# Reduce row limits in Data Explorer
# Filter data before exporting
# Close unused browser tabs
```

#### Predictive Analytics Issues

**"Insufficient data for forecasting"**
- Need at least 6 months of historical data
- Wait for more data or use simpler methods

**"Model training failed"**
- Check data quality (missing values, outliers)
- Review logs for specific errors
- Ensure ETL pipeline completed successfully

**"High MAPE (> 15%)"**
- Model may need retraining
- Patterns may have changed
- Consider collecting more data

### Debug Mode

```bash
# Run with debug logging
streamlit run main_app.py --logger.level=debug

# Check Python version
python3 --version  # Should be 3.8+

# Check dependencies
pip list | grep streamlit
pip list | grep pandas
pip list | grep plotly
```

---

## Data Clarifications

### Admissions Data
- Campaign matrix values labeled `- NA -` indicate the campaign was not active for that program/month and are excluded from totals
- Blank/`NaN` values are preserved as missing data rather than treated as zeros
- Dates represent the last day of the reporting month
- All metrics are cumulative within a cohort year

### Marketing Data
- "No Ad Spend" entries are handled as NULL (not zero)
- Spend is tracked monthly by program and channel
- FY25 Year 1 covers September 2024 - June 2025
- Search advertising represents 98% of total spend ($202K of $206K)
- General Awareness campaigns are tracked separately from program-specific campaigns

---

[← Back to Documentation](README.md)
