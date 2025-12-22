# Edulytix - Admissions Analytics Dashboard

A Streamlit-based analytics dashboard for Texas A&M Mays Business School's Flex Online Programs.

## Features

- 📊 Interactive dashboards with real-time filtering
- 📈 Admissions funnel visualization
- 📉 Trend analysis over time
- 🔍 Program-by-program comparison
- 💾 SQLite database for efficient data storage
- 📥 Data export functionality

## Quick Start

### 1. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 2. Install Dependencies (if needed)

```bash
pip install -r requirements.txt
```

### 3. Load Data into Database

```bash
python etl_pipeline.py
```

This will:
- Create `edulytix.db` SQLite database
- Load all Excel files from the `Dataset/` folder (including November 2025 data)
- Clean and structure the data
- Create necessary tables
- **Current: 1,935 records from 7 Excel files**

### 4. Run the Dashboard

```bash
streamlit run app.py
```

Or use the startup script:
```bash
./run_dashboard.sh
```

The dashboard will open in your browser at `http://localhost:8501`

## Project Structure

```
.
├── app.py                  # Main Streamlit dashboard
├── etl_pipeline.py         # ETL script to load Excel data into SQLite
├── requirements.txt        # Python dependencies
├── edulytix.db            # SQLite database (created after running ETL)
├── Dataset/               # Excel files with admissions data
│   ├── MBS-Flex-Online-Admissions-2024-04-30.xlsx
│   ├── MBS-Flex-Online-Admissions-2024-05-31.xlsx
│   └── ...
└── Context/               # Background documents and emails
```

## Database Schema

### Tables

**programs**
- program_code (TEXT, PRIMARY KEY)
- program_name (TEXT)
- is_active (INTEGER)

**admissions_metrics**
- id (INTEGER, PRIMARY KEY)
- report_date (TEXT)
- program (TEXT)
- cohort_year (INTEGER)
- metric_name (TEXT)
- metric_value (REAL)
- created_at (TIMESTAMP)

### Metrics Tracked

- inquiries_received
- applications_in_progress
- applications_received
- applications_complete
- applications_manual
- applications_verified
- applications_on_hold
- applications_undelivered
- applications_deferral
- total_applications
- admissions_pre_admission
- admissions_offered
- admissions_denied
- admissions_accepted
- admissions_declined
- admissions_deferred_to_next
- admissions_deferred_from_last
- admissions_moved_to_other
- admissions_withdrawn
- anticipated_cohort_size

## Dashboard Features

### Executive Overview
- Key metrics cards (Cohort Size, Applications, Inquiries, Conversion Rate)
- Admissions funnel visualization
- Trends over time (Applications, Cohort Size)
- Program comparison charts

### Filters
- Program selection (All Programs or specific program)
- Cohort year (2026, 2027, 2028)
- Date range (All Time, Last 6 Months, Last 3 Months, Custom)

### Data Export
- Download filtered data as CSV
- Detailed metrics table view

## Next Steps

### Phase 2: Enhancements
- [ ] Add forecasting models (Prophet/ARIMA)
- [ ] Integrate marketing spend data (when available)
- [ ] Add AI chatbot for natural language queries
- [ ] Implement user authentication
- [ ] Add email alerts for key metrics

### Phase 3: Migration to Power BI
- [ ] Export data model to Power BI
- [ ] Recreate dashboards with advanced visualizations
- [ ] Set up scheduled data refresh
- [ ] Deploy to Power BI Service

## Troubleshooting

**Issue: "No data available"**
- Make sure you've run `python etl_pipeline.py` first
- Check that Excel files are in the `Dataset/` folder
- Verify `edulytix.db` exists

**Issue: "Module not found"**
- Run `pip install -r requirements.txt`
- Make sure you're using Python 3.8+

**Issue: "Database is locked"**
- Close any other connections to `edulytix.db`
- Restart the Streamlit app

## Contact

Project Lead: Tirth Shah (tirth.shah@tamu.edu)
Sponsor: Dr. Shrihari Sridhar (ssridhar@mays.tamu.edu)
