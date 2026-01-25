# Mays Analytics - Documentation

Welcome to the comprehensive documentation for the Mays Analytics Platform.

---

## What's New in Version 5.2

**OAuth Button Refinement** - Released January 25, 2026

### 🔧 Authentication UX Improvements
- **Reliable OAuth Flow**: Simplified authentication using new-tab approach for maximum compatibility
- **Session State Fix**: Resolved Streamlit Cloud session persistence issues during OAuth redirects
- **Clean Implementation**: Removed complex JavaScript workarounds in favor of reliable `st.link_button`
- **Production Tested**: Verified working on both desktop and mobile devices

### 📱 Technical Improvements
- Streamlined OAuth button implementation
- Better handling of browser security restrictions
- Improved logout button behavior (same-tab redirect)
- Enhanced error handling and user feedback

### 🔍 Technical Details
- OAuth opens in new tab to preserve session state
- Logout uses `target="_self"` for same-tab redirect
- Removed complex device detection and JavaScript close attempts
- Accepts browser security limitations for better reliability

[View complete changelog →](CHANGELOG.md)

---

## What's New in Version 5.1

**OAuth Fix & Consent Screen** - Released January 25, 2026

### 🔧 Authentication Fixes
- **Fixed 403 Error**: Resolved persistent authentication errors with new OAuth client
- **Consent Screen**: Added proper Google consent screen showing permissions
- **State Validation**: Improved OAuth state handling for Streamlit Cloud
- **Production Ready**: Fully working authentication in production

### 🔒 Security Improvements
- New OAuth 2.0 Client ID with proper configuration
- Better error handling and user feedback
- Improved session state management during redirects

[View complete changelog →](CHANGELOG.md)

---

## What's New in Version 5.0

**Authentication & UI Optimization** - Released January 24, 2026

Version 5.0 is a major release featuring complete authentication system and optimized UI:

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

Version 4.4 completes the navigation improvements with enhanced scroll functionality:

- 🔼 **Back to Top Button - Chevron Style**: Circular button (56px) with triangle chevron icon (▲)
- ⏱️ **Smooth 2.5-Second Scroll**: Custom animation with ease-in-out easing for visible content scrolling
- 📐 **Collapsed Sidebar**: Starts closed by default, overlay mode prevents content shifting
- 🎨 **Professional Design**: Maroon gradient, white icon, semi-transparent border with glassmorphism
- 💫 **Hover Effects**: Lift 3px, scale to 1.03, enhanced shadow on hover
- 📱 **Mobile Responsive**: Adapts to 50px on mobile devices
- 🔒 **Fixed Position**: Always visible in bottom-right corner (30px from edges)
- ✨ **Smooth Animation**: Users can see content while scrolling to top

[View complete changelog →](CHANGELOG.md)

---

## What's New in Version 4.2

**Contact & Feedback Integration** - Released January 24, 2026

Version 4.2 adds direct communication capabilities to the platform:

- 📧 **Contact & Feedback Form**: Comprehensive form in Documentation page for reporting bugs, suggesting improvements, or asking questions
- 📨 **Email Integration**: Powered by Resend API - all feedback sent to tirth.shah@tamu.edu with professional HTML formatting
- 🎯 **Feedback Types**: Bug Report, Suggest Improvement, Ask Question, General Feedback, Other
- 📊 **Page Tagging**: Multi-select dropdown to specify which pages feedback relates to
- 🔒 **Secure Deployment**: Streamlit Cloud secrets integration for production environments
- 📖 **Deployment Guide**: Complete DEPLOYMENT.md with Streamlit Cloud setup instructions
- ✅ **Validation**: Required field validation and email format checking

[View complete changelog →](CHANGELOG.md) | [Deployment Guide →](DEPLOYMENT_CHECKLIST.md)

---

## What's New in Version 4.1

**UI/UX Refinements & Responsive Design** - Released January 24, 2026

Version 4.1 brings significant improvements to the user interface and responsive design:

- ✨ **Standardized Design**: Consistent metric boxes and headers across all pages
- 📱 **Responsive Layout**: Mobile-optimized with 1000px breakpoint - all layouts stack to single column
- 🎨 **Professional Appearance**: Emoji-free headers, centered content, consistent styling
- 📊 **Enhanced Data Explorer**: Individual question boxes with equal sizing using flexbox
- 📖 **Documentation Overhaul**: Chrome-style tabs with horizontal scrolling and responsive grid system
- 🔧 **Sidebar Fix**: Overlay behavior on all screen sizes - no content shifting when opening/closing
- 📐 **Centered Mobile Content**: All text and boxes centered in mobile/tablet mode for better readability

[View complete changelog →](CHANGELOG.md)

---

## Documentation Structure

### Getting Started

**[Quick Start Guide](QUICK_START.md)**  
Complete installation and setup instructions to get the platform running in minutes.

**[Technical Guide](TECHNICAL_GUIDE.md)**  
Database schema, configuration options, and troubleshooting guide.

