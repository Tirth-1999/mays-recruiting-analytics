# Changelog

All notable changes to the Mays Analytics Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [6.9.0] - 2026-02-01

### 🗄️ Optimization Release - Database Optimization

#### Changed
- **Table Names Simplified**: Renamed `marketing_etl_state` → `marketing_data` for cleaner interface
- **Table Names Simplified**: Renamed `marketing_incremental_notes` → `incremental_notes` for better readability
- **Data Explorer UX**: Shorter, more intuitive table names improve user experience
- **Code Consistency**: Updated all ETL pipelines, queries, and modules to use new table names
- **Documentation Sync**: Complete alignment between code and documentation references

#### Technical Implementation
- **Database Schema**: Maintained all data integrity during table renaming process
- **Marketing ETL Updates**: All references updated to use new table names (`marketing_data`, `incremental_notes`)
- **Query Optimization**: Updated marketing analysis module to use new table structure
- **Documentation Updates**: Synchronized all README, CHANGELOG, and code documentation
- **Production Ready**: Thoroughly tested to ensure seamless functionality with new names

---

## [6.8.0] - 2026-02-01

### 🔧 Enhancement Release - Marketing Analytics Enhancement

#### Added
- **Dynamic Sheet Detection**: Automatically detects FY25, FY26, and future fiscal year sheets (FY27+)
- **Fiscal Year-Specific Month Filtering**: Month options now depend on selected fiscal years
- **Chronological Month Sorting**: Months display in date order instead of alphabetical
- **Fiscal Year Grouping**: When multiple FYs selected, months organized by fiscal year sections
- **Separate Incremental Notes Table**: New `incremental_notes` table structure
- **State Tracking System**: Incremental updates with intelligent change detection
- **Centralized Program Mapping**: Single source of truth for program name standardization

#### Changed
- **Marketing ETL Pipeline**: Enhanced to handle dynamic Excel structures and varying month ranges
- **Month Filter Logic**: Now fiscal-year dependent with improved UX and empty states
- **Notes Database Structure**: Moved from embedded JSON to separate table (16 unique vs 167 duplicates)
- **Date Conversion Logic**: Fixed August 2026 → August 2025 for proper FY26 representation
- **Program Name Handling**: "AI" code now maps to "Flex Online AI and Business Program"
- **Notes Display**: Organized by fiscal year with expandable program-channel sections

#### Removed
- **Data Duplication**: Eliminated 151 duplicate note records through proper normalization
- **Hard-coded Month Logic**: Replaced with dynamic detection based on Excel content
- **Date Conversion Bug**: Fixed incorrect August 2026 entries in FY26 data

#### Technical Implementation
- **Enhanced ETL Processing**: Handles FY25 (Sept 2024-June 2025) and FY26 (Aug-Dec 2025) correctly
- **Database Schema Updates**: Added `incremental_notes` and `marketing_data` tables
- **Performance Optimization**: State tracking prevents unnecessary reprocessing of unchanged data
- **4-Column Filtering**: Fiscal Year → Program → Channel → Month drill-down capability
- **Robust Error Handling**: Graceful processing of dynamic Excel structures with validation
- **Data Quality Assurance**: 585 spend records, 120 totals records, 16 incremental notes across 2 fiscal years

---

## Development Timeline

