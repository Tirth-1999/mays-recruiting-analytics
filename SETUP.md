# Edulytix - Complete Setup Guide

## ✅ Current Status

Your Edulytix dashboard is **fully set up and running** with:
- ✅ Python 3.12 virtual environment
- ✅ All dependencies installed (including PyArrow)
- ✅ SQLite database with 1,833 records
- ✅ Streamlit dashboard running at http://localhost:8501

## 🚀 Quick Start

### Start the Dashboard
```bash
./run_dashboard.sh
```

This will:
1. Activate the Python 3.12 virtual environment
2. Check if database exists (create if needed)
3. Launch Streamlit dashboard at http://localhost:8501

### Stop the Dashboard
Press `Ctrl+C` in the terminal where it's running

## 🔧 Manual Setup (if needed on another machine)

### 1. Install Python 3.12
```bash
brew install python@3.12
```

### 2. Create Virtual Environment
```bash
python3.12 -m venv venv
```

### 3. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install streamlit pandas plotly openpyxl sqlalchemy python-dateutil pyarrow
```

### 5. Load Data
```bash
python etl_pipeline.py
```

### 6. Run Dashboard
```bash
streamlit run app.py
```

## 📦 Project Structure

```
Edulytix/
├── venv/                       # Python 3.12 virtual environment
├── Dataset/                    # Excel source files
│   ├── MBS-Flex-Online-Admissions-2024-04-30.xlsx
│   ├── MBS-Flex-Online-Admissions-2024-05-31.xlsx
│   ├── MBS-Flex-Online-Admissions-2024-07-31.xlsx
│   ├── MBS-Flex-Online-Admissions-2025-07-31.xlsx
│   ├── MBS-Flex-Online-Admissions-2025-10-31.xlsx
│   └── MBS-Flex-Online-Admissions-2025-10-31_New.xlsx
├── Context/                    # Background documents
├── app.py                      # Main Streamlit dashboard
├── etl_pipeline.py             # Data loading script
├── edulytix.db                 # SQLite database (1,833 records)
├── run_dashboard.sh            # Startup script
├── requirements.txt            # Python dependencies
├── README.md                   # Full documentation
├── QUICKSTART.md               # Quick reference
├── PROJECT_STATUS.md           # Status report
└── SETUP.md                    # This file
```

## 🔄 Updating Data

When you receive new Excel files (e.g., November 2025 report):

1. **Add file to Dataset folder**
   ```bash
   cp ~/Downloads/MBS-Flex-Online-Admissions-2025-11-30.xlsx Dataset/
   ```

2. **Update the ETL script** (if needed)
   Edit `etl_pipeline.py` and add the new file to the `dataset_files` list:
   ```python
   dataset_files = [
       # ... existing files ...
       ('Dataset/MBS-Flex-Online-Admissions-2025-11-30.xlsx', 2028),
   ]
   ```

3. **Reload data**
   ```bash
   source venv/bin/activate
   python etl_pipeline.py
   ```

4. **Restart dashboard**
   ```bash
   ./run_dashboard.sh
   ```

The ETL script automatically handles duplicates and updates existing records.

## 🐛 Troubleshooting

### Dashboard won't start
```bash
# Kill any existing Streamlit processes
pkill -f streamlit

# Restart
./run_dashboard.sh
```

### Port 8501 already in use
```bash
# Find and kill the process
lsof -ti:8501 | xargs kill -9

# Or use a different port
streamlit run app.py --server.port 8502
```

### Virtual environment not activating
```bash
# Recreate virtual environment
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
pip install streamlit pandas plotly openpyxl sqlalchemy python-dateutil pyarrow
```

### Database errors
```bash
# Backup and recreate database
mv edulytix.db edulytix.db.backup
python etl_pipeline.py
```

### Missing dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 🌐 Accessing from Other Devices

The dashboard is accessible from other devices on your network:

1. **Find your IP address**
   ```bash
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```

2. **Access from another device**
   Open browser to: `http://YOUR_IP:8501`
   (e.g., `http://192.168.1.100:8501`)

## 🔐 Security Notes

- The dashboard currently has no authentication
- Only run on trusted networks
- Don't expose to public internet without adding authentication
- Consider adding password protection before deploying to production

## 📊 Database Info

### Tables
- **programs**: 7 programs (MBA, MS ACCT, MS HRM, MS MISY, MS MKTG, MS ENLD, MS SPBA)
- **admissions_metrics**: 1,833 records

### Query the database directly
```bash
source venv/bin/activate
python
```

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('edulytix.db')

# See all programs
pd.read_sql('SELECT * FROM programs', conn)

# See latest metrics
pd.read_sql('''
    SELECT program, cohort_year, metric_name, metric_value 
    FROM admissions_metrics 
    WHERE report_date = (SELECT MAX(report_date) FROM admissions_metrics)
    LIMIT 10
''', conn)

conn.close()
```

## 🎯 Next Steps

1. **Demo to Dr. Sridhar** - Show the working dashboard
2. **Get feedback** - What additional metrics/visualizations needed?
3. **Add features** - Based on feedback
4. **Plan Phase 2** - Forecasting models and AI chatbot

## 📧 Support

- **Project Lead**: Tirth Shah (tirth.shah@tamu.edu)
- **Sponsor**: Dr. Shrihari Sridhar (ssridhar@mays.tamu.edu)

---

**Last Updated**: December 8, 2025  
**Python Version**: 3.12.12  
**Streamlit Version**: 1.51.0  
**Database Records**: 1,935 (includes November 2025 data)
