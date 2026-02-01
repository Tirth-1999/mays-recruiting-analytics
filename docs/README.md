# Mays Analytics - Documentation

Welcome to the comprehensive documentation for the Mays Analytics Platform.

---

## What's New in Version 6.8

**Marketing Analytics Enhancement** - Released February 1, 2026

### 📊 Enhanced Marketing ETL Pipeline
- **Dynamic Sheet Detection**: Automatically detects FY25, FY26, and future fiscal year sheets (FY27+)
- **Flexible Month Columns**: Handles varying month ranges across fiscal years (FY25: Sept 2024-June 2025, FY26: Aug-Dec 2025)
- **State Tracking System**: Incremental updates with intelligent change detection for efficient processing
- **Program Name Standardization**: Centralized mapping utility with "AI" code → "Flex Online AI and Business Program"
- **Robust Error Handling**: Graceful processing of dynamic Excel structures with comprehensive validation

### 🗓️ Fiscal Year-Specific Month Filtering
- **Smart Month Dependencies**: Month filter options now dynamically depend on selected fiscal years
- **Chronological Organization**: Months display in date order (not alphabetical) for intuitive navigation
- **Fiscal Year Grouping**: When multiple FYs selected, months organized by fiscal year sections
- **Enhanced UX**: Clear "No months available" states and improved filter interactions
- **Fixed Date Conversion Bug**: Corrected August 2026 → August 2025 for proper FY26 representation

### 📝 Incremental Notes Database Restructure
- **Separate Notes Table**: New `marketing_incremental_notes` table eliminates data duplication
- **One Note Per Combination**: Single record per program-channel-fiscal_year (reduced from 167 duplicates to 16 unique)
- **Enhanced Display**: Notes organized by fiscal year with expandable program-channel sections
- **Better Identification**: Uses short program names (MBA, AI) for cleaner interface
- **Improved Query Performance**: Dedicated table with proper indexing for faster note retrieval

### 🔧 Technical Architecture Improvements
- **4-Column Filtering Hierarchy**: Fiscal Year → Program → Channel → Month drill-down capability
- **Database Schema Optimization**: Separate tables for spend data, totals, and notes with proper relationships
- **Dynamic Excel Processing**: Handles varying sheet structures and month ranges automatically
- **Performance Optimization**: State tracking prevents unnecessary reprocessing of unchanged data
- **Centralized Program Mapping**: Single source of truth for program name standardization across the platform

### 📈 Data Quality Enhancements
- **Accurate Date Ranges**: FY25 (Sept 2024-June 2025), FY26 (Aug 2025-Dec 2025)
- **Consistent Program Names**: All programs follow standardized naming convention
- **Validated Totals**: Automatic verification that calculated totals match stored aggregates
- **Clean Data Structure**: 585 spend records, 120 totals records, 16 incremental notes across 2 fiscal years

[View complete changelog →](CHANGELOG.md)

---

## What's New in Version 6.5

**UI/UX Polish & Mobile Optimization** - Released January 27, 2026

### 🎨 Responsive Design Enhancements
- **Dynamic Font Sizing**: All key metrics use CSS clamp() for responsive text that adapts to viewport width
- **Sidebar-Aware Breakpoints**: Responsive layouts account for sidebar width (1400px, 1200px, 900px, 768px)
- **Mobile-Optimized Labels**: Chart labels display vertically (0°) on mobile, angled (-45°) on desktop
- **Centered Content**: All metrics, titles, and text properly centered with equal padding

### 📊 Chart Improvements
- **Enhanced Tooltips**: Added helpful tooltips to major charts explaining filter usage
- **Value Labels on Bars**: Numbers displayed on bar charts with extended Y-axis to prevent clipping
- **Shadow Effects**: Line graphs feature subtle shadow fills for better visual depth
- **Legend Positioning**: Legends moved to top center on mobile for better space utilization
- **Performance Radar**: Responsive at 1400px - explanation boxes move below chart on smaller screens

### 🎯 Marketing Analysis Updates
- **Channel Performance by Program**: 
  - Full-width heatmap with centered title
  - Top channels displayed in responsive card grid below heatmap
  - Color-coded spend amounts and percentages
  - Removed subtitle clutter for cleaner look
- **Spend vs Outcomes Trend**:
  - Shadow effects under line graphs
  - Proper fiscal year filtering (FY25 format support)
  - Centered subplot titles
- **Channel Analytics**:
  - Tooltips on all charts
  - Centered titles throughout
  - Values displayed on bar charts
  - Legend moved to top center with proper spacing

### 🧹 Interface Cleanup
- **Removed Dividers**: Cleaned up excessive dividers in Director's Deep Dive, Marketing Analysis, and Predictive Analytics
- **Removed Print Buttons**: Streamlit's native print functionality used instead of custom buttons
- **Removed Dead Code**: Cleaned up ~150 lines of unused print CSS from database.py

### 📱 Mobile Optimization
- **Program Comparison Chart**: Labels perfectly vertical on mobile (≤768px)
- **Spend by Program & Channel**: Legend moves to bottom on mobile with increased chart height
- **Responsive Metrics**: All 6 metrics in Director's Deep Dive adapt dynamically like Marketing Analysis