```
Apr 2024  ████████░░░░░░░░░░░░░░░░░░░░  v1.0 - Initial Release
          │
Jan 2026  ░░░░░░░░████████░░░░░░░░░░░░  v2.0 - Marketing Integration
          │
Jan 2026  ░░░░░░░░░░░░░░░░████░░░░░░░░  v2.1 - Global Filters
          │
Jan 2026  ░░░░░░░░░░░░░░░░░░░░████░░░░  v2.2 - Executive Restructure
          │
Jan 2026  ░░░░░░░░░░░░░░░░░░░░░░░░████  v2.3 - Comparison Enhancements
          │
Jan 2026  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░  v2.4 - UI/UX Refinements
          │
Jan 2026  ████████████████████████████  v3.0 - Modular Architecture
          │
Jan 2026  ████████████████████████████  v4.0 - Predictive Analytics & ML
          │
Jan 2026  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░  v4.1 - UI/UX & Responsive Design
          │
Jan 2026  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░  v4.2 - Contact & Feedback
          │
Jan 2026  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░  v4.3 - Navigation & UX (Initial)
          │
Jan 2026  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░  v4.4 - Navigation & UX (Final)
          │
Jan 2026  ████████████████████████████  v5.0 - Authentication & UI Optimization
          │
Jan 2026  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░  v5.1 - OAuth Fix & Consent Screen
          │
Jan 2026  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░  v5.2 - OAuth Button Refinement
          │
Jan 2026  ████████████████████████████  v6.0 - AI-Powered Analytics
          │
Jan 2026  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░  v6.1 - Sidebar Profile Enhancement
          │
Jan 2026  ████████████████████████████  v6.2 - Professor Feedback Implementation
          │
Jan 2026  ████████████████████████████  v6.5 - UI/UX Polish & Mobile Optimization
          │
Feb 2026  ████████████████████████████  v6.8 - Marketing Analytics Enhancement
```

---

## Summary by Version

| Version | Type | Key Achievement | Files Changed | Lines Added |
|---------|------|----------------|---------------|-------------|
| **6.9** | Minor | Database Optimization | 6 | +25 |
| **6.8** | Major | Marketing Analytics Enhancement | 3 | +450 |
| **6.5** | Major | UI/UX Polish & Mobile Optimization | 3 | +850 |
| **6.2** | Major | Professor Feedback Implementation | 20 | +4,095 |
| 6.1 | UI Enhancement | Restored profile card with scrollable sidebar | 2 | ~50 |
| **6.0** | Major | AI Chat Assistant with NLP | 25+ | +3,500 |
| **5.2** | Minor | OAuth Button Refinement | 2 | +15 |
| **5.1** | Minor | OAuth Fix & Consent Screen | 3 | +25 |
| **5.0** | Major | Authentication & UI Optimization | 7 | +601 |
| **4.4** | Minor | Navigation & UX (Final) | 2 | +120 |
| **4.3** | Minor | Navigation & UX (Initial) | 2 | +80 |
| **4.2** | Minor | Contact & Feedback Integration | 8 | +250 |
| **4.1** | Minor | UI/UX & Responsive Design | 7 | +450 |
| **4.0** | Major | Predictive Analytics & ML | 11 | +6,701 |
| **3.0** | Major | Modular Architecture | 15 | +4,734 |
| **2.4** | Minor | UI/UX Refinements | 8 | +234 |
| **2.3** | Minor | Comparison Enhancements | 3 | +156 |
| **2.2** | Minor | Executive Restructure | 5 | +423 |
| **2.1** | Minor | Global Filters | 4 | +289 |
| **2.0** | Major | Marketing Integration | 6 | +1,234 |
| **1.0** | Major | Initial Release | - | +3,500 |

---

## [6.5.0] - 2026-01-27

### 🎨 Major Release - UI/UX Polish & Mobile Optimization

#### Responsive Design Enhancements
- **Dynamic Font Sizing**: Implemented CSS `clamp()` for all key metrics
  - Marketing Analysis: 6 metrics with responsive text (numbers, labels, small text)
  - Director's Deep Dive: 6 metrics with same responsive styling
  - Font sizes adapt smoothly to viewport width
  - Breakpoints: 1400px (3 cols), 900px (2 cols), 768px (1 col)
- **Sidebar-Aware Layouts**: All responsive breakpoints account for sidebar width
- **Centered Content**: Fixed centering issues with 15px left padding on metric numbers
- **Production CSS**: Added `!important` flags to override Streamlit's global CSS

#### Chart Improvements
- **Enhanced Tooltips**: Added helpful tooltips to major charts
  - "Use the buttons above to filter channels • Click legend items to toggle data"
  - Positioned above filters for better UX
- **Value Labels on Bars**: 
  - Spend Distribution by Channel: Dollar values on bars with `texttemplate='$%{text:,.0f}'`
  - Extended Y-axis by 35% (linear) and 0.8 log units (log scale) to prevent clipping
  - Increased margins: top 80px, bottom 70px
