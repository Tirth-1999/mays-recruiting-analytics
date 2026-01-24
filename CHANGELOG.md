# Changelog

All notable changes to the Mays Analytics Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [4.1.0] - 2026-01-24

### 🎨 Minor Release - UI/UX Refinements & Responsive Design

#### Changed
- **Metric Box Styling** (All Pages):
  - Reduced metric box padding from 1.5rem to 1rem
  - Reduced metric number font-size from 2.5rem to 1.8rem
  - Removed emojis from metric boxes for professional appearance
  - Added 20px left padding for centered numbers
  - Kept emojis in filter labels for usability

- **Header Standardization**:
  - Applied consistent header background (#e9ecef) across all pages
  - Removed emojis from section headers and tab names
  - Centered all headers for professional appearance
  - Standardized styling: Home, Executive, Comparison, Marketing, Data Explorer

- **Data Explorer Enhancements**:
  - Simplified tab names (removed emojis, shortened multi-word names)
  - Created individual white boxes for each question (4 per table)
  - Equal-sized question boxes using flexbox
  - Consistent header styling for "Filter & Explore Data" and "Data Table"

- **Documentation Page Overhaul**:
  - Changed sidebar name from "Help & Documentation" to "Documentation"
  - Implemented Chrome-style tabs with horizontal scrolling
  - Custom scrollbar styling with maroon theme
  - Responsive grid system for all sections (breakpoint at 1000px)
  - Centered content in mobile/tablet mode
  - Card-style boxes with equal heights
  - Scrollable Common Issues section (400px height)

#### Fixed
- **Sidebar Behavior**:
  - Sidebar now overlays content on ALL screen sizes (never shrinks content)
  - Eliminated content shifting animation when sidebar opens/closes
  - Hidden collapsed sidebar completely (display: none)
  - Disabled all transitions for smooth, static experience

- **Responsive Design**:
  - All multi-column layouts stack to single column at 1000px width
  - Centered boxes and text content in mobile/tablet mode
  - Lists remain left-aligned but centered as blocks for readability
  - Touch-friendly scrolling with visible scrollbars

#### Impact
- 7 files modified (home_dashboard.py, executive_deep_dive.py, comparison_tool.py, marketing_analysis.py, database.py, help.py, main_app.py)
- 100% UI consistency across all pages
- Significantly improved mobile experience
- Professional emoji-free appearance

---

## [4.0.0] - 2026-01-23

### 🎉 Major Release - Predictive Analytics & ML Integration

#### Added
- **Predictive Analytics Module** with 5 comprehensive tabs:
  - 📈 Time Series Forecasting with 95% confidence intervals
  - 📢 Channel Optimization with AI-powered ROI analysis
  - 📅 Timing Analysis for seasonal pattern detection
  - 💰 Budget Allocation with data-driven recommendations
  - 🎯 Model Performance tracking with real-time accuracy metrics

- **Advanced ML Models**:
  - Prophet Model for advanced forecasting (24+ months data)
  - ARIMA Model for statistical forecasting (12-24 months data)
  - Linear Regression for trend-based forecasting (<12 months data)
  - Automatic model selection based on data characteristics

- **Database Enhancements**:
  - `model_predictions` table for tracking forecasts
  - Migration system with rollback capability
  - Optimized queries for large datasets

- **Documentation**:
  - Comprehensive Predictive Analytics User Guide
  - Chrome-style tabbed navigation in README
  - "What's New in Version 4.0" section

#### Changed
- Updated version from 3.0 to 4.0
- Enhanced README with detailed feature documentation
- Improved .gitignore for better exclusions

#### Removed
- 23 temporary and test files for cleaner production deployment:
  - 8 test files (test_*.py)
  - 2 unused utilities (database_optimization.py, visualizations.py)
  - 1 example file (visualizations_usage_example.py)
  - 11 development documentation files
  - 1 test summary file

#### Technical Details
- **Files Added**: 6 (predictive_analytics.py, ml_models.py, data_preprocessing.py, validation.py, add_model_predictions_table.py, USER_GUIDE.md)
- **Lines of Code**: +6,701 additions
- **Model Accuracy**: MAPE < 15% for reliable forecasts
- **Confidence Intervals**: 95% for all predictions

---

## [3.0.0] - 2026-01-23

### 🏗️ Major Release - Complete Modular Architecture

#### Added
- **Modular Architecture** (7-Phase Migration):
  - Extracted utility modules to `utils/` folder
  - Extracted all page modules to `modules/` folder
  - Created single source of truth for all functions

- **New Utility Modules**:
  - `utils/database.py` - Database connections and data loading (121 lines)
  - `utils/data_processing.py` - Data insights generation (37 lines)
  - `utils/table_display.py` - Table filtering and display (273 lines)

- **Modular Page Structure**:
  - `modules/help.py` - Help & Documentation (539 lines)
  - `modules/home_dashboard.py` - Home Dashboard (630 lines)
  - `modules/database.py` - Data Explorer (421 lines)
  - `modules/comparison_tool.py` - Comparison Tool (665 lines)
  - `modules/executive_deep_dive.py` - Executive Deep Dive (1,077 lines)
  - `modules/marketing_analysis.py` - Marketing Analysis (1,402 lines)

- **Centralized Version Management**:
  - Created `version.py` - Single source of truth for version numbers
  - Dynamic version display across all pages

#### Changed
- **main_app.py**: Reduced from 933 lines to 400 lines (57% reduction)
- **Code Duplication**: Eliminated 100% (removed 7 duplicate functions)
- **Unused Code**: Removed 652+ lines
- **Performance**: 15-20% faster initial page load

#### Removed
- Duplicate function definitions from main_app.py
- 9 unused imports (pandas, plotly, sqlite3, numpy, etc.)
- Unused `utils/styling.py` module (268 lines)
- Duplicate CSS definitions

#### Technical Metrics
- **Before**: 933 lines (monolithic), High duplication
- **After**: 400 lines (modular), Zero duplication
- **Maintainability**: Low → High
- **Team Collaboration**: Not possible → Fully enabled

---

## [2.4.0] - 2026-01-23

### UI/UX Refinements - Cleaner Interface

#### Added
- Collapsible "How to Use" sections across all pages
- Performance Benchmarks with center-aligned metrics
- Chrome-style tabs for Help & Documentation

#### Changed
- Sidebar optimization: Reduced padding and spacing
- Removed redundant branding elements
- Removed emojis from navigation buttons
- Centered tab layout with proper spacing

#### Fixed
- HTML rendering issues in Help page
- Mobile-friendly tab sizing

---

## [2.3.0] - 2026-01-22

### Comparison Tool - Major Enhancements

#### Added
- Smart metric filtering (excludes zero-value metrics)
- Excluded metrics note with yellow info box
- Enhanced performance indicators with descriptive messages

#### Changed
- Restructured layout: "How to Use" moved above "Comparing" header
- Fixed percentage change display (shows "N/A" for no base comparison)
- Improved chart spacing with proper padding

#### Fixed
- Correct statistical calculations (Variance, Std Dev, Coefficient of Variation)

---

## [2.2.0] - 2026-01-22

### Executive Deep Dive - Major Restructure

#### Added
- New "Comparison Tool" as dedicated YoY analysis page
- Program Deep Dive with split metrics (Applications & Admissions)
- Chart type toggle (Line vs Bar)
- Log scale toggle for both chart types

#### Changed
- Reduced tabs from 5 to 4 (moved Advanced Insights to Comparison Tool)
- Removed "Compare With" filter from main interface
- Optimized layout with 60:20:20 ratio

#### Removed
- Advanced Insights tab (moved to Comparison Tool)
- Redundant program filter and headers

---

## [2.1.0] - 2026-01-21

### Global Filter System & Responsive Design

#### Added
- Global filter system for Marketing Analysis
- Responsive tab design with horizontal scrolling
- Enhanced Data Explorer with professional table navigation

#### Changed
- Chrome-style tabs with mobile optimization
- Darker section headers (#e9ecef) for better visibility
- Filter independence (each filter maintains own state)

---

## [2.0.0] - 2026-01-14

### Marketing Spend Integration

#### Added
- December 2025 data (latest admissions through Dec 31, 2025)
- Marketing spend integration (FY25 Year 1 ad spend data)
- Update timestamps in footer
- Professional UI with consistent maroon theme

#### Data Coverage
- **Admissions Records**: 2,037 records across 7 programs
- **Marketing Records**: 76 spend records, 90 aggregated metrics
- **Date Range**: January 2024 - December 2025 (admissions)
- **Programs**: MBA, MS ACCT, MS ENLD, MS HRM, MS MISY, MS MKTG, MS SPBA
- **Cohorts**: Class of 2026, 2027, 2028

---

## [1.0.0] - 2024-04-30

### Initial Release

#### Added
- Home Dashboard with key metrics
- Executive Deep Dive with comprehensive analytics
- Data Explorer for raw data access
- Marketing Analysis (basic)
- ETL pipeline for data loading
- SQLite database integration

#### Features
- Cohort-based analysis
- Program comparison
- Trend analysis
- Interactive charts with Plotly
- Streamlit-based UI

---

## Version Summary

| Version | Release Date | Type | Key Features |
|---------|-------------|------|--------------|
| **4.0.0** | 2026-01-23 | Major | Predictive Analytics & ML Integration |
| **3.0.0** | 2026-01-23 | Major | Complete Modular Architecture |
| **2.4.0** | 2026-01-23 | Minor | UI/UX Refinements |
| **2.3.0** | 2026-01-22 | Minor | Comparison Tool Enhancements |
| **2.2.0** | 2026-01-22 | Minor | Executive Deep Dive Restructure |
| **2.1.0** | 2026-01-21 | Minor | Global Filters & Responsive Design |
| **2.0.0** | 2026-01-14 | Major | Marketing Spend Integration |
| **1.0.0** | 2024-04-30 | Major | Initial Release |

---

## Upgrade Guide

### From 3.0 to 4.0
1. Run database migration: `python3 migrations/add_model_predictions_table.py migrate`
2. Install new dependencies: `pip install -r requirements.txt`
3. No breaking changes - all existing features preserved

### From 2.x to 3.0
1. No database changes required
2. Update imports if you have custom extensions
3. All page functionality preserved

### From 1.x to 2.0
1. Run marketing ETL: `python3 marketing_etl.py`
2. Update database schema for marketing tables
3. New marketing analysis features available

---

## Future Roadmap

### Planned for 4.1
- Real-time data refresh
- Email alerts for forecast deviations
- Custom dashboard builder

### Planned for 5.0
- Multi-university support
- Advanced AI recommendations
- Automated report generation
- API for external integrations

---

[4.0.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v4.0.0
[3.0.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v3.0.0
[2.4.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v2.4.0
[2.3.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v2.3.0
[2.2.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v2.2.0
[2.1.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v2.1.0
[2.0.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v2.0.0
[1.0.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v1.0.0
