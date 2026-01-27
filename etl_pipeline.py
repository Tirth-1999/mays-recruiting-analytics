"""
ETL Pipeline: Load Excel data into SQLite database
"""
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
import re
import sys
sys.path.append('.')
from utils.program_mapping import get_program_display_name, PROGRAM_CODE_TO_NAME

def clean_value(val):
    """Clean data values - handle NaN, '- NA -', etc."""
    if pd.isna(val):
        return None
    if isinstance(val, str):
        if val.strip() in ['- NA -', 'NaN', '']:
            return None
    return val

def parse_date(date_str):
    """Parse date strings from Excel files"""
    if pd.isna(date_str):
        return None
    try:
        return pd.to_datetime(date_str).strftime('%Y-%m-%d')
    except:
        return None

def extract_program_data(file_path, sheet_name, cohort_year):
    """Extract data from a program sheet"""
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    
    # Convert sheet name (short code) to display name
    program_display_name = get_program_display_name(sheet_name)
    
    # Find the row with dates (usually row 2)
    date_row_idx = None
    for idx, row in df.iterrows():
        if any('2024' in str(cell) or '2025' in str(cell) or '2026' in str(cell) for cell in row if pd.notna(cell)):
            date_row_idx = idx
            break
    
    if date_row_idx is None:
        return []
    
    # Extract dates from header row
    dates = []
    for col_idx in range(1, len(df.columns)):
        date_val = df.iloc[date_row_idx, col_idx]
        parsed_date = parse_date(date_val)
        if parsed_date:
            dates.append((col_idx, parsed_date))
    
    # Extract metrics
    records = []
    metric_map = {
        'Inquiries - Received': 'inquiries_received',
        'Applications - In Progress': 'applications_in_progress',
        'Applications - Received': 'applications_received',
        'Applications - Complete': 'applications_complete',
        'Applications - Manual': 'applications_manual',
        'Applications - Verified': 'applications_verified',
        'Applications - On Hold': 'applications_on_hold',
        'Applications - Undelivered': 'applications_undelivered',
        'Applications - Deferral': 'applications_deferral',
        'TOTAL APPLICATIONS': 'total_applications',
        'Admissions - Pre-Admission': 'admissions_pre_admission',
        'Admissions - Offered Admission': 'admissions_offered',
        'Admissions - Denied Admission': 'admissions_denied',
        'Admissions - Accepted Offers': 'admissions_accepted',
        'Admissions - Declined Offers': 'admissions_declined',
        'Admissions - Deferred to Next Year': 'admissions_deferred_to_next',
        'Admissions - Deferred from Last Year': 'admissions_deferred_from_last',
        'Admissions - Moved to Another Mays Program': 'admissions_moved_to_other',
        'Admissions - Application Withdrawn': 'admissions_withdrawn',
        'ANTICIPATED COHORT SIZE': 'anticipated_cohort_size',
    }
    
    for idx, row in df.iterrows():
        metric_name = str(row[0]).strip() if pd.notna(row[0]) else ''
        
        if metric_name in metric_map:
            metric_key = metric_map[metric_name]
            
            for col_idx, report_date in dates:
                value = clean_value(row[col_idx])
                
                if value is not None:
                    try:
                        value = float(value)
                    except:
                        continue
                    
                    records.append({
                        'report_date': report_date,
                        'program': program_display_name,  # Use display name, not sheet name
                        'cohort_year': cohort_year,
                        'metric_name': metric_key,
                        'metric_value': value
                    })
    
    return records

def load_all_data():
    """Load all Excel files into database"""
    conn = sqlite3.connect('edulytix.db')
    
    # Create tables
    conn.execute('''
        CREATE TABLE IF NOT EXISTS admissions_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_date TEXT NOT NULL,
            program TEXT NOT NULL,
            cohort_year INTEGER NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(report_date, program, cohort_year, metric_name)
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS programs (
            program_code TEXT PRIMARY KEY,
            program_name TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Insert program data using official mapping
    programs = [(code, name) for code, name in PROGRAM_CODE_TO_NAME.items()]
    
    conn.executemany(
        'INSERT OR IGNORE INTO programs (program_code, program_name) VALUES (?, ?)',
        programs
    )
    
    # Load data from Excel files
    dataset_files = [
        ('Dataset/MBS-Flex-Online-Admissions-2024-04-30.xlsx', 2026),
        ('Dataset/MBS-Flex-Online-Admissions-2024-05-31.xlsx', 2026),
        ('Dataset/MBS-Flex-Online-Admissions-2024-07-31.xlsx', 2026),
        ('Dataset/MBS-Flex-Online-Admissions-2025-07-31.xlsx', 2027),
        ('Dataset/MBS-Flex-Online-Admissions-2025-10-31.xlsx', 2027),
        ('Dataset/MBS-Flex-Online-Admissions-2025-10-31_New.xlsx', 2028),
        ('Dataset/MBS-Flex-Online-Admissions-2025-11-30.xlsx', 2028),
        ('Dataset/MBS-Flex-Online-Admissions-2025-12-31.xlsx', 2028),
    ]
    
    all_records = []
    
    for file_path, cohort_year in dataset_files:
        if not Path(file_path).exists():
            print(f"Skipping {file_path} - file not found")
            continue
            
        print(f"Processing {file_path}...")
        
        # Get sheet names
        xl_file = pd.ExcelFile(file_path)
        program_sheets = [s for s in xl_file.sheet_names 
                         if s not in ['All Programs', 'Flex', 'Awareness', 'Metric Definitions']]
        
        for sheet in program_sheets:
            try:
                records = extract_program_data(file_path, sheet, cohort_year)
                all_records.extend(records)
                print(f"  - Extracted {len(records)} records from {sheet}")
            except Exception as e:
                print(f"  - Error processing {sheet}: {e}")
    
    # Insert all records (handle duplicates)
    if all_records:
        df_records = pd.DataFrame(all_records)
        
        # Remove duplicates within the batch
        df_records = df_records.drop_duplicates(
            subset=['report_date', 'program', 'cohort_year', 'metric_name'],
            keep='last'
        )
        
        # Insert or replace records
        for _, row in df_records.iterrows():
            conn.execute('''
                INSERT OR REPLACE INTO admissions_metrics 
                (report_date, program, cohort_year, metric_name, metric_value)
                VALUES (?, ?, ?, ?, ?)
            ''', (row['report_date'], row['program'], row['cohort_year'], 
                  row['metric_name'], row['metric_value']))
        
        print(f"\nTotal records processed: {len(df_records)}")
    
    conn.commit()
    
    # Update metadata table with last update date
    conn.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        INSERT OR REPLACE INTO metadata (key, value, updated_at)
        VALUES ('last_data_update', ?, CURRENT_TIMESTAMP)
    ''', (datetime.now().strftime('%Y-%m-%d'),))
    
    conn.commit()
    conn.close()
    print("\nDatabase created successfully: edulytix.db")
    print(f"Last data update: {datetime.now().strftime('%Y-%m-%d')}")

if __name__ == '__main__':
    load_all_data()
