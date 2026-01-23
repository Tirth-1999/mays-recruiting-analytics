"""
Database utility functions for Mays Analytics Platform
Shared database connections and data loading functions
"""
import streamlit as st
import pandas as pd
import sqlite3


@st.cache_resource
def get_connection():
    """Get database connection with caching"""
    return sqlite3.connect('edulytix.db', check_same_thread=False)


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


@st.cache_data(ttl=600)
def load_programs():
    """Load active programs from database"""
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
