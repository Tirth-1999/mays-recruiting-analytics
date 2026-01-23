"""
Mays Online Flex Recruiting Analytics Platform
Single-Page Application with Navigation
"""
import streamlit as st
import streamlit.components.v1
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
    initial_sidebar_state="expanded"
)

# Remove top padding and adjust layout for sidebar
st.markdown("""
<style>
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

# Program name normalization function
def normalize_program_name(program_name):
    """
    Normalize program names to match between marketing and admissions data.
    Examples:
    - "Flex Online Mba" -> "MBA"
    - "Flex Online Accounting" -> "ACCT"
    - "MBA" -> "MBA"
    - "MS ACCT" -> "ACCT"
    """
    if not program_name or pd.isna(program_name):
        return None
    
    # Convert to uppercase for matching
    name_upper = str(program_name).upper()
    
    # Mapping dictionary for common program abbreviations
    program_map = {
        'MBA': 'MBA',
        'ACCOUNTING': 'ACCT',
        'ACCT': 'ACCT',
        'MARKETING': 'MKTG',
        'MKTG': 'MKTG',
        'MIS': 'MISY',
        'MISY': 'MISY',
        'HRM': 'HRM',
        'HUMAN RESOURCE': 'HRM',
        'ENTREPRENEURIAL LEADERSHIP': 'ENLD',
        'ENLD': 'ENLD',
        'AI AND BUSINESS': 'SPBA',
        'SPBA': 'SPBA',
        'ARTIFICIAL INTELLIGENCE': 'SPBA'
    }
    
    # Check each key in the mapping
    for key, value in program_map.items():
        if key in name_upper:
            return value
    
    # If no match found, return the last word (usually the program abbreviation)
    words = name_upper.split()
    if words:
        return words[-1]
    
    return name_upper

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
    """Helper function to display table data with filtering options - styled like Marketing Analysis"""
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
        
        # Show formatted table description with darker background (matching Marketing Analysis)
        if selected_table in table_descriptions:
            desc = table_descriptions[selected_table]
            
            st.markdown(f"""
            <div style="text-align: center;
                        padding: 20px;
                        background: #e9ecef;
                        border-radius: 8px;
                        margin: 20px 0;">
                <h4 style="color: #500000; margin-top: 0; margin-bottom: 15px; font-size: 18px;">
                    {desc['icon']} {desc['title']}
                </h4>
                <p style="margin: 0 0 15px 0; color: #495057; font-weight: 600; font-size: 15px;">
                    💡 What questions can this table help answer?
                </p>
                <div style="background: white;
                            padding: 15px 20px;
                            border-radius: 6px;
                            max-width: 700px;
                            margin: 0 auto;
                            box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                    {''.join([f'<p style="margin: 8px 0; color: #495057; font-size: 14px; line-height: 1.5;">{q}</p>' for q in desc['questions']])}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="text-align: center;
                        padding: 15px;
                        background: #e9ecef;
                        border-radius: 8px;
                        margin: 20px 0;">
                <strong style="color: #500000;">📋 Table:</strong> <code>{selected_table}</code><br>
                <em style="color: #6c757d;">Explore the data to understand what insights it can provide.</em>
            </div>
            """, unsafe_allow_html=True)
        
        # Get table info
        table_info_query = f"PRAGMA table_info({selected_table})"
        table_info = pd.read_sql(table_info_query, conn)
        
        # Get row count
        count_query = f"SELECT COUNT(*) as count FROM {selected_table}"
        row_count = pd.read_sql(count_query, conn)['count'].iloc[0]
        
        # Show row count centered
        st.markdown(f"""
        <div style="text-align: center; margin: 15px 0; color: #6c757d;">
            <strong>{row_count:,}</strong> total rows in this table
        </div>
        """, unsafe_allow_html=True)
        
        # Show table schema in expander
        with st.expander("📋 View Table Schema"):
            st.dataframe(table_info[['name', 'type', 'notnull', 'pk']], use_container_width=True)
        
        # FILTERS SECTION with header
        st.markdown("""
        <div class="section-header">
            <h3>🔍 Filter & Explore Data</h3>
        </div>
        """, unsafe_allow_html=True)
        
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
                    "📋 Select Columns", 
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
                    "📊 Row Limit", 
                    min_value=10, 
                    max_value=1000, 
                    value=100, 
                    step=10,
                    key=f"limit_{selected_table}"
                )
            
            with filter_col3:
                # Sort options
                sort_columns = ['None'] + list(full_data.columns)
                sort_by = st.selectbox("🔄 Sort By", sort_columns, key=f"sort_{selected_table}")
            
            # Sort order on new row if sort is selected
            if sort_by != 'None':
                sort_order = st.radio(
                    "Sort Order", 
                    ['Ascending', 'Descending'], 
                    horizontal=True,
                    key=f"order_{selected_table}"
                )
            else:
                sort_order = 'Ascending'
            
            # Text search filter - FULL WIDTH
            search_term = st.text_input(
                "🔍 Search in all columns",
                placeholder="Type to search across all columns (case-insensitive)...",
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
            
            # DATA DISPLAY SECTION with header
            st.markdown("""
            <div class="section-header">
                <h3>📊 Data Table</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Showing {len(filtered_data):,} of {len(full_data):,} rows**")
            
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

/* Remove bottom border from block container */
.block-container {
    padding-bottom: 1rem !important;
    border-bottom: none !important;
}

/* Footer responsive styling */
@media (max-width: 768px) {
    .footer-content {
        text-align: center !important;
    }
}
</style>
""", unsafe_allow_html=True)

# Professional Mays Business School Banner
st.markdown("""
    <div style='background: linear-gradient(135deg, #500000 0%, #700000 50%, #500000 100%); 
                padding: 1.5rem 2rem; 
                border-radius: 10px; 
                text-align: center;
                border: 3px solid #C5A572;
                margin-bottom: 1rem;'>
        <img src='data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyBpZD0iTGF5ZXJfMSIgZGF0YS1uYW1lPSJMYXllciAxIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDgwIDEwODAiPgogIDxkZWZzPgogICAgPHN0eWxlPgogICAgICAuY2xzLTEgewogICAgICAgIGZpbGw6ICM1MDAwMDA7CiAgICAgIH0KCiAgICAgIC5jbHMtMSwgLmNscy0yLCAuY2xzLTMgewogICAgICAgIHN0cm9rZS13aWR0aDogMHB4OwogICAgICB9CgogICAgICAuY2xzLTIgewogICAgICAgIGZpbGw6ICNiMWIzYjY7CiAgICAgIH0KCiAgICAgIC5jbHMtMyB7CiAgICAgICAgZmlsbDogI2ZmZjsKICAgICAgfQogICAgPC9zdHlsZT4KICA8L2RlZnM+CiAgPHJlY3QgY2xhc3M9ImNscy0xIiB4PSIyMDEuMjgiIHk9IjIyMi41NyIgd2lkdGg9IjYyOS43OSIgaGVpZ2h0PSI2MzQuNzkiLz4KICA8cG9seWdvbiBjbGFzcz0iY2xzLTMiIHBvaW50cz0iNzQ3LjQ0IDQ3NS4yMiA3MDAuNjcgNDc1LjIyIDY5Ny45NyA0NzUuMjIgNjk2Ljc1IDQ3Ny42NyA2NjIuODQgNTQ4LjI3IDYyOC44IDQ3Ny42MyA2MjcuNjEgNDc1LjIyIDYyNC45MiA0NzUuMjIgNTc5LjcxIDQ3NS4yMiA1NzUuNDQgNDc1LjIyIDU3NS40NCA0NzkuNTIgNTc1LjQ0IDUwMy41OSA1NzUuNDQgNTA3LjkgNTc5LjcxIDUwNy45IDU4Ny40NCA1MDcuOSA1ODcuNDQgNjA5LjAxIDU3OS4wOCA2MDkuMDEgNTc0Ljc4IDYwOS4wMSA1NzQuNzggNjEzLjMyIDU3NC43OCA2MzcuMzkgNTc0Ljc4IDY0MS42OSA1NzkuMDggNjQxLjY5IDYyOS44NSA2NDEuNjkgNjM0LjE1IDY0MS42OSA2MzQuMTUgNjM3LjM5IDYzNC4xNSA2MTMuMzIgNjM0LjE1IDYwOS4wMSA2MjkuODUgNjA5LjAxIDYyMS4wNyA2MDkuMDEgNjIxLjA3IDUzNy4yNSA2NTguOTkgNjE1LjQ1IDY2Mi44NCA2MjMuNDMgNjY2Ljc2IDYxNS40NSA3MDUuMDcgNTM3LjA4IDcwNS4wNyA2MDkuMDEgNjk2LjcxIDYwOS4wMSA2OTIuMzcgNjA5LjAxIDY5Mi4zNyA2MTMuMzIgNjkyLjM3IDYzNy4zOSA2OTIuMzcgNjQxLjY5IDY5Ni43MSA2NDEuNjkgNzQ3LjQ0IDY0MS42OSA3NTEuNzUgNjQxLjY5IDc1MS43NSA2MzcuMzkgNzUxLjc1IDYxMy4zMiA3NTEuNzUgNjA5LjAxIDc0Ny40NCA2MDkuMDEgNzM4LjcgNjA5LjAxIDczOC43IDUwNy45IDc0Ny40NCA1MDcuOSA3NTEuNzUgNTA3LjkgNzUxLjc1IDUwMy41OSA3NTEuNzUgNDc5LjUyIDc1MS43NSA0NzUuMjIgNzQ3LjQ0IDQ3NS4yMiIvPgogIDxwYXRoIGNsYXNzPSJjbHMtMyIgZD0iTTQ1Mi42LDYwOC45MWgtMTMuNTFsLTQzLjk1LTEwMS40N2g4LjQ3di0zMi44MmgtNzAuNTR2MzIuNzFoOS43M2wtNDMuOTEsMTAxLjQ3aC0xOC4zdjMyLjcxaDY0LjAzdi0zMi43MWgtOS4zMWw3LjMxLTE2LjloNTIuODNsNy4yOCwxNi45aC05LjgzdjMyLjcxaDY0LjA2di0zMi43MWwtNC4zNy4xMVpNMzgxLjI5LDU1OS4zM2gtMjQuNDlsMTIuMjUtMjguMzgsMTIuMjUsMjguMzhaIi8+CiAgPHBvbHlnb24gY2xhc3M9ImNscy0zIiBwb2ludHM9IjY5My43IDM0OC4yNSAzMzcuNDkgMzQ4LjI1IDMzMi41NiAzNDguMjUgMzMyLjU2IDM1My4xOCAzMzIuNTYgNDQ4LjM1IDMzMi41NiA0NTMuMjggMzM3LjQ5IDQ1My4yOCAzOTkgNDUzLjI4IDQwMy45MyA0NTMuMjggNDAzLjkzIDQ0OC4zNSA0MDMuOTMgNDEzLjAxIDQ3OS45MyA0MTMuMDEgNDc5LjkzIDY2My43NyA0NDQuNTUgNjYzLjc3IDQzOS42NSA2NjMuNzcgNDM5LjY1IDY2OC43IDQzOS42NSA3MzAuMjEgNDM5LjY1IDczNS4xNSA0NDQuNTUgNzM1LjE1IDU4Ni42IDczNS4xNSA1OTEuNTQgNzM1LjE1IDU5MS41NCA3MzAuMjEgNTkxLjU0IDY2OC43IDU5MS41NCA2NjMuNzcgNTg2LjYgNjYzLjc3IDU1MS4zIDY2My43NyA1NTEuMyA0MTMuMDEgNjI2Ljg0IDQxMy4wMSA2MjYuODQgNDQ3Ljg5IDYyNi44NCA0NTIuODMgNjMxLjc3IDQ1Mi44MyA2OTMuNyA0NTIuODMgNjk4LjY0IDQ1Mi44MyA2OTguNjQgNDQ3Ljg5IDY5OC42NCAzNTMuMTggNjk4LjY0IDM0OC4yNSA2OTMuNyAzNDguMjUiLz4KICA8cG9seWdvbiBjbGFzcz0iY2xzLTIiIHBvaW50cz0iNTYxLjgzIDY5My4wNiA1NzYuODggNjc3LjU2IDU3Ni44OCA3MjAuMDMgNTYxLjgzIDcwNS42NSA1NjEuODMgNjkzLjA2Ii8+CiAgPHBvbHlnb24gY2xhc3M9ImNscy0yIiBwb2ludHM9IjUzNi43OCA2NzguNjggNTIxLjcgNjkzLjUxIDUyMS43IDM4My40NSA1MzYuNzggMzk4LjQ2IDUzNi43OCA2NzguNjgiLz4KICA8cG9seWdvbiBjbGFzcz0iY2xzLTIiIHBvaW50cz0iMzYyLjcyIDM3Ny45OSAzNDcuMjUgMzYyLjk0IDY3Ni40NSAzNjIuOTQgNjU3IDM3Ny45OSAzNjIuNzIgMzc3Ljk5Ii8+CiAgPHBvbHlnb24gY2xhc3M9ImNscy0yIiBwb2ludHM9IjY4NC40MyA0MzkuMDQgNjY5LjM5IDQyNC42NiA2NjkuMzkgMzg2LjM4IDY4NC40MyAzNzAuOTIgNjg0LjQzIDQzOS4wNCIvPgogIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTg1My40Niw4NDQuOGMwLTYuOTgsNS42NS0xMi42MywxMi42My0xMi42M3MxMi42Myw1LjY1LDEyLjYzLDEyLjYzLTUuNjUsMTIuNjMtMTIuNjMsMTIuNjMtMTIuNjMtNS42NS0xMi42My0xMi42M2gwWk04NzUuNjQsODQ0LjhjLS4zNS01LjI2LTQuOS05LjI1LTEwLjE2LTguOS01LjI2LjM1LTkuMjUsNC45LTguOSwxMC4xNi4zMyw1LjAxLDQuNDksOC45MSw5LjUxLDguOTIsNS4zNS0uMDcsOS42My00LjQ3LDkuNTYtOS44MiwwLS4xMiwwLS4yNC0uMDEtLjM2Wk04NjEuMjMsODM3LjU5aDUuMzJjMy41LDAsNS4yOCwxLjE5LDUuMjgsNC4yLjIsMS45Mi0xLjIsMy42NC0zLjEyLDMuODQtLjIxLjAyLS40Mi4wMi0uNjIsMGwzLjg1LDYuMjZoLTIuNzNsLTMuNzQtNi4yM2gtMS42MXY2LjEyaC0yLjY2bC4wNC0xNC4yMVpNODYzLjg4LDg0My43MWgyLjM0YzEuNTcsMCwyLjk0LS4yMSwyLjk0LTIuMTNzLTEuNTQtMS45Ni0yLjktMS45NmgtMi4zOHY0LjA5WiIvPgo8L3N2Zz4=' 
             style='width: 90px; height: 90px; margin-bottom: 0.5rem;' />
        <h1 style='color: white; margin: 0.3rem 0; font-size: 2.5rem; font-weight: bold;'>
            Mays Online Flex Recruiting Analytics Platform
        </h1>
        <p style='color: #C5A572; margin: 0.3rem 0; font-size: 1.1rem;'>
            Admissions Analytics & Strategic Insights
        </p>
        <p style='color: white; margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.9;'>
            MBA • MS ACCT • MS HRM • MS MISY • MS MKTG • MS ENLD • MS SPBA
        </p>
    </div>
""", unsafe_allow_html=True)

# Navigation Menu with forced equal heights using aggressive CSS
st.markdown("""
<style>
/* Active navigation button styling */
div[data-testid="stButton"] button[kind="primary"] {
    background-color: #500000 !important;
    color: white !important;
    border: 2px solid #500000 !important;
}
div[data-testid="stButton"] button[kind="secondary"] {
    background-color: white !important;
    color: #500000 !important;
    border: 2px solid #e0e0e0 !important;
}
</style>
""", unsafe_allow_html=True)

# Sidebar Navigation with elegant design
with st.sidebar:
    st.markdown("""
    <style>
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* Reduce top padding of sidebar */
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }
    
    /* Elegant logo/brand section - more compact */
    .sidebar-brand {
        text-align: center;
        padding: 10px 10px 15px 10px;
        margin-bottom: 15px;
        border-bottom: 2px solid #C5A572;
    }
    
    .sidebar-brand-title {
        color: #500000;
        font-size: 18px;
        font-weight: bold;
        margin: 8px 0 3px 0;
    }
    
    .sidebar-brand-subtitle {
        color: #666;
        font-size: 11px;
        margin: 0;
    }
    
    /* Navigation section divider */
    .nav-section-title {
        color: #500000;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 20px 0 10px 0;
        padding-left: 5px;
        opacity: 0.7;
    }
    
    /* Style sidebar buttons - elegant and minimal */
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        text-align: left !important;
        padding: 10px 15px !important;
        margin: 2px 0 !important;
        border-radius: 8px !important;
        border: none !important;
        background: transparent !important;
        color: #495057 !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #f0f2f6 !important;
        color: #500000 !important;
        transform: translateX(3px) !important;
    }
    
    /* Active/Primary button styling - elegant highlight */
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #500000 0%, #700000 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 8px rgba(80, 0, 0, 0.2) !important;
    }
    
    [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        transform: translateX(3px) !important;
        box-shadow: 0 4px 12px rgba(80, 0, 0, 0.3) !important;
    }
    
    /* Info cards in sidebar */
    .sidebar-info-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 12px;
        margin: 15px 0;
        font-size: 12px;
    }
    
    .sidebar-info-card strong {
        color: #500000;
        display: block;
        margin-bottom: 5px;
    }
    
    .sidebar-stat {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border-left: 3px solid #C5A572;
        padding: 10px;
        margin: 8px 0;
        border-radius: 4px;
        font-size: 11px;
    }
    
    .sidebar-stat-value {
        color: #500000;
        font-size: 18px;
        font-weight: bold;
        display: block;
    }
    
    .sidebar-stat-label {
        color: #666;
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Brand/Logo Section - more compact
    st.markdown("""
    <div class="sidebar-brand">
        <img src='data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyBpZD0iTGF5ZXJfMSIgZGF0YS1uYW1lPSJMYXllciAxIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDgwIDEwODAiPgogIDxkZWZzPgogICAgPHN0eWxlPgogICAgICAuY2xzLTEgewogICAgICAgIGZpbGw6ICM1MDAwMDA7CiAgICAgIH0KCiAgICAgIC5jbHMtMSwgLmNscy0yLCAuY2xzLTMgewogICAgICAgIHN0cm9rZS13aWR0aDogMHB4OwogICAgICB9CgogICAgICAuY2xzLTIgewogICAgICAgIGZpbGw6ICNiMWIzYjY7CiAgICAgIH0KCiAgICAgIC5jbHMtMyB7CiAgICAgICAgZmlsbDogI2ZmZjsKICAgICAgfQogICAgPC9zdHlsZT4KICA8L2RlZnM+CiAgPHJlY3QgY2xhc3M9ImNscy0xIiB4PSIyMDEuMjgiIHk9IjIyMi41NyIgd2lkdGg9IjYyOS43OSIgaGVpZ2h0PSI2MzQuNzkiLz4KICA8cG9seWdvbiBjbGFzcz0iY2xzLTMiIHBvaW50cz0iNzQ3LjQ0IDQ3NS4yMiA3MDAuNjcgNDc1LjIyIDY5Ny45NyA0NzUuMjIgNjk2Ljc1IDQ3Ny42NyA2NjIuODQgNTQ4LjI3IDYyOC44IDQ3Ny42MyA2MjcuNjEgNDc1LjIyIDYyNC45MiA0NzUuMjIgNTc5LjcxIDQ3NS4yMiA1NzUuNDQgNDc1LjIyIDU3NS40NCA0NzkuNTIgNTc1LjQ0IDUwMy41OSA1NzUuNDQgNTA3LjkgNTc5LjcxIDUwNy45IDU4Ny40NCA1MDcuOSA1ODcuNDQgNjA5LjAxIDU3OS4wOCA2MDkuMDEgNTc0Ljc4IDYwOS4wMSA1NzQuNzggNjEzLjMyIDU3NC43OCA2MzcuMzkgNTc0Ljc4IDY0MS42OSA1NzkuMDggNjQxLjY5IDYyOS44NSA2NDEuNjkgNjM0LjE1IDY0MS42OSA2MzQuMTUgNjM3LjM5IDYzNC4xNSA2MTMuMzIgNjM0LjE1IDYwOS4wMSA2MjkuODUgNjA5LjAxIDYyMS4wNyA2MDkuMDEgNjIxLjA3IDUzNy4yNSA2NTguOTkgNjE1LjQ1IDY2Mi44NCA2MjMuNDMgNjY2Ljc2IDYxNS40NSA3MDUuMDcgNTM3LjA4IDcwNS4wNyA2MDkuMDEgNjk2LjcxIDYwOS4wMSA2OTIuMzcgNjA5LjAxIDY5Mi4zNyA2MTMuMzIgNjkyLjM3IDYzNy4zOSA2OTIuMzcgNjQxLjY5IDY5Ni43MSA2NDEuNjkgNzQ3LjQ0IDY0MS42OSA3NTEuNzUgNjQxLjY5IDc1MS43NSA2MzcuMzkgNzUxLjc1IDYxMy4zMiA3NTEuNzUgNjA5LjAxIDc0Ny40NCA2MDkuMDEgNzM4LjcgNjA5LjAxIDczOC43IDUwNy45IDc0Ny40NCA1MDcuOSA3NTEuNzUgNTA3LjkgNzUxLjc1IDUwMy41OSA3NTEuNzUgNDc5LjUyIDc1MS43NSA0NzUuMjIgNzQ3LjQ0IDQ3NS4yMiIvPgogIDxwYXRoIGNsYXNzPSJjbHMtMyIgZD0iTTQ1Mi42LDYwOC45MWgtMTMuNTFsLTQzLjk1LTEwMS40N2g4LjQ3di0zMi44MmgtNzAuNTR2MzIuNzFoOS43M2wtNDMuOTEsMTAxLjQ3aC0xOC4zdjMyLjcxaDY0LjAzdi0zMi43MWgtOS4zMWw3LjMxLTE2LjloNTIuODNsNy4yOCwxNi45aC05LjgzdjMyLjcxaDY0LjA2di0zMi43MWwtNC4zNy4xMVpNMzgxLjI5LDU1OS4zM2gtMjQuNDlsMTIuMjUtMjguMzgsMTIuMjUsMjguMzhaIi8+CiAgPHBvbHlnb24gY2xhc3M9ImNscy0zIiBwb2ludHM9IjY5My43IDM0OC4yNSAzMzcuNDkgMzQ4LjI1IDMzMi41NiAzNDguMjUgMzMyLjU2IDM1My4xOCAzMzIuNTYgNDQ4LjM1IDMzMi41NiA0NTMuMjggMzM3LjQ5IDQ1My4yOCAzOTkgNDUzLjI4IDQwMy45MyA0NTMuMjggNDAzLjkzIDQ0OC4zNSA0MDMuOTMgNDEzLjAxIDQ3OS45MyA0MTMuMDEgNDc5LjkzIDY2My43NyA0NDQuNTUgNjYzLjc3IDQzOS42NSA2NjMuNzcgNDM5LjY1IDY2OC43IDQzOS42NSA3MzAuMjEgNDM5LjY1IDczNS4xNSA0NDQuNTUgNzM1LjE1IDU4Ni42IDczNS4xNSA1OTEuNTQgNzM1LjE1IDU5MS41NCA3MzAuMjEgNTkxLjU0IDY2OC43IDU5MS41NCA2NjMuNzcgNTg2LjYgNjYzLjc3IDU1MS4zIDY2My43NyA1NTEuMyA0MTMuMDEgNjI2Ljg0IDQxMy4wMSA2MjYuODQgNDQ3Ljg5IDYyNi44NCA0NTIuODMgNjMxLjc3IDQ1Mi44MyA2OTMuNyA0NTIuODMgNjk4LjY0IDQ1Mi44MyA2OTguNjQgNDQ3Ljg5IDY5OC42NCAzNTMuMTggNjk4LjY0IDM0OC4yNSA2OTMuNyAzNDguMjUiLz4KICA8cG9seWdvbiBjbGFzcz0iY2xzLTIiIHBvaW50cz0iNTYxLjgzIDY5My4wNiA1NzYuODggNjc3LjU2IDU3Ni44OCA3MjAuMDMgNTYxLjgzIDcwNS42NSA1NjEuODMgNjkzLjA2Ii8+CiAgPHBvbHlnb24gY2xhc3M9ImNscy0yIiBwb2ludHM9IjUzNi43OCA2NzguNjggNTIxLjcgNjkzLjUxIDUyMS43IDM4My40NSA1MzYuNzggMzk4LjQ2IDUzNi43OCA2NzguNjgiLz4KICA8cG9seWdvbiBjbGFzcz0iY2xzLTIiIHBvaW50cz0iMzYyLjcyIDM3Ny45OSAzNDcuMjUgMzYyLjk0IDY3Ni40NSAzNjIuOTQgNjU3IDM3Ny45OSAzNjIuNzIgMzc3Ljk5Ii8+CiAgPHBvbHlnb24gY2xhc3M9ImNscy0yIiBwb2ludHM9IjY4NC40MyA0MzkuMDQgNjY5LjM5IDQyNC42NiA2NjkuMzkgMzg2LjM4IDY4NC40MyAzNzAuOTIgNjg0LjQzIDQzOS4wNCIvPgogIDxwYXRoIGNsYXNzPSJjbHMtMSIgZD0iTTg1My40Niw4NDQuOGMwLTYuOTgsNS42NS0xMi42MywxMi42My0xMi42M3MxMi42Myw1LjY1LDEyLjYzLDEyLjYzLTUuNjUsMTIuNjMtMTIuNjMsMTIuNjMtMTIuNjMtNS42NS0xMi42My0xMi42M2gwWk04NzUuNjQsODQ0LjhjLS4zNS01LjI2LTQuOS05LjI1LTEwLjE2LTguOS01LjI2LjM1LTkuMjUsNC45LTguOSwxMC4xNi4zMyw1LjAxLDQuNDksOC45MSw5LjUxLDguOTIsNS4zNS0uMDcsOS42My00LjQ3LDkuNTYtOS44MiwwLS4xMiwwLS4yNC0uMDEtLjM2Wk04NjEuMjMsODM3LjU5aDUuMzJjMy41LDAsNS4yOCwxLjE5LDUuMjgsNC4yLjIsMS45Mi0xLjIsMy42NC0zLjEyLDMuODQtLjIxLjAyLS40Mi4wMi0uNjIsMGwzLjg1LDYuMjZoLTIuNzNsLTMuNzQtNi4yM2gtMS42MXY2LjEyaC0yLjY2bC4wNC0xNC4yMVpNODYzLjg4LDg0My43MWgyLjM0YzEuNTcsMCwyLjk0LS4yMSwyLjk0LTIuMTNzLTEuNTQtMS45Ni0yLjktMS45NmgtMi4zOHY0LjA5WiIvPgo8L3N2Zz4=' 
             style='width: 40px; height: 40px;' />
        <div class="sidebar-brand-title">Mays Analytics</div>
        <div class="sidebar-brand-subtitle">Flex Online Programs</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation Section
    
    if st.button("Home Dashboard", key="sidebar_nav_home", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Home' else "secondary"):
        st.session_state.current_page = 'Home'
        st.rerun()
    
    if st.button("Executive Dive", key="sidebar_nav_executive", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Executive_Deep_Dive' else "secondary"):
        st.session_state.current_page = 'Executive_Deep_Dive'
        st.rerun()
    
    if st.button("Comparison Tool", key="sidebar_nav_comparison", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Comparison_Tool' else "secondary"):
        st.session_state.current_page = 'Comparison_Tool'
        st.rerun()
    
    if st.button("Marketing Analysis", key="sidebar_nav_marketing", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Marketing_Analysis' else "secondary"):
        st.session_state.current_page = 'Marketing_Analysis'
        st.rerun()
    
    if st.button("Data Explorer", key="sidebar_nav_database", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Database' else "secondary"):
        st.session_state.current_page = 'Database'
        st.rerun()
    
    st.markdown('<div style="margin: 15px 0; border-top: 1px solid #e0e0e0;"></div>', unsafe_allow_html=True)
    
    if st.button("Help & Documentation", key="sidebar_nav_help", use_container_width=True,
                type="primary" if st.session_state.current_page == 'Help' else "secondary"):
        st.session_state.current_page = 'Help'
        st.rerun()
    
    # Footer with version
    st.markdown("""
    <div style="text-align: center; padding: 20px 10px; margin-top: 30px; border-top: 1px solid #e0e0e0; font-size: 10px; color: #999;">
        <div>Version 2.4</div>
    </div>
    """, unsafe_allow_html=True)

# Display current page indicator
current_page_info = {
    'Home': {'icon': '🏠', 'title': 'Home Dashboard'},
    'Executive_Deep_Dive': {'icon': '📊', 'title': 'Executive Dive'},
    'Comparison_Tool': {'icon': '🔄', 'title': 'Comparison Tool'},
    'Marketing_Analysis': {'icon': '📢', 'title': 'Marketing Analysis'},
    'Database': {'icon': '🗄️', 'title': 'Data Explorer'},
    'Help': {'icon': '📖', 'title': 'Help & Documentation'}
}

current_info = current_page_info[st.session_state.current_page]
st.markdown(f"""
<div style="text-align: center; padding: 8px; background: #f8f9fa; border-radius: 8px; margin-bottom: 15px;">
    <h2 style="margin: 0; color: #500000; font-size: 24px;">{current_info['title']}</h2>
</div>
""", unsafe_allow_html=True)

# Page Content Based on Navigation
if st.session_state.current_page == 'Home':
    # HOME PAGE CONTENT
    
    # Initialize reset counter for Home filters
    if 'home_reset_count' not in st.session_state:
        st.session_state.home_reset_count = 0
    
    # Initialize funnel log scale state
    if 'home_funnel_log_scale' not in st.session_state:
        st.session_state.home_funnel_log_scale = False
    
    # Section header for filters
    # Two-column filter layout
    col_cohort, col_program = st.columns(2)
    
    with col_cohort:
        cohort_options = [2028, 2027, 2026]
        selected_cohort = st.selectbox(
            "📅 Cohort Year",
            options=cohort_options,
            index=0,
            help="Select ONE cohort year for analysis. No mixed-cohort data.",
            key=f"cohort_select_home_{st.session_state.home_reset_count}"
        )
    
    with col_program:
        # Get available programs
        programs_df = load_programs()
        program_options = ['All Programs'] + sorted(programs_df['program_code'].tolist())
        selected_program = st.selectbox(
            "🎓 Program Focus",
            options=program_options,
            index=0,
            help="Select a specific program or view all programs",
            key=f"program_select_home_{st.session_state.home_reset_count}"
        )
    
    # Load data for selected cohort
    conn = get_connection()
    query = 'SELECT * FROM admissions_metrics WHERE cohort_year = ? ORDER BY report_date, program'
    df = pd.read_sql(query, conn, params=[selected_cohort])
    df['report_date'] = pd.to_datetime(df['report_date'])
    
    # Filter by program if specific program is selected
    if selected_program != 'All Programs':
        df = df[df['program'] == selected_program]

    if not df.empty:
        # Filter out dates with no real data
        dates_with_data = df.groupby('report_date')['metric_value'].sum()
        dates_with_data = dates_with_data[dates_with_data > 0].index
        df = df[df['report_date'].isin(dates_with_data)]

        latest_date = df['report_date'].max()
        latest_data = df[df['report_date'] == latest_date]

        # Section header for current stats
        st.markdown("""
        <div style="text-align: center;
                    padding: 15px;
                    background: #e9ecef;
                    border-radius: 8px;
                    margin: 20px 0;">
            <h3 style="color: #500000; margin: 0; font-size: 20px;">📊 Current Stats - Class of {}</h3>
            <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 14px;">
                All metrics below are specific to the {} cohort • Last updated: {}
            </p>
        </div>
        """.format(selected_cohort, selected_cohort, latest_date.strftime('%B %d, %Y')), unsafe_allow_html=True)

        # Key Metrics Row - with truly synchronized heights using CSS Grid
        st.markdown("""
        <style>
        .metrics-container {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin: 20px 0;
        }
        .metric-box {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .metric-number {
            color: #500000;
            margin: 0;
            font-size: 2.5rem;
            font-weight: bold;
            line-height: 1.2;
        }
        .metric-label {
            margin: 10px 0 5px 0;
            color: #495057;
            font-weight: 600;
            font-size: 1rem;
            line-height: 1.3;
        }
        .metric-small {
            color: #6c757d;
            font-size: 0.875rem;
        }
        @media (max-width: 768px) {
            .metrics-container {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        @media (max-width: 480px) {
            .metrics-container {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """, unsafe_allow_html=True)

        total_cohort = latest_data[latest_data['metric_name'] == 'anticipated_cohort_size']['metric_value'].sum()
        total_applications = latest_data[latest_data['metric_name'] == 'total_applications']['metric_value'].sum()
        total_inquiries = latest_data[latest_data['metric_name'] == 'inquiries_received']['metric_value'].sum()
        total_accepted = latest_data[latest_data['metric_name'] == 'admissions_accepted']['metric_value'].sum()
        conversion_rate = (total_applications / total_inquiries * 100) if total_inquiries > 0 else 0
        conversion_color = '#28a745' if conversion_rate > 30 else '#ffc107' if conversion_rate > 20 else '#dc3545'

        # Single container with all four boxes - this ensures they all have the same height
        st.markdown(f"""
        <div class="metrics-container">
            <div class="metric-box">
                <h2 class="metric-number">🎯 {int(total_cohort) if pd.notna(total_cohort) else 0}</h2>
                <p class="metric-label">Enrolled Students</p>
                <small class="metric-small">as of {latest_date.strftime('%b %d')}</small>
            </div>
            <div class="metric-box">
                <h2 class="metric-number">📝 {int(total_applications) if pd.notna(total_applications) else 0}</h2>
                <p class="metric-label">Total Applications</p>
                <small class="metric-small">submitted</small>
            </div>
            <div class="metric-box">
                <h2 class="metric-number">👥 {int(total_inquiries) if pd.notna(total_inquiries) else 0}</h2>
                <p class="metric-label">Total Inquiries</p>
                <small class="metric-small">received</small>
            </div>
            <div class="metric-box">
                <h2 class="metric-number" style="color: {conversion_color};">📈 {conversion_rate:.1f}%</h2>
                <p class="metric-label">Conversion Rate</p>
                <small class="metric-small">Inquiry → Application</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")

        # Admissions Funnel Section
        st.markdown("""
        <div style="text-align: center;
                    padding: 15px;
                    background: #e9ecef;
                    border-radius: 8px;
                    margin: 20px 0;">
            <h3 style="color: #500000; margin: 0; font-size: 20px;">🎯 Admissions Funnel - Class of {}</h3>
            <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 14px;">
                Single-cohort analysis showing the complete application journey
            </p>
        </div>
        """.format(selected_cohort), unsafe_allow_html=True)
        
        # Log scale toggle for funnel
        col_spacer1, col_toggle, col_spacer2 = st.columns([2, 1, 2])
        with col_toggle:
            if st.button(
                f"📊 {'Log' if st.session_state.home_funnel_log_scale else 'Linear'} Scale",
                key="toggle_log_funnel_home",
                use_container_width=True,
                type="secondary"
            ):
                st.session_state.home_funnel_log_scale = not st.session_state.home_funnel_log_scale
                st.rerun()

        funnel_metrics = ['inquiries_received', 'total_applications', 'admissions_offered', 'admissions_accepted']
        funnel_labels = ['Inquiries', 'Applications', 'Offers', 'Accepted']

        funnel_data = []
        for metric in funnel_metrics:
            value = latest_data[latest_data['metric_name'] == metric]['metric_value'].sum()
            funnel_data.append(value)

        # Use bar chart instead of funnel when log scale is enabled
        if st.session_state.home_funnel_log_scale:
            fig_funnel = go.Figure(go.Bar(
                x=funnel_labels,
                y=funnel_data,
                marker={"color": ["#500000", "#700000", "#900000", "#B00000"]},
                text=funnel_data,
                texttemplate='%{text:,.0f}',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Count: %{y:,.0f}<extra></extra>'
            ))
            fig_funnel.update_layout(
                height=500,
                showlegend=False,
                yaxis_type='log',
                yaxis_title='Count (Log Scale)',
                xaxis_title='Stage',
                margin=dict(t=80, b=50, l=50, r=50)  # Add top margin to prevent clipping
            )
        else:
            fig_funnel = go.Figure(go.Funnel(
                y=funnel_labels,
                x=funnel_data,
                textinfo="value+percent initial",
                marker={"color": ["#500000", "#700000", "#900000", "#B00000"]}
            ))
            fig_funnel.update_layout(height=400, showlegend=False)
        
        # Center the chart
        col_spacer1, col_chart, col_spacer2 = st.columns([0.5, 3, 0.5])
        with col_chart:
            st.plotly_chart(fig_funnel, use_container_width=True)

        st.markdown("---")

        # Program Comparison Section
        st.markdown("""
        <div style="text-align: center;
                    padding: 15px;
                    background: #e9ecef;
                    border-radius: 8px;
                    margin: 20px 0;">
            <h3 style="color: #500000; margin: 0; font-size: 20px;">📊 Program Comparison</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize program filter states
        if 'prog_home_show_inquiries' not in st.session_state:
            st.session_state.prog_home_show_inquiries = True
        if 'prog_home_show_applications' not in st.session_state:
            st.session_state.prog_home_show_applications = True
        if 'prog_home_show_accepted' not in st.session_state:
            st.session_state.prog_home_show_accepted = True
        if 'prog_home_show_cohort' not in st.session_state:
            st.session_state.prog_home_show_cohort = True
        if 'prog_home_log_scale' not in st.session_state:
            st.session_state.prog_home_log_scale = False
        
        # Filter controls with custom styling
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
                    padding: 15px;
                    border-radius: 8px;
                    margin: 15px 0;">
        """, unsafe_allow_html=True)
        
        filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns(5)
        
        with filter_col1:
            if st.button(
                f"{'✓' if st.session_state.prog_home_show_inquiries else '○'} Inquiries",
                key="toggle_inq_prog_home",
                use_container_width=True,
                type="primary" if st.session_state.prog_home_show_inquiries else "secondary"
            ):
                st.session_state.prog_home_show_inquiries = not st.session_state.prog_home_show_inquiries
                st.rerun()
        
        with filter_col2:
            if st.button(
                f"{'✓' if st.session_state.prog_home_show_applications else '○'} Applications",
                key="toggle_apps_prog_home",
                use_container_width=True,
                type="primary" if st.session_state.prog_home_show_applications else "secondary"
            ):
                st.session_state.prog_home_show_applications = not st.session_state.prog_home_show_applications
                st.rerun()
        
        with filter_col3:
            if st.button(
                f"{'✓' if st.session_state.prog_home_show_accepted else '○'} Accepted",
                key="toggle_acc_prog_home",
                use_container_width=True,
                type="primary" if st.session_state.prog_home_show_accepted else "secondary"
            ):
                st.session_state.prog_home_show_accepted = not st.session_state.prog_home_show_accepted
                st.rerun()
        
        with filter_col4:
            if st.button(
                f"{'✓' if st.session_state.prog_home_show_cohort else '○'} Cohort Size",
                key="toggle_cohort_prog_home",
                use_container_width=True,
                type="primary" if st.session_state.prog_home_show_cohort else "secondary"
            ):
                st.session_state.prog_home_show_cohort = not st.session_state.prog_home_show_cohort
                st.rerun()
        
        with filter_col5:
            if st.button(
                f"📊 {'Log' if st.session_state.prog_home_log_scale else 'Linear'} Scale",
                key="toggle_log_prog_home",
                use_container_width=True,
                type="secondary"
            ):
                st.session_state.prog_home_log_scale = not st.session_state.prog_home_log_scale
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Simple info box for interactivity
        st.markdown("""
        <div style="background: #f0f8ff;
                    padding: 12px;
                    border-radius: 6px;
                    margin-bottom: 15px;
                    text-align: center;
                    font-size: 0.9rem;">
            💡 <strong>Interactive Chart:</strong> Use buttons above to show/hide metrics • Click legend items to toggle • Hover bars for exact values
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
                'inquiries_received': ('Inquiries', st.session_state.prog_home_show_inquiries, '#500000'),
                'total_applications': ('Applications', st.session_state.prog_home_show_applications, '#700000'),
                'admissions_accepted': ('Accepted', st.session_state.prog_home_show_accepted, '#900000'),
                'anticipated_cohort_size': ('Cohort Size', st.session_state.prog_home_show_cohort, '#B00000')
            }
            
            for metric, (label, show_flag, color) in metrics_to_plot.items():
                if metric in program_comparison.columns and show_flag:
                    fig_comparison.add_trace(go.Bar(
                        name=label,
                        x=program_comparison.index,
                        y=program_comparison[metric],
                        marker_color=color,
                        text=program_comparison[metric],
                        texttemplate='%{text:,.0f}',
                        textposition='outside',
                        hovertemplate='<b>' + label + '</b><br>' +
                                     'Program: %{x}<br>' +
                                     'Count: %{y:,.0f}<br>' +
                                     '<extra></extra>'
                    ))
            
            fig_comparison.update_layout(
                barmode='group',
                height=500,
                xaxis_title='Program',
                yaxis_title='Count',
                yaxis_type='log' if st.session_state.prog_home_log_scale else 'linear',
                margin=dict(t=80, b=50, l=50, r=50),  # Add top margin to prevent clipping
                legend=dict(
                    x=1, y=1,
                    xanchor='right', yanchor='top',
                    bgcolor='rgba(255,255,255,0.9)',
                    bordercolor='rgba(0,0,0,0.2)',
                    borderwidth=1
                )
            )
            
            # Center the chart
            col_spacer1, col_chart, col_spacer2 = st.columns([0.2, 3.6, 0.2])
            with col_chart:
                st.plotly_chart(fig_comparison, use_container_width=True)
        
        st.markdown("---")
        
        # Trend Analysis Section
        st.markdown("""
        <div style="text-align: center;
                    padding: 15px;
                    background: #e9ecef;
                    border-radius: 8px;
                    margin: 20px 0;">
            <h3 style="color: #500000; margin: 0; font-size: 20px;">📊 Trend Analysis</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize session state for toggle buttons
        if 'home_trend_show_apps' not in st.session_state:
            st.session_state.home_trend_show_apps = True
        if 'home_trend_show_inq' not in st.session_state:
            st.session_state.home_trend_show_inq = True
        if 'home_trend_show_inq_conv' not in st.session_state:
            st.session_state.home_trend_show_inq_conv = True
        if 'home_trend_show_app_conv' not in st.session_state:
            st.session_state.home_trend_show_app_conv = True
        
        time_series = df[df['metric_name'].isin([
            'inquiries_received', 'total_applications', 'admissions_offered'
        ])].pivot_table(
            index='report_date',
            columns='metric_name',
            values='metric_value',
            aggfunc='sum'
        ).fillna(0)
        
        if not time_series.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<h4 style='text-align: center; color: #500000;'>📈 Application & Inquiry Trends</h4>", unsafe_allow_html=True)
                
                # Toggle buttons for line selection
                st.markdown("**📊 Select Lines to Display:**")
                filter_col1, filter_col2 = st.columns(2)
                
                with filter_col1:
                    if st.button(
                        f"{'✓' if st.session_state.home_trend_show_apps else '○'} Applications",
                        key="toggle_apps_trend_home",
                        use_container_width=True,
                        type="primary" if st.session_state.home_trend_show_apps else "secondary"
                    ):
                        st.session_state.home_trend_show_apps = not st.session_state.home_trend_show_apps
                        st.rerun()
                
                with filter_col2:
                    if st.button(
                        f"{'✓' if st.session_state.home_trend_show_inq else '○'} Inquiries",
                        key="toggle_inq_trend_home",
                        use_container_width=True,
                        type="primary" if st.session_state.home_trend_show_inq else "secondary"
                    ):
                        st.session_state.home_trend_show_inq = not st.session_state.home_trend_show_inq
                        st.rerun()
                
                fig_trend1 = go.Figure()
                
                if 'total_applications' in time_series.columns and st.session_state.home_trend_show_apps:
                    fig_trend1.add_trace(go.Scatter(
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
                
                if 'inquiries_received' in time_series.columns and st.session_state.home_trend_show_inq:
                    fig_trend1.add_trace(go.Scatter(
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
                
                fig_trend1.update_layout(
                    height=400,
                    xaxis_title='Date',
                    yaxis_title='Count',
                    legend=dict(
                        x=1, y=1,
                        xanchor='right', yanchor='top',
                        bgcolor='rgba(255,255,255,0.9)',
                        bordercolor='rgba(0,0,0,0.2)',
                        borderwidth=1
                    )
                )
                st.plotly_chart(fig_trend1, use_container_width=True)
            
            with col2:
                st.markdown("<h4 style='text-align: center; color: #500000;'>🎯 Conversion Rates Over Time</h4>", unsafe_allow_html=True)
                
                # Toggle buttons for conversion rates
                st.markdown("**📊 Select Conversion Metrics:**")
                conv_filter_col1, conv_filter_col2 = st.columns(2)
                
                with conv_filter_col1:
                    if st.button(
                        f"{'✓' if st.session_state.home_trend_show_inq_conv else '○'} Inquiry → App",
                        key="toggle_inq_conv_trend_home",
                        use_container_width=True,
                        type="primary" if st.session_state.home_trend_show_inq_conv else "secondary"
                    ):
                        st.session_state.home_trend_show_inq_conv = not st.session_state.home_trend_show_inq_conv
                        st.rerun()
                
                with conv_filter_col2:
                    if st.button(
                        f"{'✓' if st.session_state.home_trend_show_app_conv else '○'} App → Offer",
                        key="toggle_app_conv_trend_home",
                        use_container_width=True,
                        type="primary" if st.session_state.home_trend_show_app_conv else "secondary"
                    ):
                        st.session_state.home_trend_show_app_conv = not st.session_state.home_trend_show_app_conv
                        st.rerun()
                
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
                    fig_trend2 = go.Figure()
                    
                    if st.session_state.home_trend_show_inq_conv:
                        fig_trend2.add_trace(go.Scatter(
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
                    
                    if st.session_state.home_trend_show_app_conv:
                        fig_trend2.add_trace(go.Scatter(
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
                    
                    fig_trend2.update_layout(
                        height=400,
                        xaxis_title='Date',
                        yaxis_title='Conversion Rate (%)',
                        legend=dict(
                            x=1, y=1,
                            xanchor='right', yanchor='top',
                            bgcolor='rgba(255,255,255,0.9)',
                            bordercolor='rgba(0,0,0,0.2)',
                            borderwidth=1
                        )
                    )
                    st.plotly_chart(fig_trend2, use_container_width=True)

    else:
        st.warning("⚠️ No data available for the selected cohort{' and program' if selected_program != 'All Programs' else ''}.")
    
    # Footer for Home page
    st.divider()
    footer_col1, footer_col2, footer_col3 = st.columns([1, 1, 1])
    with footer_col1:
        st.markdown(f"""
        <div class="footer-left footer-content" style="text-align: left;">
            <p style="color: #6b7280; font-size: 14px; margin: 0;">📊 Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        """, unsafe_allow_html=True)
    with footer_col2:
        st.components.v1.html("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100%; min-height: 60px;">
            <button onclick="window.top.print()" 
                    style="background-color: white;
                           color: #500000;
                           border: 2px solid #e0e0e0;
                           border-radius: 8px;
                           padding: 0.6rem 1.2rem;
                           font-size: 0.95rem;
                           font-weight: 600;
                           cursor: pointer;
                           transition: all 0.3s ease;
                           width: 100%;
                           min-height: 45px;
                           font-family: 'Source Sans Pro', sans-serif;"
                    onmouseover="this.style.backgroundColor='#e9ecef'; this.style.borderColor='#500000';"
                    onmouseout="this.style.backgroundColor='white'; this.style.borderColor='#e0e0e0';">
                🖨️ Print Page
            </button>
        </div>
        """, height=70)
    with footer_col3:
        st.markdown("""
        <div class="footer-right footer-content" style="text-align: right;">
            <p style="color: #6b7280; font-size: 14px; margin: 0;">💡 Use buttons above to switch views</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_page == 'Executive_Deep_Dive':
    # EXECUTIVE DEEP DIVE CONTENT
    
    # Section header for filters
    # Two-column filter layout
    col_cohort, col_program = st.columns(2)

    with col_cohort:
        cohort_options = [2028, 2027, 2026]
        selected_cohort = st.selectbox(
            "📅 Primary Cohort",
            options=cohort_options,
            index=0,
            help="Select primary cohort for analysis"
        )

    with col_program:
        programs_df = load_programs()
        program_options = ["All Programs"] + sorted(programs_df['program_code'].tolist())
        selected_program_filter = st.selectbox(
            "🎓 Program Focus",
            options=program_options,
            help="Filter by specific program"
        )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
    # How to Use This Section - Collapsible
    with st.expander("💡 How to Use This Section", expanded=False):
        st.markdown("""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; font-size: 14px; color: #495057;">
            <div>
                <strong style="color: #500000;">📊 Navigation & Filters:</strong>
                <ul style="margin: 8px 0; padding-left: 20px;">
                    <li><strong>Primary Cohort:</strong> Select the class year you want to analyze</li>
                    <li><strong>Program Focus:</strong> Filter by specific program or view all programs</li>
                    <li><strong>Four Tabs:</strong> Navigate between Performance, Trends, Programs, and Data Tables</li>
                </ul>
            </div>
            <div>
                <strong style="color: #500000;">🎯 Interactive Features:</strong>
                <ul style="margin: 8px 0; padding-left: 20px;">
                    <li><strong>Toggle Buttons:</strong> Show/hide specific metrics on charts</li>
                    <li><strong>Log Scale:</strong> Switch between linear and logarithmic scales for better visualization</li>
                    <li><strong>Hover Details:</strong> Move mouse over charts for exact values and insights</li>
                    <li><strong>Export Data:</strong> Download tables and charts for further analysis</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    # Load data based on selection
    current_data = load_cohort_data(selected_cohort)

    # Apply program filter if selected
    if selected_program_filter != "All Programs":
        current_data = current_data[current_data['program'] == selected_program_filter]

    if current_data.empty:
        st.error(f"❌ No data available for Class of {selected_cohort}" + 
                 (f" - {selected_program_filter}" if selected_program_filter != "All Programs" else ""))
        st.info("💡 Try selecting a different cohort/program or check the database")
    else:
        # Get latest data for current cohort
        latest_date = current_data['report_date'].max()
        latest_data = current_data[current_data['report_date'] == latest_date]

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

        # FULL DEEP DIVE - Most comprehensive analysis with advanced metrics
        st.markdown("""
        <div style="text-align: center;
                    padding: 15px;
                    background: #e9ecef;
                    border-radius: 8px;
                    margin: 20px 0;">
            <h3 style="color: #500000; margin: 0; font-size: 20px;">🔍 Full Deep Dive - Class of {}</h3>
            <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 14px;">
                Complete analytics suite with advanced insights and predictive analysis
            </p>
        </div>
        """.format(selected_cohort), unsafe_allow_html=True)
        
        # Comprehensive KPI Grid using CSS Grid
        st.markdown("""
        <style>
        .full-metrics-container {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 1rem;
            margin: 20px 0;
        }
        .full-metric-box {
            background: white;
            padding: 1.2rem;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        @media (max-width: 1200px) {
            .full-metrics-container {
                grid-template-columns: repeat(3, 1fr);
            }
        }
        @media (max-width: 768px) {
            .full-metrics-container {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        @media (max-width: 480px) {
            .full-metrics-container {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="full-metrics-container">
            <div class="full-metric-box">
                <h2 style="color: #500000; margin: 0; font-size: 1.8rem;">👥 {int(inquiries)}</h2>
                <p style="margin: 8px 0 3px 0; color: #495057; font-weight: 500; font-size: 0.9rem;">Inquiries</p>
                <small style="color: #6c757d; font-size: 0.8rem;">Total received</small>
            </div>
            <div class="full-metric-box">
                <h2 style="color: #500000; margin: 0; font-size: 1.8rem;">📝 {int(applications)}</h2>
                <p style="margin: 8px 0 3px 0; color: #495057; font-weight: 500; font-size: 0.9rem;">Applications</p>
                <small style="color: {'#28a745' if conversion_1 > 30 else '#ffc107' if conversion_1 > 20 else '#dc3545'}; font-size: 0.8rem;">{conversion_1:.1f}% conv.</small>
            </div>
            <div class="full-metric-box">
                <h2 style="color: #500000; margin: 0; font-size: 1.8rem;">⏳ {int(in_progress)}</h2>
                <p style="margin: 8px 0 3px 0; color: #495057; font-weight: 500; font-size: 0.9rem;">In Progress</p>
                <small style="color: #6c757d; font-size: 0.8rem;">Applications</small>
            </div>
            <div class="full-metric-box">
                <h2 style="color: #500000; margin: 0; font-size: 1.8rem;">✅ {int(complete)}</h2>
                <p style="margin: 8px 0 3px 0; color: #495057; font-weight: 500; font-size: 0.9rem;">Complete</p>
                <small style="color: #6c757d; font-size: 0.8rem;">Applications</small>
            </div>
            <div class="full-metric-box">
                <h2 style="color: #500000; margin: 0; font-size: 1.8rem;">🎓 {int(offers)}</h2>
                <p style="margin: 8px 0 3px 0; color: #495057; font-weight: 500; font-size: 0.9rem;">Offers</p>
                <small style="color: #6c757d; font-size: 0.8rem;">{conversion_2:.1f}% rate</small>
            </div>
            <div class="full-metric-box">
                <h2 style="color: #500000; margin: 0; font-size: 1.8rem;">🎯 {int(enrolled)}</h2>
                <p style="margin: 8px 0 3px 0; color: #495057; font-weight: 500; font-size: 0.9rem;">Enrolled</p>
                <small style="color: {'#28a745' if yield_rate > 70 else '#ffc107' if yield_rate > 50 else '#dc3545'}; font-size: 0.8rem;">{yield_rate:.1f}% yield</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Advanced Analytics Tabs
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        
        # Chrome-style tabs CSS (same as Marketing Analysis)
        st.markdown("""
        <style>
        /* Chrome-style tabs - Base styles */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px !important;
            justify-content: center !important;
            background-color: transparent !important;
            padding: 0px 20px !important;
            border-bottom: none !important;
            margin-bottom: 30px !important;
            display: flex !important;
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            overflow-y: hidden !important;
            scroll-behavior: smooth !important;
            -webkit-overflow-scrolling: touch !important;
            scrollbar-width: thin !important;
            scrollbar-color: #500000 #f0f0f0 !important;
            box-sizing: border-box !important;
        }
        
        /* Always show scrollbar when content overflows */
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
            height: 10px !important;
            display: block !important;
        }
        
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-track {
            background: #f0f0f0 !important;
            border-radius: 5px !important;
        }
        
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
            background: #500000 !important;
            border-radius: 5px !important;
            min-width: 50px !important;
        }
        
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb:hover {
            background: #700000 !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 45px !important;
            padding: 0px 32px !important;
            background-color: #f5f5f5 !important;
            border-radius: 8px 8px 0px 0px !important;
            font-weight: 500 !important;
            font-size: 15px !important;
            border: none !important;
            border-bottom: 3px solid transparent !important;
            color: #666 !important;
            margin-bottom: -2px !important;
            flex-shrink: 0 !important;
            white-space: nowrap !important;
            min-width: fit-content !important;
            box-sizing: border-box !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: white !important;
            color: #500000 !important;
            border-bottom: 3px solid #500000 !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #e8e8e8 !important;
            color: #500000 !important;
        }
        
        .stTabs [aria-selected="true"]:hover {
            background-color: white !important;
        }
        
        /* Tablet adjustments - switch to left-aligned */
        @media screen and (max-width: 1024px) {
            .stTabs [data-baseweb="tab-list"] {
                justify-content: flex-start !important;
                padding: 0px 15px !important;
            }
            
            .stTabs [data-baseweb="tab"] {
                padding: 0px 24px !important;
                font-size: 14px !important;
            }
            
            .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
                height: 12px !important;
            }
        }
        
        /* Mobile adjustments - left-aligned */
        @media screen and (max-width: 768px) {
            .stTabs [data-baseweb="tab-list"] {
                justify-content: flex-start !important;
                padding: 0px 10px !important;
            }
            
            .stTabs [data-baseweb="tab"] {
                padding: 0px 20px !important;
                font-size: 13px !important;
                height: 42px !important;
            }
        }
        
        /* Small mobile adjustments - left-aligned */
        @media screen and (max-width: 480px) {
            .stTabs [data-baseweb="tab-list"] {
                justify-content: flex-start !important;
                padding: 0px 10px !important;
            }
            
            .stTabs [data-baseweb="tab"] {
                padding: 0px 16px !important;
                font-size: 12px !important;
                height: 40px !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Prepare complete_data for use across tabs (needed for Data Tables and Advanced Insights)
        complete_data = current_data.pivot_table(
            index=['report_date', 'program'],
            columns='metric_name',
            values='metric_value',
            aggfunc='sum'
        ).fillna(0).reset_index()
        
        # Tab content using native Streamlit tabs (Chrome-style)
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance Analysis", "📈 Trend Analysis", "🎓 Program Deep Dive", "📋 Data Tables"])
        
        with tab1:
            # Complete conversion funnel with log scale toggle - FULL WIDTH
            st.markdown("<h4 style='text-align: center; color: #500000;'>🎯 Complete Conversion Funnel</h4>", unsafe_allow_html=True)
            
            # Initialize log scale state for full deep dive funnel
            if 'exec_full_funnel_log' not in st.session_state:
                st.session_state.exec_full_funnel_log = False
            
            # Log scale toggle button - centered
            col_spacer1, col_toggle, col_spacer2 = st.columns([2, 1, 2])
            with col_toggle:
                toggle_label = "📊 Linear Scale" if st.session_state.exec_full_funnel_log else "📊 Log Scale"
                if st.button(
                    toggle_label,
                    key="toggle_log_full_funnel",
                    use_container_width=True,
                    type="primary" if st.session_state.exec_full_funnel_log else "secondary"
                ):
                    st.session_state.exec_full_funnel_log = not st.session_state.exec_full_funnel_log
                    st.rerun()
            
            funnel_data = [inquiries, applications, complete, offers, accepted, enrolled]
            funnel_labels = ['Inquiries', 'Applications', 'Complete Apps', 'Offers', 'Accepted', 'Enrolled']
            
            if st.session_state.exec_full_funnel_log:
                # Use bar chart with log scale
                fig = go.Figure(go.Bar(
                    x=funnel_labels,
                    y=funnel_data,
                    marker={"color": ["#500000", "#600000", "#700000", "#800000", "#900000", "#B00000"]},
                    text=funnel_data,
                    texttemplate='%{text:,.0f}',
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>Count: %{y:,.0f}<extra></extra>'
                ))
                fig.update_layout(
                    height=500,
                    showlegend=False,
                    yaxis_type='log',
                    yaxis_title='Count (Log Scale)',
                    xaxis_title='Stage',
                    margin=dict(t=80, b=50, l=80, r=80)
                )
            else:
                # Use funnel chart
                fig = go.Figure(go.Funnel(
                    y=funnel_labels,
                    x=funnel_data,
                    textinfo="value+percent initial",
                    marker={"color": ["#500000", "#600000", "#700000", "#800000", "#900000", "#B00000"]}
                ))
                fig.update_layout(
                    height=500,
                    margin=dict(t=50, b=50, l=80, r=80)
                )
            st.plotly_chart(fig, use_container_width=True)
            
            # Divider between charts
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            
            # Performance metrics radar chart - FULL WIDTH
            st.markdown("<h4 style='text-align: center; color: #500000;'>📈 Performance Radar</h4>", unsafe_allow_html=True)
            
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
                line_color='#500000',
                fillcolor='rgba(80, 0, 0, 0.3)'
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                height=500,
                margin=dict(t=50, b=50, l=80, r=80)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Add Correlation Matrix and Performance Benchmarks to Performance Analysis
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            
            # Correlation analysis - full width with better color scale
            st.markdown("<h4 style='text-align: center; color: #500000;'>📊 Correlation Matrix</h4>", unsafe_allow_html=True)
            
            if not complete_data.empty:
                numeric_data = complete_data.select_dtypes(include=[np.number])
                if len(numeric_data.columns) > 1:
                    correlation_matrix = numeric_data.corr()
                    
                    # Use green (high correlation) to red (low correlation) color scale
                    fig = px.imshow(
                        correlation_matrix,
                        labels=dict(color="Correlation"),
                        color_continuous_scale=[[0, '#dc3545'], [0.5, '#ffc107'], [1, '#28a745']],  # Red -> Yellow -> Green
                        aspect="auto",
                        zmin=-1,
                        zmax=1
                    )
                    fig.update_layout(
                        title="Correlation Matrix (Green = High Correlation, Red = Low Correlation)",
                        height=600,
                        width=1000
                    )
                    
                    # Center the chart
                    col_spacer1, col_chart, col_spacer2 = st.columns([0.2, 3, 0.2])
                    with col_chart:
                        st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            
            # Performance benchmarks - full width stretched layout with center alignment
            st.markdown("<h4 style='text-align: center; color: #500000;'>🎯 Performance Benchmarks</h4>", unsafe_allow_html=True)
            
            # Add CSS to center-align metrics while preserving styling
            st.markdown("""
            <style>
            [data-testid="stMetric"] {
                display: flex;
                flex-direction: column;
                align-items: center;
                text-align: center;
            }
            [data-testid="stMetricLabel"] {
                display: flex;
                justify-content: center;
                width: 100%;
            }
            [data-testid="stMetricLabel"] > div {
                text-align: center;
            }
            [data-testid="stMetricValue"] {
                display: flex;
                justify-content: center;
                width: 100%;
            }
            [data-testid="stMetricDelta"] {
                display: flex;
                justify-content: center;
                width: 100%;
            }
            </style>
            """, unsafe_allow_html=True)
            
            benchmarks = {
                'Inquiry Conversion': {'value': conversion_1, 'benchmark': 30, 'unit': '%'},
                'Yield Rate': {'value': yield_rate, 'benchmark': 60, 'unit': '%'},
                'Application Completion': {'value': (complete / applications * 100) if applications > 0 else 0, 'benchmark': 80, 'unit': '%'}
            }
            
            # Use columns with no gap and custom spacing
            col1, col2, col3 = st.columns([1, 1, 1])
            for idx, (metric, data) in enumerate(benchmarks.items()):
                with [col1, col2, col3][idx]:
                    performance = "🟢 Above" if data['value'] > data['benchmark'] else "🟡 At" if abs(data['value'] - data['benchmark']) < 5 else "🔴 Below"
                    st.metric(
                        metric,
                        f"{data['value']:.1f}{data['unit']}",
                        f"{performance} benchmark ({data['benchmark']}{data['unit']})"
                    )
        
        with tab2:
            
            # Initialize session state for toggle buttons
            if 'exec_full_show_inq' not in st.session_state:
                st.session_state.exec_full_show_inq = True
            if 'exec_full_show_apps' not in st.session_state:
                st.session_state.exec_full_show_apps = True
            if 'exec_full_show_offers' not in st.session_state:
                st.session_state.exec_full_show_offers = True
            if 'exec_full_show_cohort' not in st.session_state:
                st.session_state.exec_full_show_cohort = True
            
            # Toggle buttons for metric selection
            st.markdown("**📊 Select Metrics to Display:**")
            metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
            
            with metric_col1:
                if st.button(
                    f"{'✓' if st.session_state.exec_full_show_inq else '○'} Inquiries",
                    key="toggle_inq_full",
                    use_container_width=True,
                    type="primary" if st.session_state.exec_full_show_inq else "secondary"
                ):
                    st.session_state.exec_full_show_inq = not st.session_state.exec_full_show_inq
                    st.rerun()
            
            with metric_col2:
                if st.button(
                    f"{'✓' if st.session_state.exec_full_show_apps else '○'} Applications",
                    key="toggle_apps_full",
                    use_container_width=True,
                    type="primary" if st.session_state.exec_full_show_apps else "secondary"
                ):
                    st.session_state.exec_full_show_apps = not st.session_state.exec_full_show_apps
                    st.rerun()
            
            with metric_col3:
                if st.button(
                    f"{'✓' if st.session_state.exec_full_show_offers else '○'} Offers",
                    key="toggle_offers_full",
                    use_container_width=True,
                    type="primary" if st.session_state.exec_full_show_offers else "secondary"
                ):
                    st.session_state.exec_full_show_offers = not st.session_state.exec_full_show_offers
                    st.rerun()
            
            with metric_col4:
                if st.button(
                    f"{'✓' if st.session_state.exec_full_show_cohort else '○'} Cohort Size",
                    key="toggle_cohort_full",
                    use_container_width=True,
                    type="primary" if st.session_state.exec_full_show_cohort else "secondary"
                ):
                    st.session_state.exec_full_show_cohort = not st.session_state.exec_full_show_cohort
                    st.rerun()
            
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
                show_flags = [st.session_state.exec_full_show_inq, st.session_state.exec_full_show_apps, st.session_state.exec_full_show_offers, st.session_state.exec_full_show_cohort]
                
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
                    )
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Growth rate analysis
                st.markdown("<h4 style='text-align: center; color: #500000;'>📊 Growth Rate Analysis</h4>", unsafe_allow_html=True)
                
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
                        use_container_width=True
                    )
        
        with tab3:
            # Define metric categories
            applications_metrics = [
                'inquiries_received', 'applications_in_progress', 'applications_received', 
                'applications_complete', 'applications_manual', 'applications_verified', 
                'applications_on_hold', 'applications_undelivered', 'applications_deferral', 
                'total_applications', 'admissions_pre_admission'
            ]
            
            admissions_metrics = [
                'admissions_offered', 'admissions_denied', 'admissions_accepted', 
                'admissions_declined', 'admissions_deferred_to_next', 'admissions_deferred_from_last', 
                'admissions_moved_to_other', 'admissions_withdrawn', 'anticipated_cohort_size'
            ]
            
            # Get time series data for all programs
            program_time_series = current_data.pivot_table(
                index='report_date',
                columns='metric_name',
                values='metric_value',
                aggfunc='sum'
            ).fillna(0)
            
            if not program_time_series.empty:
                # ===== APPLICATIONS SECTION =====
                st.markdown("<h4 style='text-align: center; color: #500000;'>📝 Applications Metrics</h4>", unsafe_allow_html=True)
                
                # Initialize session state for applications filter
                if 'exec_app_metrics_reset' not in st.session_state:
                    st.session_state.exec_app_metrics_reset = 0
                
                # Initialize log scale state for applications
                if 'exec_app_log' not in st.session_state:
                    st.session_state.exec_app_log = False
                
                # Initialize chart type state for applications
                if 'exec_app_chart_type' not in st.session_state:
                    st.session_state.exec_app_chart_type = 'Line'
                
                available_app_metrics = [m for m in applications_metrics if m in program_time_series.columns]
                
                app_reset_suffix = f"_{st.session_state.exec_app_metrics_reset}"
                app_state_key = f'selected_app_metrics{app_reset_suffix}'
                
                if app_state_key not in st.session_state:
                    st.session_state[app_state_key] = available_app_metrics.copy()
                
                current_app_selection = st.session_state[app_state_key]
                
                if len(current_app_selection) == len(available_app_metrics):
                    app_summary_text = "All application metrics"
                elif len(current_app_selection) == 0:
                    app_summary_text = "No metrics selected"
                elif len(current_app_selection) == 1:
                    app_summary_text = current_app_selection[0].replace('_', ' ').title()
                else:
                    app_summary_text = f"{len(current_app_selection)} metrics selected"
                
                # Layout: 60% for filter, 20% for chart type, 20% for log scale button
                col_filter, col_chart_type, col_button = st.columns([3, 1, 1])
                
                with col_filter:
                    with st.popover(app_summary_text, use_container_width=True):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("✓ All", key=f"app_all{app_reset_suffix}", use_container_width=True, type="primary"):
                                st.session_state.exec_app_metrics_reset += 1
                                new_app_key = f'selected_app_metrics_{st.session_state.exec_app_metrics_reset}'
                                st.session_state[new_app_key] = available_app_metrics.copy()
                                st.rerun()
                        with col_b:
                            if st.button("✗ Clear", key=f"app_clear{app_reset_suffix}", use_container_width=True, type="secondary"):
                                st.session_state.exec_app_metrics_reset += 1
                                new_app_key = f'selected_app_metrics_{st.session_state.exec_app_metrics_reset}'
                                st.session_state[new_app_key] = []
                                st.rerun()
                        
                        st.divider()
                        
                        for idx, metric in enumerate(available_app_metrics):
                            is_checked = metric in st.session_state[app_state_key]
                            metric_display = metric.replace('_', ' ').title()
                            new_value = st.checkbox(
                                metric_display, 
                                value=is_checked, 
                                key=f"app_cb_{idx}{app_reset_suffix}"
                            )
                            
                            if new_value != is_checked:
                                if new_value:
                                    if metric not in st.session_state[app_state_key]:
                                        st.session_state[app_state_key].append(metric)
                                else:
                                    if metric in st.session_state[app_state_key]:
                                        st.session_state[app_state_key].remove(metric)
                                st.rerun()
                
                with col_chart_type:
                    if st.button(
                        f"📊 {st.session_state.exec_app_chart_type}",
                        key="toggle_chart_type_app",
                        use_container_width=True,
                        type="secondary"
                    ):
                        st.session_state.exec_app_chart_type = 'Bar' if st.session_state.exec_app_chart_type == 'Line' else 'Line'
                        st.rerun()
                
                with col_button:
                    if st.button(
                        f"📈 {'Log' if st.session_state.exec_app_log else 'Linear'}",
                        key="toggle_log_app",
                        use_container_width=True,
                        type="secondary"
                    ):
                        st.session_state.exec_app_log = not st.session_state.exec_app_log
                        st.rerun()
                
                selected_app_metrics = st.session_state.get(app_state_key, available_app_metrics)
                
                # Applications chart
                if len(selected_app_metrics) > 0:
                    fig_app = go.Figure()
                    
                    # Color palette for applications
                    app_colors = ['#500000', '#700000', '#900000', '#B00000', '#D00000', '#F00000', 
                                 '#FF4444', '#FF6666', '#FF8888', '#FFAAAA', '#FFCCCC']
                    
                    if st.session_state.exec_app_chart_type == 'Line':
                        # Line chart with data labels
                        for i, metric in enumerate(selected_app_metrics):
                            if metric in program_time_series.columns:
                                metric_display = metric.replace('_', ' ').title()
                                fig_app.add_trace(go.Scatter(
                                    x=program_time_series.index,
                                    y=program_time_series[metric],
                                    mode='lines+markers+text',
                                    name=metric_display,
                                    line=dict(color=app_colors[i % len(app_colors)], width=3),
                                    marker=dict(size=8),
                                    text=[f'{int(val)}' if val > 0 else '' for val in program_time_series[metric]],
                                    textposition='top center',
                                    textfont=dict(size=10, color=app_colors[i % len(app_colors)]),
                                    hovertemplate=f'<b>{metric_display}</b><br>' +
                                                 'Date: %{x}<br>' +
                                                 'Value: %{y:,.0f}<br>' +
                                                 '<extra></extra>'
                                ))
                    else:
                        # Bar chart (grouped)
                        for i, metric in enumerate(selected_app_metrics):
                            if metric in program_time_series.columns:
                                metric_display = metric.replace('_', ' ').title()
                                fig_app.add_trace(go.Bar(
                                    x=program_time_series.index,
                                    y=program_time_series[metric],
                                    name=metric_display,
                                    marker_color=app_colors[i % len(app_colors)],
                                    text=[f'{int(val)}' if val > 0 else '' for val in program_time_series[metric]],
                                    textposition='outside',
                                    textfont=dict(size=10),
                                    hovertemplate=f'<b>{metric_display}</b><br>' +
                                                 'Date: %{x}<br>' +
                                                 'Value: %{y:,.0f}<br>' +
                                                 '<extra></extra>'
                                ))
                        fig_app.update_layout(barmode='group')
                    
                    fig_app.update_layout(
                        title='Applications Metrics Over Time',
                        height=600,
                        xaxis_title='Date',
                        yaxis_title='Count',
                        yaxis_type='log' if st.session_state.exec_app_log else 'linear',
                        legend=dict(
                            orientation='h',
                            yanchor='bottom',
                            y=-0.35,
                            xanchor='center',
                            x=0.5,
                            bgcolor='rgba(255,255,255,0.9)',
                            bordercolor='rgba(0,0,0,0.3)',
                            borderwidth=1,
                            font=dict(size=11),
                            itemwidth=30
                        ),
                        margin=dict(b=180, t=50, l=40, r=40)
                    )
                    st.plotly_chart(fig_app, use_container_width=True)
                else:
                    st.info("💡 Please select at least one application metric to display.")
                
                # ===== ADMISSIONS SECTION =====
                st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
                st.markdown("<h4 style='text-align: center; color: #500000;'>🎓 Admissions Metrics</h4>", unsafe_allow_html=True)
                
                # Initialize session state for admissions filter
                if 'exec_adm_metrics_reset' not in st.session_state:
                    st.session_state.exec_adm_metrics_reset = 0
                
                # Initialize log scale state for admissions
                if 'exec_adm_log' not in st.session_state:
                    st.session_state.exec_adm_log = False
                
                # Initialize chart type state for admissions
                if 'exec_adm_chart_type' not in st.session_state:
                    st.session_state.exec_adm_chart_type = 'Line'
                
                available_adm_metrics = [m for m in admissions_metrics if m in program_time_series.columns]
                
                adm_reset_suffix = f"_{st.session_state.exec_adm_metrics_reset}"
                adm_state_key = f'selected_adm_metrics{adm_reset_suffix}'
                
                if adm_state_key not in st.session_state:
                    st.session_state[adm_state_key] = available_adm_metrics.copy()
                
                current_adm_selection = st.session_state[adm_state_key]
                
                if len(current_adm_selection) == len(available_adm_metrics):
                    adm_summary_text = "All admission metrics"
                elif len(current_adm_selection) == 0:
                    adm_summary_text = "No metrics selected"
                elif len(current_adm_selection) == 1:
                    adm_summary_text = current_adm_selection[0].replace('_', ' ').title()
                else:
                    adm_summary_text = f"{len(current_adm_selection)} metrics selected"
                
                # Layout: 60% for filter, 20% for chart type, 20% for log scale button
                col_filter_adm, col_chart_type_adm, col_button_adm = st.columns([3, 1, 1])
                
                with col_filter_adm:
                    with st.popover(adm_summary_text, use_container_width=True):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button("✓ All", key=f"adm_all{adm_reset_suffix}", use_container_width=True, type="primary"):
                                st.session_state.exec_adm_metrics_reset += 1
                                new_adm_key = f'selected_adm_metrics_{st.session_state.exec_adm_metrics_reset}'
                                st.session_state[new_adm_key] = available_adm_metrics.copy()
                                st.rerun()
                        with col_b:
                            if st.button("✗ Clear", key=f"adm_clear{adm_reset_suffix}", use_container_width=True, type="secondary"):
                                st.session_state.exec_adm_metrics_reset += 1
                                new_adm_key = f'selected_adm_metrics_{st.session_state.exec_adm_metrics_reset}'
                                st.session_state[new_adm_key] = []
                                st.rerun()
                        
                        st.divider()
                        
                        for idx, metric in enumerate(available_adm_metrics):
                            is_checked = metric in st.session_state[adm_state_key]
                            metric_display = metric.replace('_', ' ').title()
                        new_value = st.checkbox(
                            metric_display, 
                            value=is_checked, 
                            key=f"adm_cb_{idx}{adm_reset_suffix}"
                        )
                        
                        if new_value != is_checked:
                            if new_value:
                                if metric not in st.session_state[adm_state_key]:
                                    st.session_state[adm_state_key].append(metric)
                            else:
                                if metric in st.session_state[adm_state_key]:
                                    st.session_state[adm_state_key].remove(metric)
                            st.rerun()
                
                with col_chart_type_adm:
                    if st.button(
                        f"📊 {st.session_state.exec_adm_chart_type}",
                        key="toggle_chart_type_adm",
                        use_container_width=True,
                        type="secondary"
                    ):
                        st.session_state.exec_adm_chart_type = 'Bar' if st.session_state.exec_adm_chart_type == 'Line' else 'Line'
                        st.rerun()
                
                with col_button_adm:
                    if st.button(
                        f"📈 {'Log' if st.session_state.exec_adm_log else 'Linear'}",
                        key="toggle_log_adm",
                        use_container_width=True,
                        type="secondary"
                    ):
                        st.session_state.exec_adm_log = not st.session_state.exec_adm_log
                        st.rerun()
                
                selected_adm_metrics = st.session_state.get(adm_state_key, available_adm_metrics)
                
                # Admissions chart
                if len(selected_adm_metrics) > 0:
                    fig_adm = go.Figure()
                    
                    # Color palette for admissions (different shades)
                    adm_colors = ['#003366', '#004488', '#0055AA', '#0066CC', '#0077EE', 
                                 '#3399FF', '#5AADFF', '#7AC1FF', '#99D5FF']
                    
                    if st.session_state.exec_adm_chart_type == 'Line':
                        # Line chart with data labels
                        for i, metric in enumerate(selected_adm_metrics):
                            if metric in program_time_series.columns:
                                metric_display = metric.replace('_', ' ').title()
                                fig_adm.add_trace(go.Scatter(
                                    x=program_time_series.index,
                                    y=program_time_series[metric],
                                    mode='lines+markers+text',
                                    name=metric_display,
                                    line=dict(color=adm_colors[i % len(adm_colors)], width=3),
                                    marker=dict(size=8),
                                    text=[f'{int(val)}' if val > 0 else '' for val in program_time_series[metric]],
                                    textposition='top center',
                                    textfont=dict(size=10, color=adm_colors[i % len(adm_colors)]),
                                    hovertemplate=f'<b>{metric_display}</b><br>' +
                                                 'Date: %{x}<br>' +
                                                 'Value: %{y:,.0f}<br>' +
                                                 '<extra></extra>'
                                ))
                    else:
                        # Bar chart (grouped)
                        for i, metric in enumerate(selected_adm_metrics):
                            if metric in program_time_series.columns:
                                metric_display = metric.replace('_', ' ').title()
                                fig_adm.add_trace(go.Bar(
                                    x=program_time_series.index,
                                    y=program_time_series[metric],
                                    name=metric_display,
                                    marker_color=adm_colors[i % len(adm_colors)],
                                    text=[f'{int(val)}' if val > 0 else '' for val in program_time_series[metric]],
                                    textposition='outside',
                                    textfont=dict(size=10),
                                    hovertemplate=f'<b>{metric_display}</b><br>' +
                                                 'Date: %{x}<br>' +
                                                 'Value: %{y:,.0f}<br>' +
                                                 '<extra></extra>'
                                ))
                        fig_adm.update_layout(barmode='group')
                    
                    fig_adm.update_layout(
                        title='Admissions Metrics Over Time',
                        height=600,
                        xaxis_title='Date',
                        yaxis_title='Count',
                        yaxis_type='log' if st.session_state.exec_adm_log else 'linear',
                        legend=dict(
                            orientation='h',
                            yanchor='bottom',
                            y=-0.35,
                            xanchor='center',
                            x=0.5,
                            bgcolor='rgba(255,255,255,0.9)',
                            bordercolor='rgba(0,0,0,0.3)',
                            borderwidth=1,
                            font=dict(size=11),
                            itemwidth=30
                        ),
                        margin=dict(b=180, t=50, l=40, r=40)
                    )
                    st.plotly_chart(fig_adm, use_container_width=True)
                else:
                    st.info("💡 Please select at least one admission metric to display.")
        
        with tab4:
            # Data Tables
            st.markdown("<h4 style='text-align: center; color: #500000;'>📊 Complete Dataset</h4>", unsafe_allow_html=True)
            st.dataframe(complete_data, use_container_width=True, height=400)
            
            # Summary statistics
            st.markdown("<h4 style='text-align: center; color: #500000;'>📈 Summary Statistics</h4>", unsafe_allow_html=True)
            numeric_cols = complete_data.select_dtypes(include=[np.number]).columns
            summary_stats = complete_data[numeric_cols].describe()
            st.dataframe(summary_stats.round(2), use_container_width=True)
            
            # Download options - centered and full width
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv_complete = complete_data.to_csv(index=False)
                st.download_button(
                    "📥 Download Complete Data",
                    csv_complete,
                    f"complete_data_{selected_cohort}_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True
                )
            
            with col2:
                csv_summary = summary_stats.to_csv()
                st.download_button(
                    "📥 Download Summary Stats",
                    csv_summary,
                    f"summary_stats_{selected_cohort}_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True
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
                    "text/csv",
                    use_container_width=True
                )
    
    # Footer for Executive Deep Dive page
    st.divider()
    footer_col1, footer_col2, footer_col3 = st.columns([1, 1, 1])
    with footer_col1:
        st.markdown(f"""
        <div class="footer-left footer-content" style="text-align: left;">
            <p style="color: #6b7280; font-size: 14px; margin: 0;">📊 Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        """, unsafe_allow_html=True)
    with footer_col2:
        st.components.v1.html("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100%; min-height: 60px;">
            <button onclick="window.top.print()" 
                    style="background-color: white;
                           color: #500000;
                           border: 2px solid #e0e0e0;
                           border-radius: 8px;
                           padding: 0.6rem 1.2rem;
                           font-size: 0.95rem;
                           font-weight: 600;
                           cursor: pointer;
                           transition: all 0.3s ease;
                           width: 100%;
                           min-height: 45px;
                           font-family: 'Source Sans Pro', sans-serif;"
                    onmouseover="this.style.backgroundColor='#e9ecef'; this.style.borderColor='#500000';"
                    onmouseout="this.style.backgroundColor='white'; this.style.borderColor='#e0e0e0';">
                🖨️ Print Page
            </button>
        </div>
        """, height=70)
    with footer_col3:
        st.markdown("""
        <div class="footer-right footer-content" style="text-align: right;">
            <p style="color: #6b7280; font-size: 14px; margin: 0;">💡 Use buttons above to switch views</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_page == 'Comparison_Tool':
    # COMPARISON TOOL CONTENT
    
    # Cohort selection filters - directly after page header
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🎓 Primary Cohort**")
        cohort_options = [2028, 2027, 2026]
        primary_cohort = st.selectbox(
            "Primary Cohort",
            options=cohort_options,
            index=0,
            key="comparison_tool_primary",
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown("**🔄 Comparison Cohort**")
        comparison_cohorts = [c for c in cohort_options if c != primary_cohort]
        if comparison_cohorts:
            comparison_cohort = st.selectbox(
                "Comparison Cohort",
                options=comparison_cohorts,
                key="comparison_tool_secondary",
                label_visibility="collapsed"
            )
        else:
            st.warning("No other cohorts available for comparison")
            comparison_cohort = None
    
    with col3:
        st.markdown("**📚 Program Filter**")
        programs_df = load_programs()
        program_options = ['All Programs'] + sorted(programs_df['program_code'].tolist())
        program_filter_comp = st.selectbox(
            "Program Filter",
            options=program_options,
            key="comparison_tool_program",
            label_visibility="collapsed"
        )
    
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
    # How to Use This Comparison Tool - Collapsible
    with st.expander("💡 How to Use This Comparison Tool", expanded=False):
        st.markdown("""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; font-size: 14px; color: #495057;">
            <div>
                <strong style="color: #500000;">📊 Step-by-Step Guide:</strong>
                <ul style="margin: 8px 0; padding-left: 20px;">
                    <li><strong>Select Cohorts:</strong> Choose primary and comparison cohorts using filters above</li>
                    <li><strong>Filter by Program:</strong> Select specific program or view all programs combined</li>
                    <li><strong>Explore Time Series:</strong> Click metric selector to visualize trends over time</li>
                    <li><strong>View Data Tables:</strong> Click "Show Data Table" for detailed program breakdowns</li>
                </ul>
            </div>
            <div>
                <strong style="color: #500000;">🎯 Key Features:</strong>
                <ul style="margin: 8px 0; padding-left: 20px;">
                    <li><strong>Percentage Changes:</strong> Full-width bar chart showing growth/decline metrics</li>
                    <li><strong>Comprehensive Table:</strong> Detailed comparison with variance metrics</li>
                    <li><strong>Export Options:</strong> Download comparison tables or individual cohort data</li>
                    <li><strong>Visual Indicators:</strong> Green = growth, Red = decline, hover for exact values</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
    # Load comparison data
    if comparison_cohort:
        comp_data = load_yoy_comparison_data(primary_cohort, comparison_cohort)
        primary_data = comp_data[comp_data['cohort_year'] == primary_cohort]
        secondary_data = comp_data[comp_data['cohort_year'] == comparison_cohort]
        
        # Apply program filter
        if program_filter_comp != "All Programs":
            primary_data = primary_data[primary_data['program'] == program_filter_comp]
            secondary_data = secondary_data[secondary_data['program'] == program_filter_comp]
        
        if not primary_data.empty and not secondary_data.empty:
            # Get latest data for both cohorts
            primary_latest_date = primary_data['report_date'].max()
            primary_latest = primary_data[primary_data['report_date'] == primary_latest_date]
            
            secondary_latest_date = secondary_data['report_date'].max()
            secondary_latest = secondary_data[secondary_data['report_date'] == secondary_latest_date]
            
            program_scope = f" - {program_filter_comp}" if program_filter_comp != "All Programs" else ""
            
            # Display comparison header
            st.markdown(f"""
            <div style="text-align: center;
                        padding: 15px;
                        background: #f8f9fa;
                        border-radius: 8px;
                        margin: 20px 0;">
                <h3 style="color: #500000; margin: 0; font-size: 20px;">
                    📊 Comparing: Class of {primary_cohort} vs Class of {comparison_cohort}{program_scope}
                </h3>
                <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 14px;">
                    Primary: {primary_latest_date.strftime('%B %d, %Y')} | Comparison: {secondary_latest_date.strftime('%B %d, %Y')}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            
            # Calculate metrics for both cohorts
            primary_metrics = primary_latest.groupby('metric_name')['metric_value'].sum()
            secondary_metrics = secondary_latest.groupby('metric_name')['metric_value'].sum()
            
            # Create comprehensive comparison dataframe
            yoy_comparison = pd.DataFrame({
                f'Class of {primary_cohort}': primary_metrics,
                f'Class of {comparison_cohort}': secondary_metrics
            }).fillna(0)
            
            yoy_comparison['Absolute Change'] = yoy_comparison[f'Class of {primary_cohort}'] - yoy_comparison[f'Class of {comparison_cohort}']
            
            # Calculate % Change with proper handling of edge cases
            def calculate_pct_change(row):
                primary_val = row[f'Class of {primary_cohort}']
                comparison_val = row[f'Class of {comparison_cohort}']
                
                # Case 1: Both are zero - no change
                if primary_val == 0 and comparison_val == 0:
                    return 0.0
                
                # Case 2: Comparison is zero but primary is not - show as N/A (will be handled in display)
                if comparison_val == 0 and primary_val > 0:
                    return np.nan  # Not applicable - no base for comparison
                
                # Case 3: Primary is zero but comparison is not - 100% decline
                if primary_val == 0 and comparison_val > 0:
                    return -100.0
                
                # Case 4: Normal calculation
                return ((primary_val / comparison_val) - 1) * 100
            
            yoy_comparison['% Change'] = yoy_comparison.apply(calculate_pct_change, axis=1).round(1)
            
            # Calculate variance metrics (statistical variance for two data points)
            # Mean of the two cohorts
            yoy_comparison['Mean'] = yoy_comparison[[f'Class of {primary_cohort}', f'Class of {comparison_cohort}']].mean(axis=1)
            
            # Variance: average of squared deviations from mean
            yoy_comparison['Variance'] = (
                ((yoy_comparison[f'Class of {primary_cohort}'] - yoy_comparison['Mean']) ** 2 + 
                 (yoy_comparison[f'Class of {comparison_cohort}'] - yoy_comparison['Mean']) ** 2) / 2
            )
            
            # Standard Deviation: square root of variance
            yoy_comparison['Std Deviation'] = np.sqrt(yoy_comparison['Variance'])
            
            # Coefficient of Variation: (Std Dev / Mean) × 100
            # Avoid division by zero
            yoy_comparison['Coefficient of Variation'] = np.where(
                yoy_comparison['Mean'] != 0,
                (yoy_comparison['Std Deviation'] / yoy_comparison['Mean']) * 100,
                0
            ).round(2)
            
            # Add performance indicators with proper edge case handling
            
            # Add performance indicators with proper edge case handling
            def get_performance_indicator(row):
                pct_change = row['% Change']
                primary_val = row[f'Class of {primary_cohort}']
                comparison_val = row[f'Class of {comparison_cohort}']
                
                # Special case: no base for comparison (comparison was 0)
                if comparison_val == 0 and primary_val > 0:
                    return '🟢 New Metric - Strong Growth (No Base Year Data)'
                
                # Special case: metric disappeared (primary is 0, comparison had value)
                if primary_val == 0 and comparison_val > 0:
                    return '🔴 Complete Decline (Metric Discontinued)'
                
                # Normal cases based on % change
                if pct_change > 15:
                    return '🟢 Strong Growth'
                elif pct_change > 5:
                    return '🟡 Moderate Growth'
                elif pct_change >= -5:
                    return '➡️ Stable'
                else:
                    return '🔴 Decline'
            
            yoy_comparison['Performance Indicator'] = yoy_comparison.apply(get_performance_indicator, axis=1)
            
            # Filter out metrics where BOTH cohorts have zero values (no data for either)
            metrics_with_data = yoy_comparison[
                (yoy_comparison[f'Class of {primary_cohort}'] != 0) | 
                (yoy_comparison[f'Class of {comparison_cohort}'] != 0)
            ]
            
            # Track excluded metrics for display
            excluded_metrics = yoy_comparison[
                (yoy_comparison[f'Class of {primary_cohort}'] == 0) & 
                (yoy_comparison[f'Class of {comparison_cohort}'] == 0)
            ].index.tolist()
            
            # Use filtered data for display
            yoy_comparison = metrics_with_data.copy()
            
            # Initialize session state for time series metrics filter
            if 'comp_ts_metrics_reset' not in st.session_state:
                st.session_state.comp_ts_metrics_reset = 0
            
            # Metric selector for time series - Custom popover dropdown
            # Filter to only show metrics that have data for at least one cohort
            all_metrics = sorted(primary_data['metric_name'].unique())
            available_metrics = [m for m in all_metrics if m in yoy_comparison.index]
            
            ts_reset_suffix = f"_{st.session_state.comp_ts_metrics_reset}"
            ts_state_key = f'selected_ts_metrics{ts_reset_suffix}'
            
            # Set default selection
            default_metrics = ['inquiries_received', 'total_applications', 'admissions_offered', 'anticipated_cohort_size']
            default_selection = [m for m in default_metrics if m in available_metrics]
            if not default_selection:
                default_selection = available_metrics[:4] if len(available_metrics) >= 4 else available_metrics
            
            if ts_state_key not in st.session_state:
                st.session_state[ts_state_key] = default_selection.copy()
            
            current_ts_selection = st.session_state[ts_state_key]
            
            # Create summary text for popover button
            if len(current_ts_selection) == len(available_metrics):
                ts_summary_text = "All metrics selected"
            elif len(current_ts_selection) == 0:
                ts_summary_text = "No metrics selected - Click to select"
            elif len(current_ts_selection) == 1:
                ts_summary_text = current_ts_selection[0].replace('_', ' ').title()
            else:
                ts_summary_text = f"{len(current_ts_selection)} metrics selected"
            
            # Custom popover dropdown
            with st.popover(f"📊 {ts_summary_text}", use_container_width=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✓ All", key=f"ts_all{ts_reset_suffix}", use_container_width=True, type="primary"):
                        st.session_state.comp_ts_metrics_reset += 1
                        new_ts_key = f'selected_ts_metrics_{st.session_state.comp_ts_metrics_reset}'
                        st.session_state[new_ts_key] = available_metrics.copy()
                        st.rerun()
                with col_b:
                    if st.button("✗ Clear", key=f"ts_clear{ts_reset_suffix}", use_container_width=True, type="secondary"):
                        st.session_state.comp_ts_metrics_reset += 1
                        new_ts_key = f'selected_ts_metrics_{st.session_state.comp_ts_metrics_reset}'
                        st.session_state[new_ts_key] = []
                        st.rerun()
                
                st.divider()
                
                for idx, metric in enumerate(available_metrics):
                    is_checked = metric in st.session_state[ts_state_key]
                    metric_display = metric.replace('_', ' ').title()
                    new_value = st.checkbox(
                        metric_display, 
                        value=is_checked, 
                        key=f"ts_cb_{idx}{ts_reset_suffix}"
                    )
                    
                    if new_value != is_checked:
                        if new_value:
                            if metric not in st.session_state[ts_state_key]:
                                st.session_state[ts_state_key].append(metric)
                        else:
                            if metric in st.session_state[ts_state_key]:
                                st.session_state[ts_state_key].remove(metric)
                        st.rerun()
            
            selected_ts_metrics = st.session_state.get(ts_state_key, default_selection)
            
            if selected_ts_metrics:
                for idx, metric in enumerate(selected_ts_metrics):
                    # Properly aggregate data by date (sum across programs)
                    primary_ts = primary_data[primary_data['metric_name'] == metric].groupby('report_date')['metric_value'].sum().reset_index().sort_values('report_date')
                    secondary_ts = secondary_data[secondary_data['metric_name'] == metric].groupby('report_date')['metric_value'].sum().reset_index().sort_values('report_date')
                    
                    # Keep original data for drill-down
                    primary_detail = primary_data[primary_data['metric_name'] == metric].sort_values(['report_date', 'program'])
                    secondary_detail = secondary_data[secondary_data['metric_name'] == metric].sort_values(['report_date', 'program'])
                    
                    if not primary_ts.empty or not secondary_ts.empty:
                        # Display metric name as section header
                        st.markdown(f"""
                        <div style="text-align: center;
                                    padding: 10px;
                                    background: #e9ecef;
                                    border-radius: 6px;
                                    margin: 15px 0 10px 0;">
                            <h4 style="color: #500000; margin: 0; font-size: 16px;">{metric.replace('_', ' ').title()}</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Side-by-side comparison
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"<p style='text-align: center; font-weight: bold; color: #500000;'>Class of {primary_cohort}</p>", unsafe_allow_html=True)
                            if not primary_ts.empty:
                                fig_primary = go.Figure()
                                fig_primary.add_trace(go.Scatter(
                                    x=primary_ts['report_date'],
                                    y=primary_ts['metric_value'],
                                    mode='lines+markers+text',
                                    name=f'Class of {primary_cohort}',
                                    line=dict(color='#500000', width=4),
                                    marker=dict(size=12, symbol='circle'),
                                    text=[f'{int(val):,}' for val in primary_ts['metric_value']],
                                    textposition='top center',
                                    textfont=dict(size=10, color='#500000'),
                                    hovertemplate='<b>%{x|%b %d, %Y}</b><br>Value: %{y:,.0f}<extra></extra>',
                                    showlegend=False
                                ))
                                
                                fig_primary.update_layout(
                                    height=350,
                                    xaxis_title='Date',
                                    yaxis_title='Count',
                                    xaxis=dict(
                                        showgrid=True,
                                        gridcolor='#e0e0e0',
                                        showline=True,
                                        linecolor='#500000',
                                        linewidth=2
                                    ),
                                    yaxis=dict(
                                        showgrid=True,
                                        gridcolor='#e0e0e0',
                                        showline=True,
                                        linecolor='#500000',
                                        linewidth=2
                                    ),
                                    plot_bgcolor='#fafafa',
                                    margin=dict(t=40, b=60, l=60, r=40)
                                )
                                st.plotly_chart(fig_primary, use_container_width=True, key=f"comp_primary_{metric}_{idx}")
                            else:
                                st.info("No data available")
                        
                        with col2:
                            st.markdown(f"<p style='text-align: center; font-weight: bold; color: #B00000;'>Class of {comparison_cohort}</p>", unsafe_allow_html=True)
                            if not secondary_ts.empty:
                                fig_secondary = go.Figure()
                                fig_secondary.add_trace(go.Scatter(
                                    x=secondary_ts['report_date'],
                                    y=secondary_ts['metric_value'],
                                    mode='lines+markers+text',
                                    name=f'Class of {comparison_cohort}',
                                    line=dict(color='#B00000', width=4),
                                    marker=dict(size=12, symbol='diamond'),
                                    text=[f'{int(val):,}' for val in secondary_ts['metric_value']],
                                    textposition='top center',
                                    textfont=dict(size=10, color='#B00000'),
                                    hovertemplate='<b>%{x|%b %d, %Y}</b><br>Value: %{y:,.0f}<extra></extra>',
                                    showlegend=False
                                ))
                                
                                fig_secondary.update_layout(
                                    height=350,
                                    xaxis_title='Date',
                                    yaxis_title='Count',
                                    xaxis=dict(
                                        showgrid=True,
                                        gridcolor='#e0e0e0',
                                        showline=True,
                                        linecolor='#B00000',
                                        linewidth=2
                                    ),
                                    yaxis=dict(
                                        showgrid=True,
                                        gridcolor='#e0e0e0',
                                        showline=True,
                                        linecolor='#B00000',
                                        linewidth=2
                                    ),
                                    plot_bgcolor='#fafafa',
                                    margin=dict(t=40, b=60, l=60, r=40)
                                )
                                st.plotly_chart(fig_secondary, use_container_width=True, key=f"comp_secondary_{metric}_{idx}")
                            else:
                                st.info("No data available")
                        
                        # Centered button for this metric (controls both tables)
                        col_left, col_center, col_right = st.columns([2, 1, 2])
                        with col_center:
                            # Initialize session state for this metric's table visibility
                            table_key = f"comp_table_visible_{metric}_{idx}"
                            if table_key not in st.session_state:
                                st.session_state[table_key] = False
                            
                            # Toggle button
                            button_label = "Hide Data Table" if st.session_state[table_key] else "📊 Show Data Table"
                            if st.button(button_label, key=f"comp_btn_metric_{metric}_{idx}", use_container_width=True):
                                st.session_state[table_key] = not st.session_state[table_key]
                                st.rerun()
                        
                        # Data tables with expandable rows (only if button was clicked)
                        if st.session_state.get(table_key, False):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if not primary_ts.empty:
                                    st.markdown("**📋 Data Details (Click to expand by program)**")
                                    for date_idx, row in primary_ts.iterrows():
                                        date_val = pd.to_datetime(row['report_date'])
                                        total_val = int(row['metric_value'])
                                        date_str = date_val.strftime('%b %d, %Y')
                                        
                                        # Get program breakdown for this date
                                        date_details = primary_detail[primary_detail['report_date'] == row['report_date']]
                                        
                                        with st.expander(f"📅 {date_str} - Total: {total_val:,}"):
                                            if not date_details.empty:
                                                breakdown = date_details[['program', 'metric_value']].copy()
                                                breakdown.columns = ['Program', 'Value']
                                                breakdown['Value'] = breakdown['Value'].astype(int)
                                                st.dataframe(
                                                    breakdown.style.set_properties(**{
                                                        'text-align': 'center',
                                                        'font-size': '13px'
                                                    }).set_table_styles([
                                                        {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#500000'), ('color', 'white'), ('font-weight', 'bold')]}
                                                    ]),
                                                    use_container_width=True,
                                                    hide_index=True
                                                )
                                            else:
                                                st.info("No program breakdown available")
                            
                            with col2:
                                if not secondary_ts.empty:
                                    st.markdown("**📋 Data Details (Click to expand by program)**")
                                    for date_idx, row in secondary_ts.iterrows():
                                        date_val = pd.to_datetime(row['report_date'])
                                        total_val = int(row['metric_value'])
                                        date_str = date_val.strftime('%b %d, %Y')
                                        
                                        # Get program breakdown for this date
                                        date_details = secondary_detail[secondary_detail['report_date'] == row['report_date']]
                                        
                                        with st.expander(f"📅 {date_str} - Total: {total_val:,}"):
                                            if not date_details.empty:
                                                breakdown = date_details[['program', 'metric_value']].copy()
                                                breakdown.columns = ['Program', 'Value']
                                                breakdown['Value'] = breakdown['Value'].astype(int)
                                                st.dataframe(
                                                    breakdown.style.set_properties(**{
                                                        'text-align': 'center',
                                                        'font-size': '13px'
                                                    }).set_table_styles([
                                                        {'selector': 'th', 'props': [('text-align', 'center'), ('background-color', '#B00000'), ('color', 'white'), ('font-weight', 'bold')]}
                                                    ]),
                                                    use_container_width=True,
                                                    hide_index=True
                                                )
                                            else:
                                                st.info("No program breakdown available")
            else:
                st.info("💡 Select at least one metric to view time series comparison.")
            
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            
            # Percentage Change Analysis (FULL WIDTH with styled header)
            st.markdown("""
            <div style="text-align: center;
                        padding: 15px;
                        background: #f8f9fa;
                        border-radius: 8px;
                        margin: 20px 0;">
                <h3 style="color: #500000; margin: 0; font-size: 20px;">📈 Percentage Change Analysis</h3>
                <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 14px;">
                    Compare performance changes across all metrics
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            change_data = yoy_comparison['% Change'].dropna()
            colors = ['#28a745' if x > 0 else '#dc3545' if x < 0 else '#6c757d' for x in change_data.values]
            
            # Calculate y-axis range with padding for text labels
            max_val = change_data.max()
            min_val = change_data.min()
            y_range_padding = max(abs(max_val), abs(min_val)) * 0.2  # 20% padding
            
            fig = go.Figure(go.Bar(
                x=change_data.index,
                y=change_data.values,
                marker_color=colors,
                text=[f'{x:+.1f}%' for x in change_data.values],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Change: %{y:+.1f}%<extra></extra>'
            ))
            
            fig.update_layout(
                height=550,
                xaxis_title='Metrics',
                yaxis_title='% Change',
                yaxis=dict(
                    range=[min_val - y_range_padding, max_val + y_range_padding]
                ),
                showlegend=False,
                margin=dict(t=60, b=100, l=60, r=60)
            )
            fig.add_hline(y=0, line_dash="dash", line_color="black", line_width=2)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
            
            # Show note about excluded metrics if any
            if excluded_metrics:
                excluded_list = ', '.join([m.replace('_', ' ').title() for m in excluded_metrics])
                st.markdown(f"""
                <div style="background: #fff3cd;
                            border-left: 4px solid #ffc107;
                            padding: 12px 15px;
                            border-radius: 6px;
                            margin: 15px 0;">
                    <p style="margin: 0; color: #856404; font-size: 14px;">
                        ℹ️ <strong>Note:</strong> The following metrics were excluded from comparison as they have no data for either cohort: <strong>{excluded_list}</strong>
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Comprehensive Comparison Table with Export Buttons (styled header)
            st.markdown("""
            <div style="text-align: center;
                        padding: 15px;
                        background: #f8f9fa;
                        border-radius: 8px;
                        margin: 20px 0;">
                <h3 style="color: #500000; margin: 0; font-size: 20px;">📊 Comprehensive Comparison Table with Variance Metrics</h3>
                <p style="margin: 5px 0 0 0; color: #6c757d; font-size: 14px;">
                    Detailed comparison with statistical variance analysis
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            enhanced_comparison = yoy_comparison.copy()
            # Drop the Mean column (used only for calculation)
            if 'Mean' in enhanced_comparison.columns:
                enhanced_comparison = enhanced_comparison.drop(columns=['Mean'])
            
            # Round for display
            display_df = enhanced_comparison.copy().round(2)
            
            # Create display dataframe with selected columns
            
            # Create styled dataframe with proper formatting
            styled_df = display_df.style.format({
                f'Class of {primary_cohort}': '{:.0f}',
                f'Class of {comparison_cohort}': '{:.0f}',
                'Absolute Change': '{:+.0f}',
                '% Change': lambda x: 'N/A' if pd.isna(x) else f'{x:+.1f}%',
                'Variance': '{:.1f}',
                'Std Deviation': '{:.1f}',
                'Coefficient of Variation': '{:.1f}%'
            }).background_gradient(subset=['Coefficient of Variation'], cmap='YlOrRd')
            
            st.dataframe(
                styled_df,
                use_container_width=True,
                height=500
            )
            
            # Add spacing before export buttons
            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
            
            # Export buttons directly below the table
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv_comparison = enhanced_comparison.to_csv()
                st.download_button(
                    "📥 Download Comparison Table",
                    csv_comparison,
                    f"comparison_{primary_cohort}_vs_{comparison_cohort}_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True
                )
            
            with col2:
                csv_primary = primary_data.to_csv(index=False)
                st.download_button(
                    f"📥 Download {primary_cohort} Data",
                    csv_primary,
                    f"cohort_{primary_cohort}_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True
                )
            
            with col3:
                csv_secondary = secondary_data.to_csv(index=False)
                st.download_button(
                    f"📥 Download {comparison_cohort} Data",
                    csv_secondary,
                    f"cohort_{comparison_cohort}_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv",
                    use_container_width=True
                )
        
        else:
            st.warning("⚠️ No data available for the selected cohorts and program filter combination.")
            st.info("💡 Try selecting different cohorts or adjusting the program filter.")
    else:
        st.info("💡 Please select a comparison cohort to begin the analysis.")
    
    # Footer for Comparison Tool page
    st.divider()
    footer_col1, footer_col2, footer_col3 = st.columns([1, 1, 1])
    with footer_col1:
        st.markdown(f"""
        <div class="footer-left footer-content" style="text-align: left;">
            <p style="color: #6b7280; font-size: 14px; margin: 0;">📊 Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        """, unsafe_allow_html=True)
    with footer_col2:
        st.components.v1.html("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100%; min-height: 60px;">
            <button onclick="window.top.print()" 
                    style="background-color: white;
                           color: #500000;
                           border: 2px solid #e0e0e0;
                           border-radius: 8px;
                           padding: 0.6rem 1.2rem;
                           font-size: 0.95rem;
                           font-weight: 600;
                           cursor: pointer;
                           transition: all 0.3s ease;
                           width: 100%;
                           min-height: 45px;
                           font-family: 'Source Sans Pro', sans-serif;"
                    onmouseover="this.style.backgroundColor='#e9ecef'; this.style.borderColor='#500000';"
                    onmouseout="this.style.backgroundColor='white'; this.style.borderColor='#e0e0e0';">
                🖨️ Print Page
            </button>
        </div>
        """, height=70)
    with footer_col3:
        st.markdown("""
        <div class="footer-right footer-content" style="text-align: right;">
            <p style="color: #6b7280; font-size: 14px; margin: 0;">💡 Use buttons above to switch views</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_page == 'Marketing_Analysis':
    # MARKETING ANALYSIS CONTENT
    
    # Check if marketing data is available
    conn = get_connection()
    
    # Test if marketing tables exist
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='marketing_spend';")
    has_marketing_spend = cursor.fetchone() is not None
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='marketing_spend_totals';")
    has_marketing_totals = cursor.fetchone() is not None
    
    has_data = has_marketing_spend and has_marketing_totals
    
    if not has_data:
        st.warning("⚠️ Marketing data not yet available")
        st.info("""
        ### 🚧 Marketing Spend Dashboard
        
        Run `python3 marketing_etl.py` to load marketing spend data.
        
        **What you'll see here:**
        - 📊 Spend by program and channel
        - 💰 Monthly spend trends
        - 📈 Channel performance comparison
        - 🎯 Fiscal year breakdown
        - 📝 Incremental spend notes
        """)
    else:
        # Load data from new tables
        spend_df = pd.read_sql("""
            SELECT 
                program,
                channel,
                fiscal_year,
                month_date,
                spend_amount,
                extra_notes
            FROM marketing_spend
            ORDER BY month_date DESC, program, channel
        """, conn)
        
        # Convert dates
        spend_df['month_date'] = pd.to_datetime(spend_df['month_date'])
        
        # Add normalized program names for matching
        spend_df['program_normalized'] = spend_df['program'].apply(normalize_program_name)
        
        # GLOBAL FILTERS - Applied to all tabs
        st.markdown("""
        <style>
        /* Section headers with centered styling */
        .section-header {
            text-align: center;
            padding: 12px;
            background: #e9ecef;
            border-radius: 8px;
            margin: 20px 0 15px 0;
        }
        .section-header h3 {
            margin: 0;
            color: #500000;
            font-size: 20px;
        }
        
        /* Style bordered containers with gradient background */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"]:has(> div[data-testid="stHorizontalBlock"]) {
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%) !important;
            padding: 15px !important;
            border-radius: 8px !important;
        }
        
        /* Equal-sized buttons */
        div[data-testid="stButton"] button {
            width: 100% !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            font-size: 12px !important;
            padding: 8px 4px !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Initialize independent reset counters for each filter
        if 'fy_reset_count' not in st.session_state:
            st.session_state.fy_reset_count = 0
        if 'prog_reset_count' not in st.session_state:
            st.session_state.prog_reset_count = 0
        if 'chan_reset_count' not in st.session_state:
            st.session_state.chan_reset_count = 0
        
        col1, col2, col3 = st.columns(3)
        
        # FISCAL YEAR MULTI-SELECT
        with col1:
            fiscal_years_list_global = sorted(spend_df['fiscal_year'].unique().tolist())
            
            # Use independent reset counter for fiscal year
            fy_reset_suffix = f"_{st.session_state.fy_reset_count}"
            fy_state_key_global = f'selected_fy_global{fy_reset_suffix}'
            
            if fy_state_key_global not in st.session_state:
                st.session_state[fy_state_key_global] = fiscal_years_list_global.copy()
            
            current_fy_selection_global = st.session_state[fy_state_key_global]
            
            if len(current_fy_selection_global) == len(fiscal_years_list_global):
                fy_summary_text_global = "All fiscal years"
            elif len(current_fy_selection_global) == 0:
                fy_summary_text_global = "No fiscal years selected"
            elif len(current_fy_selection_global) == 1:
                fy_summary_text_global = str(current_fy_selection_global[0])
            else:
                fy_summary_text_global = f"{len(current_fy_selection_global)} fiscal years"
            
            st.markdown("**📅 Fiscal Year**")
            
            with st.popover(fy_summary_text_global, use_container_width=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✓ All", key=f"fy_all_global{fy_reset_suffix}", use_container_width=True, type="primary"):
                        st.session_state.fy_reset_count += 1
                        new_fy_key_global = f'selected_fy_global_{st.session_state.fy_reset_count}'
                        st.session_state[new_fy_key_global] = fiscal_years_list_global.copy()
                        st.rerun()
                with col_b:
                    if st.button("✗ Clear", key=f"fy_clear_global{fy_reset_suffix}", use_container_width=True, type="secondary"):
                        st.session_state.fy_reset_count += 1
                        new_fy_key_global = f'selected_fy_global_{st.session_state.fy_reset_count}'
                        st.session_state[new_fy_key_global] = []
                        st.rerun()
                
                st.divider()
                
                for idx, fy in enumerate(fiscal_years_list_global):
                    is_checked = fy in st.session_state[fy_state_key_global]
                    new_value = st.checkbox(
                        str(fy), 
                        value=is_checked, 
                        key=f"fy_cb_{idx}_global{fy_reset_suffix}"
                    )
                    
                    if new_value != is_checked:
                        if new_value:
                            if fy not in st.session_state[fy_state_key_global]:
                                st.session_state[fy_state_key_global].append(fy)
                        else:
                            if fy in st.session_state[fy_state_key_global]:
                                st.session_state[fy_state_key_global].remove(fy)
                        st.rerun()
        
        selected_fy_global = st.session_state.get(fy_state_key_global, fiscal_years_list_global)
        
        fy_filtered_global = spend_df.copy()
        if len(selected_fy_global) > 0:
            fy_filtered_global = fy_filtered_global[fy_filtered_global['fiscal_year'].isin(selected_fy_global)]
        else:
            fy_filtered_global = fy_filtered_global.head(0)
        
        # PROGRAM MULTI-SELECT
        with col2:
            programs_list_global = sorted(fy_filtered_global['program'].unique().tolist())
            
            # Use independent reset counter for programs
            prog_reset_suffix = f"_{st.session_state.prog_reset_count}"
            prog_state_key_global = f'selected_programs_global{prog_reset_suffix}'
            
            if prog_state_key_global not in st.session_state:
                st.session_state[prog_state_key_global] = programs_list_global.copy()
            
            # Auto-update: Remove programs that are no longer available due to fiscal year filter changes
            current_prog_selection_global = st.session_state[prog_state_key_global]
            valid_programs = [prog for prog in current_prog_selection_global if prog in programs_list_global]
            
            # If the available programs changed, update the selection to only valid ones
            if set(valid_programs) != set(current_prog_selection_global):
                st.session_state[prog_state_key_global] = valid_programs if valid_programs else programs_list_global.copy()
                current_prog_selection_global = st.session_state[prog_state_key_global]
            
            if len(current_prog_selection_global) == len(programs_list_global):
                prog_summary_text_global = "All programs"
            elif len(current_prog_selection_global) == 0:
                prog_summary_text_global = "No programs selected"
            elif len(current_prog_selection_global) == 1:
                prog_summary_text_global = current_prog_selection_global[0]
            else:
                prog_summary_text_global = f"{len(current_prog_selection_global)} programs"
            
            st.markdown("**🎓 Program**")
            
            with st.popover(prog_summary_text_global, use_container_width=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✓ All", key=f"prog_all_global{prog_reset_suffix}", use_container_width=True, type="primary"):
                        st.session_state.prog_reset_count += 1
                        new_prog_key_global = f'selected_programs_global_{st.session_state.prog_reset_count}'
                        st.session_state[new_prog_key_global] = programs_list_global.copy()
                        st.rerun()
                with col_b:
                    if st.button("✗ Clear", key=f"prog_clear_global{prog_reset_suffix}", use_container_width=True, type="secondary"):
                        st.session_state.prog_reset_count += 1
                        new_prog_key_global = f'selected_programs_global_{st.session_state.prog_reset_count}'
                        st.session_state[new_prog_key_global] = []
                        st.rerun()
                
                st.divider()
                
                for idx, program in enumerate(programs_list_global):
                    is_checked = program in st.session_state[prog_state_key_global]
                    new_value = st.checkbox(
                        program, 
                        value=is_checked, 
                        key=f"prog_cb_{idx}_global{prog_reset_suffix}"
                    )
                    
                    if new_value != is_checked:
                        if new_value:
                            if program not in st.session_state[prog_state_key_global]:
                                st.session_state[prog_state_key_global].append(program)
                        else:
                            if program in st.session_state[prog_state_key_global]:
                                st.session_state[prog_state_key_global].remove(program)
                        st.rerun()
        
        selected_programs_global = st.session_state.get(prog_state_key_global, programs_list_global)
        
        program_filtered_global = fy_filtered_global.copy()
        if len(selected_programs_global) > 0:
            program_filtered_global = program_filtered_global[program_filtered_global['program'].isin(selected_programs_global)]
        else:
            program_filtered_global = program_filtered_global.head(0)
        
        # CHANNEL MULTI-SELECT
        with col3:
            channels_list_global = sorted(program_filtered_global['channel'].unique().tolist())
            
            # Use independent reset counter for channels
            chan_reset_suffix = f"_{st.session_state.chan_reset_count}"
            chan_state_key_global = f'selected_channels_global{chan_reset_suffix}'
            
            if chan_state_key_global not in st.session_state:
                st.session_state[chan_state_key_global] = channels_list_global.copy()
            
            # Auto-update: Remove channels that are no longer available due to upstream filter changes
            current_chan_selection_global = st.session_state[chan_state_key_global]
            valid_channels = [ch for ch in current_chan_selection_global if ch in channels_list_global]
            
            # If the available channels changed, update the selection to only valid ones
            if set(valid_channels) != set(current_chan_selection_global):
                st.session_state[chan_state_key_global] = valid_channels if valid_channels else channels_list_global.copy()
                current_chan_selection_global = st.session_state[chan_state_key_global]
            
            if len(current_chan_selection_global) == len(channels_list_global):
                chan_summary_text_global = "All channels"
            elif len(current_chan_selection_global) == 0:
                chan_summary_text_global = "No channels selected"
            elif len(current_chan_selection_global) == 1:
                chan_summary_text_global = current_chan_selection_global[0]
            else:
                chan_summary_text_global = f"{len(current_chan_selection_global)} channels"
            
            st.markdown("**📢 Channel**")
            
            with st.popover(chan_summary_text_global, use_container_width=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✓ All", key=f"chan_all_global{chan_reset_suffix}", use_container_width=True, type="primary"):
                        st.session_state.chan_reset_count += 1
                        new_chan_key_global = f'selected_channels_global_{st.session_state.chan_reset_count}'
                        st.session_state[new_chan_key_global] = channels_list_global.copy()
                        st.rerun()
                with col_b:
                    if st.button("✗ Clear", key=f"chan_clear_global{chan_reset_suffix}", use_container_width=True, type="secondary"):
                        st.session_state.chan_reset_count += 1
                        new_chan_key_global = f'selected_channels_global_{st.session_state.chan_reset_count}'
                        st.session_state[new_chan_key_global] = []
                        st.rerun()
                
                st.divider()
                
                for idx, channel in enumerate(channels_list_global):
                    is_checked = channel in st.session_state[chan_state_key_global]
                    new_value = st.checkbox(
                        channel, 
                        value=is_checked, 
                        key=f"chan_cb_{idx}_global{chan_reset_suffix}"
                    )
                    
                    if new_value != is_checked:
                        if new_value:
                            if channel not in st.session_state[chan_state_key_global]:
                                st.session_state[chan_state_key_global].append(channel)
                        else:
                            if channel in st.session_state[chan_state_key_global]:
                                st.session_state[chan_state_key_global].remove(channel)
                        st.rerun()
        
        selected_channels_global = st.session_state.get(chan_state_key_global, channels_list_global)
        
        # Apply all global filters to create the master filtered dataset
        filtered_spend_global = spend_df.copy()
        
        if len(selected_fy_global) > 0:
            filtered_spend_global = filtered_spend_global[filtered_spend_global['fiscal_year'].isin(selected_fy_global)]
        else:
            filtered_spend_global = filtered_spend_global.head(0)
        
        if len(selected_programs_global) > 0:
            filtered_spend_global = filtered_spend_global[filtered_spend_global['program'].isin(selected_programs_global)]
        else:
            filtered_spend_global = filtered_spend_global.head(0)
        
        if len(selected_channels_global) > 0:
            filtered_spend_global = filtered_spend_global[filtered_spend_global['channel'].isin(selected_channels_global)]
        else:
            filtered_spend_global = filtered_spend_global.head(0)
        
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        
        # How to Use This Analysis - Collapsible
        with st.expander("💡 How to Use This Analysis", expanded=False):
            st.markdown("""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; font-size: 14px; color: #495057;">
                <div>
                    <strong style="color: #500000;">📊 What You Can Discover:</strong>
                    <ul style="margin: 8px 0; padding-left: 20px;">
                        <li><strong>Spend Analysis:</strong> Track marketing investments by channel and program</li>
                        <li><strong>Channel Performance:</strong> Compare effectiveness across different marketing channels</li>
                        <li><strong>Trend Tracking:</strong> Monitor spending patterns over time and fiscal years</li>
                        <li><strong>ROI Insights:</strong> Understand cost per inquiry and conversion metrics</li>
                    </ul>
                </div>
                <div>
                    <strong style="color: #500000;">🎯 Interactive Features:</strong>
                    <ul style="margin: 8px 0; padding-left: 20px;">
                        <li><strong>Multi-Select Filters:</strong> Choose fiscal years, programs, and channels</li>
                        <li><strong>Dynamic Charts:</strong> Click legend items to toggle data series on/off</li>
                        <li><strong>Hover Details:</strong> Move mouse over charts for exact values and breakdowns</li>
                        <li><strong>Data Export:</strong> Download filtered data for further analysis</li>
                    </ul>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        
        # Chrome-style CSS for tabs with always-visible scrollbar when needed
        st.markdown("""
        <style>
        /* Chrome-style tabs - Base styles */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px !important;
            justify-content: center !important;
            background-color: transparent !important;
            padding: 0px 20px !important;
            border-bottom: none !important;
            margin-bottom: 30px !important;
            display: flex !important;
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            overflow-y: hidden !important;
            scroll-behavior: smooth !important;
            -webkit-overflow-scrolling: touch !important;
            scrollbar-width: thin !important;
            scrollbar-color: #500000 #f0f0f0 !important;
            box-sizing: border-box !important;
        }
        
        /* Always show scrollbar when content overflows */
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
            height: 10px !important;
            display: block !important;
        }
        
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-track {
            background: #f0f0f0 !important;
            border-radius: 5px !important;
        }
        
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
            background: #500000 !important;
            border-radius: 5px !important;
            min-width: 50px !important;
        }
        
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb:hover {
            background: #700000 !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 45px !important;
            padding: 0px 32px !important;
            background-color: #f5f5f5 !important;
            border-radius: 8px 8px 0px 0px !important;
            font-weight: 500 !important;
            font-size: 15px !important;
            border: none !important;
            border-bottom: 3px solid transparent !important;
            color: #666 !important;
            margin-bottom: -2px !important;
            flex-shrink: 0 !important;
            white-space: nowrap !important;
            min-width: fit-content !important;
            box-sizing: border-box !important;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: white !important;
            color: #500000 !important;
            border-bottom: 3px solid #500000 !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #e8e8e8 !important;
            color: #500000 !important;
        }
        
        .stTabs [aria-selected="true"]:hover {
            background-color: white !important;
        }
        
        /* Tablet adjustments - switch to left-aligned */
        @media screen and (max-width: 1024px) {
            .stTabs [data-baseweb="tab-list"] {
                justify-content: flex-start !important;
                padding: 0px 15px !important;
            }
            
            .stTabs [data-baseweb="tab"] {
                padding: 0px 24px !important;
                font-size: 14px !important;
            }
            
            .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
                height: 12px !important;
            }
        }
        
        /* Mobile adjustments - left-aligned */
        @media screen and (max-width: 768px) {
            .stTabs [data-baseweb="tab-list"] {
                justify-content: flex-start !important;
                padding: 0px 10px !important;
            }
            
            .stTabs [data-baseweb="tab"] {
                padding: 0px 20px !important;
                font-size: 13px !important;
                height: 42px !important;
            }
        }
        
        /* Small mobile adjustments - left-aligned */
        @media screen and (max-width: 480px) {
            .stTabs [data-baseweb="tab-list"] {
                justify-content: flex-start !important;
                padding: 0px 10px !important;
            }
            
            .stTabs [data-baseweb="tab"] {
                padding: 0px 16px !important;
                font-size: 12px !important;
                height: 40px !important;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # TABS - Now using globally filtered data
        overview_tab, advanced_tab, channel_tab, notes_tab = st.tabs(["📊 Overview", "🔬 Advanced Analytics", "📢 Channel Analytics", "📝 Incremental Notes"])
        
        with overview_tab:
            # Use globally filtered data
            filtered_spend = filtered_spend_global.copy()
            
            if filtered_spend.empty:
                st.warning("⚠️ No data matches the selected filters")
            else:
                # Try to load admissions data for ROI metrics
                try:
                    admissions_df = pd.read_sql("""
                        SELECT 
                            report_date,
                            program,
                            metric_name,
                            metric_value
                        FROM admissions_metrics
                        WHERE metric_name IN ('inquiries_received', 'applications_received', 'admissions_accepted')
                    """, conn)
                    
                    # Normalize admissions program names
                    admissions_df['program_normalized'] = admissions_df['program'].apply(normalize_program_name)
                    admissions_df['report_date'] = pd.to_datetime(admissions_df['report_date'])
                    admissions_df['month_date'] = admissions_df['report_date'].dt.to_period('M').dt.to_timestamp()
                    
                    # Pivot admissions data
                    admissions_pivot = admissions_df.pivot_table(
                        index=['month_date', 'program_normalized'],
                        columns='metric_name',
                        values='metric_value',
                        aggfunc='sum'
                    ).reset_index()
                    
                    # Aggregate marketing spend by month and normalized program
                    monthly_spend_norm = filtered_spend.groupby(['month_date', 'program_normalized']).agg({
                        'spend_amount': 'sum'
                    }).reset_index()
                    
                    # Merge on normalized program names
                    roi_df = pd.merge(
                        monthly_spend_norm,
                        admissions_pivot,
                        on=['month_date', 'program_normalized'],
                        how='inner'
                    )
                    
                    has_roi_data = not roi_df.empty
                    
                    if has_roi_data:
                        # Calculate ROI metrics
                        roi_df['CPI'] = roi_df.apply(lambda x: x['spend_amount'] / x['inquiries_received'] if x['inquiries_received'] > 0 else 0, axis=1)
                        roi_df['CPA'] = roi_df.apply(lambda x: x['spend_amount'] / x['applications_received'] if x['applications_received'] > 0 else 0, axis=1)
                        roi_df['CPAd'] = roi_df.apply(lambda x: x['spend_amount'] / x['admissions_accepted'] if x['admissions_accepted'] > 0 else 0, axis=1)
                        roi_df['Conversion_Rate'] = roi_df.apply(lambda x: (x['applications_received'] / x['inquiries_received'] * 100) if x['inquiries_received'] > 0 else 0, axis=1)
                    else:
                        # Debug: Show why no match
                        if len(monthly_spend_norm) > 0 and len(admissions_pivot) > 0:
                            with st.expander("🔍 Debug: Why are metrics showing N/A?", expanded=False):
                                st.markdown("**Marketing Data Programs:**")
                                st.write(sorted(monthly_spend_norm['program_normalized'].unique().tolist()))
                                st.markdown("**Admissions Data Programs:**")
                                st.write(sorted(admissions_pivot['program_normalized'].unique().tolist()))
                                st.info("💡 If your selected program doesn't appear in both lists, that's why metrics show N/A. The program names need to match between marketing and admissions data.")
                except Exception as e:
                    has_roi_data = False
                    with st.expander("⚠️ Debug: Error loading admissions data", expanded=False):
                        st.error(f"Error: {str(e)}")
                        st.info("This usually means the admissions_metrics table is empty or doesn't exist. Run the ETL pipeline to populate it.")
                
                # KEY METRICS SECTION
                st.markdown("""
                <div class="section-header">
                    <h3>💰 Marketing Performance Overview</h3>
                </div>
                """, unsafe_allow_html=True)
                
                if has_roi_data:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Spend", f"${filtered_spend['spend_amount'].sum():,.2f}")
                    with col2:
                        avg_cpi = roi_df[roi_df['CPI'] > 0]['CPI'].mean()
                        st.metric("Avg Cost per Inquiry", f"${avg_cpi:,.2f}" if pd.notna(avg_cpi) and avg_cpi > 0 else "N/A")
                    with col3:
                        avg_cpa = roi_df[roi_df['CPA'] > 0]['CPA'].mean()
                        st.metric("Avg Cost per Application", f"${avg_cpa:,.2f}" if pd.notna(avg_cpa) and avg_cpa > 0 else "N/A")
                    with col4:
                        avg_conv = roi_df[roi_df['Conversion_Rate'] > 0]['Conversion_Rate'].mean()
                        st.metric("Avg Conversion Rate", f"{avg_conv:.1f}%" if pd.notna(avg_conv) and avg_conv > 0 else "N/A")
                else:
                    # Fallback to basic metrics if no ROI data
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Spend", f"${filtered_spend['spend_amount'].sum():,.2f}")
                    with col2:
                        st.metric("Programs", filtered_spend['program'].nunique())
                    with col3:
                        st.metric("Channels", filtered_spend['channel'].nunique())
                    with col4:
                        avg_spend = filtered_spend.groupby('channel')['spend_amount'].sum().mean()
                        st.metric("Avg per Channel", f"${avg_spend:,.2f}")
                
                st.divider()
                
                # SPEND BY PROGRAM SECTION
                st.markdown("""
                <div class="section-header">
                    <h3>📊 Spend by Program</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Use container with border
                filter_container_prog = st.container(border=True)
                
                with filter_container_prog:
                    # Row 1: Action buttons
                    btn_col1, btn_col2, btn_col3 = st.columns(3)
                    with btn_col1:
                        available_programs = sorted(filtered_spend['program'].unique().tolist())
                        if st.button("✓ All", key="overview_prog_all", use_container_width=True):
                            for program in available_programs:
                                st.session_state[f"overview_prog_check_{program}"] = True
                            st.rerun()
                    with btn_col2:
                        if st.button("✗ Clear", key="overview_prog_none", use_container_width=True):
                            for program in available_programs:
                                st.session_state[f"overview_prog_check_{program}"] = False
                            st.rerun()
                    with btn_col3:
                        if 'overview_prog_log_scale' not in st.session_state:
                            st.session_state.overview_prog_log_scale = False
                        if st.button("📊 " + ("Log" if not st.session_state.overview_prog_log_scale else "Linear"), 
                                   key="overview_prog_log_toggle", use_container_width=True):
                            st.session_state.overview_prog_log_scale = not st.session_state.overview_prog_log_scale
                            st.rerun()
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Program toggle buttons - FORCE multi-row layout
                    num_programs = len(available_programs)
                    programs_per_row = 4  # Force 4 buttons per row
                    
                    overview_prog_selected = []
                    
                    # Create rows explicitly
                    for row_start in range(0, num_programs, programs_per_row):
                        row_end = min(row_start + programs_per_row, num_programs)
                        row_programs = available_programs[row_start:row_end]
                        
                        # Create columns for this row
                        row_cols = st.columns(len(row_programs))
                        
                        for idx, program in enumerate(row_programs):
                            with row_cols[idx]:
                                if f"overview_prog_check_{program}" not in st.session_state:
                                    st.session_state[f"overview_prog_check_{program}"] = True
                                
                                is_selected = st.session_state[f"overview_prog_check_{program}"]
                                button_type = "primary" if is_selected else "secondary"
                                button_label = f"✓ {program}" if is_selected else program
                                
                                if st.button(button_label, key=f"overview_prog_btn_{program}", 
                                           use_container_width=True, type=button_type):
                                    st.session_state[f"overview_prog_check_{program}"] = not is_selected
                                    st.rerun()
                                
                                if st.session_state[f"overview_prog_check_{program}"]:
                                    overview_prog_selected.append(program)
                
                # Filter and display chart
                if overview_prog_selected:
                    chart1_data = filtered_spend[filtered_spend['program'].isin(overview_prog_selected)]
                    program_spend = chart1_data.groupby('program')['spend_amount'].sum().sort_values(ascending=False)
                    
                    fig = px.bar(x=program_spend.index, y=program_spend.values,
                               labels={'x': 'Program', 'y': 'Total Spend ($)'},
                               color=program_spend.values, color_continuous_scale='RdYlGn_r',
                               log_y=st.session_state.overview_prog_log_scale)
                    fig.update_layout(height=400, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True, key="overview_prog_chart")
                else:
                    st.info("No programs selected. Click '✓ All' to select all programs.")
                
                st.divider()
                
                # SPEND BY CHANNEL SECTION
                st.markdown("""
                <div class="section-header">
                    <h3>📢 Spend by Channel</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Use container with border
                filter_container_chan = st.container(border=True)
                
                with filter_container_chan:
                    # Row 1: Action buttons
                    btn_col1, btn_col2, btn_col3 = st.columns(3)
                    with btn_col1:
                        available_channels = sorted(filtered_spend['channel'].unique().tolist())
                        if st.button("✓ All", key="overview_chan_all", use_container_width=True):
                            for channel in available_channels:
                                st.session_state[f"overview_chan_check_{channel}"] = True
                            st.rerun()
                    with btn_col2:
                        if st.button("✗ Clear", key="overview_chan_none", use_container_width=True):
                            for channel in available_channels:
                                st.session_state[f"overview_chan_check_{channel}"] = False
                            st.rerun()
                    with btn_col3:
                        if 'overview_chan_chart_type' not in st.session_state:
                            st.session_state.overview_chan_chart_type = "Pie"
                        if st.button("📊 " + st.session_state.overview_chan_chart_type, 
                                   key="overview_chan_type_toggle", use_container_width=True):
                            st.session_state.overview_chan_chart_type = "Bar" if st.session_state.overview_chan_chart_type == "Pie" else "Pie"
                            st.rerun()
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Channel toggle buttons - FORCE multi-row layout
                    num_channels = len(available_channels)
                    channels_per_row = 4  # Force 4 buttons per row
                    
                    overview_chan_selected = []
                    
                    # Create rows explicitly
                    for row_start in range(0, num_channels, channels_per_row):
                        row_end = min(row_start + channels_per_row, num_channels)
                        row_channels = available_channels[row_start:row_end]
                        
                        # Create columns for this row
                        row_cols = st.columns(len(row_channels))
                        
                        for idx, channel in enumerate(row_channels):
                            with row_cols[idx]:
                                if f"overview_chan_check_{channel}" not in st.session_state:
                                    st.session_state[f"overview_chan_check_{channel}"] = True
                                
                                is_selected = st.session_state[f"overview_chan_check_{channel}"]
                                button_type = "primary" if is_selected else "secondary"
                                button_label = f"✓ {channel}" if is_selected else channel
                                
                                if st.button(button_label, key=f"overview_chan_btn_{channel}", 
                                           use_container_width=True, type=button_type):
                                    st.session_state[f"overview_chan_check_{channel}"] = not is_selected
                                    st.rerun()
                                
                                if st.session_state[f"overview_chan_check_{channel}"]:
                                    overview_chan_selected.append(channel)
                
                # Filter and display chart
                if overview_chan_selected:
                    chart2_data = filtered_spend[filtered_spend['channel'].isin(overview_chan_selected)]
                    channel_spend = chart2_data.groupby('channel')['spend_amount'].sum().sort_values(ascending=False)
                    
                    if st.session_state.overview_chan_chart_type == "Pie":
                        fig = px.pie(values=channel_spend.values, names=channel_spend.index,
                                   title='Spend Distribution by Channel')
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                    else:
                        fig = px.bar(x=channel_spend.index, y=channel_spend.values,
                                   labels={'x': 'Channel', 'y': 'Total Spend ($)'},
                                   color=channel_spend.values, color_continuous_scale='RdYlGn_r')
                        fig.update_layout(showlegend=False)
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True, key="overview_chan_chart")
                else:
                    st.info("No channels selected. Click '✓ All' to select all channels.")
        
        with advanced_tab:
            # Use globally filtered data
            filtered_spend_adv = filtered_spend_global.copy()
            
            if filtered_spend_adv.empty:
                st.warning("⚠️ No data matches the selected filters")
            else:
                try:
                    # Load admissions data
                    admissions_df = pd.read_sql("""
                        SELECT 
                            report_date,
                            program,
                            metric_name,
                            metric_value
                        FROM admissions_metrics
                        WHERE metric_name IN ('inquiries_received', 'applications_received', 'admissions_accepted')
                    """, conn)
                    
                    # Normalize admissions program names
                    admissions_df['program_normalized'] = admissions_df['program'].apply(normalize_program_name)
                    admissions_df['report_date'] = pd.to_datetime(admissions_df['report_date'])
                    admissions_df['month_date'] = admissions_df['report_date'].dt.to_period('M').dt.to_timestamp()
                    
                    # Pivot admissions data
                    admissions_pivot = admissions_df.pivot_table(
                        index=['month_date', 'program_normalized'],
                        columns='metric_name',
                        values='metric_value',
                        aggfunc='sum'
                    ).reset_index()
                    
                    # Aggregate marketing spend by month and normalized program
                    monthly_spend_norm = filtered_spend_adv.groupby(['month_date', 'program_normalized']).agg({
                        'spend_amount': 'sum'
                    }).reset_index()
                    
                    # Merge on normalized program names
                    roi_df = pd.merge(
                        monthly_spend_norm,
                        admissions_pivot,
                        on=['month_date', 'program_normalized'],
                        how='inner'
                    )
                    
                    if not roi_df.empty and len(roi_df) > 0:
                        # Calculate ROI metrics
                        roi_df['CPI'] = roi_df.apply(lambda x: x['spend_amount'] / x['inquiries_received'] if x['inquiries_received'] > 0 else 0, axis=1)
                        roi_df['CPA'] = roi_df.apply(lambda x: x['spend_amount'] / x['applications_received'] if x['applications_received'] > 0 else 0, axis=1)
                        roi_df['CPAd'] = roi_df.apply(lambda x: x['spend_amount'] / x['admissions_accepted'] if x['admissions_accepted'] > 0 else 0, axis=1)
                        roi_df['Conversion_Rate'] = roi_df.apply(lambda x: (x['applications_received'] / x['inquiries_received'] * 100) if x['inquiries_received'] > 0 else 0, axis=1)
                        
                        # ROI SUMMARY SECTION
                        st.markdown("""
                        <div class="section-header">
                            <h3>💰 ROI Summary</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            avg_cpi = roi_df[roi_df['CPI'] > 0]['CPI'].mean()
                            st.metric("Avg Cost per Inquiry", f"${avg_cpi:,.2f}" if avg_cpi > 0 else "N/A")
                        with col2:
                            avg_cpa = roi_df[roi_df['CPA'] > 0]['CPA'].mean()
                            st.metric("Avg Cost per Application", f"${avg_cpa:,.2f}" if avg_cpa > 0 else "N/A")
                        with col3:
                            avg_cpad = roi_df[roi_df['CPAd'] > 0]['CPAd'].mean()
                            st.metric("Avg Cost per Admission", f"${avg_cpad:,.2f}" if avg_cpad > 0 else "N/A")
                        with col4:
                            avg_conv = roi_df[roi_df['Conversion_Rate'] > 0]['Conversion_Rate'].mean()
                            st.metric("Avg Conversion Rate", f"{avg_conv:.1f}%" if avg_conv > 0 else "N/A")
                        
                        st.divider()
                        
                        # PROGRAM SPEND BY CHANNEL SECTION
                        st.markdown("""
                        <div class="section-header">
                            <h3>📊 Program Spend by Channel</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("*See which channels each program invests in*")
                        
                        # Aggregate spend by program and channel
                        program_channel_spend = filtered_spend_adv.groupby(['program_normalized', 'channel'])['spend_amount'].sum().reset_index()
                        
                        if not program_channel_spend.empty:
                            # Create grouped bar chart
                            fig_grouped = px.bar(
                                program_channel_spend,
                                x='program_normalized',
                                y='spend_amount',
                                color='channel',
                                title='Marketing Spend by Program and Channel',
                                labels={'program_normalized': 'Program', 'spend_amount': 'Spend ($)', 'channel': 'Channel'},
                                barmode='group',  # Use 'stack' for stacked bars
                                color_discrete_sequence=px.colors.qualitative.Set3
                            )
                            fig_grouped.update_layout(
                                height=450,
                                xaxis_title="Program",
                                yaxis_title="Spend ($)",
                                legend_title="Channel",
                                hovermode='x unified'
                            )
                            st.plotly_chart(fig_grouped, use_container_width=True, key="program_channel_grouped")
                            
                            # Add toggle for stacked view
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                if 'barmode_stacked' not in st.session_state:
                                    st.session_state.barmode_stacked = False
                                if st.button("📊 Toggle Stack/Group", key="toggle_barmode"):
                                    st.session_state.barmode_stacked = not st.session_state.barmode_stacked
                                    st.rerun()
                            with col2:
                                st.caption("Click to switch between grouped (side-by-side) and stacked (cumulative) view")
                            
                            # Show stacked version if toggled
                            if st.session_state.barmode_stacked:
                                fig_stacked = px.bar(
                                    program_channel_spend,
                                    x='program_normalized',
                                    y='spend_amount',
                                    color='channel',
                                    title='Marketing Spend by Program and Channel (Stacked)',
                                    labels={'program_normalized': 'Program', 'spend_amount': 'Spend ($)', 'channel': 'Channel'},
                                    barmode='stack',
                                    color_discrete_sequence=px.colors.qualitative.Set3
                                )
                                fig_stacked.update_layout(
                                    height=450,
                                    xaxis_title="Program",
                                    yaxis_title="Spend ($)",
                                    legend_title="Channel",
                                    hovermode='x unified'
                                )
                                st.plotly_chart(fig_stacked, use_container_width=True, key="program_channel_stacked")
                        
                        st.divider()
                        
                        # CHANNEL PERFORMANCE BY PROGRAM SECTION
                        st.markdown("""
                        <div class="section-header">
                            <h3>🔗 Channel Performance by Program</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        st.markdown("*Discover which channels drive the most admissions for each program*")
                        
                        # Aggregate spend and admissions by program and channel
                        channel_program_data = filtered_spend_adv.groupby(['program_normalized', 'channel']).agg({
                            'spend_amount': 'sum'
                        }).reset_index()
                        
                        # Merge with admissions data
                        admissions_by_program = admissions_df.groupby('program_normalized').agg({
                            'metric_value': 'sum'
                        }).reset_index()
                        admissions_by_program.columns = ['program_normalized', 'total_admissions']
                        
                        # For correlation, we need channel-level admissions
                        # Since we don't have channel-level admissions, we'll calculate efficiency metrics
                        channel_program_merged = pd.merge(
                            channel_program_data,
                            admissions_by_program,
                            on='program_normalized',
                            how='left'
                        )
                        
                        # Calculate spend share per channel within each program
                        program_totals = channel_program_merged.groupby('program_normalized')['spend_amount'].sum().reset_index()
                        program_totals.columns = ['program_normalized', 'program_total_spend']
                        
                        channel_program_merged = pd.merge(
                            channel_program_merged,
                            program_totals,
                            on='program_normalized'
                        )
                        
                        channel_program_merged['spend_share'] = (
                            channel_program_merged['spend_amount'] / channel_program_merged['program_total_spend'] * 100
                        )
                        
                        # Create pivot table for heatmap
                        heatmap_data = channel_program_merged.pivot_table(
                            index='channel',
                            columns='program_normalized',
                            values='spend_share',
                            fill_value=0
                        )
                        
                        if not heatmap_data.empty:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Heatmap showing spend share
                                fig_heatmap = px.imshow(
                                    heatmap_data,
                                    labels=dict(x="Program", y="Channel", color="Spend Share (%)"),
                                    title="Channel Spend Share by Program",
                                    color_continuous_scale='RdYlGn',
                                    aspect='auto'
                                )
                                fig_heatmap.update_layout(height=400)
                                st.plotly_chart(fig_heatmap, use_container_width=True, key="channel_program_heatmap")
                            
                            with col2:
                                # Show top channel per program
                                top_channels = channel_program_merged.loc[
                                    channel_program_merged.groupby('program_normalized')['spend_amount'].idxmax()
                                ][['program_normalized', 'channel', 'spend_amount', 'spend_share']]
                                
                                st.markdown("**Top Channel per Program:**")
                                for _, row in top_channels.iterrows():
                                    st.markdown(f"**{row['program_normalized']}**: {row['channel']} ({row['spend_share']:.1f}% of program spend)")
                        
                        st.divider()
                        
                        # SPEND VS OUTCOMES TREND SECTION
                        st.markdown("""
                        <div class="section-header">
                            <h3>📈 Spend vs Outcomes Trend</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        monthly_trends = roi_df.groupby('month_date').agg({
                            'spend_amount': 'sum',
                            'inquiries_received': 'sum',
                            'applications_received': 'sum',
                            'admissions_accepted': 'sum'
                        }).reset_index()
                        
                        if len(monthly_trends) > 1:
                            # Create subplots with shared x-axis
                            from plotly.subplots import make_subplots
                            
                            fig = make_subplots(
                                rows=2, cols=1,
                                subplot_titles=('Marketing Spend Over Time', 'Outcomes Over Time'),
                                vertical_spacing=0.15,
                                row_heights=[0.4, 0.6]
                            )
                            
                            # Top chart: Spend
                            fig.add_trace(
                                go.Bar(x=monthly_trends['month_date'], y=monthly_trends['spend_amount'],
                                      name='Spend ($)', marker_color='lightcoral'),
                                row=1, col=1
                            )
                            
                            # Bottom chart: Outcomes
                            fig.add_trace(
                                go.Scatter(x=monthly_trends['month_date'], y=monthly_trends['inquiries_received'],
                                          name='Inquiries', mode='lines+markers',
                                          line=dict(color='blue', width=3), marker=dict(size=10)),
                                row=2, col=1
                            )
                            fig.add_trace(
                                go.Scatter(x=monthly_trends['month_date'], y=monthly_trends['applications_received'],
                                          name='Applications', mode='lines+markers',
                                          line=dict(color='green', width=3), marker=dict(size=10)),
                                row=2, col=1
                            )
                            fig.add_trace(
                                go.Scatter(x=monthly_trends['month_date'], y=monthly_trends['admissions_accepted'],
                                          name='Admissions', mode='lines+markers',
                                          line=dict(color='purple', width=3), marker=dict(size=10)),
                                row=2, col=1
                            )
                            
                            fig.update_xaxes(title_text="Month", row=2, col=1)
                            fig.update_yaxes(title_text="Spend ($)", row=1, col=1)
                            fig.update_yaxes(title_text="Count", row=2, col=1)
                            
                            fig.update_layout(
                                height=650,
                                hovermode='x unified',
                                showlegend=True,
                                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                                margin=dict(b=100)  # Add bottom margin for legend
                            )
                            
                            st.plotly_chart(fig, use_container_width=True, key="adv_trend_chart")
                        
                        st.divider()
                        
                        # DETAILED ROI METRICS SECTION
                        st.markdown("""
                        <div class="section-header">
                            <h3>📋 Detailed ROI Metrics by Program</h3>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Calculate program_roi for the table
                        program_roi = roi_df.groupby('program_normalized').agg({
                            'spend_amount': 'sum',
                            'inquiries_received': 'sum',
                            'applications_received': 'sum',
                            'admissions_accepted': 'sum',
                            'CPI': 'mean',
                            'CPA': 'mean',
                            'CPAd': 'mean'
                        }).reset_index()
                        
                        display_table = program_roi.round(2).sort_values('CPAd')
                        st.dataframe(
                            display_table.style.background_gradient(
                                subset=['CPI', 'CPA', 'CPAd'], cmap='RdYlGn_r'
                            ).format({
                                'spend_amount': '${:,.2f}',
                                'inquiries_received': '{:.0f}',
                                'applications_received': '{:.0f}',
                                'admissions_accepted': '{:.0f}',
                                'CPI': '${:,.2f}',
                                'CPA': '${:,.2f}',
                                'CPAd': '${:,.2f}'
                            }),
                            use_container_width=True
                        )
                    else:
                        st.warning("⚠️ No matching data between marketing spend and admissions for selected filters")
                        st.info("Try selecting 'All' for broader results, or check that both marketing and admissions data exist for the selected programs.")
                
                except Exception as e:
                    st.error(f"Error loading ROI analytics: {str(e)}")
                    st.info("Ensure admissions data is loaded by running the ETL pipeline.")
        
        with channel_tab:
            # Use globally filtered data
            filtered_spend_chan = filtered_spend_global.copy()
            
            if filtered_spend_chan.empty:
                st.warning("⚠️ No data matches the selected filters")
            else:
                # Get available channels for per-chart filters
                available_channels = sorted(filtered_spend_chan['channel'].unique().tolist())
                
                # KEY METRICS SECTION
                st.markdown("""
                <div class="section-header">
                    <h3>💰 Key Metrics</h3>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Spend", f"${filtered_spend_chan['spend_amount'].sum():,.2f}")
                with col2:
                    st.metric("Channels", filtered_spend_chan['channel'].nunique())
                with col3:
                    st.metric("Programs", filtered_spend_chan['program'].nunique())
                with col4:
                    avg_spend = filtered_spend_chan.groupby('channel')['spend_amount'].sum().mean()
                    st.metric("Avg per Channel", f"${avg_spend:,.2f}")
                
                st.divider()
                
                # CHART 1 - Spend Distribution
                st.markdown("""
                <div class="section-header">
                    <h3>📊 Spend Distribution by Channel</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Use container with border
                filter_container = st.container(border=True)
                
                with filter_container:
                    # Row 1: Action buttons
                    btn_col1, btn_col2, btn_col3 = st.columns(3)
                    with btn_col1:
                        if st.button("✓ All", key="chart1_all", use_container_width=True):
                            for channel in available_channels:
                                st.session_state[f"chart1_check_{channel}"] = True
                            st.rerun()
                    with btn_col2:
                        if st.button("✗ Clear", key="chart1_none", use_container_width=True):
                            for channel in available_channels:
                                st.session_state[f"chart1_check_{channel}"] = False
                            st.rerun()
                    with btn_col3:
                        if 'chart1_log_scale' not in st.session_state:
                            st.session_state.chart1_log_scale = False
                        if st.button("📊 " + ("Log" if not st.session_state.chart1_log_scale else "Linear"), 
                                   key="chart1_log_toggle", use_container_width=True):
                            st.session_state.chart1_log_scale = not st.session_state.chart1_log_scale
                            st.rerun()
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Channel toggle buttons - FORCE multi-row layout
                    num_channels = len(available_channels)
                    channels_per_row = 4  # Force 4 buttons per row
                    
                    chart1_selected = []
                    
                    # Create rows explicitly
                    for row_start in range(0, num_channels, channels_per_row):
                        row_end = min(row_start + channels_per_row, num_channels)
                        row_channels = available_channels[row_start:row_end]
                        
                        # Create columns for this row
                        row_cols = st.columns(len(row_channels))
                        
                        for idx, channel in enumerate(row_channels):
                            with row_cols[idx]:
                                if f"chart1_check_{channel}" not in st.session_state:
                                    st.session_state[f"chart1_check_{channel}"] = True
                                
                                is_selected = st.session_state[f"chart1_check_{channel}"]
                                button_type = "primary" if is_selected else "secondary"
                                button_label = f"✓ {channel}" if is_selected else channel
                                
                                if st.button(button_label, key=f"chart1_btn_{channel}", 
                                           use_container_width=True, type=button_type):
                                    st.session_state[f"chart1_check_{channel}"] = not is_selected
                                    st.rerun()
                                
                                if st.session_state[f"chart1_check_{channel}"]:
                                    chart1_selected.append(channel)
                
                # Filter and display chart
                if chart1_selected:
                    chart1_data = filtered_spend_chan[filtered_spend_chan['channel'].isin(chart1_selected)]
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        channel_totals = chart1_data.groupby('channel')['spend_amount'].sum().sort_values(ascending=False)
                        fig = px.bar(x=channel_totals.index, y=channel_totals.values,
                                   labels={'x': 'Channel', 'y': 'Total Spend ($)'},
                                   title='Total Spend by Channel',
                                   color=channel_totals.values,
                                   color_continuous_scale='RdYlGn_r',
                                   log_y=st.session_state.chart1_log_scale)
                        fig.update_layout(height=400, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True, key="channel_bar_chart")
                    
                    with col2:
                        fig = px.pie(values=channel_totals.values, names=channel_totals.index,
                                   title='Channel Spend Share')
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True, key="channel_pie_chart")
                else:
                    st.info("No channels selected. Click '✓ Select All' to select all channels.")
                
                st.divider()
                
                # CHART 2 - Trend Chart
                st.markdown("""
                <div class="section-header">
                    <h3>📈 Channel Spend Trends</h3>
                </div>
                """, unsafe_allow_html=True)
                
                # Use container with border
                filter_container2 = st.container(border=True)
                
                with filter_container2:
                    # Row 1: Action buttons
                    btn_col1, btn_col2, btn_col3 = st.columns(3)
                    with btn_col1:
                        if st.button("✓ All", key="chart2_all", use_container_width=True):
                            for channel in available_channels:
                                st.session_state[f"chart2_check_{channel}"] = True
                            st.rerun()
                    with btn_col2:
                        if st.button("✗ Clear", key="chart2_none", use_container_width=True):
                            for channel in available_channels:
                                st.session_state[f"chart2_check_{channel}"] = False
                            st.rerun()
                    with btn_col3:
                        if 'chart2_log_scale' not in st.session_state:
                            st.session_state.chart2_log_scale = False
                        if st.button("📊 " + ("Log" if not st.session_state.chart2_log_scale else "Linear"), 
                                   key="chart2_log_toggle", use_container_width=True):
                            st.session_state.chart2_log_scale = not st.session_state.chart2_log_scale
                            st.rerun()
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Channel toggle buttons - FORCE multi-row layout (same as Chart 1)
                    num_channels = len(available_channels)
                    channels_per_row = 4  # Force 4 buttons per row
                    
                    chart2_selected = []
                    
                    # Create rows explicitly
                    for row_start in range(0, num_channels, channels_per_row):
                        row_end = min(row_start + channels_per_row, num_channels)
                        row_channels = available_channels[row_start:row_end]
                        
                        # Create columns for this row
                        row_cols = st.columns(len(row_channels))
                        
                        for idx, channel in enumerate(row_channels):
                            with row_cols[idx]:
                                if f"chart2_check_{channel}" not in st.session_state:
                                    st.session_state[f"chart2_check_{channel}"] = True
                                
                                is_selected = st.session_state[f"chart2_check_{channel}"]
                                button_type = "primary" if is_selected else "secondary"
                                button_label = f"✓ {channel}" if is_selected else channel
                                
                                if st.button(button_label, key=f"chart2_btn_{channel}", 
                                           use_container_width=True, type=button_type):
                                    st.session_state[f"chart2_check_{channel}"] = not is_selected
                                    st.rerun()
                                
                                if st.session_state[f"chart2_check_{channel}"]:
                                    chart2_selected.append(channel)
                
                # Filter and display chart
                if chart2_selected:
                    chart2_data = filtered_spend_chan[filtered_spend_chan['channel'].isin(chart2_selected)]
                    monthly_channel = chart2_data.groupby(['month_date', 'channel'])['spend_amount'].sum().reset_index()
                    
                    if not monthly_channel.empty:
                        fig = px.line(monthly_channel, x='month_date', y='spend_amount', color='channel',
                                    title='Monthly Spend by Channel',
                                    labels={'month_date': 'Month', 'spend_amount': 'Spend ($)', 'channel': 'Channel'},
                                    markers=True,
                                    log_y=st.session_state.chart2_log_scale)
                        fig.update_layout(height=450, hovermode='x unified')
                        st.plotly_chart(fig, use_container_width=True, key="channel_trend_chart")
                else:
                    st.info("No channels selected. Click '✓ Select All' to select all channels.")
                
                st.divider()
                
                # CHART 3: Summary Table (NO FILTERS)
                st.markdown("""
                <div class="section-header">
                    <h3>📋 Channel Performance Summary</h3>
                </div>
                """, unsafe_allow_html=True)
                
                channel_spend_summary = filtered_spend_chan.groupby('channel').agg({
                    'spend_amount': 'sum',
                    'program': 'nunique',
                    'month_date': 'nunique'
                }).reset_index()
                channel_spend_summary.columns = ['Channel', 'Total Spend', 'Programs', 'Months']
                
                st.dataframe(
                    channel_spend_summary.sort_values('Total Spend', ascending=False).style.background_gradient(
                        subset=['Total Spend'], cmap='RdYlGn_r'
                    ).format({
                        'Total Spend': '${:,.2f}'
                    }),
                    use_container_width=True
                )
        
        with notes_tab:
            # Use globally filtered data
            notes_filtered = filtered_spend_global.copy()
            notes_filtered['month_name'] = notes_filtered['month_date'].dt.strftime('%B %Y')
            
            # Extract notes
            notes_df = notes_filtered[notes_filtered['extra_notes'].notna()].copy()
            unique_notes = []
            
            if not notes_df.empty:
                for _, row in notes_df.iterrows():
                    try:
                        import json
                        notes_list = json.loads(row['extra_notes'])
                        for note in notes_list:
                            note_key = f"{row['program']}_{row['month_date'].strftime('%Y-%m')}_{note[:50]}"
                            if not any(existing['key'] == note_key for existing in unique_notes):
                                unique_notes.append({
                                    'key': note_key,
                                    'program': row['program'],
                                    'month': row['month_date'].strftime('%B %Y'),
                                    'year': row['month_date'].year,
                                    'month_num': row['month_date'].month,
                                    'fiscal_year': row['fiscal_year'],
                                    'note': note
                                })
                    except:
                        pass
            
            if unique_notes:
                notes_display_df = pd.DataFrame(unique_notes)
                notes_display_df = notes_display_df.sort_values(['year', 'month_num'], ascending=[False, False])
                
                # NOTES SECTION HEADER
                st.markdown("""
                <div class="section-header">
                    <h3>📋 Incremental Notes</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"**Found {len(notes_display_df)} notes**")
                
                # Scrollable container
                notes_container = st.container(height=450)
                with notes_container:
                    for i, (_, note_row) in enumerate(notes_display_df.iterrows()):
                        with st.expander(f"📅 {note_row['program']} - {note_row['month']} ({note_row['fiscal_year']})", expanded=(i < 3)):
                            st.markdown(f"**Note:** {note_row['note']}")
            else:
                st.info("No notes available for selected filters.")
    
    # Footer for Marketing Analysis page
    st.divider()
    footer_col1, footer_col2, footer_col3 = st.columns([1, 1, 1])
    with footer_col1:
        st.markdown(f"""
        <div class="footer-left footer-content" style="text-align: left;">
            <p style="color: #6b7280; font-size: 14px; margin: 0;">📊 Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        """, unsafe_allow_html=True)
    with footer_col2:
        st.components.v1.html("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100%; min-height: 60px;">
            <button onclick="window.top.print()" 
                    style="background-color: white;
                           color: #500000;
                           border: 2px solid #e0e0e0;
                           border-radius: 8px;
                           padding: 0.6rem 1.2rem;
                           font-size: 0.95rem;
                           font-weight: 600;
                           cursor: pointer;
                           transition: all 0.3s ease;
                           width: 100%;
                           min-height: 45px;
                           font-family: 'Source Sans Pro', sans-serif;"
                    onmouseover="this.style.backgroundColor='#e9ecef'; this.style.borderColor='#500000';"
                    onmouseout="this.style.backgroundColor='white'; this.style.borderColor='#e0e0e0';">
                🖨️ Print Page
            </button>
        </div>
        """, height=70)
    with footer_col3:
        st.markdown("""
        <div class="footer-right footer-content" style="text-align: right;">
            <p style="color: #6b7280; font-size: 14px; margin: 0;">💡 Use buttons above to switch views</p>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_page == 'Database':
    # DATA EXPLORER - Styled like Marketing Analysis
    
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
    
    # FULL-WIDTH KEYWORD SEARCH - Centered
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h4 style="color: #500000; margin-bottom: 10px;">🔍 Find Your Data</h4>
    </div>
    """, unsafe_allow_html=True)
    
    keyword_search = st.text_input(
        "Search tables, questions, or data types",
        placeholder="Type keywords like 'applications', 'marketing', 'programs', 'inquiries'...",
        key="table_keyword_search",
        label_visibility="collapsed"
    )
    
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
                st.success(f"✓ Found {len(filtered_tables)} table(s) matching '{keyword_search}'")
            else:
                st.warning(f"No tables match '{keyword_search}'. Showing all tables.")
        
        if not available_tables:
            st.warning("No tables found in the database.")
            st.info("Please ensure the ETL pipeline has been run to populate the database.")
        else:
            # Chrome-style CSS for tabs with always-visible scrollbar when needed
            st.markdown("""
            <style>
            /* Chrome-style tabs for Data Explorer */
            .stTabs [data-baseweb="tab-list"] {
                gap: 2px !important;
                justify-content: center !important;
                background-color: transparent !important;
                padding: 0px 20px !important;
                border-bottom: none !important;
                margin-bottom: 30px !important;
                margin-top: 20px !important;
                display: flex !important;
                flex-wrap: nowrap !important;
                overflow-x: auto !important;
                overflow-y: hidden !important;
                scroll-behavior: smooth !important;
                -webkit-overflow-scrolling: touch !important;
                scrollbar-width: thin !important;
                scrollbar-color: #500000 #f0f0f0 !important;
                box-sizing: border-box !important;
            }
            
            /* Always show scrollbar when content overflows */
            .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
                height: 10px !important;
                display: block !important;
            }
            
            .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-track {
                background: #f0f0f0 !important;
                border-radius: 5px !important;
            }
            
            .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb {
                background: #500000 !important;
                border-radius: 5px !important;
                min-width: 50px !important;
            }
            
            .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar-thumb:hover {
                background: #700000 !important;
            }
            
            .stTabs [data-baseweb="tab"] {
                height: 45px !important;
                padding: 0px 32px !important;
                background-color: #f5f5f5 !important;
                border-radius: 8px 8px 0px 0px !important;
                font-weight: 500 !important;
                font-size: 15px !important;
                border: none !important;
                border-bottom: 3px solid transparent !important;
                color: #666 !important;
                margin-bottom: -2px !important;
                flex-shrink: 0 !important;
                white-space: nowrap !important;
                min-width: fit-content !important;
                box-sizing: border-box !important;
            }
            
            .stTabs [aria-selected="true"] {
                background-color: white !important;
                color: #500000 !important;
                border-bottom: 3px solid #500000 !important;
            }
            
            .stTabs [data-baseweb="tab"]:hover {
                background-color: #e8e8e8 !important;
                color: #500000 !important;
            }
            
            .stTabs [aria-selected="true"]:hover {
                background-color: white !important;
            }
            
            /* Tablet adjustments - switch to left-aligned */
            @media screen and (max-width: 1024px) {
                .stTabs [data-baseweb="tab-list"] {
                    justify-content: flex-start !important;
                    padding: 0px 15px !important;
                }
                
                .stTabs [data-baseweb="tab"] {
                    padding: 0px 24px !important;
                    font-size: 14px !important;
                }
                
                .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
                    height: 12px !important;
                }
            }
            
            /* Mobile adjustments - left-aligned */
            @media screen and (max-width: 768px) {
                .stTabs [data-baseweb="tab-list"] {
                    justify-content: flex-start !important;
                    padding: 0px 10px !important;
                }
                
                .stTabs [data-baseweb="tab"] {
                    padding: 0px 20px !important;
                    font-size: 13px !important;
                    height: 42px !important;
                }
            }
            
            /* Small mobile adjustments - left-aligned */
            @media screen and (max-width: 480px) {
                .stTabs [data-baseweb="tab-list"] {
                    justify-content: flex-start !important;
                    padding: 0px 10px !important;
                }
                
                .stTabs [data-baseweb="tab"] {
                    padding: 0px 16px !important;
                    font-size: 12px !important;
                    height: 40px !important;
                }
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Create tabs for each table with icons
            table_icons = {
                'admissions_metrics': '📊',
                'programs': '🎓',
                'marketing_metrics': '📈',
                'marketing_campaigns': '📢',
                'marketing_spend': '💰',
                'inquiry_sources': '🔍',
                'sqlite_sequence': '⚙️'
            }
            
            tab_labels = []
            for table in available_tables:
                icon = table_icons.get(table, '📋')
                # Format table name nicely
                display_name = table.replace('_', ' ').title()
                tab_labels.append(f"{icon} {display_name}")
            
            tabs = st.tabs(tab_labels)
            
            for i, table in enumerate(available_tables):
                with tabs[i]:
                    # Process the table with new styling
                    process_table_display(conn, table)
    
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        st.info("Please check if the database file exists and is accessible.")

    # Footer with Print Button
    # Add print-specific CSS - simplified approach with proper margins
    st.markdown("""
    <style>
    @media print {
    /* Hide Streamlit UI */
    header[data-testid="stHeader"],
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"],
    .stDeployButton {
        display: none !important;
    }
    
    /* Hide navigation */
    #nav-buttons-container {
        display: none !important;
    }
    
    /* Hide footer */
    hr:last-of-type,
    hr:last-of-type ~ * {
        display: none !important;
    }
    
    /* Clean layout with proper margins */
    body {
        margin: 0;
        padding: 0;
    }
    
    .main .block-container {
        padding: 1.5cm 1cm 2cm 1cm !important;
        max-width: 100% !important;
        border: none !important;
    }
    
    /* Scale down and left-align charts to fit page width - default for all charts */
    .js-plotly-plot,
    .plotly {
        width: 100% !important;
        max-width: 100% !important;
        height: auto !important;
        margin: 15px 0 15px -24px !important;
        padding: 0 !important;
        display: block !important;
        page-break-inside: avoid;
        overflow: visible !important;
        transform: scale(0.84) !important;
        transform-origin: left top !important;
        position: relative !important;
        left: -24px !important;
    }
    
    /* Specific styling for funnel charts - more left and larger scale */
    .js-plotly-plot:has(g.funnellayer),
    .plotly:has(g.funnellayer) {
        transform: scale(0.85) !important;
        margin-left: -30px !important;
        left: -30px !important;
    }
    
    div[data-testid="stPlotlyChart"] {
        width: 100% !important;
        max-width: 100% !important;
        display: block !important;
        margin: 15px 0 !important;
        padding: 0 !important;
        overflow: visible !important;
        text-align: left !important;
        position: relative !important;
    }
    
    /* Force SVG charts to scale down and fit */
    .js-plotly-plot svg,
    .plotly svg {
        max-width: 100% !important;
        width: 100% !important;
        height: auto !important;
    }
    
    /* Force plotly containers to respect width and remove padding */
    .plotly-graph-div {
        width: 100% !important;
        max-width: 100% !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Remove plotly's internal margins */
    .main-svg {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Ensure metric boxes fit properly */
    .metrics-container {
        max-width: 100% !important;
        margin: 15px 0 !important;
        gap: 0.8rem !important;
    }
    
    .metric-box {
        box-shadow: none !important;
        border: 1px solid #ccc !important;
        padding: 1rem !important;
    }
    
    /* Section headers - keep readable */
    div[style*="background: #e9ecef"],
    div[style*="background:#e9ecef"] {
        background: #f5f5f5 !important;
        border: 1px solid #ddd !important;
        page-break-after: avoid;
        padding: 12px !important;
    }
    
    /* Keep text readable */
    body, p, div, span {
        font-size: 11pt !important;
        line-height: 1.4 !important;
    }
    
    h1 { font-size: 18pt !important; }
    h2 { font-size: 16pt !important; }
    h3 { font-size: 14pt !important; }
    
    /* Prevent orphaned headers */
    h1, h2, h3, h4, h5, h6 {
        page-break-after: avoid;
    }
    
    /* Print colors */
    * {
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }
    
    /* Page setup with margins */
    @page {
        margin: 1.5cm 1cm;
        size: A4 portrait;
    }
    }
    </style>
    """, unsafe_allow_html=True)


elif st.session_state.current_page == 'Help':
    # HELP & DOCUMENTATION PAGE
    
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
    
    col1, col2 = st.columns(2)
    
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
        padding: 25px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Page-by-Page Guide with Marketing Analysis style tabs - shorter labels
    st.markdown("<h3 style='text-align: center; color: #500000;'>Page-by-Page Guide</h3>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Home", 
        "Executive", 
        "Compare", 
        "Marketing", 
        "Database"
    ])
    
    with tab1:
        st.markdown("""
        **Purpose**: Get a quick snapshot of current cohort performance
        
        **Best For**:
        - Daily check-ins on enrollment progress
        - Quick program comparisons
        - Sharing high-level updates with stakeholders
        
        **How to Use**:
        1. **Select Cohort**: Choose the class year you want to analyze (2026, 2027, or 2028)
        2. **Filter by Program**: View all programs or focus on a specific one
        3. **Review Key Metrics**: See total enrolled, applications, inquiries, and conversion rates
        4. **Check the Funnel**: Visual flow from inquiries → applications → enrollment
        5. **Compare Programs**: Side-by-side bar charts show which programs are performing best
        
        **Key Metrics Explained**:
        - **Enrolled**: Students who have accepted admission and enrolled
        - **Applications**: Complete applications received
        - **Inquiries**: Initial interest expressed (top of funnel)
        - **Conversion Rate**: % of inquiries that become enrolled students
        
        **Pro Tip**: Use this page for weekly leadership meetings - it's designed for quick updates!
        """)
    
    with tab2:
        st.markdown("""
        **Purpose**: Comprehensive analysis of cohort performance with interactive visualizations
        
        **Best For**:
        - Monthly performance reviews
        - Identifying trends and patterns
        - Program-specific deep dives
        - Preparing board presentations
        
        **Four Analysis Tabs**:
        
        **1. Performance Analysis**
        - Key performance indicators with year-over-year comparisons
        - Admissions funnel visualization
        - Program comparison charts
        - Growth metrics and trend indicators
        
        **2. Trend Analysis**
        - Time-series charts showing how metrics evolve
        - Application and inquiry trends over time
        - Conversion rate tracking
        - Toggle buttons to show/hide specific metrics
        
        **3. Program Deep Dive**
        - 11 Application metrics (inquiries, applications in progress, complete, etc.)
        - 9 Admissions metrics (offered, accepted, denied, enrolled, etc.)
        - Switch between Line and Bar charts
        - Log scale option for wide-ranging values
        - Data labels on all points
        
        **4. Data Tables**
        - Complete metric breakdowns
        - Program-level details
        - CSV export for further analysis
        - Sortable columns
        
        **Pro Tip**: Use the Program Deep Dive tab to understand exactly where applicants are in the pipeline!
        """)
    
    with tab3:
        st.markdown("""
        **Purpose**: Compare two cohorts side-by-side with statistical analysis
        
        **Best For**:
        - Annual planning and goal setting
        - Understanding year-over-year growth
        - Identifying successful strategies to replicate
        - Budget justification with data
        
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
    
    workflow_col1, workflow_col2 = st.columns(2)
    
    with workflow_col1:
        st.markdown("""
        <div style="background: #f0f8ff; padding: 20px; border-radius: 8px;">
            <h4 style="color: #500000; margin: 0 0 15px 0;">Weekly Check-In</h4>
            <ol style="font-size: 14px; line-height: 1.8; color: #495057;">
                <li>Open <strong>Home Dashboard</strong></li>
                <li>Select current cohort (e.g., Class of 2028)</li>
                <li>Review key metrics vs. goals</li>
                <li>Check program comparison chart</li>
                <li>Note any programs needing attention</li>
                <li>Share screenshot with team</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #fff8f0; padding: 20px; border-radius: 8px;">
            <h4 style="color: #500000; margin: 0 0 15px 0;">Budget Planning</h4>
            <ol style="font-size: 14px; line-height: 1.8; color: #495057;">
                <li>Open <strong>Marketing Analysis</strong></li>
                <li>Go to <strong>Advanced Analytics</strong> tab</li>
                <li>Review CPI, CPA, and ROI metrics</li>
                <li>Check <strong>Channel Analytics</strong> tab</li>
                <li>Identify best-performing channels</li>
                <li>Export data for budget proposal</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with workflow_col2:
        st.markdown("""
        <div style="background: #f0fff0; padding: 20px; border-radius: 8px;">
            <h4 style="color: #500000; margin: 0 0 15px 0;">Monthly Review</h4>
            <ol style="font-size: 14px; line-height: 1.8; color: #495057;">
                <li>Open <strong>Executive Dive</strong></li>
                <li>Select cohort and program</li>
                <li>Review <strong>Performance Analysis</strong> tab</li>
                <li>Check <strong>Trend Analysis</strong> for patterns</li>
                <li>Use <strong>Program Deep Dive</strong> for details</li>
                <li>Export data tables for records</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: #fff0f8; padding: 20px; border-radius: 8px;">
            <h4 style="color: #500000; margin: 0 0 15px 0;">Annual Planning</h4>
            <ol style="font-size: 14px; line-height: 1.8; color: #495057;">
                <li>Open <strong>Comparison Tool</strong></li>
                <li>Compare current vs. previous year</li>
                <li>Review % change for all metrics</li>
                <li>Identify growth opportunities</li>
                <li>Set goals based on trends</li>
                <li>Export comparison table</li>
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
        st.markdown("""
        <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; min-height: 300px;">
            <h4 style="color: #500000; margin: 0 0 20px 0; text-align: center;">Need Help?</h4>
            <div style="font-size: 14px; line-height: 1.8; color: #495057;">
                <p style="margin-bottom: 20px;">
                    <strong>Contact:</strong><br>
                    Tirth Shah<br>
                    tirth.shah@tamu.edu
                </p>
                <p style="margin-bottom: 0;">
                    <strong>Platform Version:</strong> 2.4<br>
                    <strong>Last Updated:</strong> January 23, 2026
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
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
            © 2026 Texas A&M Mays Business School | Version 2.4
        </p>
    </div>
    """, unsafe_allow_html=True)
