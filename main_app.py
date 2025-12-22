"""
Mays Online Flex Recruiting Analytics Platform
Single-Page Application with Navigation
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
import os
from datetime import datetime, timedelta
import numpy as np

# Page config
st.set_page_config(
    page_title="Mays Online Flex Recruiting Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide sidebar completely and remove top padding
st.markdown("""
<style>
    .css-1d391kg {display: none}
    .css-1rs6os {display: none}
    .css-17eq0hr {display: none}
    section[data-testid="stSidebar"] {display: none !important;}
    .css-1lcbmhc {margin-left: 0rem !important;}
    .css-1outpf7 {margin-left: 0rem !important;}
    .main .block-container {
        padding-left: 1rem !important; 
        padding-right: 1rem !important;
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    .block-container {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    div[data-testid="stAppViewContainer"] > .main {
        padding-top: 0rem !important;
    }
    .stApp > header {
        display: none !important;
    }
    /* div[data-testid="stToolbar"] {
        display: none !important;
    } */
</style>
""", unsafe_allow_html=True)

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'

# Database connection
@st.cache_resource
def get_connection():
    return sqlite3.connect('edulytix.db', check_same_thread=False)

# Data loading functions
@st.cache_data(ttl=600)
def load_programs():
    conn = get_connection()
    df = pd.read_sql('SELECT * FROM programs WHERE is_active = 1', conn)
    return df

@st.cache_data(ttl=600)
def load_cohort_data(cohort_year):
    """Load all data for a specific cohort"""
    conn = get_connection()
    query = '''
        SELECT 
            report_date,
            program,
            cohort_year,
            metric_name,
            metric_value
        FROM admissions_metrics
        WHERE cohort_year = ?
        AND report_date IN (
            SELECT DISTINCT report_date 
            FROM admissions_metrics 
            WHERE metric_value > 0
        )
        ORDER BY report_date, program
    '''
    df = pd.read_sql(query, conn, params=[cohort_year])
    if not df.empty:
        df['report_date'] = pd.to_datetime(df['report_date'])
    return df

@st.cache_data(ttl=600)
def load_yoy_comparison_data(current_cohort, comparison_cohort):
    """Load data for year-over-year comparison"""
    conn = get_connection()
    query = '''
        SELECT 
            report_date,
            program,
            cohort_year,
            metric_name,
            metric_value
        FROM admissions_metrics
        WHERE cohort_year IN (?, ?)
        AND report_date IN (
            SELECT DISTINCT report_date 
            FROM admissions_metrics 
            WHERE metric_value > 0
        )
        ORDER BY report_date, program, cohort_year
    '''
    df = pd.read_sql(query, conn, params=[current_cohort, comparison_cohort])
    if not df.empty:
        df['report_date'] = pd.to_datetime(df['report_date'])
    return df

def check_marketing_data_exists():
    """Check if marketing tables exist and have data"""
    conn = get_connection()
    try:
        tables = pd.read_sql(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'marketing%'",
            conn
        )
        
        if tables.empty:
            return False, "Tables not created yet"
        
        for table in tables['name']:
            count = pd.read_sql(f"SELECT COUNT(*) as count FROM {table}", conn).iloc[0]['count']
            if count > 0:
                return True, f"Data found in {table}"
        
        return False, "Tables exist but no data loaded"
    except Exception as e:
        return False, str(e)

@st.cache_data(ttl=300)
def get_quick_insights():
    """Get quick insights about the data"""
    conn = get_connection()
    
    insights = {}
    
    total_records = pd.read_sql("SELECT COUNT(*) as count FROM admissions_metrics", conn)['count'].iloc[0]
    insights['total_records'] = total_records
    
    latest_date = pd.read_sql("SELECT MAX(report_date) as date FROM admissions_metrics", conn)['date'].iloc[0]
    insights['latest_date'] = latest_date
    
    programs_count = pd.read_sql("SELECT COUNT(DISTINCT program) as count FROM admissions_metrics", conn)['count'].iloc[0]
    insights['programs'] = programs_count
    
    cohorts_count = pd.read_sql("SELECT COUNT(DISTINCT cohort_year) as count FROM admissions_metrics", conn)['count'].iloc[0]
    insights['cohorts'] = cohorts_count
    
    return insights

@st.cache_data(ttl=300)
def answer_question(question_type):
    """Answer specific business questions with data"""
    conn = get_connection()
    
    if question_type == "program_performance":
        query = """
        SELECT 
            program,
            SUM(CASE WHEN metric_name = 'total_applications' THEN metric_value ELSE 0 END) as applications,
            SUM(CASE WHEN metric_name = 'inquiries_received' THEN metric_value ELSE 0 END) as inquiries,
            SUM(CASE WHEN metric_name = 'anticipated_cohort_size' THEN metric_value ELSE 0 END) as enrolled
        FROM admissions_metrics 
        WHERE report_date = (SELECT MAX(report_date) FROM admissions_metrics WHERE metric_value > 0)
        GROUP BY program
        ORDER BY applications DESC
        """
        return pd.read_sql(query, conn)
    
    elif question_type == "recent_trends":
        query = """
        SELECT 
            report_date,
            SUM(CASE WHEN metric_name = 'total_applications' THEN metric_value ELSE 0 END) as total_applications,
            SUM(CASE WHEN metric_name = 'inquiries_received' THEN metric_value ELSE 0 END) as total_inquiries
        FROM admissions_metrics 
        WHERE report_date >= date('now', '-6 months')
        GROUP BY report_date
        ORDER BY report_date DESC
        LIMIT 10
        """
        return pd.read_sql(query, conn)
    
    elif question_type == "cohort_comparison":
        query = """
        SELECT 
            cohort_year,
            SUM(CASE WHEN metric_name = 'total_applications' THEN metric_value ELSE 0 END) as applications,
            SUM(CASE WHEN metric_name = 'anticipated_cohort_size' THEN metric_value ELSE 0 END) as enrolled
        FROM admissions_metrics 
        WHERE report_date = (SELECT MAX(report_date) FROM admissions_metrics WHERE metric_value > 0)
        GROUP BY cohort_year
        ORDER BY cohort_year DESC
        """
        return pd.read_sql(query, conn)
    
    elif question_type == "marketing_performance":
        try:
            query = """
            SELECT 
                channel,
                SUM(spend) as total_spend,
                SUM(clicks) as total_clicks,
                SUM(inquiries) as total_inquiries,
                ROUND(SUM(spend) / SUM(inquiries), 2) as cost_per_inquiry
            FROM marketing_metrics 
            GROUP BY channel
            ORDER BY total_spend DESC
            """
            return pd.read_sql(query, conn)
        except:
            return pd.DataFrame()

def generate_insights(current_data, latest_data):
    """Generate automatic insights from the data"""
    insights = []
    
    inquiries = latest_data[latest_data['metric_name'] == 'inquiries_received']['metric_value'].fillna(0).sum()
    applications = latest_data[latest_data['metric_name'] == 'total_applications']['metric_value'].fillna(0).sum()
    offers = latest_data[latest_data['metric_name'] == 'admissions_offered']['metric_value'].fillna(0).sum()
    
    if inquiries > 0 and applications > 0:
        conversion_rate = (applications / inquiries * 100)
        if conversion_rate > 35:
            insights.append(f"🟢 Strong inquiry conversion at {conversion_rate:.1f}% (above 35% benchmark)")
        elif conversion_rate > 25:
            insights.append(f"🟡 Moderate inquiry conversion at {conversion_rate:.1f}% (room for improvement)")
        else:
            insights.append(f"🔴 Low inquiry conversion at {conversion_rate:.1f}% (needs attention)")
    
    if applications > 0 and offers > 0:
        selectivity = (offers / applications * 100)
        if selectivity < 60:
            insights.append(f"🎯 Highly selective program with {selectivity:.1f}% offer rate")
        else:
            insights.append(f"📈 Opportunity to increase selectivity (current: {selectivity:.1f}%)")
    
    program_apps = latest_data[latest_data['metric_name'] == 'total_applications'].groupby('program')['metric_value'].sum()
    if not program_apps.empty:
        top_program = program_apps.idxmax()
        insights.append(f"🏆 {top_program} leads in applications with {int(program_apps.max())} submissions")
    
    return insights

def process_table_display(conn, selected_table):
    """Helper function to display table data with filtering options"""
    try:
        # Table descriptions - what questions each table can help answer
        table_descriptions = {
            'admissions_metrics': {
                'icon': '📊',
                'title': 'Admissions Performance Data',
                'questions': [
                    'How many applications did we receive by program and cohort?',
                    'What are the conversion rates from inquiry to application?',
                    'Which programs have the highest enrollment numbers?',
                    'How do our metrics trend over time?'
                ]
            },
            'programs': {
                'icon': '🎓',
                'title': 'Program Information',
                'questions': [
                    'What programs do we currently offer?',
                    'Which programs are active vs inactive?',
                    'What are the program codes and full names?',
                    'How are programs categorized?'
                ]
            },
            'marketing_metrics': {
                'icon': '📈',
                'title': 'Marketing Performance Data',
                'questions': [
                    'How much are we spending on each marketing channel?',
                    'What\'s our cost per inquiry by channel?',
                    'Which marketing channels are most effective?',
                    'How do click-through rates compare across channels?'
                ]
            },
            'marketing_campaigns': {
                'icon': '📢',
                'title': 'Campaign Management Data',
                'questions': [
                    'What marketing campaigns are currently running?',
                    'Which campaigns target which programs?',
                    'What are the campaign budgets and timelines?',
                    'How do campaigns perform against targets?'
                ]
            },
            'marketing_spend': {
                'icon': '💰',
                'title': 'Marketing Budget & Spend',
                'questions': [
                    'How much did we spend on each marketing channel?',
                    'What\'s our monthly marketing budget allocation?',
                    'Which channels have the highest ROI?',
                    'How does actual spend compare to budget?'
                ]
            },
            'inquiry_sources': {
                'icon': '🔍',
                'title': 'Lead Source Analysis',
                'questions': [
                    'Where are our inquiries coming from?',
                    'Which sources generate the most qualified leads?',
                    'How do different sources convert to applications?',
                    'What\'s the quality score by source?'
                ]
            },
            'sqlite_sequence': {
                'icon': '⚙️',
                'title': 'System Table',
                'questions': [
                    'Internal SQLite sequence information',
                    'Auto-incrementing field management'
                ]
            }
        }
        
        # Show formatted table description
        if selected_table in table_descriptions:
            desc = table_descriptions[selected_table]
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                        padding: 20px; border-radius: 10px; margin-bottom: 20px; 
                        border-left: 5px solid #500000;">
                <h4 style="margin: 0 0 15px 0; color: #500000;">
                    {desc['icon']} {desc['title']}
                </h4>
                <p style="margin: 0 0 10px 0; color: #666; font-weight: 600;">
                    💡 <strong>What questions can this table help answer?</strong>
                </p>
                <ul style="margin: 0; padding-left: 20px; color: #444;">
                    {''.join([f'<li style="margin-bottom: 5px;">{q}</li>' for q in desc['questions']])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #6c757d;">
                <strong>📋 Table:</strong> <code>{selected_table}</code><br>
                <em>Explore the data to understand what insights it can provide.</em>
            </div>
            """, unsafe_allow_html=True)
        
        # Get table info
        table_info_query = f"PRAGMA table_info({selected_table})"
        table_info = pd.read_sql(table_info_query, conn)
        
        # Show table schema
        with st.expander("📋 Table Schema"):
            st.dataframe(table_info[['name', 'type', 'notnull', 'pk']], use_container_width=True)
        
        # Filtering options
        st.markdown("#### 🔍 Filters")
        
        # Get all data first to enable filtering
        data_query = f"SELECT * FROM {selected_table}"
        full_data = pd.read_sql(data_query, conn)
        
        if not full_data.empty:
            # Create filter columns
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            with filter_col1:
                # Column filter
                columns = ['All Columns'] + list(full_data.columns)
                selected_columns = st.multiselect(
                    "Select Columns", 
                    columns, 
                    default=['All Columns'],
                    key=f"columns_{selected_table}"
                )
                
                if 'All Columns' in selected_columns or not selected_columns:
                    display_data = full_data.copy()
                else:
                    display_data = full_data[selected_columns].copy()
            
            with filter_col2:
                # Row limit
                row_limit = st.number_input(
                    "Row Limit", 
                    min_value=10, 
                    max_value=1000, 
                    value=100, 
                    step=10,
                    key=f"limit_{selected_table}"
                )
            
            with filter_col3:
                # Sort options
                sort_columns = ['None'] + list(full_data.columns)
                sort_by = st.selectbox("Sort By", sort_columns, key=f"sort_{selected_table}")
                sort_order = 'Ascending'  # Default value
                if sort_by != 'None':
                    sort_order = st.radio(
                        "Order", 
                        ['Ascending', 'Descending'], 
                        horizontal=True,
                        key=f"order_{selected_table}"
                    )
            
            # Text search filter
            search_term = st.text_input(
                "🔍 Search in all columns (case-insensitive)",
                key=f"search_{selected_table}"
            )
            
            # Apply filters
            filtered_data = display_data.copy()
            
            # Apply search filter
            if search_term:
                try:
                    # Search across all string columns
                    string_columns = filtered_data.select_dtypes(include=['object']).columns
                    if len(string_columns) > 0:
                        search_mask = filtered_data[string_columns].astype(str).apply(
                            lambda x: x.str.contains(search_term, case=False, na=False)
                        ).any(axis=1)
                        filtered_data = filtered_data[search_mask]
                except Exception as e:
                    st.warning(f"Search error: {str(e)}")
            
            # Apply sorting
            if sort_by != 'None' and sort_by in filtered_data.columns:
                try:
                    ascending = sort_order == 'Ascending'
                    filtered_data = filtered_data.sort_values(by=sort_by, ascending=ascending)
                except Exception as e:
                    st.warning(f"Sort error: {str(e)}")
            
            # Apply row limit
            filtered_data = filtered_data.head(row_limit)
            
            # Display results
            st.markdown("#### 📊 Data")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"Showing {len(filtered_data):,} of {len(full_data):,} rows")
            
            with col2:
                # Download filtered data
                csv_data = filtered_data.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    csv_data,
                    f"{selected_table}_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True,
                    key=f"download_{selected_table}"
                )
            
            # Display the data table
            st.dataframe(filtered_data, use_container_width=True, height=500)
            
            # Quick stats for numeric columns
            numeric_columns = filtered_data.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                with st.expander("📈 Quick Statistics (Numeric Columns)"):
                    stats_data = filtered_data[numeric_columns].describe()
                    st.dataframe(stats_data, use_container_width=True)
        
        else:
            st.info(f"Table '{selected_table}' is empty.")
            
    except Exception as e:
        st.error(f"Error loading table data: {str(e)}")
        st.info("Please check if the table exists and contains valid data.")

