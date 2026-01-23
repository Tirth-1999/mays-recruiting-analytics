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
    
    # Key Questions This Platform Answers - centered header
    st.markdown("<h3 style='text-align: center; color: #500000;'>Key Questions This Platform Answers</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; height: 100%;">
            <h4 style="color: #500000; margin: 0 0 15px 0; text-align: center;">Enrollment Questions</h4>
            <ul style="font-size: 14px; line-height: 1.8; color: #495057;">
                <li>Are we on track to meet our cohort size goals?</li>
                <li>Which programs are over/under-performing?</li>
                <li>How do conversion rates compare to last year?</li>
                <li>Where are we losing applicants in the funnel?</li>
                <li>What's our inquiry-to-enrollment conversion rate?</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; height: 100%;">
            <h4 style="color: #500000; margin: 0 0 15px 0; text-align: center;">Marketing Questions</h4>
            <ul style="font-size: 14px; line-height: 1.8; color: #495057;">
                <li>What's our cost per inquiry and application?</li>
                <li>Which marketing channels deliver the best ROI?</li>
                <li>How should we allocate next year's budget?</li>
                <li>Are we spending efficiently across programs?</li>
                <li>What's the trend in our marketing effectiveness?</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; height: 100%;">
            <h4 style="color: #500000; margin: 0 0 15px 0; text-align: center;">Forecasting Questions</h4>
            <ul style="font-size: 14px; line-height: 1.8; color: #495057;">
                <li>What will our enrollment numbers be next year?</li>
                <li>Which marketing channels should we invest in?</li>
                <li>When is the best time to run campaigns?</li>
                <li>How should we distribute our marketing budget?</li>
                <li>Are our predictions accurate and reliable?</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Custom Chrome-style tab styling
    st.markdown("""
    <style>
    /* Chrome-style tabs for Help page */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        justify-content: center;
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
    </style>
    """, unsafe_allow_html=True)
    
    # Page-by-Page Guide with Chrome-style tabs
    st.markdown("<h3 style='text-align: center; color: #500000;'>Page-by-Page Guide</h3>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Home",
        "📊 Executive",
        "🔄 Compare",
        "📈 Marketing",
        "🔮 Forecasting",
        "💾 Database"
    ])
    
    with tab1:
        st.markdown("""
        **Purpose**: Quick overview of current cohort performance and goal tracking
        
        **Best For**:
        - Daily/weekly check-ins
        - Quick status updates
        - Identifying programs needing attention
        - Sharing high-level metrics with leadership
        
        **How to Use**:
        1. **Select Cohort**: Choose the cohort you want to analyze (e.g., Class of 2028)
        2. **Review Key Metrics**: See total inquiries, applications, admissions, and anticipated cohort size
        3. **Check Goal Progress**: Visual indicators show if you're on track (green), at risk (yellow), or behind (red)
        4. **Compare Programs**: Bar chart shows performance across all programs
        5. **Analyze Trends**: Line chart displays monthly progression
        6. **Export Data**: Download charts and tables for presentations
        
        **Key Features**:
        - **Goal Tracking**: Set and monitor cohort size goals
        - **Program Comparison**: See which programs are over/under-performing
        - **Trend Visualization**: Understand monthly patterns
        - **Quick Insights**: AI-generated insights highlight important trends
        
        **Pro Tip**: Use this page for your weekly team meetings to quickly show progress!
        """)
    
    with tab2:
        st.markdown("""
        **Purpose**: Deep-dive analysis into specific programs and cohorts with advanced metrics
        
        **Best For**:
        - Monthly reviews
        - Program-specific analysis
        - Understanding conversion rates
        - Identifying bottlenecks in the funnel
        
        **Four Analysis Tabs**:
        
        **1. Performance Analysis Tab**
        - Funnel visualization (Inquiries → Applications → Admissions → Enrolled)
        - Conversion rates at each stage
        - Performance benchmarks (Inquiry Conversion Rate, Yield Rate, Application Completion Rate)
        - Goal tracking with visual indicators
        
        **2. Trend Analysis Tab**
        - Monthly trends for all metrics
        - Interactive line charts
        - Identify seasonal patterns
        - Spot anomalies or changes
        
        **3. Program Deep Dive Tab**
        - Detailed data table with all metrics
        - Month-by-month breakdown
        - Sortable columns
        - Export capability
        
        **4. Comparative Insights Tab**
        - Compare selected program against all programs
        - Benchmark performance
        - Identify best practices
        - See relative standing
        
        **How to Use**:
        1. **Select Cohort**: Choose your cohort (e.g., Class of 2028)
        2. **Select Program**: Focus on specific program or view "All Programs"
        3. **Navigate Tabs**: Explore different analysis views
        4. **Interpret Metrics**: Use the conversion rates to identify improvement areas
        5. **Export Data**: Download tables for detailed analysis
        
        **Pro Tip**: Use the Performance Analysis tab to identify where you're losing applicants in the funnel!
        """)
    
    with tab3:
        st.markdown("""
        **Purpose**: Year-over-year comparison to track growth and identify trends
        
        **Best For**:
        - Annual planning
        - Board presentations
        - Identifying growth opportunities
        - Benchmarking performance
        
        **How to Use**:
        1. **Select Primary Cohort**: Choose your main cohort (e.g., Class of 2028)
        2. **Select Comparison Cohort**: Choose the cohort to compare against (e.g., Class of 2027)
        3. **Filter by Program**: Focus on specific program or view all
        4. **Review Comparison Table**: See all metrics side-by-side with % change
        5. **Explore Time Series**: Click metric selectors to see trends over time
        6. **Export Data**: Download comparison tables for presentations
        
        **Understanding the Statistics**:
        - **Absolute Change**: Simple difference between cohorts (Primary - Comparison)
        - **% Change**: Percentage growth or decline
        - **Variance**: Measure of spread between the two values
        - **Standard Deviation**: How much the values differ from their average
        - **Coefficient of Variation**: Relative variability (useful for comparing different metrics)
        - **Performance Indicator**: Growth, Decline, or Stable
        
        **Smart Features**:
        - Automatically excludes metrics where both cohorts have zero values
        - Shows "N/A" for % change when comparison cohort has no data
        - Descriptive messages for edge cases (e.g., "New Metric - Strong Growth")
        
        **Pro Tip**: Use this for annual reviews to show leadership how programs are trending!
        """)
    
    with tab4:
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
        
        **1. Overview Tab**
        - Total spend and key ROI metrics
        - Cost per Inquiry (CPI) and Cost per Application (CPA)
        - Spend by program (bar chart with log scale)
        - Spend by channel (pie and bar charts)
        - Quick snapshot of marketing performance
        
        **2. Advanced Analytics Tab**
        - Detailed ROI metrics: CPI, CPA, Cost per Admission, Conversion Rate
        - Spend vs Outcomes Trend: Correlate spend with inquiries, applications, admissions
        - Program-by-program ROI comparison table
        - Deep-dive analysis connecting spend to outcomes
        
        **3. Channel Analytics Tab**
        - Channel-focused performance analysis
        - Spend distribution across channels
        - Monthly trend lines for each channel
        - Performance summary table
        
        **4. Incremental Notes Tab**
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
    
    with tab5:
        st.markdown("""
        **Purpose**: AI-powered forecasting and optimization for enrollment planning and marketing strategy
        
        **Best For**:
        - Predicting future inquiries, applications, and enrollments
        - Optimizing marketing channel allocation
        - Identifying best months for marketing campaigns
        - Data-driven budget planning
        - Tracking model accuracy over time
        
        **Five Analysis Tabs**:
        
        **1. Forecasting Tab**
        - **Time Series Predictions**: Forecast inquiries, applications, and enrollments
        - **Confidence Intervals**: 95% confidence ranges for all predictions
        - **Model Selection**: Automatic selection of best model (Prophet, ARIMA, Linear Regression)
        - **Forecast Horizons**: 3, 6, 9, 12, 18, or 24 months ahead
        - **Interactive Charts**: Visualize historical data and future predictions
        
        **2. Channel Optimization Tab**
        - **ROI Analysis**: Identify most effective marketing channels
        - **Effectiveness Scores**: Composite metrics combining ROI, conversion rate, consistency
        - **Performance History**: Track channel performance over time
        - **Recommendations**: Top channels ranked by effectiveness
        - **Data-Driven Decisions**: Allocate budget to highest-performing channels
        
        **3. Timing Analysis Tab**
        - **Seasonal Patterns**: Identify optimal months for marketing investments
        - **Conversion Heatmap**: Visualize patterns across years and months
        - **Timing Recommendations**: Ranked months by effectiveness
        - **Consistency Scores**: Reliability of seasonal patterns
        - **Campaign Planning**: Schedule marketing in high-conversion months
        
        **4. Budget Allocation Tab**
        - **Optimization**: Data-driven budget distribution across programs
        - **Expected Outcomes**: Predicted inquiries, applications, enrollments
        - **Sensitivity Analysis**: Impact of budget changes on outcomes
        - **Constraint Management**: Set minimum/maximum allocations per program
        - **What-If Scenarios**: Test different budget distributions
        
        **5. Model Performance Tab**
        - **Accuracy Tracking**: Monitor prediction accuracy over time
        - **Model Health**: Status indicators (Healthy, Warning, Needs Retraining)
        - **Trend Analysis**: Identify performance degradation
        - **Multiple Models**: Compare Prophet, ARIMA, and Linear Regression
        - **Metrics**: MAPE (Mean Absolute Percentage Error), RMSE, MAE
        
        **How to Use**:
        
        **For Forecasting**:
        1. Select Program to forecast
        2. Select Cohort year (optional)
        3. Select Metric (inquiries, applications, or enrollments)
        4. Select Forecast Horizon (3-24 months)
        5. Click "Generate Forecast"
        6. Review predictions with confidence intervals
        
        **For Channel Optimization**:
        1. Select Program to analyze
        2. Review top performing channels
        3. Check ROI and effectiveness scores
        4. Apply insights to budget allocation
        
        **For Budget Planning**:
        1. Enter Total Budget available
        2. Select Programs to include
        3. Set Constraints (optional min/max per program)
        4. Generate recommended allocation
        5. Review expected outcomes
        6. Test sensitivity with different budgets
        
        **ML Models Explained**:
        - **Prophet**: Best for 24+ months of data, handles seasonality automatically
        - **ARIMA**: Best for 12-24 months of data, statistical forecasting
        - **Linear Regression**: Best for <12 months of data, trend-based forecasting
        - **Automatic Selection**: System chooses best model based on data availability
        
        **Accuracy Thresholds**:
        - **MAPE < 10%**: Excellent accuracy
        - **MAPE 10-15%**: Good accuracy
        - **MAPE > 15%**: Needs attention, consider retraining
        
        **Pro Tips**:
        - Use at least 12 months of historical data for reliable forecasts
        - Review model performance regularly (monthly)
        - Combine channel and timing insights for optimal marketing strategy
        - Test multiple budget scenarios before finalizing allocation
        - Monitor accuracy metrics and retrain models when MAPE > 15%
        """)
    
    with tab6:
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
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Common Workflows - centered
    st.markdown("<h3 style='text-align: center; color: #500000;'>Common Workflows</h3>", unsafe_allow_html=True)
    
    workflow_col1, workflow_col2, workflow_col3 = st.columns(3)
    
    with workflow_col1:
        st.markdown("""
        <div style="background: #f0f8ff; padding: 20px; border-radius: 8px; height: 100%;">
            <h4 style="color: #500000; margin: 0 0 15px 0;">Weekly Check-In</h4>
            <ol style="font-size: 14px; line-height: 1.8; color: #495057;">
                <li>Open <strong>Home Dashboard</strong></li>
                <li>Select current cohort</li>
                <li>Review key metrics vs. goals</li>
                <li>Check program comparison</li>
                <li>Note programs needing attention</li>
                <li>Share screenshot with team</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #f0fff0; padding: 20px; border-radius: 8px; height: 100%;">
            <h4 style="color: #500000; margin: 0 0 15px 0;">Monthly Review</h4>
            <ol style="font-size: 14px; line-height: 1.8; color: #495057;">
                <li>Open <strong>Executive Dive</strong></li>
                <li>Select cohort and program</li>
                <li>Review Performance Analysis</li>
                <li>Check Trend Analysis</li>
                <li>Use Program Deep Dive</li>
                <li>Export data tables</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with workflow_col2:
        st.markdown("""
        <div style="background: #fff8f0; padding: 20px; border-radius: 8px; height: 100%;">
            <h4 style="color: #500000; margin: 0 0 15px 0;">Budget Planning</h4>
            <ol style="font-size: 14px; line-height: 1.8; color: #495057;">
                <li>Open <strong>Marketing Analysis</strong></li>
                <li>Go to Advanced Analytics</li>
                <li>Review CPI, CPA, ROI metrics</li>
                <li>Check Channel Analytics</li>
                <li>Identify best channels</li>
                <li>Export for budget proposal</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #fff0f8; padding: 20px; border-radius: 8px; height: 100%;">
            <h4 style="color: #500000; margin: 0 0 15px 0;">Annual Planning</h4>
            <ol style="font-size: 14px; line-height: 1.8; color: #495057;">
                <li>Open <strong>Comparison Tool</strong></li>
                <li>Compare current vs. previous year</li>
                <li>Review % change for metrics</li>
                <li>Identify growth opportunities</li>
                <li>Set goals based on trends</li>
                <li>Export comparison table</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with workflow_col3:
        st.markdown("""
        <div style="background: #f8f0ff; padding: 20px; border-radius: 8px; height: 100%;">
            <h4 style="color: #500000; margin: 0 0 15px 0;">Enrollment Forecasting</h4>
            <ol style="font-size: 14px; line-height: 1.8; color: #495057;">
                <li>Open <strong>Forecasting</strong></li>
                <li>Select program and metric</li>
                <li>Choose forecast horizon</li>
                <li>Generate predictions</li>
                <li>Review confidence intervals</li>
                <li>Export forecast data</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #fffaf0; padding: 20px; border-radius: 8px; height: 100%;">
            <h4 style="color: #500000; margin: 0 0 15px 0;">Marketing Optimization</h4>
            <ol style="font-size: 14px; line-height: 1.8; color: #495057;">
                <li>Open <strong>Forecasting</strong></li>
                <li>Go to Channel Optimization</li>
                <li>Review effectiveness scores</li>
                <li>Check Timing Analysis</li>
                <li>Use Budget Allocation tool</li>
                <li>Implement recommendations</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tips & Best Practices - centered
    st.markdown("<h3 style='text-align: center; color: #500000;'>Tips & Best Practices</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: white; padding: 25px; border-radius: 8px; border: 2px solid #C5A572;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div>
                <h4 style="color: #500000; margin: 0 0 10px 0;">Do's</h4>
                <ul style="font-size: 14px; line-height: 1.8; color: #495057;">
                    <li>Check data regularly (weekly minimum)</li>
                    <li>Compare year-over-year trends</li>
                    <li>Export data for presentations</li>
                    <li>Use filters to focus analysis</li>
                    <li>Hover over charts for exact values</li>
                    <li>Share insights with your team</li>
                    <li>Track marketing ROI monthly</li>
                </ul>
            </div>
            <div>
                <h4 style="color: #500000; margin: 0 0 10px 0;">Don'ts</h4>
                <ul style="font-size: 14px; line-height: 1.8; color: #495057;">
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
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Data Understanding - using separate divs with consistent styling
    st.markdown("<h3 style='text-align: center; color: #500000;'>Understanding Your Data</h3>", unsafe_allow_html=True)
    
    # Data Coverage
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                padding: 25px;
                border-radius: 8px 8px 0 0;
                border: 1px solid #e0e0e0;
                border-bottom: none;">
        <h4 style="color: #500000; margin: 0 0 15px 0;">Data Coverage</h4>
        <ul style="font-size: 14px; line-height: 1.8; color: #495057; margin-bottom: 0;">
            <li><strong>Admissions Data</strong>: January 2024 - December 2025 (2,037 records)</li>
            <li><strong>Marketing Data</strong>: September 2024 - June 2025 (FY25 Year 1)</li>
            <li><strong>Programs</strong>: MBA, MS ACCT, MS ENLD, MS HRM, MS MISY, MS MKTG, MS SPBA</li>
            <li><strong>Cohorts</strong>: Class of 2026, 2027, 2028</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Important Notes
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                padding: 25px;
                border-left: 1px solid #e0e0e0;
                border-right: 1px solid #e0e0e0;">
        <h4 style="color: #500000; margin: 0 0 15px 0;">Important Notes</h4>
        <ul style="font-size: 14px; line-height: 1.8; color: #495057; margin-bottom: 0;">
            <li><strong>Cumulative Data</strong>: All metrics are cumulative within a cohort year</li>
            <li><strong>Monthly Reports</strong>: Dates represent the last day of the reporting month</li>
            <li><strong>Missing Data</strong>: Blank values indicate data not yet available (not zero)</li>
            <li><strong>Campaign Matrix</strong>: "- NA -" means campaign was not active for that program/month</li>
            <li><strong>Marketing Spend</strong>: "No Ad Spend" entries are treated as NULL (not zero)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics Definitions
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                padding: 25px;
                border-radius: 0 0 8px 8px;
                border: 1px solid #e0e0e0;
                border-top: none;">
        <h4 style="color: #500000; margin: 0 0 15px 0;">Key Metrics Definitions</h4>
        <ul style="font-size: 14px; line-height: 1.8; color: #495057; margin-bottom: 0;">
            <li><strong>Inquiries</strong>: Initial interest expressed (top of funnel)</li>
            <li><strong>Applications</strong>: Complete applications received</li>
            <li><strong>Admissions Offered</strong>: Offers extended to applicants</li>
            <li><strong>Admissions Accepted</strong>: Offers accepted by applicants</li>
            <li><strong>Enrolled</strong>: Students who have enrolled in the program</li>
            <li><strong>Anticipated Cohort Size</strong>: Expected final enrollment (most important metric!)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Troubleshooting - with proper boxes
    st.markdown("<h3 style='text-align: center; color: #500000;'>Troubleshooting</h3>", unsafe_allow_html=True)
    
    trouble_col1, trouble_col2 = st.columns(2)
    
    with trouble_col1:
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; min-height: 300px;">
            <h4 style="color: #500000; margin: 0 0 20px 0; text-align: center;">Common Issues</h4>
            <div style="font-size: 14px; line-height: 1.8; color: #495057;">
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
                <p style="margin-bottom: 0;">
                    <strong>Q: Charts not loading?</strong><br>
                    <span style="color: #666;">A: Try refreshing the page or clearing your browser cache.</span>
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with trouble_col2:
        st.markdown(f"""
        <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; min-height: 300px;">
            <h4 style="color: #500000; margin: 0 0 20px 0; text-align: center;">Need Help?</h4>
            <div style="font-size: 14px; line-height: 1.8; color: #495057;">
                <p style="margin-bottom: 20px;">
                    <strong>Contact:</strong><br>
                    Tirth Shah<br>
                    tirth.shah@tamu.edu
                </p>
                <p style="margin-bottom: 0;">
                    <strong>Platform Version:</strong> {VERSION}<br>
                    <strong>Last Updated:</strong> {LAST_UPDATED}
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
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
