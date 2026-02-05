"""
Help & Documentation Page Module
Extracted from main_app.py as part of Phase 2 refactoring
"""

import streamlit as st
from version import VERSION, VERSION_FULL, LAST_UPDATED


def render():
    """Render the Help & Documentation page"""
    
    # Center-aligned welcome section
    st.markdown("""
    <style>
    /* Responsive grid for Key Questions - stack when tabs need scrollbar */
    .key-questions-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin: 20px 0;
    }
    
    @media screen and (max-width: 1000px) {
        .key-questions-grid {
            grid-template-columns: 1fr;
            justify-items: center;
        }
        .key-questions-grid > div {
            max-width: 600px;
            width: 100%;
            text-align: center;
        }
        .key-questions-grid ul {
            text-align: left;
            display: inline-block;
        }
    }
    
    /* Responsive grid for Workflows - stack when tabs need scrollbar */
    .workflows-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin: 20px 0;
    }
    
    @media screen and (max-width: 1000px) {
        .workflows-grid {
            grid-template-columns: 1fr;
            justify-items: center;
        }
        .workflows-grid > div {
            max-width: 600px;
            width: 100%;
            text-align: center;
        }
        .workflows-grid ol {
            text-align: left;
            display: inline-block;
        }
    }
    
    /* Responsive grid for Tips - stack when tabs need scrollbar */
    .tips-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin: 20px 0;
    }
    
    @media screen and (max-width: 1000px) {
        .tips-grid {
            grid-template-columns: 1fr;
            justify-items: center;
        }
        .tips-grid > div {
            max-width: 600px;
            width: 100%;
            text-align: center;
        }
        .tips-grid ul {
            text-align: left;
            display: inline-block;
        }
    }
    
    /* Responsive grid for Data Understanding - stack when tabs need scrollbar */
    .data-understanding-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin: 20px 0;
    }
    
    @media screen and (max-width: 1000px) {
        .data-understanding-grid {
            grid-template-columns: 1fr;
            justify-items: center;
        }
        .data-understanding-grid > div {
            max-width: 600px;
            width: 100%;
            text-align: center;
        }
        .data-understanding-grid ul {
            text-align: left;
            display: inline-block;
        }
    }
    
    /* Responsive grid for Troubleshooting - stack when tabs need scrollbar */
    .troubleshooting-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin: 20px 0;
    }
    
    @media screen and (max-width: 1000px) {
        .troubleshooting-grid {
            grid-template-columns: 1fr;
            justify-items: center;
        }
        .troubleshooting-grid > div {
            max-width: 600px;
            width: 100%;
            text-align: center;
        }
        .troubleshooting-grid p {
            text-align: center;
        }
    }
    </style>
    
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 30px;
                text-align: center;">
        <h2 style="color: #500000; margin: 0 0 15px 0;">Welcome to the Analytics Platform</h2>
        <p style="color: #495057; font-size: 16px; line-height: 1.6; margin: 0;">
            Your comprehensive analytics platform for Mays Business School's Flex Online Programs.
            This guide will help you understand how to use each feature to make data-driven decisions
            about admissions, marketing, and program performance.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Flex Online Programs Section
    st.markdown("""
    <style>
    .program-link-button {
        background: white;
        padding: 20px;
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        text-decoration: none !important;
        display: block;
        text-align: center;
        transition: all 0.3s ease;
        margin-bottom: 15px;
    }
    
    .program-link-button:hover {
        border-color: #500000;
        box-shadow: 0 4px 12px rgba(80, 0, 0, 0.15);
        transform: translateY(-2px);
        text-decoration: none !important;
    }
    
    .program-link-icon {
        font-size: 32px;
        margin-bottom: 8px;
        display: block;
    }
    
    .program-link-title {
        color: #500000;
        font-size: 15px;
        font-weight: 600;
        margin: 0;
        line-height: 1.3;
        display: block;
        text-decoration: none !important;
    }
    
    .program-link-button:hover .program-link-title {
        color: #700000;
        text-decoration: none !important;
    }
    
    .program-link-code {
        color: #999;
        font-size: 11px;
        margin-top: 5px;
        font-weight: 500;
        letter-spacing: 0.5px;
        display: block;
    }
    
    /* Remove underline from links */
    a.program-link-button, a.program-link-button:hover, a.program-link-button:visited, a.program-link-button:active {
        text-decoration: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center; color: #500000; margin-top: 30px; margin-bottom: 10px;'>Flex Online Programs</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 14px; margin-bottom: 25px;'>Explore our graduate programs designed for working professionals</p>", unsafe_allow_html=True)
    
    programs = [
        {
            "icon": "🎓",
            "title": "Flex Online MBA",
            "code": "MBA",
            "url": "https://mays.tamu.edu/graduate/mba/flex-online-mba/"
        },
        {
            "icon": "📊",
            "title": "Flex Online MS in Accounting",
            "code": "MS ACCT",
            "url": "https://mays.tamu.edu/graduate/flex-online/ms-accounting/"
        },
        {
            "icon": "🚀",
            "title": "Flex Online MS in Entrepreneurial Leadership",
            "code": "MS ENLD",
            "url": "https://mays.tamu.edu/graduate/flex-online/ms-entrepreneurial-leadership/"
        },
        {
            "icon": "👥",
            "title": "Flex Online MS in Human Resource Management",
            "code": "MS HRM",
            "url": "https://mays.tamu.edu/graduate/flex-online/human-resource-management/"
        },
        {
            "icon": "💻",
            "title": "Flex Online MS in Management Information Systems",
            "code": "MS MISY",
            "url": "https://mays.tamu.edu/graduate/flex-online/management-information-systems-online/"
        },
        {
            "icon": "📈",
            "title": "Flex Online MS in Marketing",
            "code": "MS MKTG",
            "url": "https://mays.tamu.edu/graduate/flex-online/ms-marketing/"
        },
        {
            "icon": "🤖",
            "title": "Flex Online AI & Business Certificate",
            "code": "CERTIFICATE",
            "url": "https://mays.tamu.edu/ai/artificial-intelligence-ai-and-business-certificate/"
        }
    ]
    
    # First 6 programs in 3 columns (2 rows)
    col1, col2, col3 = st.columns(3)
    
    for idx in range(6):
        col = [col1, col2, col3][idx % 3]
        program = programs[idx]
        with col:
            st.markdown(f"""
            <a href="{program['url']}" target="_blank" class="program-link-button">
                <span class="program-link-icon">{program['icon']}</span>
                <span class="program-link-title">{program['title']}</span>
                <span class="program-link-code">{program['code']}</span>
            </a>
            """, unsafe_allow_html=True)
    
    # Last program centered
    col_left, col_center, col_right = st.columns([1, 1, 1])
    with col_center:
        program = programs[6]
        st.markdown(f"""
        <a href="{program['url']}" target="_blank" class="program-link-button">
            <span class="program-link-icon">{program['icon']}</span>
            <span class="program-link-title">{program['title']}</span>
            <span class="program-link-code">{program['code']}</span>
        </a>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Key Questions This Platform Answers - centered header with responsive grid
    st.markdown("<h3 style='text-align: center; color: #500000;'>Key Questions This Platform Answers</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="key-questions-grid">
        <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; display: flex; flex-direction: column;">
            <h4 style="color: #500000; margin: 0 0 15px 0; text-align: center;">Enrollment Questions</h4>
            <ul style="font-size: 14px; line-height: 1.8; color: #495057; flex: 1;">
                <li>Are we on track to meet our cohort size goals?</li>
                <li>Which programs are over/under-performing?</li>
                <li>How do conversion rates compare to last year?</li>
                <li>Where are we losing applicants in the funnel?</li>
                <li>What's our inquiry-to-enrollment conversion rate?</li>
            </ul>
        </div>
        <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; display: flex; flex-direction: column;">
            <h4 style="color: #500000; margin: 0 0 15px 0; text-align: center;">Marketing Questions</h4>
            <ul style="font-size: 14px; line-height: 1.8; color: #495057; flex: 1;">
                <li>What's our cost per inquiry and application?</li>
                <li>Which marketing channels deliver the best ROI?</li>
                <li>How should we allocate next year's budget?</li>
                <li>Are we spending efficiently across programs?</li>
                <li>What's the trend in our marketing effectiveness?</li>
            </ul>
        </div>
        <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; display: flex; flex-direction: column;">
            <h4 style="color: #500000; margin: 0 0 15px 0; text-align: center;">Forecasting Questions</h4>
            <ul style="font-size: 14px; line-height: 1.8; color: #495057; flex: 1;">
                <li>What will our enrollment numbers be next year?</li>
                <li>Which marketing channels should we invest in?</li>
                <li>When is the best time to run campaigns?</li>
                <li>How should we distribute our marketing budget?</li>
                <li>Are our predictions accurate and reliable?</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Custom Chrome-style tab styling with horizontal scroll
    st.markdown("""
    <style>
    /* Chrome-style tabs for Help page with horizontal scroll */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        justify-content: center;
        overflow-x: auto !important;
        overflow-y: hidden !important;
        white-space: nowrap !important;
        -webkit-overflow-scrolling: touch !important;
        scrollbar-width: thin !important;
        scrollbar-color: #500000 #f0f0f0 !important;
    }
    
    /* Show scrollbar on mobile/tablet */
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
        height: 8px !important;
        display: block !important;
    }
    
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-track {
        background: #f0f0f0 !important;
        border-radius: 4px !important;
    }
    
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
        background: #500000 !important;
        border-radius: 4px !important;
    }
    
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb:hover {
        background: #700000 !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 8px 8px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
        padding-left: 15px;
        padding-right: 15px;
        font-size: 12px;
        font-weight: 500;
        color: #495057;
        border: 1px solid #dee2e6;
        border-bottom: none;
        flex-shrink: 0 !important;
        min-width: fit-content !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        color: #500000;
        font-weight: 600;
        border-top: 3px solid #500000;
        border-left: 1px solid #dee2e6;
        border-right: 1px solid #dee2e6;
        border-bottom: 1px solid white;
    }
    
    .stTabs [data-baseweb="tab-panel"] {
        background-color: white;
        border: 1px solid #dee2e6;
        border-radius: 0 0 8px 8px;
        padding: 30px;
    }
    
    /* Mobile/Tablet: left-align tabs and ensure scroll works */
    @media screen and (max-width: 1200px) {
        .stTabs [data-baseweb="tab-list"] {
            justify-content: flex-start !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Page-by-Page Guide with Chrome-style tabs
    st.markdown("<h3 style='text-align: center; color: #500000;'>Page-by-Page Guide</h3>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Executive Dashboard",
        "📊 Director's Deep Dive",
        "📈 Marketing Analysis",
        "🔮 Predictive Analytics",
        "💾 Data Explorer",
        "💬 AI Chat Assistant"
    ])
    
    with tab1:
        st.markdown("""
        **Purpose**: High-level overview of program performance with goal tracking and marketing insights
        
        **Best For**:
        - Executive briefings and leadership updates
        - Quick status checks across all programs
        - Identifying programs needing attention
        - Tracking progress toward enrollment goals
        
        **Two Main Sections**:
        
        **1. Program Comparison**
        - Compare enrollment metrics across programs
        - Filter by cohort and specific programs
        - View inquiries, applications, admissions, and enrollments
        - Toggle between linear and log scale for better visualization
        - Interactive bar charts with detailed tooltips
        
        **2. Marketing Insights**
        - Overview of marketing spend and effectiveness
        - Filter by fiscal year, program, and channel
        - Key metrics: Total spend, CPI, CPA, conversion rates
        - Spend distribution by program and channel
        - ROI analysis and trend visualization
        
        **How to Use**:
        1. **Select Filters**: Choose cohort, programs, fiscal year, and channels
        2. **Review Metrics**: See key performance indicators at a glance
        3. **Compare Programs**: Identify top and underperforming programs
        4. **Analyze Marketing**: Understand spend efficiency and ROI
        5. **Export Data**: Download charts for presentations
        
        **Pro Tip**: Use this page for executive briefings to show both enrollment and marketing performance in one view!
        """)
    
    with tab2:
        st.markdown("""
        **Purpose**: Detailed program-level analysis with conversion funnels and trend tracking
        
        **Best For**:
        - Monthly program reviews
        - Deep-dive into specific program performance
        - Understanding conversion rates and bottlenecks
        - Identifying areas for improvement
        
        **Four Analysis Tabs**:
        
        **1. Performance Analysis**
        - Funnel visualization (Inquiries → Applications → Admissions → Enrolled)
        - Conversion rates at each stage
        - Performance benchmarks (Inquiry Conversion Rate, Yield Rate, Application Completion Rate)
        - Goal tracking with visual indicators
        
        **2. Trend Analysis**
        - Monthly trends for all metrics
        - Interactive line charts
        - Identify seasonal patterns
        - Spot anomalies or changes
        
        **3. Program Deep Dive**
        - Detailed data table with all metrics
        - Month-by-month breakdown
        - Sortable columns
        - Export capability
        
        **4. Comparative Insights**
        - Compare selected program against all programs
        - Benchmark performance
        - Identify best practices
        - See relative standing
        
        **How to Use**:
        1. **Select Cohort**: Choose your cohort (e.g., Class of 2028)
        2. **Select Program**: Focus on specific program or view "All Programs"
        3. **Navigate Tabs**: Explore different analysis views
        4. **Interpret Metrics**: Use conversion rates to identify improvement areas
        5. **Export Data**: Download tables for detailed analysis
        
        **Pro Tip**: Use the Performance Analysis tab to identify where you're losing applicants in the funnel!
        """)
    
    with tab3:
        st.markdown("""
        **Purpose**: Analyze marketing spend effectiveness and channel performance
        
        **Best For**:
        - Budget planning and allocation
        - ROI analysis and optimization
        - Channel performance comparison
        - Marketing strategy decisions
        
        **Global Filters** (Apply to All Tabs):
        - **Fiscal Year**: Filter by FY25, FY26, etc.
        - **Program**: Focus on specific program or view all
        - **Channel**: Filter by Search, Display, LinkedIn, Meta, YouTube, etc.
        
        **Four Analysis Tabs**:
        
        **1. Overview**
        - Total spend and key ROI metrics
        - Cost per Inquiry (CPI) and Cost per Application (CPA)
        - Spend by program (bar chart with log scale)
        - Spend by channel (pie and bar charts)
        - Quick snapshot of marketing performance
        
        **2. Advanced Analytics**
        - Detailed ROI metrics: CPI, CPA, Cost per Admission, Conversion Rate
        - Spend vs Outcomes Trend: Correlate spend with inquiries, applications, admissions
        - Program-by-program ROI comparison table
        - Deep-dive analysis connecting spend to outcomes
        
        **3. Channel Analytics**
        - Channel-focused performance analysis
        - Spend distribution across channels
        - Monthly trend lines for each channel
        - Performance summary table
        
        **4. Incremental Notes**
        - Document campaign changes and special events
        - Track performance anomalies
        - Searchable notes database
        - Historical context for data analysis
        
        **Key Metrics Explained**:
        - **CPI (Cost per Inquiry)**: Marketing spend ÷ Number of inquiries
        - **CPA (Cost per Application)**: Marketing spend ÷ Number of applications
        - **CPAd (Cost per Admission)**: Marketing spend ÷ Number of admissions
        - **Conversion Rate**: (Applications ÷ Inquiries) × 100
        
        **Pro Tip**: Use the Advanced Analytics tab to justify marketing budget increases with ROI data!
        """)
    
    with tab4:
        st.markdown("""
        **Purpose**: Intelligent marketing insights with three focused analysis tools for data-driven decision making
        
        **Best For**:
        - Identifying top-performing marketing channels with ROI forecasting
        - Discovering optimal timing for channel investments with seasonal intelligence
        - Getting data-driven budget distribution recommendations
        - Making strategic marketing decisions based on effectiveness data
        
        **Three Analysis Sub-Tabs**:
        
        **1. Channel Performance**
        - **Investment Filters**: Set monthly investment amount ($1,000-$50,000) and duration (1-12 months)
        - **Top 3 Channel Forecasts**: Clean white cards showing:
          - Channel ranking by effectiveness (#1, #2, #3)
          - Monthly forecast, total forecast, ROI, and confidence percentage
          - Color-coded recommendations (Recommended/Consider/Caution)
        - **Channel Comparison Table**: Complete performance breakdown with efficiency, effectiveness scores, and ratings
        - **Professional Layout**: Everything contained within clean white tiles with subtle shadows
        
        **2. Timing Intelligence**
        - **Channel-Timing Matrix**: Interactive heatmap showing effectiveness by channel and month
        - **Investment Filters**: Monthly investment amount ($1,000-$25,000) and forecast period (3-12 months)
        - **Top 5 Opportunities**: Clean white cards displaying:
          - Channel and month combinations ranked by effectiveness
          - Seasonal badges (Peak Season, High Season) for optimal timing
          - Expected outcomes prominently displayed
          - Investment recommendations with forecasted results
        - **Seasonal Analysis**: Identifies peak periods (Jan-Mar: 1.2x, Sep-Oct: 1.1x multipliers)
        
        **3. Budget Allocation**
        - **Budget Filters**: Total budget ($5,000-$500,000) and planning period (3-12 months)
        - **Single Generate Button**: "Generate Budget Allocation" creates optimized recommendations
        - **Results Display**: After generation shows:
          - Summary metrics (Total Allocated, Expected Outcomes, Average ROI)
          - Detailed allocation table by channel and best month
          - Key recommendations with strategic insights
        - **Optimization Logic**: Budget distributed proportionally based on effectiveness scores
        
        **Key Features**:
        - **Clean Interface**: Streamlined design with direct access to filters and functionality
        - **Professional Cards**: White tiles with subtle shadows, no borders, everything contained within
        - **Effectiveness Scoring**: Composite metrics combining efficiency, consistency, and attribution
        - **Real-time Analysis**: Recommendations update instantly when filters change
        - **Seasonal Intelligence**: Automatic detection of peak performance periods
        - **ROI Forecasting**: Expected return calculations with confidence levels
        
        **How to Use Each Sub-Tab**:
        
        **Channel Performance Workflow**:
        1. Set your monthly investment amount and duration
        2. Review the top 3 channels in clean white cards
        3. Compare metrics: forecast, ROI, confidence, and recommendations
        4. Analyze the comprehensive comparison table
        5. Focus budget on "Recommended" channels with high effectiveness scores
        
        **Timing Intelligence Workflow**:
        1. Analyze the heatmap to identify green cells (high effectiveness periods)
        2. Set investment parameters for timing analysis
        3. Review top 5 month-channel opportunities in white cards
        4. Note seasonal indicators and expected outcomes
        5. Schedule campaigns during peak effectiveness periods
        
        **Budget Allocation Workflow**:
        1. Enter total marketing budget and planning timeframe
        2. Click "Generate Budget Allocation" for optimization
        3. Review summary metrics and allocation breakdown
        4. Read key recommendations for strategic insights
        5. Implement data-driven budget distribution
        
        **Understanding the Metrics**:
        - **Effectiveness Score**: Composite metric (0-1 scale) combining efficiency and consistency
        - **ROI**: Expected return multiplier (>2.0x excellent, 1.5-2.0x good, <1.0x below breakeven)
        - **Confidence**: Prediction reliability (70-100% high, 50-70% moderate, <50% lower)
        - **Seasonal Multipliers**: Peak Season (1.2x), High Season (1.1x), Standard (1.0x)
        
        **Data Requirements**:
        - **Minimum**: 6+ months of admissions and marketing data with overlapping periods
        - **Optimal**: 12+ months for better seasonal pattern detection
        - **Quality**: Complete records across all channels and months for reliable insights
        
        **Best Practices**:
        - **Channel Performance**: Focus on channels with high consistency scores, test different investment scenarios
        - **Timing Intelligence**: Plan campaigns 2-3 months in advance, allocate extra budget to peak seasons
        - **Budget Allocation**: Run multiple scenarios, align with strategic priorities, update quarterly
        - **General**: Combine insights from all three tools for comprehensive marketing strategy
        
        **Professional Interface Design**:
        - **No Unnecessary Titles**: Direct access to functionality without space-wasting headers
        - **Clean White Cards**: All information contained within professional tiles
        - **Subtle Shadows**: Modern design with depth but no borders
        - **Consistent Styling**: Maroon color scheme (#500000) throughout
        - **Responsive Layout**: Works seamlessly across desktop and mobile devices
        
        **Pro Tips**:
        - Use Channel Performance to identify your best channels, then use Timing Intelligence to optimize when to invest in them
        - Combine seasonal insights with channel effectiveness for maximum impact
        - Test Budget Allocation scenarios with different total budgets to understand sensitivity
        - Track actual vs. predicted outcomes to validate model accuracy
        - Review and update recommendations monthly as new data becomes available
        """)
    
    
    with tab5:
        st.markdown("""
        **Purpose**: Access and export raw data for custom analysis
        
        **Best For**:
        - Creating custom reports
        - Exporting data to Excel/PowerPoint
        - Detailed data validation
        - Ad-hoc analysis
        
        **Seven Database Tables**:
        1. **Admissions Matrix**: All admissions metrics by cohort, program, and date
        2. **Inquiry Sources**: Where inquiries come from (future use)
        3. **Marketing Campaigns**: Campaign-level tracking (future use)
        4. **Marketing Spend**: Monthly spend by program and channel
        5. **Marketing Spend Totals**: Aggregated spend metrics
        6. **Metadata Programs**: Program codes and names
        7. **SQLite Sequence**: System table
        
        **Advanced Features**:
        - **Column Selection**: Choose which columns to display
        - **Row Limits**: View 10, 25, 50, 100, 500, or all rows
        - **Sort**: Click column headers to sort ascending/descending
        - **Search**: Filter across all columns with text search
        - **Statistics**: Quick stats for numeric columns
        - **Export**: Download filtered data as CSV
        
        **Pro Tip**: Export data to Excel for custom pivot tables and charts!
        """)
    
    with tab6:
        st.markdown("""
        **Purpose**: Natural language interface to query and explore your analytics data using AI
        
        **Best For**:
        - Quick data lookups without navigating pages
        - Asking questions in plain English
        - Getting instant answers about metrics
        - Learning how to navigate the platform
        - Exploring data conversationally
        
        **How to Use**:
        1. **Sign In**: Must be authenticated with Google OAuth to access
        2. **Ask Questions**: Type your question in natural language
        3. **Get Answers**: AI generates SQL queries and returns results
        4. **Follow Up**: Ask related questions to dig deeper
        5. **Rate Responses**: Use 👍/👎 to help improve accuracy
        
        **What You Can Ask**:
        
        **Data Queries**:
        - "How many MBA applications in 2026?"
        - "Show me inquiries for MS ACCT"
        - "What's the conversion rate for all programs?"
        - "Compare enrollments between MBA and MS MKTG"
        - "What's the cost per inquiry for each program?"
        
        **Navigation Questions**:
        - "Where can I see program comparisons?"
        - "How do I analyze marketing ROI?"
        - "Which page shows forecasts?"
        - "Where can I export data?"
        
        **Help Questions**:
        - "What metrics are available?"
        - "How do I filter by cohort?"
        - "What's the difference between admissions offered and accepted?"
        - "How is anticipated cohort size calculated?"
        
        **Key Features**:
        - **Conversation Memory**: Remembers context from previous messages
        - **Smart Query Processing**: Understands business terms and abbreviations
        - **Rate Limiting**: 10 queries per minute per user
        - **Feedback System**: Rate responses to improve accuracy
        - **Chat History**: View and search past conversations
        - **Privacy Controls**: GDPR-compliant data management
        
        **Pro Tip**: Be specific about programs and time periods for best results!
        """)
    

    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Common Workflows - centered with responsive grid
    st.markdown("<h3 style='text-align: center; color: #500000;'>Common Workflows</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="workflows-grid">
        <div style="background: #f0f8ff; padding: 20px; border-radius: 8px; display: flex; flex-direction: column;">
            <h4 style="color: #500000; margin: 0 0 15px 0;">Weekly Check-In</h4>
            <ol style="font-size: 14px; line-height: 1.8; color: #495057; flex: 1;">
                <li>Open <strong>Executive Dashboard</strong></li>
                <li>Select current cohort</li>
                <li>Review key metrics vs. goals</li>
                <li>Check program comparison</li>
                <li>Note programs needing attention</li>
                <li>Share screenshot with team</li>
            </ol>
        </div>
        <div style="background: #fff8f0; padding: 20px; border-radius: 8px; display: flex; flex-direction: column;">
            <h4 style="color: #500000; margin: 0 0 15px 0;">Budget Planning</h4>
            <ol style="font-size: 14px; line-height: 1.8; color: #495057; flex: 1;">
                <li>Open <strong>Marketing Analysis</strong></li>
                <li>Go to Advanced Analytics</li>
                <li>Review CPI, CPA, ROI metrics</li>
                <li>Check Channel Analytics</li>
                <li>Identify best channels</li>
                <li>Export for budget proposal</li>
            </ol>
        </div>
        <div style="background: #f8f0ff; padding: 20px; border-radius: 8px; display: flex; flex-direction: column;">
            <h4 style="color: #500000; margin: 0 0 15px 0;">Marketing Intelligence</h4>
            <ol style="font-size: 14px; line-height: 1.8; color: #495057; flex: 1;">
                <li>Open <strong>Predictive Analytics</strong></li>
                <li>Review Channel Performance cards</li>
                <li>Analyze Timing Intelligence matrix</li>
                <li>Generate Budget Allocation</li>
                <li>Review ROI forecasts</li>
                <li>Export recommendations</li>
            </ol>
        </div>
        <div style="background: #f0fff0; padding: 20px; border-radius: 8px; display: flex; flex-direction: column;">
            <h4 style="color: #500000; margin: 0 0 15px 0;">Monthly Review</h4>
            <ol style="font-size: 14px; line-height: 1.8; color: #495057; flex: 1;">
                <li>Open <strong>Director's Deep Dive</strong></li>
                <li>Select cohort and program</li>
                <li>Review Performance Analysis</li>
                <li>Check Trend Analysis</li>
                <li>Use Program Deep Dive</li>
                <li>Export data tables</li>
            </ol>
        </div>
        <div style="background: #fff0f8; padding: 20px; border-radius: 8px; display: flex; flex-direction: column;">
            <h4 style="color: #500000; margin: 0 0 15px 0;">Annual Planning</h4>
            <ol style="font-size: 14px; line-height: 1.8; color: #495057; flex: 1;">
                <li>Open <strong>Director's Deep Dive</strong></li>
                <li>Compare current vs. previous cohort</li>
                <li>Review conversion rate trends</li>
                <li>Identify growth opportunities</li>
                <li>Set goals based on trends</li>
                <li>Export comparison data</li>
            </ol>
        </div>
        <div style="background: #fffaf0; padding: 20px; border-radius: 8px; display: flex; flex-direction: column;">
            <h4 style="color: #500000; margin: 0 0 15px 0;">Marketing Optimization</h4>
            <ol style="font-size: 14px; line-height: 1.8; color: #495057; flex: 1;">
                <li>Open <strong>Predictive Analytics</strong></li>
                <li>Go to Channel Performance</li>
                <li>Review top 3 channel forecasts</li>
                <li>Check Timing Intelligence heatmap</li>
                <li>Use Budget Allocation tool</li>
                <li>Implement recommendations</li>
            </ol>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tips & Best Practices - centered with responsive grid
    st.markdown("<h3 style='text-align: center; color: #500000;'>Tips & Best Practices</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="tips-grid">
        <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; display: flex; flex-direction: column;">
            <h4 style="color: #500000; margin: 0 0 15px 0; text-align: center;">Do's</h4>
            <ul style="font-size: 14px; line-height: 1.8; color: #495057; flex: 1;">
                <li>Check data regularly (weekly minimum)</li>
                <li>Compare year-over-year trends</li>
                <li>Export data for presentations</li>
                <li>Use filters to focus analysis</li>
                <li>Hover over charts for exact values</li>
                <li>Share insights with your team</li>
                <li>Track marketing ROI monthly</li>
            </ul>
        </div>
        <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; display: flex; flex-direction: column;">
            <h4 style="color: #500000; margin: 0 0 15px 0; text-align: center;">Don'ts</h4>
            <ul style="font-size: 14px; line-height: 1.8; color: #495057; flex: 1;">
                <li>Don't ignore declining trends</li>
                <li>Don't compare incomplete data</li>
                <li>Don't make decisions on single data points</li>
                <li>Don't forget to check "Last Updated" date</li>
                <li>Don't overlook small programs</li>
                <li>Don't skip the "How to Use" guides</li>
                <li>Don't hesitate to export and explore</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Data Understanding - using CSS Grid with simple responsive breakpoints
    st.markdown("<h3 style='text-align: center; color: #500000;'>Understanding Your Data</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <style>
    .data-understanding-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin: 20px 0;
    }
    
    /* Mobile/Tablet: Stack vertically (one below another) */
    @media screen and (max-width: 1200px) {
        .data-understanding-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    
    <div class="data-understanding-grid">
        <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; display: flex; flex-direction: column;">
            <h4 style="color: #500000; margin: 0 0 15px 0; text-align: center;">Data Coverage</h4>
            <ul style="font-size: 14px; line-height: 1.8; color: #495057; margin-bottom: 0; flex: 1;">
                <li><strong>Admissions Data</strong>: January 2024 - December 2025 (2,037 records)</li>
                <li><strong>Marketing Data</strong>: September 2024 - June 2025 (FY25 Year 1)</li>
                <li><strong>Programs</strong>: MBA, MS ACCT, MS ENLD, MS HRM, MS MISY, MS MKTG, MS SPBA</li>
                <li><strong>Cohorts</strong>: Class of 2026, 2027, 2028</li>
            </ul>
        </div>
        <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; display: flex; flex-direction: column;">
            <h4 style="color: #500000; margin: 0 0 15px 0; text-align: center;">Important Notes</h4>
            <ul style="font-size: 14px; line-height: 1.8; color: #495057; margin-bottom: 0; flex: 1;">
                <li><strong>Cumulative Data</strong>: All metrics are cumulative within a cohort year</li>
                <li><strong>Monthly Reports</strong>: Dates represent the last day of the reporting month</li>
                <li><strong>Missing Data</strong>: Blank values indicate data not yet available (not zero)</li>
                <li><strong>Campaign Matrix</strong>: "- NA -" means campaign was not active for that program/month</li>
                <li><strong>Marketing Spend</strong>: "No Ad Spend" entries are treated as NULL (not zero)</li>
            </ul>
        </div>
        <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; display: flex; flex-direction: column;">
            <h4 style="color: #500000; margin: 0 0 15px 0; text-align: center;">Key Metrics Definitions</h4>
            <ul style="font-size: 14px; line-height: 1.8; color: #495057; margin-bottom: 0; flex: 1;">
                <li><strong>Inquiries</strong>: Initial interest expressed (top of funnel)</li>
                <li><strong>Applications</strong>: Complete applications received</li>
                <li><strong>Admissions Offered</strong>: Offers extended to applicants</li>
                <li><strong>Admissions Accepted</strong>: Offers accepted by applicants</li>
                <li><strong>Enrolled</strong>: Students who have enrolled in the program</li>
                <li><strong>Anticipated Cohort Size</strong>: Expected final enrollment (most important metric!)</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Troubleshooting - with responsive grid
    st.markdown("<h3 style='text-align: center; color: #500000;'>Troubleshooting</h3>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="troubleshooting-grid">
        <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; height: 400px; display: flex; flex-direction: column;">
            <h4 style="color: #500000; margin: 0 0 20px 0; text-align: center;">Common Issues</h4>
            <div style="font-size: 14px; line-height: 1.8; color: #495057; overflow-y: auto; flex: 1; padding-right: 10px;">
                <p style="margin-bottom: 15px;">
                    <strong>Q: Why is my data not showing?</strong><br>
                    <span style="color: #666;">A: Check the 'Last Updated' date in the sidebar. Data may need to be refreshed.</span>
                </p>
                <p style="margin-bottom: 15px;">
                    <strong>Q: Why do some metrics show 'N/A'?</strong><br>
                    <span style="color: #666;">A: This means there is no comparison data available.</span>
                </p>
                <p style="margin-bottom: 15px;">
                    <strong>Q: Why are some programs missing?</strong><br>
                    <span style="color: #666;">A: Programs may not have data for the selected time period or cohort.</span>
                </p>
                <p style="margin-bottom: 15px;">
                    <strong>Q: Charts not loading?</strong><br>
                    <span style="color: #666;">A: Try refreshing the page or clearing your browser cache.</span>
                </p>
                <p style="margin-bottom: 15px;">
                    <strong>Q: How do I export data?</strong><br>
                    <span style="color: #666;">A: Look for the "Download CSV" button below each data table.</span>
                </p>
                <p style="margin-bottom: 15px;">
                    <strong>Q: Can I compare programs across cohorts?</strong><br>
                    <span style="color: #666;">A: Yes, use the Director's Deep Dive page to compare programs and analyze trends across different cohorts.</span>
                </p>
                <p style="margin-bottom: 0;">
                    <strong>Q: Why are forecasts showing errors?</strong><br>
                    <span style="color: #666;">A: Ensure you have at least 12 months of historical data for reliable predictions.</span>
                </p>
            </div>
        </div>
        <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; height: 400px; display: flex; flex-direction: column;">
            <h4 style="color: #500000; margin: 0 0 20px 0; text-align: center;">Need Help?</h4>
            <div style="font-size: 14px; line-height: 1.8; color: #495057; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                <p style="margin-bottom: 25px; text-align: center;">
                    <strong style="font-size: 16px;">Contact:</strong><br>
                    <span style="font-size: 15px;">Tirth Shah</span><br>
                    <a href="mailto:tirth.shah@tamu.edu" style="color: #500000; text-decoration: none;">tirth.shah@tamu.edu</a>
                </p>
                <p style="margin-bottom: 25px; text-align: center;">
                    <strong style="font-size: 16px;">Platform Version:</strong><br>
                    <span style="font-size: 15px;">{VERSION}</span>
                </p>
                <p style="margin-bottom: 0; text-align: center;">
                    <strong style="font-size: 16px;">Last Updated:</strong><br>
                    <span style="font-size: 15px;">{LAST_UPDATED}</span>
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Contact & Feedback Form
    st.markdown("<h3 style='text-align: center; color: #500000;'>Contact & Feedback</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #495057; margin-bottom: 30px;'>Have a question, found a bug, or want to suggest an improvement? We'd love to hear from you!</p>", unsafe_allow_html=True)
    
    # Create the form
    with st.form("contact_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name *", placeholder="Your full name")
            email = st.text_input("Email *", placeholder="your.email@example.com")
        
        with col2:
            phone = st.text_input("Phone Number", placeholder="(123) 456-7890")
            feedback_type = st.selectbox(
                "Type *",
                ["Report a Bug", "Suggest Improvement", "Ask a Question", "General Feedback", "Other"]
            )
        
        # Multi-select for pages
        pages_affected = st.multiselect(
            "Pages Affected (optional)",
            ["Executive Dashboard", "Director's Deep Dive", "Marketing Analysis", 
             "Data Explorer", "Predictive Analytics", "AI Chat Assistant", "Documentation", "All Pages", "Other"],
            help="Select the page(s) related to your feedback"
        )
        
        subject = st.text_input("Subject *", placeholder="Brief description of your feedback")
        message = st.text_area("Message *", placeholder="Please provide details...", height=150)
        
        submitted = st.form_submit_button("Send Feedback", use_container_width=True)
        
        if submitted:
            # Validate required fields
            if not name or not email or not subject or not message:
                st.error("Please fill in all required fields (marked with *)")
            elif "@" not in email:
                st.error("Please enter a valid email address")
            else:
                # Send email using Resend API
                try:
                    import resend
                    
                    # Try to get secrets from Streamlit Cloud first, then fall back to local config
                    try:
                        # Streamlit Cloud secrets
                        RESEND_API_KEY = st.secrets["RESEND_API_KEY"]
                        CONTACT_EMAIL = st.secrets["CONTACT_EMAIL"]
                        FROM_EMAIL = st.secrets.get("FROM_EMAIL", "onboarding@resend.dev")
                    except (KeyError, FileNotFoundError):
                        # Local development - use config_secrets.py
                        from config_secrets import RESEND_API_KEY, CONTACT_EMAIL, FROM_EMAIL
                    
                    resend.api_key = RESEND_API_KEY
                    
                    # Format pages list
                    pages_list = ", ".join(pages_affected) if pages_affected else "Not specified"
                    
                    # Create email content
                    email_html = f"""
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                            <h2 style="color: #500000; border-bottom: 2px solid #C5A572; padding-bottom: 10px;">
                                New Feedback: {feedback_type}
                            </h2>
                            
                            <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                                <p style="margin: 5px 0;"><strong>From:</strong> {name}</p>
                                <p style="margin: 5px 0;"><strong>Email:</strong> {email}</p>
                                <p style="margin: 5px 0;"><strong>Phone:</strong> {phone if phone else "Not provided"}</p>
                                <p style="margin: 5px 0;"><strong>Type:</strong> {feedback_type}</p>
                                <p style="margin: 5px 0;"><strong>Pages:</strong> {pages_list}</p>
                            </div>
                            
                            <div style="margin: 20px 0;">
                                <h3 style="color: #500000; margin-bottom: 10px;">Subject:</h3>
                                <p style="background: #fff; padding: 10px; border-left: 3px solid #500000;">{subject}</p>
                            </div>
                            
                            <div style="margin: 20px 0;">
                                <h3 style="color: #500000; margin-bottom: 10px;">Message:</h3>
                                <p style="background: #fff; padding: 15px; border: 1px solid #e0e0e0; border-radius: 5px; white-space: pre-wrap;">{message}</p>
                            </div>
                            
                            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0; font-size: 12px; color: #666;">
                                <p>Sent from Mays Analytics Platform v{VERSION}</p>
                                <p>Timestamp: {LAST_UPDATED}</p>
                            </div>
                        </div>
                    </body>
                    </html>
                    """
                    
                    # Send email
                    params = {
                        "from": FROM_EMAIL,
                        "to": [CONTACT_EMAIL],
                        "subject": f"[Mays Analytics] {feedback_type}: {subject}",
                        "html": email_html,
                        "reply_to": email
                    }
                    
                    response = resend.Emails.send(params)
                    
                    st.success("✅ Thank you! Your feedback has been sent successfully. We'll get back to you soon!")
                    
                except ImportError:
                    st.error("Email service is not configured. Please contact tirth.shah@tamu.edu directly.")
                except Exception as e:
                    st.error(f"Failed to send feedback. Please email tirth.shah@tamu.edu directly.")
                    # Log error for debugging (don't show to user)
                    print(f"Email error: {str(e)}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Footer
    st.markdown(f"""
    <div style="text-align: center;
                padding: 30px;
                background: linear-gradient(135deg, #500000 0%, #700000 100%);
                border-radius: 10px;
                color: white;
                margin-top: 30px;">
        <h3 style="color: white; margin: 0 0 15px 0;">Mays Flex Online Programs</h3>
        <p style="margin: 0; font-size: 14px; opacity: 0.9;">
            Analytics Platform for Data-Driven Decisions
        </p>
        <p style="margin: 15px 0 0 0; font-size: 12px; opacity: 0.7;">
            © 2026 Texas A&M Mays Business School | {VERSION_FULL}
        </p>
    </div>
    """, unsafe_allow_html=True)
