# Mays Analytics - Flex Online Programs Analytics Platform

**Last Updated**: January 23, 2026  
**Version**: 2.4  
**Status**: ✅ Production Ready with Enhanced UI/UX

A comprehensive data analytics platform for Texas A&M Mays Business School's Flex Online Programs, providing real-time insights into admissions performance and marketing effectiveness.

---

## 🎯 What's New (January 2026)

### ✅ Latest Updates (v2.4 - January 23, 2026)

**UI/UX Refinements - Cleaner Interface:**
- **Sidebar Optimization**: Reduced padding and spacing for more compact navigation
  - Logo size reduced from 50px to 40px
  - Brand section padding reduced from 20px to 10px
  - Button padding reduced from 12px to 10px
  - Removed "Quick Stats" and "System Info" sections
  - Removed "Edulytix Platform" branding from footer
  - Removed "Pages" section title
  - Removed all emojis from navigation buttons
  - Cleaner, more professional appearance

**Help & Documentation - Complete Redesign:**
- **Removed Sections**: Eliminated "For Program Directors & Deans" section
- **Chrome-Style Tabs**: Professional tab styling matching Marketing Analysis
  - Shorter tab labels: Home, Executive, Compare, Marketing, Database
  - Smaller font size (12px) for better mobile fit
  - No emojis for cleaner appearance
  - Centered tab layout with proper spacing
- **Center-Aligned Content**: All headers and sections now centered
- **Understanding Your Data**: Three connected boxes (Data Coverage, Important Notes, Key Metrics)
- **Troubleshooting**: Proper white boxes with all content contained
  - Common Issues with 4 Q&A pairs
  - Need Help with contact info and version
- **Fixed HTML Rendering**: No more raw HTML code showing
- **Mobile-Friendly**: Compact tabs fit on phone-sized screens

**Version Updates:**
- Updated all version references from 2.3 to 2.4
- Updated "Last Updated" date to January 23, 2026
- Consistent versioning across sidebar, Help page, and footer

### ✅ Previous Updates (v2.3 - January 22, 2026)

**Comparison Tool - Major Enhancements:**
- **Restructured Layout**: Moved "How to Use This Comparison Tool" above "Comparing" header for better UX
- **Fixed Percentage Change Display**: Shows "N/A" instead of confusing values when no base comparison exists
- **Enhanced Performance Indicators**: Descriptive messages like "🟢 New Metric - Strong Growth (No Base Year Data)"
- **Smart Metric Filtering**: Automatically excludes metrics where both cohorts have zero values
- **Excluded Metrics Note**: Yellow info box shows which metrics were filtered out and why
- **Dynamic Metric Selector**: Only shows metrics with data for at least one cohort
- **Improved Chart Spacing**: Percentage Change Analysis chart with proper padding (top: 120px, bottom: 100px, height: 550px)
- **Correct Statistical Calculations**:
  - Variance: `((Primary - Mean)² + (Comparison - Mean)²) / 2`
  - Standard Deviation: `√Variance`
  - Coefficient of Variation: `(Std Dev / Mean) × 100`

**Executive Deep Dive - Simplified Interface:**
- **Removed Analysis Depth Dropdown**: No more "Detailed Analytics" vs "Full Deep Dive" selection
- **Direct to Full Deep Dive**: Content flows immediately to comprehensive 4-tab interface
- **Removed Detailed Analytics Section**: Eliminated redundant metrics boxes and performance analysis
- **Removed Trend Analysis**: Cleaned up Application & Inquiry Trends and Conversion Rates charts from Detailed Analytics
- **Centered Filters**: Two-column layout matching Home Dashboard style
- **Added Section Header**: "🎓 Select Cohort and Program for Analysis" with gray background
- **Added How to Use Guide**: Comprehensive two-column guide below filters with:
  - Left: Navigation & Filters (Primary Cohort, Program Focus, Four Tabs)
  - Right: Interactive Features (Toggle Buttons, Log Scale, Hover Details, Export Data)
- **Removed Info Line**: Eliminated "Primary Cohort: Class of X | Latest Data: date" redundancy

**Marketing Analysis - Reorganized Layout:**
- **Moved How to Use Section**: Now appears after filters instead of before
- **Removed "What You Can Discover Here"**: Eliminated redundant bottom section
- **Consistent Structure**: Matches Comparison Tool and Executive Deep Dive patterns
- **New Order**: Filters → How to Use → Tabs (Overview, Advanced Analytics, Channel Analytics, Incremental Notes)