- **Centered Titles**: All chart titles properly centered across platform
- **Shadow Effects**: Line graphs feature subtle shadow fills (`fill='tozeroy'` with 10% opacity)

#### Marketing Analysis Updates
- **Channel Performance by Program**:
  - Restructured from 2-column to full-width heatmap (500px height)
  - Moved "Top Channel per Program" below heatmap
  - Created responsive card grid (min 300px per card)
  - Color coding: spend amount (relative), percentage (absolute thresholds)
  - Removed left borders, emoticons, and subtitle clutter
  - Fixed HTML rendering by building string without indentation
- **Spend vs Outcomes Trend**:
  - Fixed fiscal year filtering (parses 'FY25' format correctly)
  - Added shadow effects under line graphs
  - Removed peak zones and annotations for cleaner look
  - Centered subplot titles
  - Height: 650px with proper legend positioning
- **Channel Analytics**:
  - Added tooltips to Spend Distribution and Channel Spend Trends
  - Centered all chart titles
  - Channel Spend Trends: Legend moved from right to top center (horizontal)
  - Increased height to 500px with 120px top margin
  - Legend font size: 10px for better readability

#### Mobile Optimization
- **Program Comparison Chart (Executive Dashboard)**:
  - Desktop: -45° angle for x-axis labels
  - Mobile (≤768px): 0° angle (perfectly vertical)
  - JavaScript dynamically adjusts based on screen width
  - Increased bottom margin to 150px for labels
- **Spend by Program & Channel**:
  - Desktop: Legend on right side (vertical)
  - Mobile (≤768px): Legend moves to bottom (horizontal), height increases to 600px
  - JavaScript adjusts layout dynamically
  - Bottom margin increases to 150px on mobile