### 🔧 Technical Implementation
- CSS clamp() for fluid typography: `clamp(min, preferred, max)`
- Media queries for responsive breakpoints
- JavaScript for dynamic layout adjustments
- Aggressive !important flags to override Streamlit's global CSS
- Flexbox for proper centering without wrapping issues

[View complete changelog →](CHANGELOG.md)

---

## What's New in Version 6.0

**AI-Powered Analytics** - Released January 25, 2026

### 💬 AI Chat Assistant (Complete Implementation)
- **Natural Language Queries**: Ask questions in plain English and get instant answers
- **Conversation Memory**: Context-aware follow-up questions and reference resolution
- **Smart Query Processing**: Understands business terms, abbreviations, and complex queries
- **Rate Limiting**: 10 queries/minute per user with visual indicators and countdown timer
- **Feedback System**: Thumbs up/down ratings with comprehensive analytics dashboard
- **Suggested Queries**: Context-aware query suggestions after each response
- **In-App Help**: Quick reference guide accessible from chat header
- **Chat History**: Search, export, and manage all conversations with JSON export
- **Settings & Privacy**: GDPR-compliant data management with automatic 90-day cleanup

### 🎯 Enhanced User Experience
- **Three-Tab Interface**: Current Conversation, Chat History, Settings & Privacy
- **Usage Statistics**: Track conversations, messages, and token usage
- **Feedback Analytics**: Satisfaction rates by query type with color-coded cards
- **Export Capability**: Download all chat data in JSON format
- **Privacy Controls**: Delete conversations, GDPR data deletion, automatic cleanup

### 📊 Technical Implementation
- **Google Gemini AI**: Powered by Gemini 2.5 Flash for fast, accurate responses
- **ChromaDB Vector Store**: Semantic search for schema intelligence
- **Query Pattern Recognition**: Cached templates for common queries (30%+ speed improvement)
- **Token Optimization**: Compressed prompts, limited context (avg <1000 tokens/query)
- **Response Caching**: 5-minute cache with LRU eviction (100 entry limit)
- **Performance Metrics**: <3s response time for 80% of queries, <5s for 95%

### 🔒 Security & Privacy
- **OAuth Required**: Secure authentication for all chat features
- **SQL Validation**: All generated queries validated before execution
- **Rate Limiting**: Per-user (10/min) and global (100/min) limits
- **Data Retention**: Automatic cleanup after 90 days
- **GDPR Compliance**: Complete data deletion on request
- **User Isolation**: Users can only access their own chat history

### 📚 Documentation
- **Comprehensive User Guide**: [AI Chat Assistant Guide](AI_CHAT_ASSISTANT.md)
- **Deployment Guide**: [AI Chat Deployment](AI_CHAT_DEPLOYMENT.md)
- **Help Integration**: AI Chat tab added to Documentation & Help page
- **Feedback Form**: AI Chat Assistant option in contact form

[View complete changelog →](CHANGELOG.md) | [AI Chat Documentation →](AI_CHAT_ASSISTANT.md)

---

## What's New in Version 5.2

**AI Chat Assistant & OAuth Refinement** - Released January 25, 2026

### 🤖 NEW: AI Chat Assistant (Phase 1 MVP)
- **Natural Language Queries**: Ask questions in plain English about admissions data
- **Smart Query Processing**: Automatically classifies and routes data, navigation, help, and conversational queries
- **SQL Generation**: AI generates and executes secure SQL queries from natural language
- **Chat History**: All conversations saved and organized by user
- **Platform Navigation**: Get guidance on which page to use and how to navigate
- **Feature Help**: Learn about platform features and capabilities
- **Full Page Experience**: Dedicated page with chat history sidebar and conversation window
- **Secure & Authenticated**: Only accessible to signed-in users, with rate limiting and SQL validation

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
- Google Gemini 2.5 Flash integration for AI responses
- ChromaDB vector store for semantic search
- Comprehensive chat history with user statistics

[View complete changelog →](CHANGELOG.md) | [AI Chat Documentation →](AI_CHAT_ASSISTANT.md)

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

**[AI Chat Assistant](AI_CHAT_ASSISTANT.md)** 🆕  
Natural language interface to query data and get platform guidance.

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

**Current Version:** 6.8  
**Last Updated:** February 1, 2026

### Analytics Pages
- Home Dashboard
- Executive Deep Dive
- Comparison Tool
- Marketing Analysis
- Data Explorer
- Predictive Analytics
- 🤖 AI Chat Assistant (New!)

### Programs Tracked
MBA, MS ACCT, MS ENLD, MS HRM, MS MISY, MS MKTG, MS SPBA

### Cohorts
Class of 2024, 2025, 2026

### ML Models
Prophet, ARIMA, Linear Regression

### AI Features (New in v5.2)
- Natural language data queries
- Platform navigation assistance
- Feature explanations and help
- Conversation history
- SQL query transparency
- Secure and authenticated access

### Authentication Features (v5.0-5.2)
- Google OAuth 2.0 integration
- Role-based access control
- User profiles and session management
- Reliable new-tab OAuth flow

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
- [AI Chat Assistant](AI_CHAT_ASSISTANT.md) - Natural language queries

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

**Mays Analytics Documentation** | Version 6.8 | Last Updated: February 1, 2026
