<div align="center">

# Mays Analytics
### Flex Online Programs Analytics Platform

**Version 6.8** | **Last Updated: February 1, 2026**

AI-powered analytics platform for Texas A&M Mays Business School's Flex Online Programs, featuring natural language query interface, real-time insights, and secure Google OAuth authentication.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-6.8-blue.svg)](docs/CHANGELOG.md)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)

[Documentation](docs/README.md) • [Quick Start](docs/QUICK_START.md) • [Changelog](docs/CHANGELOG.md)

</div>

---

## What's New in Version 6.8

**Marketing Analytics Enhancement** - Released February 1, 2026

### 📊 Enhanced Marketing ETL Pipeline
- **Dynamic Sheet Detection**: Automatically detects FY25, FY26, and future fiscal year sheets
- **Flexible Month Columns**: Handles varying month ranges (FY25: Sept-June, FY26: Aug-Dec)
- **State Tracking**: Incremental updates with change detection for efficient processing
- **Program Name Standardization**: Centralized mapping with "AI" → "Flex Online AI and Business Program"

### 🗓️ Fiscal Year-Specific Month Filtering
- **Smart Month Filtering**: Month options now depend on selected fiscal years
- **Chronological Sorting**: Months appear in date order, not alphabetical
- **Fiscal Year Grouping**: When multiple FYs selected, months grouped by fiscal year
- **Fixed Date Bug**: Corrected August 2026 → August 2025 for FY26

### 📝 Incremental Notes Restructure
- **Separate Notes Table**: One note per program-channel-fiscal_year (no duplication)
- **Enhanced Notes Display**: Organized by fiscal year with expandable sections
- **Reduced Data Redundancy**: From 167 duplicated records to 16 unique combinations
- **Better UX**: Clear program-channel identification with short names

### 🔧 Technical Improvements
- **4-Column Filtering**: Fiscal Year → Program → Channel → Month drill-down
- **Database Optimization**: New `marketing_incremental_notes` table structure
- **Error Handling**: Robust processing of dynamic Excel structures
- **Performance**: Efficient state tracking prevents unnecessary reprocessing

[View complete changelog →](docs/CHANGELOG.md)

---

## Overview

Mays Analytics is an AI-powered platform designed for Texas A&M Mays Business School to track, analyze, and predict admissions performance across 7 graduate programs. The platform combines real-time data visualization with machine learning, natural language query interface, and secure authentication to provide actionable insights for enrollment planning and marketing optimization.

**Key Capabilities:**
- **AI Chat Assistant**: Natural language interface for instant data queries and insights
- **Secure Authentication**: Google OAuth 2.0 with role-based access control
- **Real-time Analytics**: Track admissions metrics across cohorts and programs
- **Predictive Forecasting**: AI-powered predictions with 95% confidence intervals
- **Marketing ROI Analysis**: Comprehensive spend tracking and channel optimization
- **Year-over-Year Comparisons**: Detailed cohort performance analysis
- **Conversation Memory**: Context-aware follow-up questions and smart query processing
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Data Export**: Full CSV download capabilities with role-based permissions

---

## Quick Start

```bash
# Clone and setup
git clone https://github.com/Tirth-1999/mays-recruiting-analytics.git
cd mays-recruiting-analytics
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Load data
python3 etl_pipeline.py
python3 marketing_etl.py

# Run dashboard
streamlit run main_app.py
```