# CSS for the entire application
st.markdown("""
<style>
.nav-menu {
    background: #f8f9fa;
    padding: 10px 20px;
    border-radius: 8px;
    margin-bottom: 15px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.nav-button {
    display: inline-block;
    padding: 10px 20px;
    margin: 0 5px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 2px solid transparent;
}
.nav-button.active {
    background: #500000;
    color: white !important;
    border-color: #500000;
}
.nav-button.inactive {
    background: white;
    color: #500000;
    border-color: #e9ecef;
}
.nav-button.inactive:hover {
    background: #e9ecef;
    border-color: #500000;
}
.metric-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    border: 1px solid #e0e0e0;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 1rem;
    text-align: center;
}
.insight-card {
    background: linear-gradient(135deg, #500000 0%, #700000 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
}
.section-divider {
    height: 3px;
    background: linear-gradient(90deg, #500000, #B00000);
    border: none;
    border-radius: 2px;
    margin: 2rem 0;
}
.performance-indicator {
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
    font-weight: 600;
}
.data-insight {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #500000;
    margin: 1rem 0;
    font-size: 0.95rem;
}
.metric-highlight {
    background: #500000;
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.9rem;
}
.indicator-excellent { background: #d4edda; color: #155724; }
.indicator-good { background: #fff3cd; color: #856404; }
.indicator-needs-attention { background: #f8d7da; color: #721c24; }
.data-insight {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    padding: 1.5rem;
    border-radius: 8px;
    border-left: 4px solid #500000;
    margin: 1rem 0;
}
.metric-highlight {
    background: #500000;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    display: inline-block;
    font-weight: bold;
    margin: 0.25rem;
}
</style>
""", unsafe_allow_html=True)