- **Performance Radar (Director's Deep Dive)**:
  - Responsive breakpoint at 1400px
  - Explanation boxes move from right side to bottom on smaller screens
  - Vertical spacing (120px) only applies on screens >1400px
  - CSS media queries force columns to stack

#### Interface Cleanup
- **Removed Dividers**:
  - Director's Deep Dive: Before/after "How to Use This Section", 2 from Comparison Tool
  - Marketing Analysis: Before/after "How to Use This Analysis"
  - Predictive Analytics: After "How to Use This Page"
  - Cleaner interface with less visual clutter
- **Removed Print Buttons**:
  - Removed custom Print buttons from footers (directors_deep_dive, marketing_analysis, executive_dashboard)
  - Replaced with empty center column in footer
  - Users now use Streamlit's built-in print functionality
- **Removed Dead Code**:
  - Removed ~150 lines of unused print CSS from database.py
  - Cleaned up duplicate code blocks

#### Technical Implementation
- **Files Modified**: 3 (modules/directors_deep_dive.py, modules/marketing_analysis.py, modules/executive_dashboard.py)
- **CSS Techniques**: 
  - `clamp(min, preferred, max)` for fluid typography
  - Media queries for responsive breakpoints
  - Flexbox for centering without wrapping
  - `!important` flags for production CSS
- **JavaScript**: Dynamic layout adjustments based on screen width
- **Performance**: No impact on load times, all changes are CSS/JS only

#### User Experience Impact
- Metrics properly centered and responsive across all devices
- Charts display values without clipping
- Mobile users get optimized layouts (vertical labels, repositioned legends)
- Cleaner interface with less visual noise
- Professional appearance with consistent styling

---

## [6.2.0] - 2026-01-27

### 🎓 Major Release - Professor Feedback Implementation

#### Data Standardization
- **Program Name Standardization**: All programs now use full names consistently
  - Created centralized mapping utility (`utils/program_mapping.py`)
  - Converted short codes (MBA, ACCT) to full names (Flex Online MBA, MS Accounting)
  - Updated 2,037 admissions records and 585 marketing records
  - Migrated programs table with full names
- **ETL Pipeline Updates**: Both admissions and marketing ETL pipelines now convert codes to full names
- **AI Chat Enhancement**: Updated schema context and SQL generation to handle both short codes and full names

#### Page Restructuring
- **Renamed Pages**:
  - "Home Dashboard" → "Executive Dashboard"
  - "Executive Deep Dive" → "Director's Deep Dive"
- **Comparison Tool Integration**: Moved from standalone page to 5th tab in Director's Deep Dive
- **Platform Header**: Updated with full program names on two lines:
  - Line 1: MBA • MS Accounting • MS Human Resource Management
  - Line 2: MS Management Information Systems • MS Marketing • MS Entrepreneurial Leadership • AI in Business

#### Executive Dashboard Enhancements
- **Marketing Insights Section**:
  - Added independent fiscal year and program multi-select filters
  - 4 key metrics: Total Spend, Programs Marketed, Channels, Avg Spend/Program
  - Spend by Program & Channel (stacked bar chart with 12 distinct colors)
  - Spend by Channel (pie chart)
  - Includes General Awareness data
- **Program Comparison Section**:
  - Added independent cohort and program multi-select filters
  - Filters override top page selections for flexible analysis
  - Data aggregation across multiple selected cohorts
  - Metric toggle buttons: Inquiries, Applications, Accepted, Cohort Size, Log Scale
- **Cohesive Color Palette**: Implemented 18 completely distinct colors across all charts
  - Admissions Funnel: Maroon gradient (dark to light)
  - Program metrics: Blue, Orange, Red, Maroon
  - Marketing channels: 12 unique colors (no similar shades)

#### Bug Fixes & Improvements
- **Empty Data Handling**: Fixed ValueError when selecting cohorts with no enrollment data
  - Special message for active programs with no data yet (AI in Business)
  - Generic message for cohorts with no data
- **Chart Spacing**: 
  - Increased y-axis range by 20% to prevent number clipping
  - Increased margins (top: 120px, bottom: 80px, left/right: 60px)
  - Removed excessive spacing after filter sections
- **Data Aggregation**: Fixed to properly aggregate latest data across multiple cohorts
- **Filter Behavior**: Smart cascading filters that update available options dynamically

#### Technical Implementation
- **Files Modified**: 15 files
- **Files Added**: 7 files (program_mapping.py, comparison_tool_content.py, executive_dashboard.py, directors_deep_dive.py, update_program_names.py, test_app_functionality.py, PROFESSOR_FEEDBACK_ANALYSIS.md)
- **Files Renamed**: 2 files (home_dashboard.py → executive_dashboard.py, executive_deep_dive.py → directors_deep_dive.py)
- **Database Migration**: Successfully migrated all historical data to use full program names

---

## [6.1.0] - 2026-01-26

### 🎨 Minor Release - Sidebar Profile Enhancement

#### Added
- **Profile Card**: Restored user profile card in sidebar with compact design
  - Circular profile picture with gold border
  - User name, email, and role display
  - Inline logout button within card
  - White card background with subtle border
  - Positioned above navigation buttons
- **Sidebar Spacing**: Added 30px top margin to header for better visual balance
- **Gold Divider**: Restored gold divider after profile section

#### Changed
- **Sidebar Scrolling**: Enabled default Streamlit scrollbar for sidebar overflow
  - Removed forced non-scrollable constraints
  - Allows natural scrolling when content exceeds viewport
- **Profile Card Styling**: Matched original GitHub version exactly
  - 36px circular profile image
  - 12px name font, 9px email/role fonts
  - Proper color hierarchy for text readability

#### Technical Implementation
- Updated `main_app.py` sidebar section with profile card HTML
- Modified CSS to remove overflow restrictions
- Maintained fixed sidebar overlay behavior
- Profile card uses inline styles for production compatibility

---

## [6.0.0] - 2026-01-25

### 🤖 Major Release - AI-Powered Analytics

#### Added
- **AI Chat Assistant Module** (`modules/ai_chat.py`): Complete natural language query interface
- **Gemini Client** (`utils/ai_chat/gemini_client.py`): Google Gemini AI integration
- **Vector Store** (`utils/ai_chat/vector_store.py`): ChromaDB for semantic schema search
- **SQL Generator** (`utils/ai_chat/sql_generator.py`): Natural language to SQL conversion
- **Chat History** (`utils/ai_chat/chat_history.py`): Conversation storage and retrieval
- **Rate Limiter** (`utils/ai_chat/rate_limiter.py`): Per-user and global rate limiting
- **Query Processor** (`utils/ai_chat/query_processor.py`): Query classification and routing
- **Prompts** (`utils/ai_chat/prompts.py`): Optimized AI prompts for different query types
- **Cache** (`utils/ai_chat/cache.py`): Response caching for performance
- **Metrics** (`utils/ai_chat/metrics.py`): Usage tracking and analytics

#### Features
- **Natural Language Queries**: Ask questions in plain English about admissions data
- **Conversation Memory**: Context-aware follow-ups with reference resolution ("it", "that", "same")
- **Smart Query Processing**: Understands business terms, abbreviations, complex queries with JOINs
- **Rate Limiting**: 10 queries/minute per user, 100/minute globally with visual indicators
- **Feedback System**: Thumbs up/down ratings with satisfaction analytics by query type
- **Suggested Queries**: Context-aware suggestions after each response
- **In-App Help**: Quick reference modal with examples and tips
- **Chat History**: Three-tab interface (Current, History, Settings & Privacy)
- **Search & Export**: Search across conversations, export to JSON
- **Settings & Privacy**: Usage stats, feedback analytics, GDPR-compliant deletion

#### Technical Implementation
- **Google Gemini 2.5 Flash**: Fast, accurate AI responses
- **ChromaDB**: Vector embeddings for 11 schema documents
- **Query Pattern Recognition**: 5 cached patterns for 30%+ speed improvement
- **Token Optimization**: Compressed prompts, avg <1000 tokens/query
- **Response Caching**: 5-minute LRU cache (100 entries)
- **Performance**: <3s for 80% queries, <5s for 95%
- **SQL Validation**: Security checks before execution
- **User Isolation**: Users only see their own chat history

#### Database Changes
- **chat_history table**: Stores all conversations with metadata
- **chat_feedback table**: Tracks user ratings and comments
- **Indexes**: Optimized for user_id, conversation_id, timestamp queries

#### Documentation
- **AI Chat Assistant Guide** (`docs/AI_CHAT_ASSISTANT.md`): Comprehensive user documentation
- **AI Chat Deployment** (`docs/AI_CHAT_DEPLOYMENT.md`): Deployment and configuration guide
- **Help Integration**: AI Chat tab added to Documentation & Help page
- **Feedback Form**: AI Chat Assistant option in contact form

#### Files Modified
- `main_app.py` - Added AI Chat page to navigation
- `modules/ai_chat.py` - Complete chat interface implementation
- `modules/help.py` - Added AI Chat documentation tab
- `utils/ai_chat/*.py` - 10 new utility modules
- `migrations/add_chat_history_table.py` - Database migration
- `migrations/add_chat_indexes.py` - Performance indexes
- `migrations/add_feedback_table.py` - Feedback system
- `requirements.txt` - Added google-generativeai, chromadb, sentence-transformers
- `version.py` - Updated to v6.0 with ENABLE_AI_CHAT flag

#### User Experience
- Users access AI Chat from main navigation
- Ask questions like "How many MBA applications in 2026?"
- Get instant answers with SQL query transparency
- Rate responses to improve accuracy
- Manage chat history and privacy settings

---

## [5.2.0] - 2026-01-25

### 🔧 Minor Release - OAuth Button Refinement

#### Changed
- **OAuth Button Implementation**: Simplified to use `st.link_button` for maximum reliability
- **New-Tab Approach**: OAuth now opens in new tab to preserve Streamlit session state
- **Logout Behavior**: Added `target="_self"` to logout link for same-tab redirect
- **Removed Complexity**: Eliminated JavaScript workarounds and device detection code

#### Fixed
- **Session State Persistence**: Resolved issue where OAuth state was lost during same-tab redirects
- **Browser Compatibility**: Accepted browser security limitations instead of fighting them
- **403 Errors**: Eliminated 403 errors caused by session state loss during redirects

#### Technical Implementation
- Streamlit's `st.session_state` is tied to WebSocket connection
- Same-tab redirect closes connection and loses session
- New-tab approach keeps original session alive during OAuth
- Simple, reliable solution that works on all devices

#### Removed
- Complex JavaScript button with `components.html`
- Device detection logic for mobile vs desktop
- Attempts to programmatically close tabs (browser security prevents this)
- Custom HTML/CSS OAuth button implementations

#### Files Modified
- `main_app.py` - Simplified OAuth button to `st.link_button`, added `target="_self"` to logout
- `version.py` - Updated to v5.2

#### User Experience
- Users click "Sign in with Google" → opens in new tab
- Complete authentication in new tab
- Manually close original tab (browser security prevents auto-close)
- Clean, working solution that prioritizes reliability over perfect UX

---

## [5.1.0] - 2026-01-25

### 🔧 Minor Release - OAuth Fix & Consent Screen

#### Fixed
- **403 Authentication Error**: Created new OAuth 2.0 Client ID to resolve persistent 403 errors
- **State Validation**: Improved OAuth state handling to work with Streamlit Cloud session persistence
- **Redirect URI**: Fixed callback URL construction to use production redirect URI dynamically

#### Added
- **Consent Screen**: Added `prompt='consent'` to show users what permissions they're granting
- **Better Error Messages**: Improved user feedback with clear error messages and emojis
- **Session Cleanup**: Proper cleanup of oauth_state after successful login

#### Changed
- **OAuth Client**: Switched to new OAuth 2.0 Client ID with proper web application configuration
- **State Validation Logic**: Only validates state if it exists in session (handles session loss gracefully)
- **Error Handling**: Production-ready error handling without debug tracebacks

#### Technical Implementation
- New OAuth Client ID: `944889847818-oqkqt241omg77kbqth0p1vp5jmlro5id.apps.googleusercontent.com`
- Improved `get_authorization_url()` with consent prompt
- Enhanced callback handling in `main_app.py`
- Better session state management

#### Files Modified
- `utils/auth.py` - Added consent prompt, improved error handling
- `main_app.py` - Fixed state validation, better error messages
- `config_secrets.py` - Updated with new OAuth credentials

---

## [5.0.0] - 2026-01-24

### 🔐 Major Release - Authentication & UI Optimization

#### Added
- **Google OAuth 2.0 Authentication System**:
  - Full OAuth 2.0 flow with Google Cloud Console integration
  - User database with `users` table (user_id, google_id, email, name, profile_picture_url, role, created_at, last_login)
  - Secure session management with OAuth state validation (CSRF protection)
  - User profile display with name, email, profile picture, and role
  - Admin and regular user roles with permission controls
  - Database migrations: `add_users_table.py`, `add_user_roles.py`
  - New authentication module: `utils/auth.py`

- **Role-Based Access Control**:
  - Admin access to all tables in Data Explorer
  - Regular users restricted from sensitive tables: `users`, `metadata`, `model_predictions`, `chat_history`
  - Backend enforcement of access permissions
  - Admin emails configured: `tirthdhara108@gmail.com`, `tirth.shah@tamu.edu`
  - Regular user: `tirth.170410107110@gmail.com`

- **Sidebar UI Complete Redesign**:
  - Compact header with Texas A&M logo
  - "Mays Analytics" title with "Flex Online Programs" subtitle
  - Gold divider (2px solid #C5A572) below header
  - Profile section with inline logout button
  - Role display (Admin/User) in subtle italic text
  - Navigation reordered: Home Dashboard, Executive Dive, Comparison Tool, Marketing Analysis, Predictive Analytics, Chat with AI, Data Explorer
  - Documentation renamed to "Documentation & Help"
  - Footer with version number and gold divider

#### Changed
- **Spacing Optimization**:
  - Removed all Streamlit default gaps between elements
  - Consistent 10px margins between all major sections (Laptop)
  - Responsive spacing: Desktop (12px), Laptop (10px), Tablet (8px)
  - Header padding-bottom: 6px
  - Profile margin-top: 10px, margin-bottom: 12px
  - No scrolling required on laptop/desktop screens

- **Navigation Tabs**:
  - White background on inactive tabs
  - Maroon gradient on active tabs
  - Compact button padding: 6px vertical, 0px margins
  - Smooth hover animation: 3px slide with 0.2s transition
  - Professional appearance without emojis

- **Profile Section**:
  - Consolidated design: picture, name, email, role in single card
  - Full-width logout button integrated in profile card
  - Role text on separate line below email
  - Optimized padding: 10px internal
  - White background with subtle border

- **CSS Improvements**:
  - Aggressive removal of default Streamlit spacing
  - Added `margin-block-start: 0px` and `margin-block-end: 0px`
  - Production-ready CSS with `!important` flags
  - Fixed Streamlit Cloud caching issues

#### Technical Implementation
- **Dependencies Added**:
  - `google-auth==2.27.0`
  - `google-auth-oauthlib==1.2.0`
  - `google-auth-httplib2==0.2.0`

- **Files Modified**:
  - `main_app.py` - Complete sidebar redesign (601 lines changed)
  - `modules/database.py` - Role-based table filtering (54 lines added)
  - `utils/auth.py` - New authentication module (complete OAuth flow)
  - `requirements.txt` - Added Google auth packages

- **Database Schema**:
  - Users table with role field
  - Indexes on google_id and email for performance
  - Automatic role assignment on first login

#### Security
- OAuth state validation for CSRF protection
- Secure credential storage (not in git)
- Session-based authentication
- Backend role verification
- Admin role enforcement

#### Removed
- `GOOGLE_AUTH_SETUP_COMPLETE.md` - Temporary setup guide

---

## [4.4.0] - 2026-01-24

### 🎨 Minor Release - Navigation & UX Enhancements (Final)

#### Added
- **Back to Top Button - Chevron Style**:
  - Circular button (56px) with triangle chevron icon (▲)
  - Maroon gradient background matching platform theme
  - Smooth 2.5-second scroll animation with easing
  - Positioned bottom-right (30px from edges)
  - Hover effects: lift, scale, enhanced shadow
  - Mobile responsive (50px on mobile)
  - Always visible on all pages

#### Changed
- **Sidebar Behavior**:
  - `initial_sidebar_state` changed to "collapsed"
  - Sidebar starts closed by default
  - Overlay mode prevents content shifting
  - Users open sidebar when needed

- **Scroll Animation**:
  - Custom JavaScript with `requestAnimationFrame`
  - 2.5-second duration for smooth, visible scrolling
  - Ease-in-out quad easing function
  - Users can see content while scrolling up
  - Anchor at absolute top of page

#### Design Details
- Circular border (border-radius: 50%)
- White triangle chevron (▲) icon
- Semi-transparent border with glassmorphism
- Professional shadow (6px blur, 18px spread)
- 0.4s transition timing
- Scale to 1.03 on hover

#### Technical Implementation
- Used `st.components.html` for JavaScript execution
- Global function for cross-iframe communication
- CSS smooth scroll as fallback
- Mobile breakpoint at 768px
- Z-index: 999999 for always-on-top

#### Files Modified
- main_app.py: Back-to-top button, scroll animation, sidebar config
- version.py: Updated to 4.4

#### Impact
- Enhanced navigation UX
- Professional floating button
- Smooth, visible scroll animations
- Reduced visual clutter
- Better mobile experience

---

## [4.3.0] - 2026-01-24

### 🎨 Minor Release - Navigation & UX Enhancements (Initial)

#### Added
- **Floating "Back to Top" Button**:
  - Beautiful rounded square design (56x56px) with maroon gradient
  - White upward arrow icon, perfectly centered
  - Fixed position in bottom-right corner (30px from edges)
  - Smooth hover animations with lift effect and scale
  - Professional shadow effects and glassmorphism border
  - Mobile responsive (48x48px on smaller screens)
  - Scrolls to absolute top of page including headers

#### Changed
- **Sidebar Behavior**:
  - Changed `initial_sidebar_state` from "expanded" to "collapsed"
  - Sidebar now starts collapsed by default
  - Users can open when needed for navigation
  - Content never shifts when sidebar opens/closes (overlay mode)

- **Scroll Behavior**:
  - Added smooth scroll behavior to HTML
  - Page anchor placed at absolute top for proper scroll-to-top
  - Back to top button scrolls to very beginning of content

#### Design Improvements
- Modern rounded square button (16px border-radius) instead of circle
- Larger, more clickable button size
- Enhanced shadow effects (8px blur, 24px spread)
- Subtle white semi-transparent border for depth
- Backdrop blur effect for glassmorphism
- Smooth cubic-bezier easing for professional animations
- Hover effect: lifts 4px and scales to 105%
- Active state with reduced lift for tactile feedback

#### Technical
- Removed non-working JavaScript scroll attempts
- Simplified scroll-to-top implementation using anchor links
- Added proper CSS for button centering and responsiveness
- Improved z-index management (999999) for button visibility

#### Impact
- Better user experience with easy navigation back to top
- Cleaner interface with collapsed sidebar by default
- Professional, modern design matching platform aesthetics
- Mobile-friendly responsive design

---

## [4.2.0] - 2026-01-24

### 🎉 Minor Release - Contact & Feedback Integration

#### Added
- **Contact & Feedback Form** on Documentation page:
  - Name, Email, Phone Number fields
  - Feedback type selector (Bug Report, Improvement, Question, General, Other)
  - Multi-select for affected pages
  - Subject and detailed message fields
  - Form validation for required fields
  - Email format validation

- **Email Integration**:
  - Resend API integration for reliable email delivery
  - Professional HTML email formatting with maroon/gold theme
  - Reply-to set to user's email for easy responses
  - Includes platform version and timestamp
  - All feedback sent to tirth.shah@tamu.edu

- **Deployment Support**:
  - Streamlit Cloud secrets integration
  - Automatic fallback to local config for development
  - DEPLOYMENT.md guide for Streamlit Cloud setup
  - secrets.toml.template for easy configuration

#### Changed
- **README.md**:
  - Updated contact section with feedback form reference
  - Removed GitHub Issues link (replaced with form)
  - Updated version badge to 4.2

- **Code Architecture**:
  - Smart secret loading (Streamlit Cloud → local config)
  - Graceful error handling for missing secrets
  - Import conflict resolution (renamed secrets.py to config_secrets.py)

#### Security
- API keys stored securely in Streamlit secrets (production)
- Local config_secrets.py for development (not committed)
- Added .streamlit/secrets.toml to .gitignore
- Email validation and sanitization

#### Files Modified
- modules/help.py: Added contact form with dual secret loading
- .gitignore: Added secrets.toml exclusion
- requirements.txt: Added resend==2.4.0
- version.py: Updated to 4.2

#### Files Added
- DEPLOYMENT.md: Complete deployment guide
- .streamlit/secrets.toml.template: Secret configuration template

#### Impact
- Users can now report bugs and provide feedback directly in the app
- No need to leave the platform to contact support
- Streamlined communication channel
- Works in both development and production environments

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
| **6.5.0** | 2026-01-27 | Major | UI/UX Polish & Mobile Optimization |
| **6.2.0** | 2026-01-27 | Major | Professor Feedback Implementation |
| **6.1.0** | 2026-01-26 | Minor | Sidebar Profile Enhancement |
| **6.0.0** | 2026-01-25 | Major | AI Chat Assistant with NLP |
| **5.2.0** | 2026-01-25 | Minor | OAuth Button Refinement |
| **5.1.0** | 2026-01-25 | Minor | OAuth Fix & Consent Screen |
| **5.0.0** | 2026-01-24 | Major | Authentication & UI Optimization |
| **4.4.0** | 2026-01-24 | Minor | Navigation & UX (Final) |
| **4.3.0** | 2026-01-24 | Minor | Navigation & UX (Initial) |
| **4.2.0** | 2026-01-24 | Minor | Contact & Feedback Integration |
| **4.1.0** | 2026-01-24 | Minor | UI/UX & Responsive Design |
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

[6.5.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v6.5
[6.2.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v6.2
[6.1.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v6.1
[6.0.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v6.0
[5.2.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v5.2
[5.1.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v5.1
[5.0.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v5.0
[4.4.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v4.4
[4.3.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v4.3
[4.2.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v4.2
[4.1.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v4.1
[4.0.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v4.0.0
[3.0.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v3.0.0
[2.4.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v2.4.0
[2.3.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v2.3.0
[2.2.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v2.2.0
[2.1.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v2.1.0
[2.0.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v2.0.0
[1.0.0]: https://github.com/Tirth-1999/mays-recruiting-analytics/releases/tag/v1.0.0