### Platform Features

**[Home Dashboard](HOME_DASHBOARD.md)**  
Overview and key metrics for cohort performance tracking.

**[Executive Deep Dive](EXECUTIVE_DEEP_DIVE.md)**  
Comprehensive cohort analysis with four specialized tabs.

**[Comparison Tool](COMPARISON_TOOL.md)**  
Year-over-year cohort comparisons with statistical analysis.

**[Marketing Analysis](MARKETING_ANALYSIS.md)**  
Marketing spend tracking and ROI analysis across channels.

**[Data Explorer](DATA_EXPLORER.md)**  
Raw data access with advanced filtering and CSV export.

**[Predictive Analytics](PREDICTIVE_ANALYTICS.md)**  
AI-powered forecasting and optimization using machine learning.

### Project Information

**[Version History](CHANGELOG.md)**  
Complete development timeline and version details.

**[Changelog](CHANGELOG.md)**  
Detailed change log for all releases.

**[Security Policy](../SECURITY.md)**  
Security guidelines and vulnerability reporting.

**[Code of Conduct](../CODE_OF_CONDUCT.md)**  
Community guidelines and contribution standards.

**[License](../LICENSE)**  
MIT License information.

---

## Platform Overview

**Current Version:** 4.4  
**Last Updated:** January 24, 2026

### Analytics Pages
- Home Dashboard
- Executive Deep Dive
- Comparison Tool
- Marketing Analysis
- Data Explorer
- Predictive Analytics

### Programs Tracked
MBA, MS ACCT, MS ENLD, MS HRM, MS MISY, MS MKTG, MS SPBA

### Cohorts
Class of 2026, 2027, 2028

### ML Models
Prophet, ARIMA, Linear Regression

### Navigation Features (New in v4.3)
- Floating "Back to Top" button with professional design
- Collapsed sidebar by default
- Smooth scroll behavior
- Mobile-responsive button sizing

### Communication Features (v4.2)
- In-app contact & feedback form
- Email integration with Resend API
- Multi-select page tagging
- Professional HTML email formatting

### Design Features (v4.1)
- Responsive grid system (1000px breakpoint)
- Chrome-style tabs with horizontal scrolling
- Consistent metric box styling
- Mobile-optimized centered layouts
- Professional emoji-free headers

---

## Documentation by Role

### Administrators
- [Quick Start Guide](QUICK_START.md) - Installation and setup
- [Technical Guide](TECHNICAL_GUIDE.md) - Configuration and maintenance
- [Security Policy](../SECURITY.md) - Security best practices

### Data Analysts
- [Home Dashboard](HOME_DASHBOARD.md) - Quick overview
- [Executive Deep Dive](EXECUTIVE_DEEP_DIVE.md) - Detailed analysis
- [Comparison Tool](COMPARISON_TOOL.md) - Year-over-year comparisons
- [Data Explorer](DATA_EXPLORER.md) - Raw data access

### Marketing Teams
- [Marketing Analysis](MARKETING_ANALYSIS.md) - Spend and ROI tracking
- [Predictive Analytics](PREDICTIVE_ANALYTICS.md) - Channel optimization and forecasting

### Developers
- [Technical Guide](TECHNICAL_GUIDE.md) - Architecture and database schema
- [Version History](CHANGELOG.md) - Development timeline
- [Code of Conduct](../CODE_OF_CONDUCT.md) - Contribution guidelines

---

## Quick Reference

### Key Features
- Real-time admissions analytics
- Marketing ROI tracking
- AI-powered forecasting
- Year-over-year comparisons
- Interactive visualizations
- Data export capabilities

### Technology Stack
- Frontend: Streamlit 1.28+
- Visualization: Plotly
- ML/AI: Prophet, statsmodels, scikit-learn
- Database: SQLite
- Language: Python 3.8+

### Data Coverage
- Admissions: 2,037 records across 7 programs
- Marketing: 76 spend records, 90 aggregated metrics
- Date Range: January 2024 - December 2025

---

## Version History Summary

| Version | Date | Key Features |
|---------|------|--------------|
| 4.0 | Jan 23, 2026 | Predictive Analytics & ML Integration |
| 3.0 | Jan 23, 2026 | Complete Modular Architecture |
| 2.0 | Jan 14, 2026 | Marketing Spend Integration |
| 1.0 | Apr 30, 2024 | Initial Release |

[View complete version history](CHANGELOG.md)

---

## Support

**GitHub Issues**  
[Report bugs or request features](https://github.com/Tirth-1999/mays-recruiting-analytics/issues)

**Troubleshooting**  
See the [Technical Guide](TECHNICAL_GUIDE.md) for common issues and solutions.

**Repository**  
[github.com/Tirth-1999/mays-recruiting-analytics](https://github.com/Tirth-1999/mays-recruiting-analytics)

---

**Mays Analytics Documentation** | Version 4.0 | Last Updated: January 23, 2026