Dashboard opens at `http://localhost:8501` (or visit the live deployment at https://mays-recruiting-analytics.streamlit.app/)

For detailed setup instructions, see the [Quick Start Guide](docs/QUICK_START.md).

---

## Platform Features

### Analytics Pages

| Page | Description | Documentation |
|------|-------------|---------------|
| **Home Dashboard** | Overview with key metrics and trends | [Guide](docs/HOME_DASHBOARD.md) |
| **Executive Deep Dive** | Comprehensive cohort analysis with 4 tabs | [Guide](docs/EXECUTIVE_DEEP_DIVE.md) |
| **Comparison Tool** | Year-over-year cohort comparisons | [Guide](docs/COMPARISON_TOOL.md) |
| **Marketing Analysis** | Spend tracking and ROI analysis | [Guide](docs/MARKETING_ANALYSIS.md) |
| **Data Explorer** | Raw data access and CSV export | [Guide](docs/DATA_EXPLORER.md) |
| **Predictive Analytics** | AI forecasting and optimization | [Guide](docs/PREDICTIVE_ANALYTICS.md) |
| **AI Chat Assistant** | Natural language query interface | [Guide](docs/AI_CHAT_ASSISTANT.md) |

### AI Chat Assistant (New in v6.0)

- **Natural Language Queries**: Ask questions in plain English about your data
- **Conversation Memory**: Context-aware follow-ups and reference resolution
- **Smart Processing**: Understands business terms, abbreviations, and complex queries
- **Rate Limiting**: 10 queries/minute with visual indicators and countdown timer
- **Feedback System**: Rate responses to improve accuracy over time
- **Chat History**: Search, export, and manage all conversations
- **Privacy Controls**: GDPR-compliant data management and automatic cleanup

### Predictive Analytics (v4.0)

- **Time Series Forecasting**: Predict inquiries, applications, and enrollments with 95% confidence intervals
- **Channel Optimization**: AI-powered ROI analysis for marketing channels
- **Timing Analysis**: Identify optimal months for marketing investments
- **Budget Allocation**: Data-driven budget distribution recommendations
- **Model Performance**: Real-time accuracy tracking with MAPE, RMSE, MAE

[View complete feature list →](docs/README.md)

---

## Technology Stack

- **Frontend**: Streamlit 1.28+
- **Visualization**: Plotly
- **ML/AI**: Prophet, statsmodels (ARIMA), scikit-learn
- **Database**: SQLite
- **Language**: Python 3.8+

---

## Project Structure

```
.
├── main_app.py                 # Main application (routing)
├── version.py                  # Version management
├── etl_pipeline.py             # Admissions data ETL
├── marketing_etl.py            # Marketing data ETL
├── requirements.txt            # Dependencies
├── edulytix.db                # SQLite database
│
├── modules/                   # Page modules
│   ├── home_dashboard.py
│   ├── executive_deep_dive.py
│   ├── comparison_tool.py
│   ├── marketing_analysis.py
│   ├── database.py
│   └── predictive_analytics.py
│
├── utils/                     # Utility modules
│   ├── database.py
│   ├── data_processing.py
│   ├── data_preprocessing.py
│   ├── ml_models.py
│   ├── table_display.py
│   └── validation.py
│
├── docs/                      # Documentation
│   ├── README.md
│   ├── QUICK_START.md
│   └── [Page guides]
│
└── Dataset/                   # Data files
    └── [Excel files]
```

---

## Data Coverage

- **Admissions**: 2,037 records across 7 programs
- **Marketing**: 76 spend records, 90 aggregated metrics
- **Date Range**: January 2024 - December 2025
- **Programs**: MBA, MS ACCT, MS ENLD, MS HRM, MS MISY, MS MKTG, MS SPBA
- **Cohorts**: Class of 2026, 2027, 2028

---

## Documentation

- **[Complete Documentation](docs/README.md)** - Central documentation hub
- **[Quick Start Guide](docs/QUICK_START.md)** - Installation and setup
- **[Changelog](docs/CHANGELOG.md)** - Complete version history and changes
- **[Security Policy](SECURITY.md)** - Security guidelines
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Community guidelines

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| **6.8** | Feb 1, 2026 | Marketing Analytics Enhancement & Fiscal Year-Specific Month Filtering |
| **6.5** | Jan 27, 2026 | UI/UX Polish & Mobile Optimization |
| **6.0** | Jan 25, 2026 | AI Chat Assistant with Natural Language Queries |
| **5.2** | Jan 25, 2026 | OAuth Button Refinement |
| **5.1** | Jan 25, 2026 | OAuth Fix & Consent Screen |
| **5.0** | Jan 24, 2026 | Authentication & UI Optimization |
| **4.0** | Jan 23, 2026 | Predictive Analytics & ML Integration |
| **3.0** | Jan 23, 2026 | Complete Modular Architecture |
| **2.0** | Jan 14, 2026 | Marketing Spend Integration |
| **1.0** | Apr 30, 2024 | Initial Release |

[View full version history →](docs/CHANGELOG.md)

---

## Contributing

We welcome contributions! Please see our [Code of Conduct](CODE_OF_CONDUCT.md) for guidelines.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact

- **Email**: [tirth.shah@tamu.edu](mailto:tirth.shah@tamu.edu)
- **GitHub**: [@Tirth-1999](https://github.com/Tirth-1999)
- **Repository**: [mays-recruiting-analytics](https://github.com/Tirth-1999/mays-recruiting-analytics)
- **Feedback Form**: Use the Contact & Feedback form in the Documentation page to report bugs, suggest improvements, or ask questions

---

<div align="center">

**Mays Analytics Platform** • Version 6.8 • Built for Texas A&M Mays Business School

</div>
