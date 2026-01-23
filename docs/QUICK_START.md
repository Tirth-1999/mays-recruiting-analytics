# 🚀 Quick Start Guide

Get the Mays Analytics Platform up and running in minutes.

## Prerequisites

- **Python**: 3.8 or higher
- **Operating System**: macOS, Linux, or Windows
- **Storage**: At least 500MB free space
- **Memory**: 4GB RAM minimum (8GB recommended)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/Tirth-1999/mays-recruiting-analytics.git
cd mays-recruiting-analytics
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Load Data

```bash
# Load admissions data
python3 etl_pipeline.py

# Load marketing data
python3 marketing_etl.py

# (Optional) Create model predictions table
python3 migrations/add_model_predictions_table.py migrate
```

### 5. Run the Dashboard

```bash
streamlit run main_app.py
```

Or use the startup script:
```bash
chmod +x run_dashboard.sh
./run_dashboard.sh
```

The dashboard will open automatically at `http://localhost:8501`

## First Time Setup

### Verify Installation

1. **Check Python Version**
   ```bash
   python3 --version
   # Should show 3.8 or higher
   ```

2. **Verify Dependencies**
   ```bash
   pip list | grep streamlit
   pip list | grep pandas
   pip list | grep plotly
   ```

3. **Check Database**
   ```bash
   ls -lh edulytix.db
   # Should show database file with size > 0
   ```

### Test the Application

1. Open browser to `http://localhost:8501`
2. Navigate through all 6 pages:
   - 🏠 Home Dashboard
   - 📊 Executive Deep Dive
   - 🔄 Comparison Tool
   - 📢 Marketing Analysis
   - 🗄️ Data Explorer
   - 🔮 Predictive Analytics

3. Verify data loads correctly on each page

## Common Issues

### Port Already in Use

```bash
# Kill existing Streamlit process
pkill -f streamlit

# Or use different port
streamlit run main_app.py --server.port 8502
```

### Database Not Found

```bash
# Re-run ETL pipelines
python3 etl_pipeline.py
python3 marketing_etl.py
```

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Permission Denied

```bash
# Make script executable
chmod +x run_dashboard.sh

# Or run with python directly
python3 -m streamlit run main_app.py
```

## Next Steps

- 📖 Read the [Full Documentation](../README.md)
- 🔮 Explore [Predictive Analytics Guide](../.kiro/specs/predictive-analytics/USER_GUIDE.md)
- 📊 Check [Version History](../CHANGELOG.md)
- 🔒 Review [Security Policy](../SECURITY.md)

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/Tirth-1999/mays-recruiting-analytics/issues)
- **Documentation**: Check README.md for detailed guides
- **Contact**: [Your Email]

---

**Quick Start Guide** • Version 4.0 • Last Updated: January 23, 2026
