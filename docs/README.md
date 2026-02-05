# Mays Analytics - Documentation

Welcome to the comprehensive documentation for the Mays Analytics Platform.

---

## What's New in Version 9.0

**Professional Marketing Intelligence Platform** - Released February 4, 2026

### 🎨 Complete Predictive Analytics Redesign
- **Three Focused Sub-Tabs**: Revolutionary transformation from 5 complex ML tabs to 3 intuitive analysis tools for streamlined user experience
  - **Channel Performance**: ROI forecasting with investment scenario modeling and effectiveness scoring
  - **Timing Intelligence**: Seasonal optimization with interactive heatmap visualization and peak period detection
  - **Budget Allocation**: Data-driven budget distribution with optimization algorithms and sensitivity analysis
- **Professional Interface Architecture**: Enterprise-grade clean white cards with subtle shadows, eliminating unnecessary borders and visual clutter
- **Streamlined Workflows**: Direct access to core functionality without space-wasting titles, descriptions, or redundant navigation elements

### 🏢 Enterprise-Grade UI/UX Transformation
- **Clean White Tile System**: All information professionally contained within organized card layouts with consistent spacing and typography
- **Consistent Brand Styling**: Unified maroon color scheme (#500000) throughout platform for professional brand consistency and visual hierarchy
- **Mature Design Philosophy**: Eliminated unnecessary titles, descriptions, and decorative elements for clean, business-appropriate appearance
- **Everything Contained Principle**: Metrics, recommendations, forecasts, and analysis data all properly organized within structured tiles
- **Responsive Professional Layout**: Seamless experience across desktop (1400px+), laptop (1200px), tablet (900px), and mobile (768px) devices

### 📊 Advanced Marketing Intelligence Engine
- **Composite Effectiveness Scoring**: Sophisticated metrics combining efficiency, consistency, attribution, and recency for comprehensive channel evaluation
- **Seasonal Intelligence System**: Automatic detection and optimization of peak performance periods (Peak Season 1.2x, High Season 1.1x multipliers)
- **ROI Forecasting Engine**: Advanced expected return calculations with confidence levels (70-100% high, 50-70% moderate, <50% lower confidence)
- **Real-time Analysis Pipeline**: Recommendations and forecasts update instantly when investment filters change for dynamic decision-making
- **Professional Badge System**: Clean seasonal indicators and performance ratings replacing emoticons for business-appropriate interface

### 🔧 Technical Architecture Excellence
- **Brick-Style Card Framework**: Modern card layouts with proper 25px padding, 20px margins, and professional typography hierarchy
- **Single Button Logic**: Eliminated confusing duplicate buttons (removed "Generate Allocation", kept "Generate Budget Allocation") for better UX
- **Centered Header System**: All section titles properly centered with custom #f8f9fa backgrounds and subtle shadow effects
- **Grid Layout Consistency**: Standardized 4-column metric grids for organized information display and visual balance
- **Shadow Effect Implementation**: Subtle depth effects (0 4px 12px rgba(0,0,0,0.1)) without borders for modern professional appearance

### 📚 Comprehensive Documentation Overhaul
- **Complete Help System Rewrite**: Updated Predictive Analytics documentation to reflect new three-tab structure and professional interface
- **Detailed Workflow Guides**: Step-by-step instructions for Channel Performance, Timing Intelligence, and Budget Allocation workflows
- **Interface Documentation**: Comprehensive descriptions of professional card layouts, styling principles, and user interaction patterns
- **Best Practices Integration**: Practical guidance for combining insights from all three analysis tools for comprehensive marketing strategy
- **Updated Navigation Workflows**: Revised Marketing Optimization and Marketing Intelligence workflows to reflect new tab structure

### 🎯 User Experience Impact
- **Reduced Cognitive Load**: Streamlined from 5 complex tabs to 3 focused tools reduces decision paralysis and improves task completion
- **Professional Credibility**: Clean, mature interface appropriate for executive presentations and stakeholder meetings
- **Improved Task Flow**: Direct access to functionality eliminates navigation friction and reduces time-to-insight
- **Enhanced Data Comprehension**: Organized card layouts improve information scanning and decision-making speed
- **Mobile-First Responsive**: Professional appearance maintained across all device sizes for consistent user experience

### 🔍 Technical Implementation Details
- **CSS Architecture**: Custom brick-style classes with consistent spacing, typography, and shadow effects
- **Component Organization**: Modular card system with reusable styling patterns and responsive breakpoints
- **Performance Optimization**: Streamlined interface reduces rendering overhead and improves page load times
- **Accessibility Compliance**: Proper contrast ratios, semantic HTML structure, and keyboard navigation support
- **Cross-Browser Compatibility**: Tested and optimized for Chrome, Firefox, Safari, and Edge browsers

[View complete changelog →](CHANGELOG.md)

---

## What's New in Version 8.0

**Enhanced Cohort-Aware Forecasting** - Released February 3, 2026

### 🚀 Revolutionary Forecasting System
- **ARIMA-Style Components**: Implemented comprehensive trend, seasonal, and error components for robust time series forecasting with mean-reverting random walks and realistic volatility modeling
- **Prophet-Style Seasonal Decomposition**: Advanced multiplicative seasonal effects with academic calendar awareness, blending historical patterns with theoretical seasonal models
- **Academic Seasonality Integration**: Built-in understanding of vacation dips (summer lulls), campaign surges (spring pushes), enrollment cycles, and holiday slowdowns for realistic predictions
- **Realistic Growth Constraints**: Predictions now constrained to 1.5-2x of historical peaks (vs previous 60x overestimations), with maximum 30% total growth over lifecycle

### 🧠 Multi-Model Integration & Architecture
- **Combined Methodologies**: Seamlessly integrates ARIMA trend analysis, Prophet seasonal decomposition, Linear growth modeling, and academic Seasonality patterns in unified framework
- **Component-Based Architecture**: Separates trend, seasonal, and error components for transparency and debugging, allowing individual component analysis and validation
- **Robust Growth Rate Calculation**: Fixed infinite growth rates from zero-to-positive transitions by implementing capped growth rates (max 100% monthly) and proper zero-value handling
- **Conservative Prediction Logic**: Extremely conservative growth caps with deceleration factors, seasonal decline allowances, and realistic month-to-month constraints

### 📊 Enhanced Prediction Quality & Reliability
- **Eliminated NaN Values**: All predictions now generate valid numbers across all scenarios with automatic fallback to linear growth models when baseline patterns contain NaN
- **Consistent 8-Month Predictions**: Reliable timeline generation for all programs and metrics, properly handling both existing data continuation and new cohort lifecycle starts
- **Seasonal Decline Support**: Models now properly account for summer application lulls, holiday slowdowns, and semester transition effects with flexible constraint systems
- **Historical Pattern Learning**: Intelligent blending of learned historical patterns (70%) with theoretical academic calendar models (30%) for optimal prediction accuracy

### 🔧 Technical Implementation & Robustness
- **Zero Start Value Handling**: Comprehensive handling of cohorts starting with zero applications through baseline value detection and reasonable default substitution
- **Fallback Model Enhancement**: Improved edge case handling with conservative linear growth models when complex seasonal patterns fail
- **Mean-Reverting Error Terms**: ARIMA-style random walk error components with configurable mean reversion (-0.3 factor) for realistic prediction variation
- **Multiplicative Seasonal Effects**: Stronger seasonal impact through multiplicative rather than additive seasonal adjustments for realistic ups and downs

### 🎯 Prediction Accuracy Improvements
- **MS Marketing Applications**: Fixed from 6,535 unrealistic prediction to 160 (1.5x historical peak of 104) - 97.5% improvement in realism
- **Cross-Program Consistency**: All programs now generate predictions within 1.1-2.0x of historical peaks across different training scenarios
- **Seasonal Variation**: Proper modeling of month-to-month fluctuations with both growth and decline periods reflecting real academic cycles
- **Training Flexibility**: Robust performance whether training on single cohorts (2026 only), multiple cohorts (2026+2027), or mixed scenarios

[View complete changelog →](CHANGELOG.md)

---

## What's New in Version 7.5

**Professional UI Enhancement** - Released February 3, 2026

### 🎨 Professional Interface Improvements
- **Enhanced Model Cards**: Redesigned accuracy and performance rating cards in Predictive Analytics with professional styling, gradient backgrounds, elegant shadows, and consistent sizing (2.8em font for perfect alignment)
- **Improved Tab Structure**: Reorganized Predictive Analytics tabs for better user flow - "Simple Case Study" moved to first position as "Forecast", "Forecasting" renamed to "Advanced Forecasting", removed redundant "Case Study" tab
- **Consistent Chart Titles**: Fixed capitalization across all model comparison charts - "Inquiries Received" properly formatted, "Cohort-Aware" changed to "Cohort Aware" for consistency
- **Clean Debug Interface**: Removed all debug messages ("About to run with prediction_months = 11"), unnecessary emoticons from error messages, and technical clutter for professional user experience

### 🧹 Code Quality & Performance
- **Massive Project Cleanup**: Removed 27+ unnecessary files including all test files (`test_*.py`), temporary markdown files, and cache directories for clean production codebase
- **Streamlined File Structure**: Eliminated duplicate functions, unused code, and redundant implementations while maintaining full functionality
- **Professional Error Messaging**: Cleaned up "challenging issue" messages by removing emoticons and making text more business-appropriate
- **Optimized Tab Navigation**: Reduced from 7 to 6 tabs with logical flow - basic forecasting first, then advanced features

### 🔧 Technical Enhancements
- **Card Styling Consistency**: Both model accuracy and performance rating cards now use identical font sizes and dimensions for perfect visual alignment
- **Helper Functions**: Added `get_metric_display_name()` and `get_model_display_name()` functions for consistent naming across all charts and interfaces
- **Syntax Error Resolution**: Fixed all parentheses mismatches, duplicate function definitions, and code structure issues
- **Enhanced Chart Formatting**: Improved chart titles in Compare All Models section with proper capitalization and consistent styling

### 🎯 User Experience Impact
- **Professional Appearance**: Cards now look modern and consistent with proper shadows, gradients, and color-coded performance indicators
- **Intuitive Navigation**: Forecast functionality prominently placed as first tab for immediate access to core features
- **Clean Interface**: Removed technical debug information that was confusing to end users
- **Consistent Branding**: All chart titles and model names follow consistent capitalization and formatting standards

[View complete changelog →](CHANGELOG.md)

---

## What's New in Version 7.1

**Marketing Analysis ROI Fix** - Released February 2, 2026

### 🔧 Critical Marketing Analysis Fixes
- **Fixed Cost per Application**: Resolved "N/A" values in Marketing Analysis Overview and Advanced Analytics tabs by connecting to correct `total_applications` metric
- **Fixed Average Conversion Rate**: Now properly calculates inquiry-to-application conversion rates using accurate admissions data
- **Enhanced Debug Information**: Added comprehensive debug sections showing program name matching, date ranges, and data availability
- **Corrected Data Connections**: Fixed all utility files to reference the correct admissions metrics for consistent calculations

### 📊 State Snapshot User Experience Improvements  
- **Professional Explanation Boxes**: Added centered, clean state snapshot explanations across Executive Dashboard, Director's Deep Dive, and Marketing Analysis
- **Consistent Styling**: Uniform light gray background with proper padding, spacing, and professional appearance
- **Shortened Messaging**: Concise, business-appropriate explanations without overwhelming technical details
- **Enhanced Performance Radar**: Added auto-scale functionality, better zoom controls, and clear user guidance for chart interaction

### 🔍 Technical Database Improvements
- **Database Query Optimization**: Updated marketing analysis to use `total_applications` (2,403 records) instead of `applications_received` (62 records)
- **Utility File Consistency**: Updated `utils/validation.py`, `utils/ml_models.py`, `utils/database.py`, and `utils/ai_chat/vector_store.py`
- **Enhanced Error Handling**: Better debugging information when marketing-admissions data matching fails
- **Program Name Normalization**: Verified consistent program name matching between marketing spend and admissions metrics

### 🎯 User Experience Impact
- **Marketing ROI Metrics**: Cost per Application and Conversion Rate now display actual values instead of "N/A"
- **Professional Interface**: Clean, centered state snapshot explanations improve user understanding
- **Better Chart Controls**: Performance radar chart with proper zoom/reset functionality
- **Comprehensive Debugging**: Clear visibility into data matching issues for troubleshooting

[View complete changelog →](CHANGELOG.md)

---

## What's New in Version 7.0

**State Snapshot ETL & Dashboard Enhancement** - Released February 2, 2026

### 🔄 Enhanced ETL Pipeline with State Snapshot Processing
- **State Snapshot Approach**: Completely redesigned ETL to treat all data as point-in-time snapshots rather than cumulative totals
- **Unified Cohort Calculation**: All programs (including MBA) now use consistent +2 years cohort assignment for accurate tracking
- **Smart File Processing**: Processes only 3 key files with `_fall` suffix (2024-07-31, 2025-07-31, 2025-12-31) for precise cohort data
- **Enhanced Database Schema**: Added `cohort_season` and `file_source` columns for better data lineage and tracking
- **Fixed Cohort Assignment**: Corrected Class 2028 data that was incorrectly marked as Class 2027 in previous versions

### 📊 Comprehensive Dashboard Improvements
- **Executive Dashboard Filtering Fix**: Resolved broken filter logic with proper flow control structure, restored "All Programs" functionality
- **Enhanced No-Data Handling**: Comprehensive handling for programs without data, clear messaging for edge cases
- **Director's Deep Dive Major Enhancements**:
  - Added comprehensive metrics breakdown with expandable Application Status and Admissions Decision sections
  - Implemented trend analysis scale options (Linear → Log → Square Root) for better data visualization
  - Fixed growth rate analysis to compare fiscal year start vs end values for accurate performance metrics
  - Enhanced chart type buttons to show what you can switch TO instead of current type
  - Cleaned up legend labels by removing redundant prefixes while keeping full names in dropdowns
- **Comparison Tool Data Quality**: Implemented smart backfilling logic to prevent artificial data drops in cumulative metrics
- **Marketing Analysis Space Optimization**: Consolidated program/channel/fiscal year into single header line, achieving 70% space reduction

### 🔧 Data Quality & Performance Improvements
- **Smart Backfilling Logic**: Cumulative metrics (inquiries, applications) never decrease with intelligent previous-value backfilling
- **Suspicious Zero Detection**: Enhanced filtering to prevent artificial drops in visualizations caused by missing data
- **Column-Level Filtering**: Skips empty date columns for cleaner data processing and more accurate trend analysis
- **Enhanced Data Validation**: Comprehensive validation with proper error handling for edge cases and missing data
- **Professional Interface Styling**: Removed emoticons throughout interface and improved spacing for business-appropriate appearance

### 📈 Advanced Analytics Features
- **Trend Analysis Scale Options**: Multiple scaling options (Linear, Log, Square Root) for optimal data visualization based on data distribution
- **Fiscal Year Growth Rate Analysis**: Compares true fiscal year start vs end values instead of last two data points
- **Chart Type Flexibility**: Improved chart switching between line and bar graphs with proper zero-value handling for line charts
- **Legend Optimization**: Shortened legend labels (e.g., "Admissions Offered" → "Offered") while maintaining full names in selection dropdowns
- **Incremental Notes Optimization**: Achieved 70% space reduction by consolidating headers and removing redundant titles

### 🎯 User Experience Enhancements
- **Fixed Vertical Line Issues**: Line charts now properly connect only actual data points, eliminating vertical artifacts
- **Improved Chart Buttons**: Buttons now show what you can switch TO rather than current state for better UX
- **Enhanced Expandable Sections**: Proper spacing and professional styling for Application Status and Admissions Decision breakdowns
- **Cleaner Interface**: Removed padding inconsistencies and improved visual hierarchy throughout the platform
- **Better Error Messaging**: Clear, professional messaging for edge cases and data availability issues

[View complete changelog →](CHANGELOG.md)

---

## What's New in Version 6.10

**Data Explorer Restructure** - Released February 1, 2026

### 📊 Organized Data Explorer Interface
- **Grouped Categories**: Transformed overwhelming 13 individual table tabs into 4 logical groups for better user experience
- **Two-Level Navigation**: Intuitive category tabs → table sub-tabs structure reduces cognitive load
- **Marketing Tables Group**: Spend (individual channels), Totals (aggregated), Notes (strategy context), Processing Logs (ETL metadata)
- **Core Data Tables Group**: Admissions (funnel metrics), Programs (definitions), Metadata (system info)
- **AI Chat Tables Group**: History (conversations), Feedback (ratings), Metrics (performance)
- **System Tables Group**: Users (authentication), Predictions (ML forecasts)

### 🎨 Enhanced User Experience Design
- **Centered Navigation**: All main tabs and sub-tabs properly centered for balanced visual hierarchy
- **Professional Styling**: Removed emoticons and decorative elements for clean, business-appropriate interface
- **Improved CSS Architecture**: Fixed camouflaging issues, better hover states, and clearer active tab indicators
- **Responsive Layout**: Seamless experience across desktop, tablet, and mobile devices
- **Logical Information Architecture**: Related tables grouped together for intuitive data discovery

### 🔧 Technical Implementation
- **Maintained Full Functionality**: All existing filtering, sorting, export, and analysis features preserved
- **Enhanced Performance**: Optimized CSS reduces rendering overhead with cleaner selectors
- **Better Accessibility**: Improved contrast ratios and clearer visual states for better usability
- **Documentation Updates**: Complete alignment between interface changes and user guides

[View complete changelog →](CHANGELOG.md)

---

## What's New in Version 6.9

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
- **Separate Notes Table**: New `incremental_notes` table eliminates data duplication
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

**Mays Analytics Documentation** | Version 9.0 | Last Updated: February 4, 2026