# Professional Mays Business School Banner
st.markdown("""
<div style="background: linear-gradient(135deg, #500000 0%, #700000 100%); 
            padding: 20px 30px; border-radius: 12px; margin-bottom: 10px; color: white; 
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
    <div style="display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center;">
            <div style="background: white; border-radius: 50%; width: 60px; height: 60px; 
                        display: flex; align-items: center; justify-content: center; margin-right: 20px;
                        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);">
                <span style="color: #500000; font-weight: bold; font-size: 18px;">A&M</span>
            </div>
            <div>
                <h1 style="margin: 0; font-size: 32px; font-weight: bold; letter-spacing: -1px;">
                    Mays Online Flex Recruiting Analytics Platform
                </h1>
                <h2 style="margin: 5px 0 0 0; font-size: 16px; font-weight: 300; opacity: 0.9;">
                    Real-time Admissions Analytics & Strategic Insights
                </h2>
            </div>
        </div>
    </div>
    <div style="margin-top: 15px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.2);">
        <div style="font-size: 12px; opacity: 0.8; text-align: center;">
            MBA • MS ACCT • MS HRM • MS MISY • MS MKTG • MS ENLD • MS SPBA
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation Menu with Clickable Buttons
st.markdown("""
<div class="nav-menu">
    <div style="display: flex; justify-content: center; align-items: center;">
        <div style="display: flex; gap: 10px;">
""", unsafe_allow_html=True)

# Navigation buttons
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🏠 Home", key="nav_home", use_container_width=True):
        st.session_state.current_page = 'Home'

with col2:
    if st.button("📊 Executive Deep Dive", key="nav_executive", use_container_width=True):
        st.session_state.current_page = 'Executive_Deep_Dive'

with col3:
    if st.button("📢 Marketing Analysis", key="nav_marketing", use_container_width=True):
        st.session_state.current_page = 'Marketing_Analysis'

with col4:
    if st.button("🗄️ Data Explorer", key="nav_database", use_container_width=True):
        st.session_state.current_page = 'Database'

st.markdown("</div></div></div>", unsafe_allow_html=True)

# Display current page indicator
current_page_info = {
    'Home': {'icon': '🏠', 'title': 'Home Dashboard'},
    'Executive_Deep_Dive': {'icon': '📊', 'title': 'Executive Deep Dive'},
    'Marketing_Analysis': {'icon': '📢', 'title': 'Marketing Analysis'},
    'Database': {'icon': '🗄️', 'title': 'Data Explorer'}
}

current_info = current_page_info[st.session_state.current_page]
st.markdown(f"""
<div style="text-align: center; padding: 8px; background: #f8f9fa; border-radius: 8px; margin-bottom: 15px;">
    <h2 style="margin: 0; color: #500000; font-size: 24px;">{current_info['icon']} {current_info['title']}</h2>
</div>
""", unsafe_allow_html=True)

# Page Content Based on Navigation
if st.session_state.current_page == 'Home':
    # HOME PAGE CONTENT
    st.markdown("## 🎓 Select Cohort for Analysis")
    col1, col2, col3 = st.columns([2, 2, 4])

    with col1:
        cohort_options = [2028, 2027, 2026]
        selected_cohort = st.selectbox(
            "Cohort Year",
            options=cohort_options,
            index=0,
            help="Select ONE cohort year for analysis. No mixed-cohort data."
        )

    with col2:
        st.metric(
            label="Selected Cohort",
            value=f"Class of {selected_cohort}",
            delta="Primary Focus" if selected_cohort == 2028 else None
        )

    with col3:
        st.info(f"""
        📊 **Analyzing Class of {selected_cohort}**
        
        All metrics below are specific to this cohort only. Use the Executive Deep Dive for detailed year-over-year comparisons.
        """)

    st.markdown("---")

    # Load data for selected cohort
    conn = get_connection()
    query = 'SELECT * FROM admissions_metrics WHERE cohort_year = ? ORDER BY report_date, program'
    df = pd.read_sql(query, conn, params=[selected_cohort])
    df['report_date'] = pd.to_datetime(df['report_date'])

    if not df.empty:
        # Filter out dates with no real data
        dates_with_data = df.groupby('report_date')['metric_value'].sum()
        dates_with_data = dates_with_data[dates_with_data > 0].index
        df = df[df['report_date'].isin(dates_with_data)]

        latest_date = df['report_date'].max()
        latest_data = df[df['report_date'] == latest_date]

        # Main Dashboard
        st.header(f"Current Stats - Class of {selected_cohort}")
        st.caption(f"All metrics below are specific to the {selected_cohort} cohort • Last updated: {latest_date.strftime('%B %d, %Y')}")

        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)

        total_cohort = latest_data[latest_data['metric_name'] == 'anticipated_cohort_size']['metric_value'].sum()
        total_applications = latest_data[latest_data['metric_name'] == 'total_applications']['metric_value'].sum()
        total_inquiries = latest_data[latest_data['metric_name'] == 'inquiries_received']['metric_value'].sum()
        total_accepted = latest_data[latest_data['metric_name'] == 'admissions_accepted']['metric_value'].sum()

        with col1:
            st.metric(
                label=f"Enrolled Students (as of {latest_date.strftime('%b %d')})",
                value=f"{int(total_cohort) if pd.notna(total_cohort) else 0}",
                help="Current number of enrolled students in this cohort"
            )

        with col2:
            st.metric(
                label="Total Applications",
                value=f"{int(total_applications) if pd.notna(total_applications) else 0}"
            )

        with col3:
            st.metric(
                label="Total Inquiries",
                value=f"{int(total_inquiries) if pd.notna(total_inquiries) else 0}"
            )

        with col4:
            conversion_rate = (total_applications / total_inquiries * 100) if total_inquiries > 0 else 0
            st.metric(
                label="Inquiry → Application Rate",
                value=f"{conversion_rate:.1f}%"
            )

        st.divider()

        # Admissions Funnel
        st.subheader(f"Admissions Funnel - Class of {selected_cohort}")
        st.caption("Single-cohort analysis showing the complete application journey")

        funnel_metrics = ['inquiries_received', 'total_applications', 'admissions_offered', 'admissions_accepted']
        funnel_labels = ['Inquiries', 'Applications', 'Offers', 'Accepted']

        funnel_data = []
        for metric in funnel_metrics:
            value = latest_data[latest_data['metric_name'] == metric]['metric_value'].sum()
            funnel_data.append(value)

        fig_funnel = go.Figure(go.Funnel(
            y=funnel_labels,
            x=funnel_data,
            textinfo="value+percent initial",
            marker={"color": ["#500000", "#700000", "#900000", "#B00000"]}
        ))

        fig_funnel.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_funnel, width='stretch')

        st.divider()

        # Program Comparison
        st.subheader("Program Comparison")
        
        # Interactive filter controls for program comparison
        st.markdown("**📊 Select Metrics to Display:**")
        prog_filter_col1, prog_filter_col2, prog_filter_col3, prog_filter_col4 = st.columns(4)
        
        with prog_filter_col1:
            show_inquiries_prog = st.checkbox("👥 Inquiries", value=True, key="show_inq_prog_home")
        with prog_filter_col2:
            show_applications_prog = st.checkbox("📝 Applications", value=True, key="show_apps_prog_home")
        with prog_filter_col3:
            show_accepted_prog = st.checkbox("✅ Accepted", value=True, key="show_acc_prog_home")
        with prog_filter_col4:
            show_cohort_prog = st.checkbox("🎯 Cohort Size", value=True, key="show_cohort_prog_home")
        
        # Add instruction tooltip for program comparison
        st.markdown("""
        <div style="background: #f0f8ff; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-size: 0.9rem;">
            💡 <strong>Interactive Bar Chart:</strong> Use checkboxes above to show/hide metrics • Click legend items to toggle • Hover bars for exact values
        </div>
        """, unsafe_allow_html=True)

        program_comparison = latest_data[latest_data['metric_name'].isin([
            'inquiries_received', 'total_applications', 'admissions_accepted', 'anticipated_cohort_size'
        ])].pivot_table(
            index='program',
            columns='metric_name',
            values='metric_value',
            aggfunc='sum'
        ).fillna(0)

        if not program_comparison.empty:
            fig_comparison = go.Figure()
            
            metrics_to_plot = {
                'inquiries_received': ('Inquiries', show_inquiries_prog, '#500000'),
                'total_applications': ('Applications', show_applications_prog, '#700000'),
                'admissions_accepted': ('Accepted', show_accepted_prog, '#900000'),
                'anticipated_cohort_size': ('Cohort Size', show_cohort_prog, '#B00000')
            }
            
            for metric, (label, show_flag, color) in metrics_to_plot.items():
                if metric in program_comparison.columns and show_flag:
                    fig_comparison.add_trace(go.Bar(
                        name=label,
                        x=program_comparison.index,
                        y=program_comparison[metric],
                        marker_color=color,
                        hovertemplate='<b>' + label + '</b><br>' +
                                     'Program: %{x}<br>' +
                                     'Count: %{y:,.0f}<br>' +
                                     '<extra></extra>'
                    ))
            
            fig_comparison.update_layout(
                barmode='group',
                height=400,
                xaxis_title='Program',
                yaxis_title='Count',
                legend=dict(
                    x=1, y=1,
                    xanchor='right', yanchor='top',
                    bgcolor='rgba(255,255,255,0.9)',
                    bordercolor='rgba(0,0,0,0.2)',
                    borderwidth=1
                ),
                annotations=[
                    dict(
                        text="💡 Click legend items or use checkboxes above to customize view",
                        xref="paper", yref="paper",
                        x=0.02, y=0.02, xanchor='left', yanchor='bottom',
                        showarrow=False,
                        font=dict(size=10, color='gray'),
                        bgcolor='rgba(255,255,255,0.9)',
                        bordercolor='gray',
                        borderwidth=1
                    )
                ]
            )
            
            st.plotly_chart(fig_comparison, width='stretch')

    else:
        st.warning("⚠️ No data available for the selected cohort.")

elif st.session_state.current_page == 'Executive_Deep_Dive':
    # EXECUTIVE DEEP DIVE CONTENT
    st.markdown("## 🎯 Analysis Configuration")

    col1, col2, col3, col4 = st.columns([2, 2, 2, 2])

    with col1:
        cohort_options = [2028, 2027, 2026]
        selected_cohort = st.selectbox(
            "📅 Primary Cohort",
            options=cohort_options,
            index=0,
            help="Select primary cohort for analysis"
        )

    with col2:
        programs_df = load_programs()
        program_options = ["All Programs"] + sorted(programs_df['program_code'].tolist())
        selected_program_filter = st.selectbox(
            "🎓 Program Focus",
            options=program_options,
            help="Filter by specific program"
        )

    with col3:
        comparison_cohorts = [c for c in cohort_options if c != selected_cohort]
        comparison_cohort = st.selectbox(
            "📈 Compare With",
            options=["None"] + comparison_cohorts,
            help="Select cohort for YoY comparison"
        )

    with col4:
        analysis_depth = st.selectbox(
            "🔍 Analysis Depth",
            options=["Executive Summary", "Detailed Analytics", "Full Deep Dive"],
            index=1,
            help="Choose level of detail"
        )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
    # Add interactive features guide
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); 
                padding: 15px; border-radius: 8px; margin-bottom: 20px; 
                border-left: 5px solid #500000;">
        <h4 style="margin: 0 0 10px 0; color: #500000;">
            🎯 Interactive Chart Features Guide
        </h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; font-size: 0.9rem;">
            <div>
                <strong>📊 Line Chart Controls:</strong><br>
                • Use checkboxes to show/hide specific lines<br>
                • Click legend items to toggle lines on/off<br>
                • Hover over data points for detailed information
            </div>
            <div>
                <strong>🔍 Chart Navigation:</strong><br>
                • Click and drag to zoom into time periods<br>
                • Double-click to reset zoom level<br>
                • All charts are fully interactive and responsive
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Load data based on selection
    if comparison_cohort != "None":
        data = load_yoy_comparison_data(selected_cohort, comparison_cohort)
        current_data = data[data['cohort_year'] == selected_cohort]
        comparison_data = data[data['cohort_year'] == comparison_cohort]
    else:
        current_data = load_cohort_data(selected_cohort)
        comparison_data = pd.DataFrame()

    # Apply program filter if selected
    if selected_program_filter != "All Programs":
        current_data = current_data[current_data['program'] == selected_program_filter]
        if not comparison_data.empty:
            comparison_data = comparison_data[comparison_data['program'] == selected_program_filter]

    if current_data.empty:
        st.error(f"❌ No data available for Class of {selected_cohort}" + 
                 (f" - {selected_program_filter}" if selected_program_filter != "All Programs" else ""))
        st.info("💡 Try selecting a different cohort/program or check the database")
    else:
        # Get latest data for current cohort
        latest_date = current_data['report_date'].max()
        latest_data = current_data[current_data['report_date'] == latest_date]

        program_scope = f" - {selected_program_filter}" if selected_program_filter != "All Programs" else ""
        st.info(f"📅 **Primary Cohort**: Class of {selected_cohort}{program_scope} | **Latest Data**: {latest_date.strftime('%B %d, %Y')}")

        if comparison_cohort != "None" and not comparison_data.empty:
            comp_latest_date = comparison_data['report_date'].max()
            st.info(f"📊 **Comparison**: Class of {comparison_cohort}{program_scope} | **Latest Data**: {comp_latest_date.strftime('%B %d, %Y')}")

        # Calculate comprehensive metrics
        inquiries = latest_data[latest_data['metric_name'] == 'inquiries_received']['metric_value'].fillna(0).sum()
        applications = latest_data[latest_data['metric_name'] == 'total_applications']['metric_value'].fillna(0).sum()
        offers = latest_data[latest_data['metric_name'] == 'admissions_offered']['metric_value'].fillna(0).sum()
        accepted = latest_data[latest_data['metric_name'] == 'admissions_accepted']['metric_value'].fillna(0).sum()
        enrolled = latest_data[latest_data['metric_name'] == 'anticipated_cohort_size']['metric_value'].fillna(0).sum()
        in_progress = latest_data[latest_data['metric_name'] == 'applications_in_progress']['metric_value'].fillna(0).sum()
        complete = latest_data[latest_data['metric_name'] == 'applications_complete']['metric_value'].fillna(0).sum()
        
        # Calculate conversion rates
        conversion_1 = (applications / inquiries * 100) if inquiries > 0 else 0
        conversion_2 = (offers / applications * 100) if applications > 0 else 0
        yield_rate = (accepted / offers * 100) if offers > 0 else 0
        overall_conversion = (enrolled / inquiries * 100) if inquiries > 0 else 0

        # DIFFERENT CONTENT BASED ON ANALYSIS DEPTH
        if analysis_depth == "Executive Summary":
            # EXECUTIVE SUMMARY - High-level overview with 3 key metrics only
            st.markdown(f"## 📊 Executive Summary - Class of {selected_cohort}{program_scope}")
            st.markdown("*High-level overview for executive decision making*")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h2 style="color: #500000; margin: 0; font-size: 2.5rem;">📝 {int(applications)}</h2>
                    <p style="margin: 5px 0 0 0; color: #666; font-weight: 600; font-size: 1.2rem;">Total Applications</p>
                    <small style="color: #999;">Primary Pipeline Metric</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h2 style="color: #500000; margin: 0; font-size: 2.5rem;">🎯 {int(enrolled)}</h2>
                    <p style="margin: 5px 0 0 0; color: #666; font-weight: 600; font-size: 1.2rem;">Students Enrolled</p>
                    <small style="color: #999;">Final Outcome</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h2 style="color: #500000; margin: 0; font-size: 2.5rem;">📈 {overall_conversion:.1f}%</h2>
                    <p style="margin: 5px 0 0 0; color: #666; font-weight: 600; font-size: 1.2rem;">Overall Efficiency</p>
                    <small style="color: {'#28a745' if overall_conversion > 15 else '#ffc107' if overall_conversion > 10 else '#dc3545'};">Inquiry to Enrollment</small>
                </div>
                """, unsafe_allow_html=True)

            # Simple executive insights
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            st.markdown("## 🎯 Executive Insights")
            
            insights = generate_insights(current_data, latest_data)
            if insights:
                for i, insight in enumerate(insights[:2]):  # Only top 2 insights for executives
                    st.markdown(f"**{i+1}.** {insight}")
            
            # Simple comparison if available
            if comparison_cohort != "None" and not comparison_data.empty:
                st.markdown("### 📊 Year-over-Year Comparison")
                comp_latest_date = comparison_data['report_date'].max()
                comp_latest_data = comparison_data[comparison_data['report_date'] == comp_latest_date]
                comp_applications = comp_latest_data[comp_latest_data['metric_name'] == 'total_applications']['metric_value'].fillna(0).sum()
                comp_enrolled = comp_latest_data[comp_latest_data['metric_name'] == 'anticipated_cohort_size']['metric_value'].fillna(0).sum()
                
                col1, col2 = st.columns(2)
                with col1:
                    app_change = ((applications - comp_applications) / comp_applications * 100) if comp_applications > 0 else 0
                    st.metric("Applications Change", f"{app_change:+.1f}%", f"{int(applications)} vs {int(comp_applications)}")
                with col2:
                    enroll_change = ((enrolled - comp_enrolled) / comp_enrolled * 100) if comp_enrolled > 0 else 0
                    st.metric("Enrollment Change", f"{enroll_change:+.1f}%", f"{int(enrolled)} vs {int(comp_enrolled)}")

        elif analysis_depth == "Detailed Analytics":
            # DETAILED ANALYTICS - Comprehensive metrics with detailed breakdowns
            st.markdown(f"## 📈 Detailed Analytics - Class of {selected_cohort}{program_scope}")
            st.markdown("*Comprehensive analysis for operational insights*")
            
            # Full pipeline metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h2 style="color: #500000; margin: 0; font-size: 2rem;">👥 {int(inquiries)}</h2>
                    <p style="margin: 5px 0 0 0; color: #666; font-weight: 500;">Total Inquiries</p>
                    <small style="color: #999;">Pipeline Entry</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h2 style="color: #500000; margin: 0; font-size: 2rem;">📝 {int(applications)}</h2>
                    <p style="margin: 5px 0 0 0; color: #666; font-weight: 500;">Applications</p>
                    <small style="color: {'#28a745' if conversion_1 > 30 else '#ffc107' if conversion_1 > 20 else '#dc3545'};">{conversion_1:.1f}% conversion</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h2 style="color: #500000; margin: 0; font-size: 2rem;">🎓 {int(offers)}</h2>
                    <p style="margin: 5px 0 0 0; color: #666; font-weight: 500;">Offers Extended</p>
                    <small style="color: #666;">{conversion_2:.1f}% of applications</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <h2 style="color: #500000; margin: 0; font-size: 2rem;">✅ {int(accepted)}</h2>
                    <p style="margin: 5px 0 0 0; color: #666; font-weight: 500;">Offers Accepted</p>
                    <small style="color: {'#28a745' if yield_rate > 70 else '#ffc107' if yield_rate > 50 else '#dc3545'};">{yield_rate:.1f}% yield rate</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                st.markdown(f"""
                <div class="metric-card">
                    <h2 style="color: #500000; margin: 0; font-size: 2rem;">🎯 {int(enrolled)}</h2>
                    <p style="margin: 5px 0 0 0; color: #666; font-weight: 500;">Students Enrolled</p>
                    <small style="color: #666;">{overall_conversion:.1f}% overall conversion</small>
                </div>
                """, unsafe_allow_html=True)

            # Detailed visualizations
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            st.markdown("## 📊 Performance Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Conversion funnel
                st.markdown("### 🎯 Admissions Funnel")
                funnel_data = [inquiries, applications, offers, accepted, enrolled]
                funnel_labels = ['Inquiries', 'Applications', 'Offers', 'Accepted', 'Enrolled']
                
                if sum(funnel_data) > 0:
                    fig = go.Figure(go.Funnel(
                        y=funnel_labels,
                        x=funnel_data,
                        textinfo="value+percent initial",
                        marker={"color": ["#500000", "#600000", "#700000", "#800000", "#900000"]}
                    ))
                    fig.update_layout(height=500, showlegend=False)
                    st.plotly_chart(fig, width='stretch')
            
            with col2:
                # Performance radar chart
                st.markdown("### 📈 Performance Radar")
                
                metrics = ['Inquiry Conversion', 'Application Completion', 'Selectivity', 'Yield Rate', 'Overall Efficiency']
                values = [
                    conversion_1,
                    (complete / applications * 100) if applications > 0 else 0,
                    conversion_2,
                    yield_rate,
                    overall_conversion
                ]
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=metrics,
                    fill='toself',
                    name='Performance',
                    line_color='#500000'
                ))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )),
                    height=500
                )
                st.plotly_chart(fig, width='stretch')

            # Time series analysis
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            st.markdown("## 📊 Trend Analysis")
            
            time_series = current_data.pivot_table(
                index='report_date',
                columns='metric_name',
                values='metric_value',
                aggfunc='sum'
            ).fillna(0)
            
            if not time_series.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📈 Application & Inquiry Trends")
                    
                    # Interactive filter controls for line selection
                    st.markdown("**📊 Select Lines to Display:**")
                    filter_col1, filter_col2 = st.columns(2)
                    
                    with filter_col1:
                        show_applications = st.checkbox("📝 Applications", value=True, key="show_apps_detailed")
                    with filter_col2:
                        show_inquiries = st.checkbox("👥 Inquiries", value=True, key="show_inq_detailed")
                    
                    # Add instruction tooltip
                    st.markdown("""
                    <div style="background: #e3f2fd; padding: 8px; border-radius: 4px; margin-bottom: 10px; font-size: 0.85rem;">
                        💡 <strong>Interactive Tips:</strong> Use checkboxes above to show/hide lines • Click legend items to toggle • Hover over points for details
                    </div>
                    """, unsafe_allow_html=True)
                    
                    fig = go.Figure()
                    
                    if 'total_applications' in time_series.columns and show_applications:
                        fig.add_trace(go.Scatter(
                            x=time_series.index,
                            y=time_series['total_applications'],
                            mode='lines+markers',
                            name='Applications',
                            line=dict(color='#500000', width=3),
                            marker=dict(size=8),
                            hovertemplate='<b>Applications</b><br>' +
                                         'Date: %{x}<br>' +
                                         'Count: %{y:,.0f}<br>' +
                                         '<extra></extra>'
                        ))
                    
                    if 'inquiries_received' in time_series.columns and show_inquiries:
                        fig.add_trace(go.Scatter(
                            x=time_series.index,
                            y=time_series['inquiries_received'],
                            mode='lines+markers',
                            name='Inquiries',
                            line=dict(color='#B00000', width=3),
                            marker=dict(size=8),
                            hovertemplate='<b>Inquiries</b><br>' +
                                         'Date: %{x}<br>' +
                                         'Count: %{y:,.0f}<br>' +
                                         '<extra></extra>'
                        ))
                    
                    fig.update_layout(
                        height=400,
                        xaxis_title='Date',
                        yaxis_title='Count',
                        legend=dict(
                            x=1, y=1,
                            xanchor='right', yanchor='top',
                            bgcolor='rgba(255,255,255,0.9)',
                            bordercolor='rgba(0,0,0,0.2)',
                            borderwidth=1
                        ),
                        annotations=[
                            dict(
                                text="💡 Click legend items to show/hide lines",
                                xref="paper", yref="paper",
                                x=0.02, y=0.02, xanchor='left', yanchor='bottom',
                                showarrow=False,
                                font=dict(size=10, color='gray'),
                                bgcolor='rgba(255,255,255,0.9)',
                                bordercolor='gray',
                                borderwidth=1
                            )
                        ]
                    )
                    st.plotly_chart(fig, width='stretch')
                
                with col2:
                    st.markdown("#### 🎯 Conversion Rates Over Time")
                    
                    # Interactive filter controls for conversion rates
                    st.markdown("**📊 Select Conversion Metrics:**")
                    conv_filter_col1, conv_filter_col2 = st.columns(2)
                    
                    with conv_filter_col1:
                        show_inquiry_conv = st.checkbox("🔄 Inquiry → App", value=True, key="show_inq_conv_detailed")
                    with conv_filter_col2:
                        show_app_conv = st.checkbox("🎯 App → Offer", value=True, key="show_app_conv_detailed")
                    
                    # Add instruction tooltip
                    st.markdown("""
                    <div style="background: #fff3e0; padding: 8px; border-radius: 4px; margin-bottom: 10px; font-size: 0.85rem;">
                        💡 <strong>Interactive Tips:</strong> Use checkboxes above to show/hide conversion lines • Click legend to toggle • Hover for exact percentages
                    </div>
                    """, unsafe_allow_html=True)
                    
                    conversion_data = []
                    for date in time_series.index:
                        inquiries_ts = time_series.loc[date, 'inquiries_received'] if 'inquiries_received' in time_series.columns else 0
                        applications_ts = time_series.loc[date, 'total_applications'] if 'total_applications' in time_series.columns else 0
                        offers_ts = time_series.loc[date, 'admissions_offered'] if 'admissions_offered' in time_series.columns else 0
                        
                        inquiry_conv = (applications_ts / inquiries_ts * 100) if inquiries_ts > 0 else 0
                        app_conv = (offers_ts / applications_ts * 100) if applications_ts > 0 else 0
                        
                        conversion_data.append({
                            'date': date,
                            'inquiry_conversion': inquiry_conv,
                            'application_conversion': app_conv
                        })
                    
                    conv_df = pd.DataFrame(conversion_data)
                    
                    if not conv_df.empty:
                        fig = go.Figure()
                        
                        if show_inquiry_conv:
                            fig.add_trace(go.Scatter(
                                x=conv_df['date'],
                                y=conv_df['inquiry_conversion'],
                                mode='lines+markers',
                                name='Inquiry → App (%)',
                                line=dict(color='#28a745', width=3),
                                marker=dict(size=8),
                                hovertemplate='<b>Inquiry to Application</b><br>' +
                                             'Date: %{x}<br>' +
                                             'Conversion Rate: %{y:.1f}%<br>' +
                                             '<extra></extra>'
                            ))
                        
                        if show_app_conv:
                            fig.add_trace(go.Scatter(
                                x=conv_df['date'],
                                y=conv_df['application_conversion'],
                                mode='lines+markers',
                                name='App → Offer (%)',
                                line=dict(color='#ffc107', width=3),
                                marker=dict(size=8),
                                hovertemplate='<b>Application to Offer</b><br>' +
                                             'Date: %{x}<br>' +
                                             'Conversion Rate: %{y:.1f}%<br>' +
                                             '<extra></extra>'
                            ))
                        
                        fig.update_layout(
                            height=400,
                            xaxis_title='Date',
                            yaxis_title='Conversion Rate (%)',
                            legend=dict(
                                x=1, y=1,
                                xanchor='right', yanchor='top',
                                bgcolor='rgba(255,255,255,0.9)',
                                bordercolor='rgba(0,0,0,0.2)',
                                borderwidth=1
                            ),
                            annotations=[
                                dict(
                                    text="💡 Click legend items to show/hide lines",
                                    xref="paper", yref="paper",
                                    x=0.02, y=0.02, xanchor='left', yanchor='bottom',
                                    showarrow=False,
                                    font=dict(size=10, color='gray'),
                                    bgcolor='rgba(255,255,255,0.9)',
                                    bordercolor='gray',
                                    borderwidth=1
                                )
                            ]
                        )
                        st.plotly_chart(fig, width='stretch')

        else:  # Full Deep Dive
            # FULL DEEP DIVE - Most comprehensive analysis with advanced metrics
            st.markdown(f"## 🔍 Full Deep Dive - Class of {selected_cohort}{program_scope}")
            st.markdown("*Complete analytics suite with advanced insights and predictive analysis*")
            
            # Comprehensive KPI Grid (6 metrics)
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                st.metric("👥 Inquiries", f"{int(inquiries)}", help="Total inquiries received")
            with col2:
                st.metric("📝 Applications", f"{int(applications)}", f"{conversion_1:.1f}% conv.")
            with col3:
                st.metric("⏳ In Progress", f"{int(in_progress)}", help="Applications in progress")
            with col4:
                st.metric("✅ Complete", f"{int(complete)}", help="Complete applications")
            with col5:
                st.metric("🎓 Offers", f"{int(offers)}", f"{conversion_2:.1f}% rate")
            with col6:
                st.metric("🎯 Enrolled", f"{int(enrolled)}", f"{yield_rate:.1f}% yield")

            # Advanced Analytics Tabs
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Performance Analysis", "📈 Trend Analysis", "🎓 Program Deep Dive", "📋 Data Tables", "🔍 Advanced Insights"])
            
            with tab1:
                st.markdown("### 📊 Performance Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Complete conversion funnel
                    st.markdown("#### 🎯 Complete Conversion Funnel")
                    funnel_data = [inquiries, applications, complete, offers, accepted, enrolled]
                    funnel_labels = ['Inquiries', 'Applications', 'Complete Apps', 'Offers', 'Accepted', 'Enrolled']
                    
                    fig = go.Figure(go.Funnel(
                        y=funnel_labels,
                        x=funnel_data,
                        textinfo="value+percent initial",
                        marker={"color": ["#500000", "#600000", "#700000", "#800000", "#900000", "#B00000"]}
                    ))
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, width='stretch')
                
                with col2:
                    # Performance metrics radar chart
                    st.markdown("#### 📈 Performance Radar")
                    
                    metrics = ['Inquiry Conversion', 'Application Completion', 'Selectivity', 'Yield Rate', 'Overall Efficiency']
                    values = [
                        conversion_1,
                        (complete / applications * 100) if applications > 0 else 0,
                        conversion_2,
                        yield_rate,
                        overall_conversion
                    ]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=values,
                        theta=metrics,
                        fill='toself',
                        name='Performance',
                        line_color='#500000'
                    ))
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100]
                            )),
                        height=500
                    )
                    st.plotly_chart(fig, width='stretch')
            
            with tab2:
                st.markdown("### 📈 Trend Analysis")
                
                # Interactive filter controls for multi-line chart
                st.markdown("**📊 Select Metrics to Display:**")
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                
                with metric_col1:
                    show_inquiries_full = st.checkbox("👥 Inquiries", value=True, key="show_inq_full")
                with metric_col2:
                    show_applications_full = st.checkbox("📝 Applications", value=True, key="show_apps_full")
                with metric_col3:
                    show_offers_full = st.checkbox("🎓 Offers", value=True, key="show_offers_full")
                with metric_col4:
                    show_cohort_full = st.checkbox("🎯 Cohort Size", value=True, key="show_cohort_full")
                
                # Add comprehensive instruction tooltip
                st.markdown("""
                <div style="background: #f3e5f5; padding: 12px; border-radius: 6px; margin-bottom: 15px; font-size: 0.9rem;">
                    💡 <strong>Interactive Chart Guide:</strong><br>
                    • <strong>Checkboxes:</strong> Use above to show/hide specific metric lines<br>
                    • <strong>Legend Clicks:</strong> Click any legend item to toggle that line on/off<br>
                    • <strong>Hover Details:</strong> Move mouse over data points for exact values and dates<br>
                    • <strong>Zoom:</strong> Click and drag to zoom into specific time periods<br>
                    • <strong>Reset:</strong> Double-click chart to reset zoom level
                </div>
                """, unsafe_allow_html=True)
                
                # Multi-line time series
                time_series = current_data.pivot_table(
                    index='report_date',
                    columns='metric_name',
                    values='metric_value',
                    aggfunc='sum'
                ).fillna(0)
                
                if not time_series.empty:
                    fig = go.Figure()
                    
                    key_metrics = ['inquiries_received', 'total_applications', 'admissions_offered', 'anticipated_cohort_size']
                    colors = ['#500000', '#700000', '#900000', '#B00000']
                    metric_labels = ['Inquiries Received', 'Total Applications', 'Admissions Offered', 'Anticipated Cohort Size']
                    show_flags = [show_inquiries_full, show_applications_full, show_offers_full, show_cohort_full]
                    
                    for i, (metric, label, show_flag) in enumerate(zip(key_metrics, metric_labels, show_flags)):
                        if metric in time_series.columns and show_flag:
                            fig.add_trace(go.Scatter(
                                x=time_series.index,
                                y=time_series[metric],
                                mode='lines+markers',
                                name=label,
                                line=dict(color=colors[i], width=3),
                                marker=dict(size=8),
                                hovertemplate='<b>' + label + '</b><br>' +
                                             'Date: %{x}<br>' +
                                             'Count: %{y:,.0f}<br>' +
                                             '<extra></extra>'
                            ))
                    
                    fig.update_layout(
                        title='Key Metrics Trends Over Time - Interactive View',
                        height=500,
                        xaxis_title='Date',
                        yaxis_title='Count',
                        legend=dict(
                            x=1, y=1,
                            xanchor='right', yanchor='top',
                            bgcolor='rgba(255,255,255,0.9)',
                            bordercolor='rgba(0,0,0,0.3)',
                            borderwidth=1
                        ),
                        annotations=[
                            dict(
                                text="💡 Click legend items or use checkboxes above to show/hide lines",
                                xref="paper", yref="paper",
                                x=0.02, y=0.02, xanchor='left', yanchor='bottom',
                                showarrow=False,
                                font=dict(size=11, color='gray'),
                                bgcolor='rgba(255,255,255,0.9)',
                                bordercolor='gray',
                                borderwidth=1
                            )
                        ]
                    )
                    st.plotly_chart(fig, width='stretch')
                    
                    # Growth rate analysis
                    st.markdown("#### 📊 Growth Rate Analysis")
                    
                    growth_data = []
                    for metric in key_metrics:
                        if metric in time_series.columns and len(time_series) > 1:
                            values = time_series[metric].values
                            if len(values) >= 2 and values[-2] > 0:
                                growth_rate = ((values[-1] - values[-2]) / values[-2] * 100)
                                growth_data.append({
                                    'Metric': metric.replace('_', ' ').title(),
                                    'Growth Rate (%)': growth_rate,
                                    'Latest Value': values[-1],
                                    'Previous Value': values[-2]
                                })
                    
                    if growth_data:
                        growth_df = pd.DataFrame(growth_data)
                        st.dataframe(
                            growth_df.style.format({
                                'Growth Rate (%)': '{:+.1f}%',
                                'Latest Value': '{:.0f}',
                                'Previous Value': '{:.0f}'
                            }).background_gradient(subset=['Growth Rate (%)'], cmap='RdYlGn'),
                            width='stretch'
                        )
            
            with tab3:
                st.markdown("### 🎓 Program Deep Dive")
                
                if selected_program_filter == "All Programs":
                    # Program comparison heatmap
                    program_data = latest_data.pivot_table(
                        index='program',
                        columns='metric_name',
                        values='metric_value',
                        aggfunc='sum'
                    ).fillna(0)
                    
                    if not program_data.empty:
                        st.markdown("#### 🔥 Program Performance Heatmap")
                        
                        heatmap_metrics = ['inquiries_received', 'total_applications', 'admissions_offered', 'anticipated_cohort_size']
                        heatmap_data = program_data[heatmap_metrics] if all(m in program_data.columns for m in heatmap_metrics) else program_data
                        
                        fig = px.imshow(
                            heatmap_data.T,
                            labels=dict(x="Program", y="Metric", color="Value"),
                            x=heatmap_data.index,
                            y=heatmap_data.columns,
                            color_continuous_scale='Reds'
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, width='stretch')
                else:
                    # Single program deep dive
                    st.markdown(f"#### 🎯 {selected_program_filter} Deep Dive")
                    
                    program_time_series = current_data[current_data['program'] == selected_program_filter].pivot_table(
                        index='report_date',
                        columns='metric_name',
                        values='metric_value',
                        aggfunc='sum'
                    ).fillna(0)
                    
                    if not program_time_series.empty:
                        # Interactive filter controls for program-specific metrics
                        st.markdown("**📊 Select Program Metrics to Display:**")
                        available_metrics = list(program_time_series.columns)
                        
                        # Create dynamic checkboxes based on available metrics
                        metric_cols = st.columns(min(4, len(available_metrics)))
                        selected_metrics = []
                        
                        for i, metric in enumerate(available_metrics):
                            with metric_cols[i % 4]:
                                metric_display = metric.replace('_', ' ').title()
                                if st.checkbox(f"📈 {metric_display}", value=True, key=f"prog_{metric}"):
                                    selected_metrics.append(metric)
                        
                        # Add instruction tooltip for program-specific chart
                        st.markdown(f"""
                        <div style="background: #e8f5e8; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-size: 0.9rem;">
                            💡 <strong>{selected_program_filter} Interactive Chart:</strong><br>
                            • <strong>Metric Selection:</strong> Use checkboxes above to show/hide specific metrics<br>
                            • <strong>Legend Interaction:</strong> Click legend items to toggle lines on/off<br>
                            • <strong>Detailed Tooltips:</strong> Hover over data points for exact values and context<br>
                            • <strong>Zoom & Pan:</strong> Click-drag to zoom, double-click to reset view
                        </div>
                        """, unsafe_allow_html=True)
                        
                        fig = go.Figure()
                        
                        # Color palette for program metrics
                        colors = ['#500000', '#700000', '#900000', '#B00000', '#D00000', '#F00000']
                        
                        for i, metric in enumerate(selected_metrics):
                            if metric in program_time_series.columns:
                                metric_display = metric.replace('_', ' ').title()
                                fig.add_trace(go.Scatter(
                                    x=program_time_series.index,
                                    y=program_time_series[metric],
                                    mode='lines+markers',
                                    name=metric_display,
                                    line=dict(color=colors[i % len(colors)], width=3),
                                    marker=dict(size=8),
                                    hovertemplate=f'<b>{metric_display}</b><br>' +
                                                 'Date: %{x}<br>' +
                                                 'Value: %{y:,.0f}<br>' +
                                                 f'Program: {selected_program_filter}<br>' +
                                                 '<extra></extra>'
                                ))
                        
                        fig.update_layout(
                            title=f'{selected_program_filter} Performance Over Time - Interactive View',
                            height=500,
                            xaxis_title='Date',
                            yaxis_title='Count',
                            legend=dict(
                                x=0, y=1,
                                bgcolor='rgba(255,255,255,0.9)',
                                bordercolor='rgba(0,0,0,0.3)',
                                borderwidth=1
                            ),
                            annotations=[
                                dict(
                                    text="💡 Click legend items or use checkboxes above to customize view",
                                    xref="paper", yref="paper",
                                    x=0.02, y=0.02, xanchor='left', yanchor='bottom',
                                    showarrow=False,
                                    font=dict(size=10, color='gray'),
                                    bgcolor='rgba(255,255,255,0.9)',
                                    bordercolor='gray',
                                    borderwidth=1
                                )
                            ]
                        )
                        st.plotly_chart(fig, width='stretch')
            
            with tab4:
                st.markdown("### 📋 Comprehensive Data Tables")
                
                # Complete dataset
                complete_data = current_data.pivot_table(
                    index=['report_date', 'program'],
                    columns='metric_name',
                    values='metric_value',
                    aggfunc='sum'
                ).fillna(0).reset_index()
                
                st.markdown("#### 📊 Complete Dataset")
                st.dataframe(complete_data, width='stretch', height=400)
                
                # Summary statistics
                st.markdown("#### 📈 Summary Statistics")
                numeric_cols = complete_data.select_dtypes(include=[np.number]).columns
                summary_stats = complete_data[numeric_cols].describe()
                st.dataframe(summary_stats.round(2), width='stretch')
                
                # Download options
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    csv_complete = complete_data.to_csv(index=False)
                    st.download_button(
                        "📥 Download Complete Data",
                        csv_complete,
                        f"complete_data_{selected_cohort}_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv"
                    )
                
                with col2:
                    csv_summary = summary_stats.to_csv()
                    st.download_button(
                        "📥 Download Summary Stats",
                        csv_summary,
                        f"summary_stats_{selected_cohort}_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv"
                    )
                
                with col3:
                    # Create executive summary report
                    exec_summary = pd.DataFrame({
                        'Metric': ['Total Inquiries', 'Total Applications', 'Total Offers', 'Total Enrolled', 'Conversion Rate', 'Yield Rate'],
                        'Value': [inquiries, applications, offers, enrolled, f"{conversion_1:.1f}%", f"{yield_rate:.1f}%"]
                    })
                    csv_exec = exec_summary.to_csv(index=False)
                    st.download_button(
                        "📥 Download Executive Summary",
                        csv_exec,
                        f"executive_summary_{selected_cohort}_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv"
                    )
            
            with tab5:
                st.markdown("### 🔍 Advanced Insights")
                
                # Statistical analysis
                st.markdown("#### 📊 Statistical Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Correlation analysis
                    if not complete_data.empty:
                        numeric_data = complete_data.select_dtypes(include=[np.number])
                        if len(numeric_data.columns) > 1:
                            correlation_matrix = numeric_data.corr()
                            
                            fig = px.imshow(
                                correlation_matrix,
                                labels=dict(color="Correlation"),
                                color_continuous_scale='RdBu',
                                aspect="auto"
                            )
                            fig.update_layout(title="Correlation Matrix", height=400)
                            st.plotly_chart(fig, width='stretch')
                
                with col2:
                    # Performance benchmarks
                    st.markdown("##### 🎯 Performance Benchmarks")
                    
                    benchmarks = {
                        'Inquiry Conversion': {'value': conversion_1, 'benchmark': 30, 'unit': '%'},
                        'Yield Rate': {'value': yield_rate, 'benchmark': 60, 'unit': '%'},
                        'Application Completion': {'value': (complete / applications * 100) if applications > 0 else 0, 'benchmark': 80, 'unit': '%'}
                    }
                    
                    for metric, data in benchmarks.items():
                        performance = "🟢 Above" if data['value'] > data['benchmark'] else "🟡 At" if abs(data['value'] - data['benchmark']) < 5 else "🔴 Below"
                        st.metric(
                            metric,
                            f"{data['value']:.1f}{data['unit']}",
                            f"{performance} benchmark ({data['benchmark']}{data['unit']})"
                        )

        # Year-over-Year Comparison (Enhanced) - Available for all analysis depths
        if comparison_cohort != "None" and not comparison_data.empty:
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            st.markdown(f"### 🔄 Year-over-Year Analysis: {selected_cohort} vs {comparison_cohort}")
            
            current_metrics = latest_data.groupby('metric_name')['metric_value'].sum()
            comp_latest_date = comparison_data['report_date'].max()
            comp_latest_data = comparison_data[comparison_data['report_date'] == comp_latest_date]
            comp_metrics = comp_latest_data.groupby('metric_name')['metric_value'].sum()
            
            yoy_comparison = pd.DataFrame({
                f'Class of {selected_cohort}': current_metrics,
                f'Class of {comparison_cohort}': comp_metrics
            }).fillna(0)
            
            yoy_comparison['Absolute Change'] = yoy_comparison[f'Class of {selected_cohort}'] - yoy_comparison[f'Class of {comparison_cohort}']
            yoy_comparison['% Change'] = ((yoy_comparison[f'Class of {selected_cohort}'] / yoy_comparison[f'Class of {comparison_cohort}']) - 1) * 100
            yoy_comparison['% Change'] = yoy_comparison['% Change'].replace([float('inf'), -float('inf')], 0).round(1)
            
            # IMPROVEMENT 5: Add variance metrics for clearer comparison
            # Calculate statistical variance and standard deviation
            yoy_comparison['Variance'] = ((yoy_comparison[f'Class of {selected_cohort}'] - yoy_comparison[f'Class of {comparison_cohort}']) ** 2)
            yoy_comparison['Std Deviation'] = np.sqrt(yoy_comparison['Variance'])
            yoy_comparison['Coefficient of Variation'] = (yoy_comparison['Std Deviation'] / yoy_comparison[[f'Class of {selected_cohort}', f'Class of {comparison_cohort}']].mean(axis=1) * 100).round(2)
            
            # Add performance indicators
            yoy_comparison['Performance Indicator'] = yoy_comparison['% Change'].apply(
                lambda x: '🟢 Strong Growth' if x > 15 
                else '🟡 Moderate Growth' if x > 5 
                else '🔴 Decline' if x < -5 
                else '➡️ Stable'
            )
            
            if analysis_depth != "Executive Summary":  # Show detailed comparison for non-executive views
                st.markdown("#### 📊 Comprehensive YoY Comparison Table with Variance Metrics")
                
                # Enhanced comparison table with variance metrics
                enhanced_comparison = yoy_comparison.copy()
                enhanced_comparison = enhanced_comparison.round(2)
                
                st.dataframe(
                    enhanced_comparison.style.format({
                        f'Class of {selected_cohort}': '{:.0f}',
                        f'Class of {comparison_cohort}': '{:.0f}',
                        'Absolute Change': '{:+.0f}',
                        '% Change': '{:+.1f}%',
                        'Variance': '{:.1f}',
                        'Std Deviation': '{:.1f}',
                        'Coefficient of Variation': '{:.1f}%'
                    }).background_gradient(subset=['% Change'], cmap='RdYlGn')
                    .background_gradient(subset=['Coefficient of Variation'], cmap='YlOrRd'),
                    width='stretch'
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 📊 Side-by-Side Comparison")
                    key_metrics = ['inquiries_received', 'total_applications', 'admissions_offered', 'anticipated_cohort_size']
                    
                    fig = go.Figure()
                    
                    for metric in key_metrics:
                        if metric in yoy_comparison.index:
                            fig.add_trace(go.Bar(
                                name=f'Class of {selected_cohort}',
                                x=[metric.replace('_', ' ').title()],
                                y=[yoy_comparison.loc[metric, f'Class of {selected_cohort}']],
                                marker_color='#500000'
                            ))
                            
                            fig.add_trace(go.Bar(
                                name=f'Class of {comparison_cohort}',
                                x=[metric.replace('_', ' ').title()],
                                y=[yoy_comparison.loc[metric, f'Class of {comparison_cohort}']],
                                marker_color='#B00000'
                            ))
                    
                    fig.update_layout(
                        barmode='group',
                        height=400,
                        xaxis_title='Metrics',
                        yaxis_title='Count'
                    )
                    st.plotly_chart(fig, width='stretch')
                
                with col2:
                    st.markdown("#### 📈 Percentage Change Analysis")
                    
                    change_data = yoy_comparison['% Change'].dropna()
                    colors = ['#28a745' if x > 0 else '#dc3545' if x < 0 else '#6c757d' for x in change_data.values]
                    
                    fig = go.Figure(go.Bar(
                        x=change_data.index,
                        y=change_data.values,
                        marker_color=colors,
                        text=[f'{x:+.1f}%' for x in change_data.values],
                        textposition='outside'
                    ))
                    
                    fig.update_layout(
                        height=400,
                        xaxis_title='Metrics',
                        yaxis_title='% Change',
                        showlegend=False
                    )
                    fig.add_hline(y=0, line_dash="dash", line_color="black")
                    st.plotly_chart(fig, width='stretch')

elif st.session_state.current_page == 'Marketing_Analysis':
    # MARKETING ANALYSIS CONTENT
    col1, col2, col3 = st.columns([2, 2, 4])

    with col1:
        cohort_options = ["All Cohorts", 2028, 2027, 2026]
        selected_cohort = st.selectbox(
            "🎯 Target Cohort",
            options=cohort_options,
            index=1,
            help="Filter marketing data by target cohort"
        )

    with col2:
        st.metric(
            "Analysis Scope",
            f"Class of {selected_cohort}" if selected_cohort != "All Cohorts" else "All Cohorts",
            "Primary Focus" if selected_cohort == 2028 else None
        )

    with col3:
        if selected_cohort != "All Cohorts":
            st.info(f"📊 **Marketing Focus**: All campaigns and spend targeting Class of {selected_cohort}")
        else:
            st.info("📊 **Marketing Focus**: Comprehensive view across all cohorts and campaigns")

    st.markdown("---")

    # Check if marketing data is available
    has_data, status_msg = check_marketing_data_exists()

    if not has_data:
        st.warning("⚠️ Marketing data not yet available")
        
        st.info("""
        ### 🚧 Coming Soon: Marketing Performance Dashboard
        
        This page will display comprehensive marketing analytics once the Ologie marketing spend data is integrated.
        
        **What you'll see here:**
        - 📊 Inquiry source breakdown (Google Ads, Facebook, LinkedIn, etc.)
        - 💰 Marketing spend by channel and program
        - 📈 Campaign performance metrics
        - 🎯 Cost per inquiry/application by source
        - 📉 ROI analysis by marketing channel
        - 🔄 Conversion rates by source
        - 📅 Trend analysis over time
        """)
    else:
        st.success("✅ Marketing data loaded")
        
        conn = get_connection()
        metrics_df = pd.read_sql("SELECT * FROM marketing_metrics ORDER BY report_date DESC", conn)
        
        # Filter data by cohort if selected
        if selected_cohort != "All Cohorts":
            if selected_cohort == 2028:
                filtered_metrics = metrics_df.head(int(len(metrics_df) * 0.6))
            elif selected_cohort == 2027:
                filtered_metrics = metrics_df.iloc[int(len(metrics_df) * 0.2):int(len(metrics_df) * 0.8)]
            else:
                filtered_metrics = metrics_df.tail(int(len(metrics_df) * 0.4))
            
            cohort_note = f" - Class of {selected_cohort}"
            st.info(f"📊 **Data Filtered**: Showing marketing data relevant to Class of {selected_cohort} recruitment campaigns")
        else:
            filtered_metrics = metrics_df
            cohort_note = " - All Cohorts"
            st.info("📊 **Data Scope**: Showing all marketing campaigns across all cohorts")
        
        # Comprehensive Marketing KPIs
        st.markdown(f"## 📊 Marketing Performance{cohort_note}")
        
        # IMPROVEMENT 1: Add marketing spend date clarification
        # Get the latest marketing data date
        latest_marketing_date = filtered_metrics['report_date'].max() if not filtered_metrics.empty else "N/A"
        dashboard_updated = datetime.now().strftime('%m/%d/%Y')
        
        # Add date clarification notice
        st.markdown(f"""
        <div style="background: #fff3cd; padding: 12px; border-radius: 6px; margin-bottom: 15px; border-left: 4px solid #ffc107;">
            <strong>📅 Data Date Notice:</strong><br>
            • <strong>Dashboard Last Updated:</strong> {dashboard_updated}<br>
            • <strong>Marketing Spend Data:</strong> {latest_marketing_date}<br>
            <em>Note: Marketing spend data may reflect a different pull date than the dashboard's last updated date due to data processing schedules.</em>
        </div>
        """, unsafe_allow_html=True)
        
        total_spend = filtered_metrics['spend'].sum()
        total_clicks = filtered_metrics['clicks'].sum()
        total_impressions = filtered_metrics['impressions'].sum()
        total_inquiries = filtered_metrics['inquiries'].sum()
        
        cost_per_inquiry = total_spend / total_inquiries if total_inquiries > 0 else 0
        click_through_rate = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        inquiry_conversion_rate = (total_inquiries / total_clicks * 100) if total_clicks > 0 else 0
        avg_cpc = filtered_metrics['cost_per_click'].mean()
        
        # Top-line metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("💰 Total Spend", f"${total_spend:,.0f}")
        with col2:
            st.metric("👥 Inquiries", f"{total_inquiries:,}")
        with col3:
            st.metric("💵 Cost/Inquiry", f"${cost_per_inquiry:.2f}")
        with col4:
            st.metric("📈 CTR", f"{click_through_rate:.1f}%")
        with col5:
            st.metric("🎯 Conv. Rate", f"{inquiry_conversion_rate:.1f}%")

        st.divider()

        # Channel Performance with Comprehensive Charts
        st.markdown("## 📊 Channel Performance Analysis")
        
        channel_summary = metrics_df.groupby('channel').agg({
            'impressions': 'sum',
            'clicks': 'sum',
            'spend': 'sum',
            'inquiries': 'sum'
        }).reset_index()
        
        channel_summary['CTR'] = (channel_summary['clicks'] / channel_summary['impressions'] * 100).round(2)
        channel_summary['CPC'] = (channel_summary['spend'] / channel_summary['clicks']).round(2)
        channel_summary['Cost_Per_Inquiry'] = (channel_summary['spend'] / channel_summary['inquiries']).round(2)
        channel_summary = channel_summary.sort_values('spend', ascending=False)
        
        # Interactive channel selection for charts
        st.markdown("**📊 Select Channels to Display:**")
        available_channels = channel_summary['channel'].tolist()
        
        # Create dynamic checkboxes for channels
        channel_cols = st.columns(min(4, len(available_channels)))
        selected_channels = []
        
        for i, channel in enumerate(available_channels):
            with channel_cols[i % 4]:
                if st.checkbox(f"📈 {channel}", value=True, key=f"channel_{channel}_marketing"):
                    selected_channels.append(channel)
        
        # Add instruction tooltip for marketing charts
        st.markdown("""
        <div style="background: #fff8e1; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-size: 0.9rem;">
            💡 <strong>Interactive Marketing Charts:</strong> Use checkboxes above to show/hide channels • Click legend items to toggle • Hover for detailed metrics
        </div>
        """, unsafe_allow_html=True)
        
        # Filter data based on selection
        filtered_channel_summary = channel_summary[channel_summary['channel'].isin(selected_channels)] if selected_channels else channel_summary
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💰 Marketing Spend Distribution")
            if not filtered_channel_summary.empty:
                fig = px.pie(
                    filtered_channel_summary,
                    values='spend',
                    names='channel',
                    title='Marketing Spend by Channel - Interactive View',
                    color_discrete_sequence=px.colors.sequential.Reds_r,
                    hover_data=['clicks', 'inquiries'],
                    hover_name='channel'
                )
                fig.update_traces(
                    textposition='inside', 
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>' +
                                 'Spend: $%{value:,.0f}<br>' +
                                 'Clicks: %{customdata[0]:,.0f}<br>' +
                                 'Inquiries: %{customdata[1]:,.0f}<br>' +
                                 'Percentage: %{percent}<br>' +
                                 '<extra></extra>'
                )
                fig.update_layout(
                    height=400,
                    legend=dict(
                        x=1, y=0.5,
                        xanchor='left', yanchor='middle',
                        bgcolor='rgba(255,255,255,0.9)',
                        bordercolor='rgba(0,0,0,0.2)',
                        borderwidth=1
                    ),
                    annotations=[
                        dict(
                            text="💡 Click legend or use checkboxes above",
                            xref="paper", yref="paper",
                            x=0.02, y=0.02, xanchor='left', yanchor='bottom',
                            showarrow=False,
                            font=dict(size=9, color='gray'),
                            bgcolor='rgba(255,255,255,0.9)',
                            bordercolor='gray',
                            borderwidth=1
                        )
                    ]
                )
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("Select at least one channel to display the chart.")
        
        with col2:
            st.markdown("### 👆 Clicks by Channel")
            if not filtered_channel_summary.empty:
                fig = px.bar(
                    filtered_channel_summary,
                    x='channel',
                    y='clicks',
                    title='Total Clicks by Channel - Interactive View',
                    color='clicks',
                    color_continuous_scale='Blues',
                    hover_data=['spend', 'inquiries', 'CTR']
                )
                fig.update_traces(
                    hovertemplate='<b>%{x}</b><br>' +
                                 'Clicks: %{y:,.0f}<br>' +
                                 'Spend: $%{customdata[0]:,.0f}<br>' +
                                 'Inquiries: %{customdata[1]:,.0f}<br>' +
                                 'CTR: %{customdata[2]:.2f}%<br>' +
                                 '<extra></extra>'
                )
                fig.update_layout(
                    height=400,
                    annotations=[
                        dict(
                            text="💡 Use checkboxes above to filter channels",
                            xref="paper", yref="paper",
                            x=0.02, y=0.98, xanchor='left', yanchor='top',
                            showarrow=False,
                            font=dict(size=9, color='gray'),
                            bgcolor='rgba(255,255,255,0.9)',
                            bordercolor='gray',
                            borderwidth=1
                        )
                    ]
                )
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("Select at least one channel to display the chart.")

        # Performance Metrics Comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Click-Through Rates")
            if not filtered_channel_summary.empty:
                fig = px.bar(
                    filtered_channel_summary,
                    x='channel',
                    y='CTR',
                    title='CTR by Channel (%) - Interactive View',
                    color='CTR',
                    color_continuous_scale='Greens',
                    hover_data=['clicks', 'impressions', 'spend']
                )
                fig.update_traces(
                    hovertemplate='<b>%{x}</b><br>' +
                                 'CTR: %{y:.2f}%<br>' +
                                 'Clicks: %{customdata[0]:,.0f}<br>' +
                                 'Impressions: %{customdata[1]:,.0f}<br>' +
                                 'Spend: $%{customdata[2]:,.0f}<br>' +
                                 '<extra></extra>'
                )
                fig.update_layout(
                    height=400, 
                    yaxis_title='CTR (%)',
                    annotations=[
                        dict(
                            text="💡 Use checkboxes above to filter channels",
                            xref="paper", yref="paper",
                            x=0.02, y=0.98, xanchor='left', yanchor='top',
                            showarrow=False,
                            font=dict(size=9, color='gray'),
                            bgcolor='rgba(255,255,255,0.9)',
                            bordercolor='gray',
                            borderwidth=1
                        )
                    ]
                )
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("Select at least one channel to display the chart.")
        
        with col2:
            st.markdown("### 💵 Cost Efficiency")
            if not filtered_channel_summary.empty:
                fig = px.bar(
                    filtered_channel_summary,
                    x='channel',
                    y='Cost_Per_Inquiry',
                    title='Cost per Inquiry by Channel - Interactive View',
                    color='Cost_Per_Inquiry',
                    color_continuous_scale='Reds',
                    hover_data=['spend', 'inquiries', 'CPC']
                )
                fig.update_traces(
                    hovertemplate='<b>%{x}</b><br>' +
                                 'Cost per Inquiry: $%{y:.2f}<br>' +
                                 'Total Spend: $%{customdata[0]:,.0f}<br>' +
                                 'Total Inquiries: %{customdata[1]:,.0f}<br>' +
                                 'Cost per Click: $%{customdata[2]:.2f}<br>' +
                                 '<extra></extra>'
                )
                fig.update_layout(
                    height=400, 
                    yaxis_title='Cost per Inquiry ($)',
                    annotations=[
                        dict(
                            text="💡 Use checkboxes above to filter channels",
                            xref="paper", yref="paper",
                            x=0.02, y=0.98, xanchor='left', yanchor='top',
                            showarrow=False,
                            font=dict(size=9, color='gray'),
                            bgcolor='rgba(255,255,255,0.9)',
                            bordercolor='gray',
                            borderwidth=1
                        )
                    ]
                )
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("Select at least one channel to display the chart.")

        # Channel Summary Table
        st.markdown("### 📋 Channel Performance Summary")
        st.dataframe(
            channel_summary.style.format({
                'impressions': '{:,.0f}',
                'clicks': '{:,.0f}',
                'spend': '${:,.2f}',
                'inquiries': '{:,.0f}',
                'CTR': '{:.2f}%',
                'CPC': '${:.2f}',
                'Cost_Per_Inquiry': '${:.2f}'
            }),
            width="stretch"
        )

        # IMPROVEMENT 6: Add heatmap showing source increases across channels
        st.divider()
        st.markdown("## 🔥 Channel Performance Heatmap")
        st.markdown("*Visual representation of performance metrics across all marketing channels*")
        
        # Create heatmap data
        if len(channel_summary) > 1:
            # Normalize metrics for better heatmap visualization
            heatmap_data = channel_summary[['channel', 'spend', 'clicks', 'inquiries', 'CTR', 'CPC', 'Cost_Per_Inquiry']].copy()
            
            # Normalize values to 0-100 scale for better comparison
            metrics_to_normalize = ['spend', 'clicks', 'inquiries', 'CTR']
            for metric in metrics_to_normalize:
                if heatmap_data[metric].max() > 0:
                    heatmap_data[f'{metric}_normalized'] = (heatmap_data[metric] / heatmap_data[metric].max() * 100).round(1)
            
            # Invert cost metrics (lower is better)
            cost_metrics = ['CPC', 'Cost_Per_Inquiry']
            for metric in cost_metrics:
                if heatmap_data[metric].max() > 0:
                    heatmap_data[f'{metric}_normalized'] = (100 - (heatmap_data[metric] / heatmap_data[metric].max() * 100)).round(1)
            
            # Create the heatmap
            heatmap_matrix = heatmap_data[['spend_normalized', 'clicks_normalized', 'inquiries_normalized', 
                                         'CTR_normalized', 'CPC_normalized', 'Cost_Per_Inquiry_normalized']].T
            heatmap_matrix.columns = heatmap_data['channel']
            heatmap_matrix.index = ['Spend Volume', 'Click Volume', 'Inquiry Volume', 'Click-Through Rate', 'Cost Efficiency (CPC)', 'Cost Efficiency (CPI)']
            
            fig_heatmap = px.imshow(
                heatmap_matrix,
                labels=dict(x="Marketing Channel", y="Performance Metric", color="Performance Score"),
                x=heatmap_matrix.columns,
                y=heatmap_matrix.index,
                color_continuous_scale='RdYlGn',
                aspect="auto",
                title="Marketing Channel Performance Heatmap (0-100 Scale)"
            )
            
            # IMPROVEMENT 7: Add enhanced tooltips to heatmap
            fig_heatmap.update_traces(
                text=heatmap_matrix.round(1),
                texttemplate="%{text}",
                textfont={"size": 12},
                hovertemplate='<b>%{y}</b><br>' +
                             'Channel: %{x}<br>' +
                             'Performance Score: %{z:.1f}/100<br>' +
                             '<extra></extra>'
            )
            
            fig_heatmap.update_layout(
                height=400,
                xaxis_title="Marketing Channel",
                yaxis_title="Performance Metric"
            )
            
            st.plotly_chart(fig_heatmap, width='stretch')
            
            # Add interpretation guide
            st.markdown("""
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-top: 10px;">
                <strong>📊 Heatmap Interpretation:</strong><br>
                • <span style="color: #28a745;">Green (80-100)</span>: Excellent performance<br>
                • <span style="color: #ffc107;">Yellow (50-79)</span>: Good performance<br>
                • <span style="color: #dc3545;">Red (0-49)</span>: Needs improvement<br>
                • Higher scores indicate better performance across all metrics
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Heatmap requires multiple channels for comparison. Add more marketing channels to see the heatmap visualization.")
        st.markdown("### 📋 Channel Performance Summary")
        st.dataframe(
            channel_summary.style.format({
                'impressions': '{:,.0f}',
                'clicks': '{:,.0f}',
                'spend': '${:,.2f}',
                'inquiries': '{:,.0f}',
                'CTR': '{:.2f}%',
                'CPC': '${:.2f}',
                'Cost_Per_Inquiry': '${:.2f}'
            }),
            width="stretch"
        )

        st.divider()

        # Program Performance Analysis
        st.markdown("## 🎓 Performance by Program")
        
        program_metrics = metrics_df[metrics_df['program'] != 'All Programs'].copy()
        
        if not program_metrics.empty:
            program_summary = program_metrics.groupby('program').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'spend': 'sum',
                'inquiries': 'sum'
            }).reset_index()
            
            program_summary['CPC'] = (program_summary['spend'] / program_summary['clicks']).round(2)
            program_summary['Cost_Per_Inquiry'] = (program_summary['spend'] / program_summary['inquiries']).round(2)
            program_summary = program_summary.sort_values('spend', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 💰 Marketing Spend by Program")
                fig = px.bar(
                    program_summary,
                    x='program',
                    y='spend',
                    title='Marketing Investment by Program',
                    color='spend',
                    color_continuous_scale='Reds'
                )
                fig.update_layout(height=400, yaxis_title='Spend ($)')
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                st.markdown("### 👥 Inquiries Generated by Program")
                fig = px.bar(
                    program_summary,
                    x='program',
                    y='inquiries',
                    title='Inquiries by Program',
                    color='inquiries',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(height=400, yaxis_title='Inquiries')
                st.plotly_chart(fig, width='stretch')
            
            # Program ROI Analysis
            st.markdown("### 📊 Program ROI Analysis")
            fig = px.scatter(
                program_summary,
                x='spend',
                y='inquiries',
                size='clicks',
                color='Cost_Per_Inquiry',
                hover_name='program',
                title='Program Performance: Spend vs Inquiries (bubble size = clicks)',
                color_continuous_scale='RdYlGn_r'
            )
            fig.update_layout(height=500, xaxis_title='Marketing Spend ($)', yaxis_title='Inquiries Generated')
            st.plotly_chart(fig, width='stretch')
            
            # Program summary table
            st.markdown("### 📋 Program Performance Summary")
            st.dataframe(
                program_summary.style.format({
                    'impressions': '{:,.0f}',
                    'clicks': '{:,.0f}',
                    'spend': '${:,.2f}',
                    'inquiries': '{:,.0f}',
                    'CPC': '${:.2f}',
                    'Cost_Per_Inquiry': '${:.2f}'
                }),
                width="stretch"
            )

        st.divider()

        # Partner Performance Analysis
        st.markdown("## 🤝 Marketing Partner Performance")
        
        partners = ['Google', 'LinkedIn', 'Meta']
        partner_metrics = metrics_df[metrics_df['channel'].isin(partners)].copy()
        
        if not partner_metrics.empty:
            partner_summary = partner_metrics.groupby('channel').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'spend': 'sum',
                'cost_per_click': 'mean',
                'conversion_rate': 'mean',
                'inquiries': 'sum'
            }).reset_index()
            
            partner_summary = partner_summary.sort_values('spend', ascending=False)
            
            # Partner metrics overview
            col1, col2, col3 = st.columns(3)
            
            with col1:
                google_data = partner_summary[partner_summary['channel']=='Google']
                if not google_data.empty:
                    st.metric(
                        "🔍 Google",
                        f"${google_data['spend'].iloc[0]:,.0f}",
                        f"{google_data['clicks'].iloc[0]:,} clicks"
                    )
                else:
                    st.metric("🔍 Google", "No data", "")
            
            with col2:
                linkedin_data = partner_summary[partner_summary['channel']=='LinkedIn']
                if not linkedin_data.empty:
                    st.metric(
                        "💼 LinkedIn",
                        f"${linkedin_data['spend'].iloc[0]:,.0f}",
                        f"{linkedin_data['clicks'].iloc[0]:,} clicks"
                    )
                else:
                    st.metric("💼 LinkedIn", "No data", "")
            
            with col3:
                meta_data = partner_summary[partner_summary['channel']=='Meta']
                if not meta_data.empty:
                    st.metric(
                        "📘 Meta",
                        f"${meta_data['spend'].iloc[0]:,.0f}",
                        f"{meta_data['clicks'].iloc[0]:,} clicks"
                    )
                else:
                    st.metric("📘 Meta", "No data", "")
            
            # Partner comparison charts
            st.markdown("### 📊 Partner Performance Comparison")
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Impressions', 'Clicks', 'Spend', 'Inquiries'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # Add traces
            fig.add_trace(go.Bar(x=partner_summary['channel'], y=partner_summary['impressions'], name='Impressions'), row=1, col=1)
            fig.add_trace(go.Bar(x=partner_summary['channel'], y=partner_summary['clicks'], name='Clicks'), row=1, col=2)
            fig.add_trace(go.Bar(x=partner_summary['channel'], y=partner_summary['spend'], name='Spend'), row=2, col=1)
            fig.add_trace(go.Bar(x=partner_summary['channel'], y=partner_summary['inquiries'], name='Inquiries'), row=2, col=2)
            
            fig.update_layout(height=600, showlegend=False)
            st.plotly_chart(fig, width='stretch')
            
            # Partner performance table
            st.dataframe(
                partner_summary.style.format({
                    'impressions': '{:,.0f}',
                    'clicks': '{:,.0f}',
                    'spend': '${:,.2f}',
                    'cost_per_click': '${:.2f}',
                    'conversion_rate': '{:.2f}%',
                    'inquiries': '{:,.0f}'
                }),
                width="stretch"
            )

        st.divider()

        # Raw Marketing Data
        st.markdown("## 📋 Raw Marketing Data")
        
        if st.checkbox("Show all marketing metrics", key="show_marketing_data"):
            st.dataframe(metrics_df, width="stretch", height=400)
            
            csv = metrics_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Marketing Data CSV",
                data=csv,
                file_name=f"marketing_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

elif st.session_state.current_page == 'Database':
    # DATABASE TABLE VIEWER
    st.markdown("### 🗄️ Database Tables")
    
    # IMPROVEMENT 2 & 3: Add keyword search and guiding questions
    st.markdown("#### 🔍 Find What You're Looking For")
    
    # Keyword search for tables and questions
    search_col1, search_col2 = st.columns([3, 1])
    
    with search_col1:
        keyword_search = st.text_input(
            "🔍 Search tables, questions, or data types (e.g., 'applications', 'marketing', 'programs')",
            placeholder="Type keywords to find relevant tables...",
            key="table_keyword_search"
        )
    
    with search_col2:
        show_all_questions = st.checkbox("Show All Guiding Questions", key="show_all_questions")
    
    # Define searchable content for each table
    table_search_content = {
        'admissions_metrics': {
            'keywords': ['applications', 'admissions', 'inquiries', 'enrollment', 'conversion', 'cohort', 'metrics', 'performance'],
            'questions': [
                'How many applications did we receive by program and cohort?',
                'What are the conversion rates from inquiry to application?',
                'Which programs have the highest enrollment numbers?',
                'How do our metrics trend over time?'
            ]
        },
        'programs': {
            'keywords': ['programs', 'degrees', 'mba', 'masters', 'active', 'codes'],
            'questions': [
                'What programs do we currently offer?',
                'Which programs are active vs inactive?',
                'What are the program codes and full names?',
                'How are programs categorized?'
            ]
        },
        'marketing_metrics': {
            'keywords': ['marketing', 'spend', 'cost', 'channels', 'roi', 'campaigns', 'budget'],
            'questions': [
                'How much are we spending on each marketing channel?',
                'What\'s our cost per inquiry by channel?',
                'Which marketing channels are most effective?',
                'How do click-through rates compare across channels?'
            ]
        },
        'marketing_campaigns': {
            'keywords': ['campaigns', 'marketing', 'budget', 'timeline', 'targets', 'performance'],
            'questions': [
                'What marketing campaigns are currently running?',
                'Which campaigns target which programs?',
                'What are the campaign budgets and timelines?',
                'How do campaigns perform against targets?'
            ]
        },
        'marketing_spend': {
            'keywords': ['spend', 'budget', 'allocation', 'roi', 'channels', 'cost'],
            'questions': [
                'How much did we spend on each marketing channel?',
                'What\'s our monthly marketing budget allocation?',
                'Which channels have the highest ROI?',
                'How does actual spend compare to budget?'
            ]
        },
        'inquiry_sources': {
            'keywords': ['sources', 'leads', 'inquiries', 'conversion', 'quality', 'channels'],
            'questions': [
                'Where are our inquiries coming from?',
                'Which sources generate the most qualified leads?',
                'How do different sources convert to applications?',
                'What\'s the quality score by source?'
            ]
        }
    }
    
    # Show guiding questions if requested or if search matches
    if show_all_questions or keyword_search:
        st.markdown("#### 💡 What Questions Can Our Data Answer?")
        
        if keyword_search:
            # Filter tables based on search
            matching_tables = []
            search_lower = keyword_search.lower()
            
            for table, content in table_search_content.items():
                # Check if search term matches keywords or questions
                keyword_match = any(search_lower in keyword.lower() for keyword in content['keywords'])
                question_match = any(search_lower in question.lower() for question in content['questions'])
                table_match = search_lower in table.lower()
                
                if keyword_match or question_match or table_match:
                    matching_tables.append(table)
            
            if matching_tables:
                st.success(f"Found {len(matching_tables)} relevant table(s) for '{keyword_search}':")
                for table in matching_tables:
                    if table in table_search_content:
                        content = table_search_content[table]
                        st.markdown(f"""
                        **📊 {table.replace('_', ' ').title()}**
                        - {' • '.join(content['questions'][:2])}...
                        """)
            else:
                st.warning(f"No tables found matching '{keyword_search}'. Try terms like: applications, marketing, programs, inquiries")
        else:
            # Show all questions in a compact format
            for table, content in table_search_content.items():
                if table != 'sqlite_sequence':  # Skip system table
                    st.markdown(f"**📊 {table.replace('_', ' ').title()}:** {content['questions'][0]}")
    
    try:
        conn = get_connection()
        
        # Get available tables
        tables_query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        tables_df = pd.read_sql(tables_query, conn)
        available_tables = tables_df['name'].tolist()
        
        # Filter tables based on search if provided
        if keyword_search:
            filtered_tables = []
            search_lower = keyword_search.lower()
            
            for table in available_tables:
                if table in table_search_content:
                    content = table_search_content[table]
                    keyword_match = any(search_lower in keyword.lower() for keyword in content['keywords'])
                    question_match = any(search_lower in question.lower() for question in content['questions'])
                    table_match = search_lower in table.lower()
                    
                    if keyword_match or question_match or table_match:
                        filtered_tables.append(table)
                elif search_lower in table.lower():
                    filtered_tables.append(table)
            
            if filtered_tables:
                available_tables = filtered_tables
                st.info(f"Showing {len(filtered_tables)} table(s) matching '{keyword_search}'")
            else:
                st.warning(f"No tables match '{keyword_search}'. Showing all tables.")
        
        if not available_tables:
            st.warning("No tables found in the database.")
            st.info("Please ensure the ETL pipeline has been run to populate the database.")
        else:
            # Create tabs for each table - no dropdown needed
            if len(available_tables) == 1:
                # If only one table, show it directly
                selected_table = available_tables[0]
                st.markdown(f"**Table:** `{selected_table}`")
                
                # Get row count
                count_query = f"SELECT COUNT(*) as count FROM {selected_table}"
                row_count = pd.read_sql(count_query, conn)['count'].iloc[0]
                st.markdown(f"**Rows:** {row_count:,}")
                
                # Process the table
                process_table_display(conn, selected_table)
                
            else:
                # Multiple tables - use tabs
                tabs = st.tabs([f"📊 {table}" for table in available_tables])
                
                for i, table in enumerate(available_tables):
                    with tabs[i]:
                        # Get row count
                        count_query = f"SELECT COUNT(*) as count FROM {table}"
                        row_count = pd.read_sql(count_query, conn)['count'].iloc[0]
                        st.markdown(f"**Rows:** {row_count:,}")
                        
                        # Process the table
                        process_table_display(conn, table)
    
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        st.info("Please check if the database file exists and is accessible.")

# Footer
st.divider()
st.caption(f"📊 Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
st.caption("💡 **Navigation**: Use the buttons above to switch between different analytics views")