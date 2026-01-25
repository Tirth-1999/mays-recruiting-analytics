<div align="center">

# Mays Analytics
### Flex Online Programs Analytics Platform

**Version 5.0** | **Last Updated: January 24, 2026**

AI-powered analytics platform for Texas A&M Mays Business School's Flex Online Programs, providing real-time insights into admissions performance and marketing effectiveness with secure Google OAuth authentication.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-5.0-blue.svg)](VERSIONING.md)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)

[Documentation](docs/README.md) • [Quick Start](docs/QUICK_START.md) • [Deployment](DEPLOYMENT.md) • [Changelog](CHANGELOG.md)

</div>

---

## What's New in Version 5.0

**Authentication & UI Optimization** - Released January 24, 2026

### 🔐 Google OAuth 2.0 Authentication
- **Secure Login**: Full Google OAuth 2.0 integration with user profiles
- **Role-Based Access**: Admin and regular user roles with permission controls
- **Profile Management**: User name, email, profile picture, and role display
- **Session Security**: OAuth state validation and secure session handling

### 🎨 Sidebar UI Complete Redesign
- **Optimized Layout**: Compact profile, navigation, and footer sections
- **Minimal Spacing**: Perfect 10px margins between all sections
- **No Scrolling**: Fits all elements on laptop/desktop screens
- **Responsive Design**: Adapts to Desktop (12px), Laptop (10px), Tablet (8px)

### 🔒 Role-Based Access Control
- **Data Explorer**: Admins see all tables, users restricted from sensitive data
- **Admin Tables**: `users`, `metadata`, `model_predictions`, `chat_history`
- **Security**: Backend enforcement of access rules

### 📱 Professional UI
- **Clean Design**: No emojis, professional appearance
- **White Backgrounds**: Visual distinction for navigation tabs
- **Smooth Animations**: 3px slide on hover, maroon gradient for active tabs
- **Gold Dividers**: 2px solid gold separators between sections

[View complete changelog →](CHANGELOG.md)

---

## What's New in Version 4.4

**Navigation & UX Enhancements (Final)** - Released January 24, 2026

- 🔼 **Back to Top Button - Chevron Style**: Circular button with triangle icon (▲) and 2.5-second smooth scroll
- 📐 **Collapsed Sidebar**: Starts closed by default, overlay mode prevents content shifting
- ✨ **Smooth Animations**: Ease-in-out scrolling with visible content during animation
- 📱 **Mobile Responsive**: Button adapts to mobile screens (50px)
- 🎨 **Professional Design**: Maroon gradient, white icon, glassmorphism effects

[View complete changelog →](CHANGELOG.md)

---

## Overview

Mays Analytics is an AI-powered platform designed for Texas A&M Mays Business School to track, analyze, and predict admissions performance across 7 graduate programs. The platform combines real-time data visualization with machine learning and secure authentication to provide actionable insights for enrollment planning and marketing optimization.

**Key Capabilities:**
- **Secure Authentication**: Google OAuth 2.0 with role-based access control
- **Real-time Analytics**: Track admissions metrics across cohorts and programs
- **Predictive Forecasting**: AI-powered predictions with 95% confidence intervals
- **Marketing ROI Analysis**: Comprehensive spend tracking and channel optimization
- **Year-over-Year Comparisons**: Detailed cohort performance analysis
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

### Predictive Analytics (New in v4.0)

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
- **[Version History](VERSIONING.md)** - Complete development timeline
- **[Changelog](CHANGELOG.md)** - Detailed change log
- **[Security Policy](SECURITY.md)** - Security guidelines
- **[Code of Conduct](CODE_OF_CONDUCT.md)** - Community guidelines

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| **4.0** | Jan 23, 2026 | Predictive Analytics & ML Integration |
| **3.0** | Jan 23, 2026 | Complete Modular Architecture |
| **2.0** | Jan 14, 2026 | Marketing Spend Integration |
| **1.0** | Apr 30, 2024 | Initial Release |

[View full version history →](VERSIONING.md)

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

**Mays Analytics Platform** • Version 4.3 • Built for Texas A&M Mays Business School

</div>