**UI/UX Consistency Across All Pages:**
- **Standardized "How to Use" Sections**: All pages now have consistent gray background (`#e9ecef`) with white inner content
- **Two-Column Grid Layout**: Left column for features/steps, right column for interactive elements
- **Positioned After Filters**: User guidance appears after filter selection, before main content
- **Professional Styling**: Maroon headings (`#500000`), proper spacing, and clear hierarchy

### ✅ Previous Updates (v2.2 - January 22, 2026)

**Executive Deep Dive - Major Restructure:**
- **Removed "Compare With" Filter**: Simplified main filter interface (3 filters instead of 4)
- **New Analysis Depth**: Added "Comparison Tool" as third option for dedicated year-over-year analysis
- **Full Deep Dive Tabs**: Reduced from 5 to 4 tabs (removed Advanced Insights, moved to Comparison Tool)
  - 📊 Performance Analysis
  - 📈 Trend Analysis
  - 🎓 Program Deep Dive
  - 📋 Data Tables

**Program Deep Dive Tab - Complete Transformation:**
- **Split Metrics**: Separated into Applications (11 metrics) and Admissions (9 metrics) charts
- **Chart Type Toggle**: Switch between Line and Bar charts to solve overlapping labels
- **Log Scale Toggle**: Independent log scale for both chart types
- **Data Labels**: Exact numbers displayed on all data points
- **Bottom Legend**: Moved legend below charts for maximum chart width
- **Optimized Layout**: 60:20:20 ratio (Metric Selector : Chart Type : Log Scale)
- **Removed Redundancy**: Eliminated program filter and repetitive headers

**Comparison Tool (New):**
- **Dedicated YoY Analysis**: Centralized location for cohort comparisons
- **Independent Filters**: Select Primary Cohort, Comparison Cohort, and Program Filter
- **Comprehensive Tables**: Side-by-side metrics with variance analysis
- **Visual Comparisons**: Bar charts for absolute values and percentage changes
- **Time Series Overlay**: Compare trends over time for both cohorts
- **Three Export Options**: Download comparison table, primary data, and comparison data

**Marketing Analysis:**
- **Enhanced UX**: Added "How to Use This Analysis" section with white subsection
- **Consistent Styling**: Matches Executive Deep Dive information card design

**UI/UX Improvements:**
- **Removed Headers**: Cleaner interface without "Analysis Configuration" header
- **Full-Width Filters**: 3-column layout utilizing entire screen width
- **Centered Labels**: Professional appearance for all filter labels
- **Proper Spacing**: Optimized legend positioning with no overlap

