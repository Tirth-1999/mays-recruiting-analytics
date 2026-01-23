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


