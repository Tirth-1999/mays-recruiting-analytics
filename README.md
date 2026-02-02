# Mays Analytics Platform

[![Version](https://img.shields.io/badge/version-7.0-blue.svg)](https://github.com/Tirth-1999/mays-recruiting-analytics)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)](https://streamlit.io)

**Version 7.0** | **Last Updated: February 2, 2026**

A comprehensive analytics platform for Texas A&M University's Mays Business School Flex Online Programs, providing real-time admissions tracking, marketing ROI analysis, and AI-powered insights.

---

## What's New in Version 7.0

**State Snapshot ETL & Dashboard Enhancement** - Released February 2, 2026

### 🔄 Enhanced ETL Pipeline with State Snapshot Processing
- **State Snapshot Approach**: All data now treated as point-in-time snapshots rather than cumulative totals
- **Unified Cohort Calculation**: All programs (including MBA) use consistent +2 years cohort assignment
- **Smart File Processing**: Processes only 3 key files with `_fall` suffix for accurate cohort tracking
- **Enhanced Schema**: Added `cohort_season` and `file_source` columns for better data lineage
- **Fixed Cohort Assignment**: Corrected Class 2028 data that was incorrectly marked as 2027

### 📊 Comprehensive Dashboard Improvements
- **Executive Dashboard Filtering**: Fixed broken filter logic with proper flow control structure
- **No-Data Handling**: Enhanced handling for programs without data, restored "All Programs" functionality
- **Director's Deep Dive Enhancements**: 
  - Added comprehensive metrics breakdown with expandable sections
  - Implemented trend analysis with scale options (Linear → Log → Square Root)
  - Fixed growth rate analysis to show true fiscal year performance
  - Enhanced chart type buttons and legend label cleanup
- **Comparison Tool Data Quality**: Smart backfilling logic prevents artificial data drops
- **Marketing Analysis Optimization**: Consolidated program/channel/fiscal year into single header line

### 🔧 Data Quality & Performance Improvements
- **Smart Backfilling**: Cumulative metrics (inquiries, applications) never decrease with intelligent backfill
- **Suspicious Zero Detection**: Prevents artificial drops in visualizations
- **Column-Level Filtering**: Skips empty date columns for cleaner data processing
- **Enhanced Validation**: Comprehensive data validation with proper error handling
- **Professional Styling**: Removed emoticons and improved spacing throughout interface

### 📈 Advanced Analytics Features
- **Trend Analysis Scale Options**: Multiple scaling options for better data visualization
- **Growth Rate Analysis**: Compares fiscal year start vs end values for accurate performance metrics
- **Chart Type Flexibility**: Improved chart switching between line and bar graphs
- **Legend Optimization**: Shortened legend labels while maintaining full dropdown names
- **Incremental Notes Optimization**: 70% space reduction with consolidated headers

[View complete changelog →](docs/CHANGELOG.md)

---

## Platform Overview

### 🎯 Key Features
- **Real-time Admissions Analytics**: Track inquiries, applications, and enrollments across all programs
- **Marketing ROI Analysis**: Monitor spend effectiveness across channels and programs
- **AI-Powered Chat Assistant**: Natural language queries for instant data insights
- **Predictive Analytics**: ML-powered forecasting for enrollment and marketing optimization
- **Year-over-Year Comparisons**: Statistical analysis of cohort performance trends
- **Interactive Visualizations**: Dynamic charts with filtering and export capabilities

### 📚 Programs Tracked
- **Flex Online MBA** - Master of Business Administration
- **MS Accounting** - Master of Science in Accounting
- **MS Human Resource Management** - Master of Science in Human Resource Management
- **MS Management Information Systems** - Master of Science in Management Information Systems
- **MS Marketing** - Master of Science in Marketing
- **MS Entrepreneurial Leadership** - Master of Science in Entrepreneurial Leadership
- **AI and Business Program** - Flex Online AI and Business Program

### 📊 Analytics Pages
1. **Executive Dashboard** - High-level metrics and program comparisons
2. **Director's Deep Dive** - Comprehensive cohort analysis with 4 specialized tabs
3. **Marketing Analysis** - Spend tracking and ROI analysis across channels
4. **Predictive Analytics** - AI-powered forecasting and optimization
5. **AI Chat Assistant** - Natural language data queries and platform guidance
6. **Data Explorer** - Raw data access with advanced filtering and export

### 🔐 Authentication & Security
- **Google OAuth 2.0** - Secure authentication with user profiles
- **Role-Based Access** - Admin and regular user permissions
- **Data Privacy** - GDPR-compliant with automatic cleanup
- **Session Security** - OAuth state validation and secure session handling

---

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Git
- Google Cloud Console account (for OAuth)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Tirth-1999/mays-recruiting-analytics.git
   cd mays-recruiting-analytics
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure secrets**
   ```bash
   cp config_secrets.py.template config_secrets.py
   # Edit config_secrets.py with your credentials
   ```

5. **Run the application**
   ```bash
   streamlit run main_app.py
   ```

6. **Access the platform**
   - Open your browser to `http://localhost:8501`
   - Sign in with Google OAuth
   - Start exploring your data!

For detailed setup instructions, see the [Quick Start Guide](docs/QUICK_START.md).

---

## Technology Stack

### Frontend & Visualization
- **Streamlit 1.28+** - Web application framework
- **Plotly** - Interactive charts and visualizations
- **HTML/CSS/JavaScript** - Custom styling and interactions

### Backend & Data Processing
- **Python 3.8+** - Core programming language
- **SQLite** - Database for data storage
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing

### AI & Machine Learning
- **Google Gemini AI** - Natural language processing
- **ChromaDB** - Vector database for semantic search
- **Prophet** - Time series forecasting
- **scikit-learn** - Machine learning algorithms
- **statsmodels** - Statistical analysis

### Authentication & Security
- **Google OAuth 2.0** - Secure authentication
- **google-auth** - Authentication libraries
- **Session management** - Secure user sessions

---

## Data Coverage

### Admissions Data
- **Records**: 2,037+ admissions records
- **Programs**: 7 graduate programs
- **Cohorts**: Classes of 2026, 2027, 2028
- **Metrics**: 20+ tracked metrics per application
- **Date Range**: July 2024 - December 2025

### Marketing Data
- **Spend Records**: 585+ individual channel records
- **Totals**: 120+ aggregated metrics
- **Fiscal Years**: FY25 (Sept 2024-June 2025), FY26 (Aug-Dec 2025)
- **Channels**: Google Ads, Facebook, LinkedIn, Email, General Awareness
- **Programs**: All 7 programs with channel-specific tracking

### AI Chat Data
- **Conversations**: User-specific chat history
- **Feedback**: Thumbs up/down ratings with analytics
- **Performance**: <3s response time for 80% of queries
- **Security**: Rate limiting and SQL validation

---

## Documentation

### User Guides
- **[Quick Start Guide](docs/QUICK_START.md)** - Installation and setup
- **[Executive Dashboard](docs/EXECUTIVE_DASHBOARD.md)** - Overview and key metrics
- **[Director's Deep Dive](docs/DIRECTORS_DEEP_DIVE.md)** - Comprehensive analysis
- **[Marketing Analysis](docs/MARKETING_ANALYSIS.md)** - Spend and ROI tracking
- **[AI Chat Assistant](docs/AI_CHAT_ASSISTANT.md)** - Natural language queries
- **[Data Explorer](docs/DATA_EXPLORER.md)** - Raw data access
- **[Predictive Analytics](docs/PREDICTIVE_ANALYTICS.md)** - ML forecasting

### Technical Documentation
- **[Technical Guide](docs/TECHNICAL_GUIDE.md)** - Architecture and configuration
- **[Deployment Checklist](docs/DEPLOYMENT_CHECKLIST.md)** - Production deployment
- **[Changelog](docs/CHANGELOG.md)** - Complete version history

---

## Version History

| Version | Date | Type | Key Features |
|---------|------|------|--------------|
| **7.0** | Feb 2, 2026 | Major | State Snapshot ETL & Dashboard Enhancement |
| **6.10** | Feb 1, 2026 | Major | Data Explorer Restructure |
| **6.9** | Feb 1, 2026 | Minor | Database Optimization |
| **6.8** | Feb 1, 2026 | Major | Marketing Analytics Enhancement |
| **6.5** | Jan 27, 2026 | Major | UI/UX Polish & Mobile Optimization |
| **6.2** | Jan 27, 2026 | Major | Professor Feedback Implementation |
| **6.0** | Jan 25, 2026 | Major | AI-Powered Analytics |
| **5.0** | Jan 24, 2026 | Major | Authentication & UI Optimization |
| **4.0** | Jan 23, 2026 | Major | Predictive Analytics & ML Integration |
| **3.0** | Jan 23, 2026 | Major | Complete Modular Architecture |
| **2.0** | Jan 14, 2026 | Major | Marketing Integration |
| **1.0** | Apr 30, 2024 | Major | Initial Release |

[View complete changelog →](docs/CHANGELOG.md)

---

## Contributing

We welcome contributions! Please see our [Code of Conduct](CODE_OF_CONDUCT.md) for guidelines.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Reporting Issues
- Use GitHub Issues for bug reports
- Include detailed reproduction steps
- Attach screenshots if relevant

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

### Getting Help
- **Documentation**: [docs/README.md](docs/README.md)
- **Issues**: [GitHub Issues](https://github.com/Tirth-1999/mays-recruiting-analytics/issues)
- **Contact**: Use the in-app feedback form in Documentation & Help

### Troubleshooting
- Check the [Technical Guide](docs/TECHNICAL_GUIDE.md) for common issues
- Verify all dependencies are installed correctly
- Ensure Python 3.8+ is being used
- Check that all required secrets are configured

---

## Acknowledgments

- **Texas A&M University** - Mays Business School
- **Flex Online Programs** - Data and requirements
- **Streamlit Community** - Framework and support
- **Google Cloud** - AI and authentication services

---

**Mays Analytics Platform** | Version 7.0 | © 2024-2026 Texas A&M University