### ✅ Previous Updates (v2.1 - January 21, 2026)
- **Global Filter System**: Centralized filters across all Marketing Analysis tabs with dynamic cascading
- **Responsive Tab Design**: Chrome-style tabs with horizontal scrolling on mobile/tablet devices
- **Enhanced Data Explorer**: Professional table navigation with icon-labeled tabs and centered layout
- **Improved UX**: Darker section headers (#e9ecef) for better visibility across all tabs
- **Mobile Optimization**: Touch-friendly scrolling with always-visible maroon scrollbar
- **Filter Independence**: Each filter maintains its own state without interfering with others

### ✅ Previous Updates (v2.0 - January 14, 2026)
- **December 2025 Data**: Latest admissions data through Dec 31, 2025
- **Marketing Spend Integration**: FY25 Year 1 ad spend data (Sep 2024 - Jun 2025)
- **Update Timestamps**: Clear indicators of data freshness in footer
- **Professional UI**: Consistent styling with maroon theme throughout

### 📊 Current Data Coverage
- **Admissions Records**: 2,037 records across 7 programs
- **Marketing Records**: 76 spend records, 90 aggregated metrics
- **Date Range**: January 2024 - December 2025 (admissions), September 2024 - June 2025 (marketing)
- **Programs**: MBA, MS ACCT, MS ENLD, MS HRM, MS MISY, MS MKTG, MS SPBA
- **Cohorts**: Class of 2026, 2027, 2028

---

## 🚀 Quick Start

### 1. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 2. Install Dependencies (if needed)

```bash
pip install -r requirements.txt
```

### 3. Load Data into Database

```bash
# Load admissions data (includes December 2025 file)
python3 etl_pipeline.py

# Load marketing spend data (NEW!)
python3 marketing_etl.py
```

This will:
- Create/update `edulytix.db` SQLite database
- Load all Excel files from the `Dataset/` folder
- Clean and structure the data
- Create necessary tables (admissions + marketing)
- Track update timestamps in metadata table

### 4. Run the Dashboard

```bash
streamlit run main_app.py
```

Or use the startup script:
```bash
./run_dashboard.sh
```

The dashboard will open in your browser at `http://localhost:8501`

---

## 📁 Project Structure

```
.
├── main_app.py                 # Main Streamlit dashboard (single-page app)
├── etl_pipeline.py             # ETL for admissions data
├── marketing_etl.py            # ETL for marketing spend data (NEW!)
├── marketing_etl_template.py   # Template for future marketing data
├── marketing_schema.sql        # Marketing database schema
├── requirements.txt            # Python dependencies
├── edulytix.db                # SQLite database (created after running ETL)
├── run_dashboard.sh           # Startup script
├── Dataset/                   # Excel files with admissions & marketing data
│   ├── MBS-Flex-Online-Admissions-2024-04-30.xlsx
│   ├── MBS-Flex-Online-Admissions-2024-05-31.xlsx
│   ├── MBS-Flex-Online-Admissions-2024-07-31.xlsx
│   ├── MBS-Flex-Online-Admissions-2025-07-31.xlsx
│   ├── MBS-Flex-Online-Admissions-2025-10-31.xlsx
│   ├── MBS-Flex-Online-Admissions-2025-10-31_New.xlsx
│   ├── MBS-Flex-Online-Admissions-2025-11-30.xlsx
│   ├── MBS-Flex-Online-Admissions-2025-12-31.xlsx (NEW!)
│   └── Mays Flex Online Ad Spend Year 1.xlsx (NEW!)
├── Context/                   # Background documents and emails
├── UPDATE_SUMMARY.md          # Latest update details (NEW!)
└── PROFESSOR_FEEDBACK_GUIDE.md # Feedback implementation guide (NEW!)
```

---

## 🎨 UI/UX Features

### Global Filter System (Marketing Analysis)
- **Centralized Control**: Set filters once at the top, applies to all four tabs
- **Dynamic Cascading**: Downstream filters auto-update based on upstream selections
  - Example: Select FY25 → Program filter shows only programs with FY25 data
  - Select "Marketing" → Channel filter shows only channels with Marketing data
- **Independent State Management**: Each filter (Fiscal Year, Program, Channel) maintains its own state
- **Smart Buttons**: ✓ All and ✗ Clear buttons for quick selection/deselection
- **Empty State Handling**: Shows "⚠️ No data matches the selected filters" when no data available

### Responsive Tab Navigation
- **Desktop (>1024px)**: Tabs centered with proper spacing
- **Mobile/Tablet (≤1024px)**: Tabs left-aligned with horizontal scrolling
- **Always-Visible Scrollbar**: Maroon (#500000) scrollbar matching theme
  - 10px height on desktop, 12px on mobile
  - Touch-friendly with smooth scroll behavior
- **Chrome-Style Design**: Professional tab appearance across Marketing Analysis and Data Explorer

### Section Headers
- **Darker Background**: #e9ecef (medium gray) for better visibility
- **Consistent Styling**: Applied across all tabs and sections
- **Clear Hierarchy**: Distinguishes sections from content areas

### Information Cards
- **White Subsections**: Content cards within gray background sections
- **Centered Text**: Professional alignment for descriptions and bullet points
- **Subtle Shadows**: Depth and visual separation

---

## 🗄️ Database Schema

### Admissions Tables

**programs**
- program_code (TEXT, PRIMARY KEY)
- program_name (TEXT)
- is_active (INTEGER)

**admissions_metrics**
- id (INTEGER, PRIMARY KEY)
- report_date (TEXT)
- program (TEXT)
- cohort_year (INTEGER)
- metric_name (TEXT)
- metric_value (REAL)
- created_at (TIMESTAMP)
- UNIQUE constraint on (report_date, program, cohort_year, metric_name)

### Marketing Tables (NEW!)

**marketing_spend**
- spend_id (INTEGER, PRIMARY KEY)
- spend_date (TEXT)
- program (TEXT)
- channel (TEXT) - Search, Display, LinkedIn, Meta, etc.
- amount (REAL)
- fiscal_year (TEXT)
- currency (TEXT)

**marketing_metrics**
- metric_id (INTEGER, PRIMARY KEY)
- report_date (TEXT)
- program (TEXT)
- channel (TEXT)
- spend (REAL)
- is_active (INTEGER) - 1 = active, 0 = inactive
- impressions, clicks, inquiries, applications (for future use)

**marketing_campaigns** (ready for future data)
- campaign_id, campaign_name, campaign_type, start_date, end_date, etc.

**inquiry_sources** (ready for future data)
- inquiry_id, inquiry_date, source, campaign_id, converted_to_application, etc.

### System Tables

**metadata** (NEW!)
- key (TEXT, PRIMARY KEY)
- value (TEXT)
- updated_at (TIMESTAMP)

Tracks:
- `last_data_update` - When admissions data was last loaded
- `last_marketing_update` - When marketing data was last loaded

---

## 📊 Dashboard Features

### 🏠 Home Dashboard
- **Cohort Selection**: Choose Class of 2026, 2027, or 2028
- **Key Metrics**: Enrolled students, applications, inquiries, conversion rates
- **Admissions Funnel**: Visual flow from inquiries to enrollment
- **Program Comparison**: Side-by-side performance across all 7 programs
- **Interactive Charts**: Click legend items, use checkboxes to customize view

### 📊 Executive Deep Dive
A comprehensive analytics suite providing deep insights into cohort performance with interactive visualizations.

**Filter Configuration:**
- **Primary Cohort**: Select Class of 2026, 2027, or 2028
- **Program Focus**: Choose specific program or "All Programs"

**How to Use This Section:**
- Gray background guide with white content card
- Left column: Navigation & Filters (cohort selection, program filtering, tab navigation)
- Right column: Interactive Features (toggle buttons, log scale, hover details, export options)

**Four Analysis Tabs:**

1. **📊 Performance Analysis**: Comprehensive metrics with YoY comparisons
   - Key performance indicators
   - Conversion funnel visualization
   - Program comparison charts
   - Trend indicators and growth metrics

2. **📈 Trend Analysis**: Time-series charts with interactive filtering
   - Application and inquiry trends over time
   - Conversion rate tracking
   - Toggle buttons to show/hide specific metrics
   - Hover for exact values and dates

3. **🎓 Program Deep Dive**: Detailed application and admission metrics (see below)
   - Split metrics: Applications (11) and Admissions (9)
   - Chart type toggle (Line/Bar)
   - Log scale option
   - Data labels on all points

4. **📋 Data Tables**: Exportable data with advanced filtering
   - Complete metric breakdowns
   - Program-level details
   - CSV export functionality
   - Sortable columns

### 🎓 Program Deep Dive (within Full Deep Dive)
Advanced visualization of application and admission metrics with flexible chart options.

**Split Metrics Approach:**
- **📝 Applications Metrics** (11 metrics): inquiries_received, applications_in_progress, applications_received, applications_complete, applications_manual, applications_verified, applications_on_hold, applications_undelivered, applications_deferral, total_applications, admissions_pre_admission
- **🎯 Admissions Metrics** (9 metrics): admissions_offered, admissions_denied, admissions_accepted, admissions_declined, admissions_deferred_to_next, admissions_deferred_from_last, admissions_moved_to_other, admissions_withdrawn, anticipated_cohort_size

**Interactive Controls (60:20:20 Layout):**
- **Metric Selector** (60%): Multi-select dropdown to choose which metrics to display
- **Chart Type Toggle** (20%): Switch between Line and Bar charts
  - Line Chart: Best for trend analysis with connected data points
  - Bar Chart: Best for comparing values, solves overlapping label issues
- **Log Scale Toggle** (20%): Apply logarithmic scale to both chart types for better visualization of wide-ranging values

**Chart Features:**
- **Data Labels**: Exact numbers displayed on all data points (values > 0)
- **Bottom Legend**: Maximizes chart width, positioned below with proper spacing
- **Color Schemes**: Red for Applications, Blue for Admissions
- **Aggregate View**: Shows data across all programs (no program filter)

### 🔄 Comparison Tool
A dedicated year-over-year analysis tool for comparing cohort performance with statistical rigor.

**Filter Configuration:**
- **Primary Cohort**: Select the main cohort for analysis (2028, 2027, or 2026)
- **Comparison Cohort**: Choose the cohort to compare against
- **Program Filter**: Focus on specific program or view all programs

**How to Use This Comparison Tool:**
- Positioned after filters, before comparison results
- Left column: Step-by-step guide (cohort selection, program filtering, time series exploration, data tables)
- Right column: Key features (percentage changes, comprehensive table, export options, visual indicators)

**Smart Data Handling:**
- **Automatic Filtering**: Excludes metrics where both cohorts have zero values
- **Excluded Metrics Note**: Yellow info box shows which metrics were filtered out
- **N/A for No Base**: Shows "N/A" for % Change when comparison cohort has no data
- **Descriptive Indicators**: "🟢 New Metric - Strong Growth (No Base Year Data)" instead of generic labels

**Statistical Analysis:**
- **Correct Variance Calculation**: `((Primary - Mean)² + (Comparison - Mean)²) / 2`
- **Standard Deviation**: `√Variance` for measuring spread
- **Coefficient of Variation**: `(Std Dev / Mean) × 100` for relative variability
- **Performance Indicators**: Based on % change thresholds with special handling for edge cases

**Visualization Components:**
1. **Comparing Header**: Shows selected cohorts, programs, and latest data dates
2. **Time Series Comparison**: Side-by-side charts for each metric with toggle buttons
3. **Percentage Change Analysis**: Full-width bar chart with proper spacing (550px height, 120px top margin)
4. **Comprehensive Table**: All metrics with variance analysis and performance indicators
5. **Export Options**: Three download buttons (comparison table, primary data, comparison data)

**Interactive Features:**
- **Metric Selector**: Only shows metrics with data for at least one cohort
- **Show Data Table Button**: Centered button per metric to reveal program-level breakdowns
- **Hover Details**: Exact values and dates on all charts
- **Color Coding**: Green for growth, red for decline, gray for stable

### 📢 Marketing Analysis
A comprehensive multi-tab dashboard with global filters for analyzing marketing spend, channel performance, and ROI across programs.

**Global Filter System:**
- **Centralized Filters**: Set Fiscal Year, Program, and Channel once at the top - applies to all tabs
- **Dynamic Updates**: Downstream filters auto-update based on available data (e.g., selecting FY25 shows only programs with FY25 data)
- **Independent State**: Each filter maintains its own state without interfering with others
- **Smart Defaults**: "All" option available for each filter with ✓ All and ✗ Clear buttons

**How to Use This Analysis:**
- Positioned after filters, before tabs
- Left column: What You Can Discover (Spend Analysis, Channel Performance, Trend Tracking, ROI Insights)
- Right column: Interactive Features (Multi-Select Filters, Dynamic Charts, Hover Details, Data Export)
- Consistent styling with other pages (gray background, white content card)

**Four Analysis Tabs:**

1. **📊 Overview Tab**
   - Key ROI metrics: Total Spend, Avg Cost per Inquiry (CPI), Avg Cost per Application (CPA), Avg Conversion Rate
   - Spend by Program: Bar chart with log scale option and multi-select filters
   - Spend by Channel: Toggle between pie and bar chart views
   - Quick snapshot of marketing performance across all dimensions

2. **🔬 Advanced Analytics Tab**
   - ROI Summary: CPI, CPA, Cost per Admission (CPAd), Conversion Rate
   - Spend vs Outcomes Trend: Dual-axis chart correlating spend with inquiries, applications, and admissions
   - Detailed ROI Metrics Table: Program-by-program comparison with gradient styling
   - Deep-dive analysis connecting marketing spend to admissions outcomes

3. **📢 Channel Analytics Tab**
   - Channel-focused performance analysis
   - Spend Distribution: Side-by-side bar and pie charts
   - Channel Spend Trends: Monthly trend lines for each channel
   - Performance Summary Table: Total spend, program count, and activity months per channel

4. **📝 Incremental Notes Tab**
   - Document campaign changes, special events, and performance anomalies
   - Searchable notes database organized by program, month, and fiscal year
   - Expandable note cards for easy browsing
   - Historical context for data analysis

**Responsive Design:**
- Chrome-style tabs with horizontal scrolling on mobile/tablet
- Tabs centered on desktop (>1024px), left-aligned on smaller screens
- Always-visible maroon scrollbar matching theme
- Touch-friendly with smooth scroll behavior

### 🗄️ Data Explorer
A professional data exploration interface with Chrome-style tabs and advanced filtering capabilities.

**Chrome-Style Navigation:**
- Seven database tables with icon-labeled tabs: 📊 Admissions Matrix, 📈 Inquiry Sources, 💰 Marketing Campaigns, 🔍 Marketing Spend, 🎓 Marketing Spend Totals, 📢 Metadata Programs, ⚙️ SQLite Sequence
- Centered tab bar with proper spacing on desktop
- Horizontal scrolling on mobile/tablet with visible maroon scrollbar
- Full-width keyword search: "🔍 Find Your Data"

**Table Information Sections:**
- Darker background (#e9ecef) for section headers
- White subsection cards for table descriptions
- "What questions can this table help answer?" with centered bullet points
- Professional styling with subtle shadows

**Advanced Filtering:**
- Column selection with multi-select
- Row limits (10, 25, 50, 100, 500, All)
- Sort by any column (ascending/descending)
- Search across all columns with text filter
- Real-time data updates

**Data Analysis:**
- Quick statistics for numeric columns (count, mean, std, min, max, quartiles)
- Export filtered data as CSV
- Interactive table display with pagination
- Clear indicators of data availability

**Responsive Design:**
- Tabs centered on desktop, left-aligned on mobile/tablet
- Touch-friendly scrolling with always-visible scrollbar
- Consistent styling with Marketing Analysis tabs

---

## 📈 Metrics Tracked

### Admissions Metrics (20+ metrics)
- inquiries_received
- applications_in_progress
- applications_received
- applications_complete
- applications_manual
- applications_verified
- applications_on_hold
- applications_undelivered
- applications_deferral
- total_applications
- admissions_pre_admission
- admissions_offered
- admissions_denied
- admissions_accepted
- admissions_declined
- admissions_deferred_to_next
- admissions_deferred_from_last
- admissions_moved_to_other
- admissions_withdrawn
- **anticipated_cohort_size** (most important!)

### Marketing Metrics (NEW!)
- Spend by channel (Search, Display, LinkedIn, Meta, YouTube, OOH)
- Spend by program
- Monthly spend trends
- Channel distribution
- Program allocation

---

## 💡 Data Clarifications

### Admissions Data
- Campaign matrix values labeled `- NA -` indicate the campaign was not active for that program/month and are excluded from totals
- Blank/`NaN` values are preserved as missing data rather than treated as zeros
- Dates represent the last day of the reporting month
- All metrics are cumulative within a cohort year

### Marketing Data
- "No Ad Spend" entries are handled as NULL (not zero)
- Spend is tracked monthly by program and channel
- FY25 Year 1 covers September 2024 - June 2025
- Search advertising represents 98% of total spend ($202K of $206K)
- General Awareness campaigns are tracked separately from program-specific campaigns

---

## 🔧 Troubleshooting

### Common Issues

**Issue: "No data available"**
- Make sure you've run both ETL scripts:
  ```bash
  python3 etl_pipeline.py
  python3 marketing_etl.py
  ```
- Check that Excel files are in the `Dataset/` folder
- Verify `edulytix.db` exists

**Issue: "Marketing Analysis page is empty"**
- Run `python3 marketing_etl.py` to load marketing data
- Check that `Mays Flex Online Ad Spend Year 1.xlsx` exists in Dataset folder

**Issue: "Module not found"**
- Run `pip install -r requirements.txt`
- Make sure you're using Python 3.8+
- Activate virtual environment: `source venv/bin/activate`

**Issue: "Database is locked"**
- Close any other connections to `edulytix.db`
- Restart the Streamlit app
- Check for other Python processes accessing the database

**Issue: "Dashboard shows old data"**
- Re-run ETL scripts to refresh data
- Clear Streamlit cache: Click "Clear cache" in app menu (top right)
- Check footer for last update timestamps

**Issue: "Charts not loading"**
- Check browser console for errors (F12)
- Try a different browser (Chrome recommended)
- Clear browser cache
- Ensure stable internet connection

---

## 📚 Documentation

- **UPDATE_SUMMARY.md** - Detailed summary of January 2026 updates
- **PROFESSOR_FEEDBACK_GUIDE.md** - How feedback has been addressed
- **SETUP.md** - Detailed setup instructions
- **Context/** folder - Background documents and requirements

---

## 🔄 Adding New Data

### Monthly Admissions Data
1. Place new Excel file in `Dataset/` folder
2. Add filename to `etl_pipeline.py` in the `dataset_files` list:
   ```python
   dataset_files = [
       # ... existing files ...
       ('Dataset/NEW-FILE-NAME.xlsx', COHORT_YEAR),
   ]
   ```
3. Run: `python3 etl_pipeline.py`
4. Verify in dashboard

### Marketing Data
1. Place new marketing file in `Dataset/` folder
2. Update `marketing_etl.py` if file structure differs
3. Run: `python3 marketing_etl.py`
4. Check Marketing Analysis page

---

## 🎯 Next Steps

### Immediate Priorities
- [x] Load December 2025 admissions data
- [x] Integrate marketing spend data
- [x] Add update timestamps
- [ ] Link marketing spend to inquiry generation (requires source tracking)
- [ ] Add FY26 Year 2 marketing data (when available)

### Phase 2: Enhancements
- [ ] Calculate true marketing ROI (spend → inquiries → applications → revenue)
- [ ] Add forecasting models (Prophet/ARIMA) for cohort size predictions
- [ ] Implement automated email alerts for key metrics
- [ ] Add campaign-level tracking (beyond channel level)
- [ ] Create executive summary PDF export

### Phase 3: Advanced Features
- [ ] AI chatbot for natural language queries
- [ ] What-if scenario planning tool
- [ ] Automated monthly reports
- [ ] Integration with CRM systems
- [ ] Mobile-responsive design

### Phase 4: Scale to SaaS
- [ ] Multi-tenant architecture
- [ ] User authentication and roles
- [ ] White-label customization
- [ ] API for third-party integrations
- [ ] Marketplace for dashboard templates

---

## 📊 Success Metrics

### Technical KPIs
- ✅ Data Pipeline: 100% accuracy (2,037 records loaded)
- ✅ Dashboard Load Time: < 3 seconds
- ✅ Data Coverage: 7 programs, 3 cohorts, 24 months
- ✅ Marketing Integration: 76 spend records loaded
- ⏳ Forecast Accuracy: TBD (models not yet implemented)

### Business KPIs
- ⏳ User Adoption: TBD (track monthly active users)
- ⏳ Time Savings: TBD (measure reduction in manual reporting)
- ⏳ Decision Impact: TBD (track strategic decisions made using Edulytix)
- ⏳ Stakeholder Satisfaction: TBD (conduct user surveys)

---

## 🤝 Contributing

### Reporting Issues
1. Check existing issues in PROFESSOR_FEEDBACK_GUIDE.md
2. Provide specific details (page, metric, date, expected vs actual)
3. Include screenshots if possible
4. Email Tirth Shah with details

### Requesting Features
1. Describe the use case (what decision are you trying to make?)
2. Specify priority (urgent, important, nice-to-have)
3. Provide example of desired output
4. Submit via email or during office hours

---

## 📞 Contact

**Project Lead**: Tirth Shah (tirth.shah@tamu.edu)  
**Sponsor**: Dr. Shrihari Sridhar (ssridhar@mays.tamu.edu)  
**Data Provider**: Jon Jasperson  
**Marketing Contact**: Brooke Perry

---

## 📄 License

Internal use only - Texas A&M Mays Business School

---

## 🙏 Acknowledgments

- Texas A&M Mays Business School for project sponsorship
- Ologie marketing agency for ad spend data
- All stakeholders providing feedback and requirements

---

**Version History**:
- v2.4 (Jan 23, 2026) - UI/UX refinements: compact sidebar, redesigned Help & Documentation with Chrome-style tabs, center-aligned content, mobile-friendly layout
- v2.3 (Jan 22, 2026) - Comparison Tool enhancements with correct statistics, Executive Deep Dive simplification, Marketing Analysis reorganization, consistent "How to Use" sections across all pages
- v2.2 (Jan 22, 2026) - Executive Deep Dive restructure, Program Deep Dive transformation with chart types, Comparison Tool, Marketing Analysis enhancements
- v2.1 (Jan 21, 2026) - Global filter system with dynamic cascading, responsive tab design, enhanced Data Explorer
- v2.0 (Jan 14, 2026) - Marketing data integration, December 2025 data, metadata tracking
- v1.0 (Nov 30, 2025) - Initial release with admissions data through November 2025
