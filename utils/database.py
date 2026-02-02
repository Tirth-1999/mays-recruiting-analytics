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
    # Order matters - check more specific patterns first
    program_map = {
        'MANAGEMENT INFORMATION SYSTEMS': 'MISY',
        'INFORMATION SYSTEMS': 'MISY',
        'MIS': 'MISY',
        'MISY': 'MISY',
        'AI IN BUSINESS': 'SPBA',
        'AI AND BUSINESS': 'SPBA',
        'ARTIFICIAL INTELLIGENCE': 'SPBA',
        'SPBA': 'SPBA',
        'ENTREPRENEURIAL LEADERSHIP': 'ENLD',
        'ENLD': 'ENLD',
        'HUMAN RESOURCE': 'HRM',
        'HRM': 'HRM',
        'ACCOUNTING': 'ACCT',
        'ACCT': 'ACCT',
        'MARKETING': 'MKTG',
        'MKTG': 'MKTG',
        'MBA': 'MBA',
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
    """Load all data for a specific cohort - only actual reported values (no zeros for missing data)"""
    conn = get_connection()
    query = '''
        SELECT 
            report_date,
            program,
            cohort_year,
            cohort_season,
            metric_name,
            metric_value
        FROM admissions_metrics
        WHERE cohort_year = ? AND cohort_season = 'fall'
        ORDER BY report_date, program
    '''
    df = pd.read_sql(query, conn, params=[cohort_year])
    if not df.empty:
        df['report_date'] = pd.to_datetime(df['report_date'])
    return df


@st.cache_data(ttl=600)
def load_yoy_comparison_data(current_cohort, comparison_cohort):
    """Load data for year-over-year comparison with smart backfilling"""
    conn = get_connection()
    query = '''
        SELECT 
            report_date,
            program,
            cohort_year,
            cohort_season,
            metric_name,
            metric_value
        FROM admissions_metrics
        WHERE cohort_year IN (?, ?) AND cohort_season = 'fall'
        ORDER BY report_date, program, cohort_year, metric_name
    '''
    df = pd.read_sql(query, conn, params=[current_cohort, comparison_cohort])
    if df.empty:
        return df
    
    df['report_date'] = pd.to_datetime(df['report_date'])
    
    # Apply smart backfilling logic for each cohort-program-metric combination
    backfilled_data = []
    
    for (cohort, program, metric), group in df.groupby(['cohort_year', 'program', 'metric_name']):
        group = group.sort_values('report_date')
        
        # Get all dates for this cohort (to ensure consistent timeline)
        all_dates = df[df['cohort_year'] == cohort]['report_date'].unique()
        all_dates = sorted(all_dates)
        
        # Create a complete timeline for this metric
        last_valid_value = None
        
        for date in all_dates:
            # Check if we have data for this date
            date_data = group[group['report_date'] == date]
            
            if not date_data.empty:
                # We have actual data for this date
                current_value = date_data['metric_value'].iloc[0]
                
                # For cumulative metrics, ensure non-decreasing values
                cumulative_metrics = [
                    'inquiries_received', 
                    'total_applications', 
                    'applications_received',
                    'applications_complete', 
                    'applications_in_progress',
                    'applications_manual',
                    'applications_verified',
                    'applications_on_hold',
                    'applications_deferral',
                    'applications_undelivered',
                    'admissions_offered'
                ]
                
                if metric in cumulative_metrics and last_valid_value is not None:
                    # Ensure cumulative metrics don't decrease (use max of current and previous)
                    current_value = max(current_value, last_valid_value)
                
                last_valid_value = current_value
            else:
                # No data for this date - use backfilling logic
                if last_valid_value is not None:
                    # Backfill with last valid value for cumulative metrics
                    cumulative_metrics = [
                        'inquiries_received', 
                        'total_applications', 
                        'applications_received',
                        'applications_complete', 
                        'applications_in_progress',
                        'applications_manual',
                        'applications_verified',
                        'applications_on_hold',
                        'applications_deferral',
                        'applications_undelivered',
                        'admissions_offered'
                    ]
                    
                    if metric in cumulative_metrics:
                        current_value = last_valid_value  # Backfill cumulative metrics
                    else:
                        current_value = None  # Don't backfill non-cumulative metrics
                else:
                    current_value = None  # No previous value to backfill with
            
            # Add to backfilled data if we have a value
            if current_value is not None:
                backfilled_data.append({
                    'report_date': date,
                    'program': program,
                    'cohort_year': cohort,
                    'cohort_season': 'fall',
                    'metric_name': metric,
                    'metric_value': current_value
                })
    
    # Convert back to DataFrame
    if backfilled_data:
        backfilled_df = pd.DataFrame(backfilled_data)
        backfilled_df['report_date'] = pd.to_datetime(backfilled_df['report_date'])
        return backfilled_df
    else:
        return df


