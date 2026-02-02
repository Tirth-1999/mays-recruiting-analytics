"""
ETL Pipeline: Load Excel data into SQLite database as State Snapshots
Enhanced to process admissions data as point-in-time state snapshots
"""
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import datetime
import re
import sys
import logging

sys.path.append('.')
from utils.program_mapping import get_program_display_name, PROGRAM_CODE_TO_NAME

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_value(val):
    """
    Clean data values - handle NaN, '- NA -', etc. 
    Also detect placeholder zeros (when a metric drops from significant value to 0)
    Return None for missing data to skip storage
    """
    if pd.isna(val):
        return None  # Missing data - don't store
    if isinstance(val, str):
        if val.strip() in ['- NA -', 'NaN', '', ' ']:
            return None  # Missing data - don't store
    try:
        return float(val)
    except:
        return None  # Invalid data - don't store

def parse_date(date_str):
    """Parse date strings from Excel files"""
    if pd.isna(date_str):
        return None
    try:
        return pd.to_datetime(date_str).strftime('%Y-%m-%d')
    except:
        return None

def parse_filename_cohort(file_path: str):
    """
    Parse cohort information from filename
    Example: MBS-Flex-Online-Admissions-2025-07-31_fall.xlsx
    Returns: (start_year, season, cohort_year)
    """
    filename = Path(file_path).name
    
    # Explicit mapping based on actual files and their cohorts
    file_cohort_map = {
        'MBS-Flex-Online-Admissions-2024-07-31_fall.xlsx': 2026,  # Class 2026 (completed)
        'MBS-Flex-Online-Admissions-2025-07-31_fall.xlsx': 2027,  # Class 2027 (in progress)
        'MBS-Flex-Online-Admissions-2025-12-31_fall.xlsx': 2028   # Class 2028 (early stage)
    }
    
    if filename in file_cohort_map:
        cohort_year = file_cohort_map[filename]
        
        # Extract year and season from filename for consistency
        match = re.search(r'(\d{4})-(\d{2})-(\d{2})_(fall|spring)\.xlsx', filename)
        if match:
            start_year = int(match.group(1))
            season = match.group(4)
            logger.info(f"Parsed {filename}: Start {start_year}, Season {season}, Cohort {cohort_year}")
            return start_year, season, cohort_year
    
    raise ValueError(f"Cannot parse cohort info from filename: {filename}")

def discover_program_sheets(file_path: str):
    """
    Dynamically discover program sheets, excluding utility sheets
    """
    try:
        xl_file = pd.ExcelFile(file_path)
        all_sheets = xl_file.sheet_names
        
        # Exclude utility sheets as per enhancement plan
        excluded_sheets = ['All Programs', 'Flex', 'Awareness', 'Metric Definitions']
        
        # Get program sheets
        program_sheets = [sheet for sheet in all_sheets if sheet not in excluded_sheets]
        
        # Exclude non-existent programs
        excluded_programs = ['MS SPBA']  # Program doesn't exist in Flex Online
        program_sheets = [sheet for sheet in program_sheets if sheet not in excluded_programs]
        
        logger.info(f"Discovered program sheets in {Path(file_path).name}: {program_sheets}")
        return program_sheets
        
    except Exception as e:
        logger.error(f"Error discovering sheets in {file_path}: {e}")
        return []

def check_date_has_other_metrics(df, col_idx, date_row_idx, current_metric):
    """
    Check if a specific date column has other metrics reported (indicating active reporting)
    This helps determine if we should backfill missing values or skip the date entirely
    """
    # Count non-null, non-zero values in this date column (excluding current metric)
    column_data = df.iloc[:, col_idx]
    
    # Define key metrics that indicate active reporting
    key_reporting_indicators = [
        'Inquiries - Received',
        'Applications - In Progress', 
        'Applications - Complete',
        'TOTAL APPLICATIONS',
        'Admissions - Offered Admission',
        'Admissions - Accepted Offers',
        'ANTICIPATED COHORT SIZE'
    ]
    
    reported_metrics = 0
    for idx, row in df.iterrows():
        if idx == date_row_idx:  # Skip header row
            continue
            
        metric_name = str(row[0]).strip() if pd.notna(row[0]) else ''
        
        # Skip the current metric we're processing
        if current_metric in metric_name.lower().replace(' ', '_').replace('-', '_'):
            continue
            
        # Check if this is a key reporting indicator
        if any(indicator in metric_name for indicator in key_reporting_indicators):
            value = row[col_idx]
            if pd.notna(value) and value != 0 and str(value).strip() not in ['- NA -', 'NaN', '']:
                reported_metrics += 1
    
    # If we have at least 2 other key metrics reported, consider this an active reporting date
    return reported_metrics >= 2


def extract_program_data(file_path, sheet_name, start_year, season, cohort_year):
    """Extract state snapshot data from a program sheet"""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        
        # Convert sheet name (short code) to display name
        program_display_name = get_program_display_name(sheet_name)
        
        # Find the row with dates (usually row 2)
        date_row_idx = None
        for idx, row in df.iterrows():
            if any('2024' in str(cell) or '2025' in str(cell) or '2026' in str(cell) 
                   for cell in row if pd.notna(cell)):
                date_row_idx = idx
                break
        
        if date_row_idx is None:
            logger.warning(f"No date row found in {sheet_name}")
            return []
        
        # Extract dates from header row - only process columns with actual data
        dates = []
        for col_idx in range(1, len(df.columns)):
            date_val = df.iloc[date_row_idx, col_idx]
            parsed_date = parse_date(date_val)
            if parsed_date:
                # Check if this column has any actual data (not all NaN/blank)
                column_data = df.iloc[:, col_idx]
                non_null_count = column_data.notna().sum()
                non_zero_count = (column_data.fillna(0) != 0).sum()
                
                # Only include columns with meaningful data
                if non_null_count > 5 and non_zero_count > 2:  # At least some real data
                    dates.append((col_idx, parsed_date))
                else:
                    logger.info(f"Skipping empty date column {parsed_date} in {sheet_name} (non-null: {non_null_count}, non-zero: {non_zero_count})")
        
        if not dates:
            logger.warning(f"No valid date columns with data found in {sheet_name}")
            return []
        
        logger.info(f"Processing {len(dates)} date columns with actual data in {sheet_name}")
        
        # Extract state snapshot metrics
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
                
                # Extract values for this metric across valid date columns
                metric_values = []
                for col_idx, report_date in dates:
                    value = clean_value(row[col_idx])
                    metric_values.append((report_date, value))  # Store all values (including None)
                
                # Apply smart backfill logic for state snapshots
                processed_values = []
                for i, (report_date, value) in enumerate(metric_values):
                    if value is not None:
                        # We have actual data - store it
                        processed_values.append((report_date, value))
                    else:
                        # Missing data - check if we should backfill
                        if i > 0:  # Not the first date
                            prev_value = None
                            # Find the last non-None value
                            for j in range(i-1, -1, -1):
                                if metric_values[j][1] is not None:
                                    prev_value = metric_values[j][1]
                                    break
                            
                            if prev_value is not None:
                                # Check if this date has OTHER metrics reported (indicating active reporting)
                                date_has_other_data = check_date_has_other_metrics(df, col_idx, date_row_idx, metric_key)
                                
                                if date_has_other_data:
                                    # Backfill with previous value (state snapshot logic)
                                    logger.info(f"Backfilling {program_display_name} {metric_key} on {report_date} with previous value {prev_value} (other metrics reported)")
                                    processed_values.append((report_date, prev_value))
                                else:
                                    # No other metrics reported - skip this date entirely
                                    logger.info(f"Skipping {program_display_name} {metric_key} on {report_date} (no other metrics reported)")
                
                # Additional filtering: skip suspicious zeros (dramatic drops)
                filtered_values = []
                for i, (report_date, value) in enumerate(processed_values):
                    if value == 0 and i > 0:
                        prev_value = processed_values[i-1][1]
                        if prev_value > 50:  # Significant previous value
                            logger.info(f"Skipping suspicious zero for {program_display_name} {metric_key} on {report_date} (prev: {prev_value})")
                            continue
                    filtered_values.append((report_date, value))
                
                # Store the filtered values
                for report_date, value in filtered_values:
                    records.append({
                        'report_date': report_date,
                        'program': program_display_name,
                        'cohort_year': cohort_year,
                        'cohort_season': season,
                        'metric_name': metric_key,
                        'metric_value': value,
                        'file_source': Path(file_path).name
                    })
        
        logger.info(f"Extracted {len(records)} state snapshot records from {program_display_name}")
        return records
        
    except Exception as e:
        logger.error(f"Error extracting data from {sheet_name}: {e}")
        return []

def load_all_data():
    """Load all Excel files into database as state snapshots"""
    conn = sqlite3.connect('edulytix.db')
    
    try:
        logger.info("🔄 Starting State Snapshot ETL Pipeline...")
        
        # Create enhanced tables for state snapshots
        conn.execute('''
            CREATE TABLE IF NOT EXISTS admissions_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date TEXT NOT NULL,
                program TEXT NOT NULL,
                cohort_year INTEGER NOT NULL,
                cohort_season TEXT NOT NULL DEFAULT 'fall',
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL DEFAULT 0,
                file_source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(report_date, program, cohort_year, cohort_season, metric_name)
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS programs (
                program_code TEXT PRIMARY KEY,
                program_name TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        # Create indexes for performance
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_admissions_date_program 
            ON admissions_metrics(report_date, program)
        ''')
        
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_admissions_program_cohort
            ON admissions_metrics(program, cohort_year, cohort_season)
        ''')
        
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_admissions_metric_name 
            ON admissions_metrics(metric_name)
        ''')
        
        # Insert program data using official mapping
        programs = [(code, name) for code, name in PROGRAM_CODE_TO_NAME.items()]
        conn.executemany(
            'INSERT OR IGNORE INTO programs (program_code, program_name) VALUES (?, ?)',
            programs
        )
        
        # Load data from renamed Excel files (only the 3 key files)
        dataset_files = [
            'Dataset/MBS-Flex-Online-Admissions-2024-07-31_fall.xlsx',  # Class 2026
            'Dataset/MBS-Flex-Online-Admissions-2025-07-31_fall.xlsx',  # Class 2027
            'Dataset/MBS-Flex-Online-Admissions-2025-12-31_fall.xlsx'   # Class 2028
        ]
        
        all_records = []
        
        for file_path in dataset_files:
            if not Path(file_path).exists():
                logger.warning(f"Skipping {file_path} - file not found")
                continue
                
            logger.info(f"Processing {file_path}...")
            
            try:
                # Parse cohort information from filename
                start_year, season, cohort_year = parse_filename_cohort(file_path)
                
                # Get program sheets dynamically
                program_sheets = discover_program_sheets(file_path)
                
                for sheet in program_sheets:
                    try:
                        records = extract_program_data(file_path, sheet, start_year, season, cohort_year)
                        all_records.extend(records)
                        logger.info(f"  - Processed {len(records)} records from {sheet}")
                    except Exception as e:
                        logger.error(f"  - Error processing {sheet}: {e}")
                        
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
        
        # Insert all records (handle duplicates)
        if all_records:
            df_records = pd.DataFrame(all_records)
            
            # Remove duplicates within the batch
            df_records = df_records.drop_duplicates(
                subset=['report_date', 'program', 'cohort_year', 'cohort_season', 'metric_name'],
                keep='last'
            )
            
            # Insert or replace records
            for _, row in df_records.iterrows():
                conn.execute('''
                    INSERT OR REPLACE INTO admissions_metrics 
                    (report_date, program, cohort_year, cohort_season, metric_name, metric_value, file_source)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (row['report_date'], row['program'], row['cohort_year'], 
                      row['cohort_season'], row['metric_name'], row['metric_value'], row['file_source']))
            
            logger.info(f"Total state snapshot records processed: {len(df_records)}")
        
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
        
        conn.execute('''
            INSERT OR REPLACE INTO metadata (key, value, updated_at)
            VALUES ('etl_version', 'state_snapshot_v1.0', CURRENT_TIMESTAMP)
        ''')
        
        conn.commit()
        
        # Print summary statistics
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM admissions_metrics')
        total_records = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT program) FROM admissions_metrics')
        total_programs = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT cohort_year) FROM admissions_metrics')
        total_cohorts = cursor.fetchone()[0]
        
        logger.info("✅ State Snapshot ETL completed successfully!")
        logger.info(f"Database: edulytix.db")
        logger.info(f"Summary: {total_records} snapshots, {total_programs} programs, {total_cohorts} cohorts")
        
        # Show final state examples for all cohorts (dynamic final state per program)
        for cohort in [2026, 2027, 2028]:
            cursor.execute('''
                WITH final_states AS (
                    SELECT 
                        program,
                        MAX(CASE WHEN metric_value > 0 THEN report_date END) as final_date
                    FROM admissions_metrics 
                    WHERE cohort_year = ? AND metric_name = 'inquiries_received'
                    GROUP BY program
                )
                SELECT 
                    fs.program,
                    fs.final_date,
                    am.metric_value
                FROM final_states fs
                JOIN admissions_metrics am ON fs.program = am.program 
                    AND fs.final_date = am.report_date 
                    AND am.cohort_year = ?
                    AND am.metric_name = 'inquiries_received'
                ORDER BY fs.program
            ''', (cohort, cohort))
            
            results = cursor.fetchall()
            if results:
                logger.info(f"Class {cohort} Final States (latest non-zero data per program):")
                for program, final_date, inquiries in results:
                    program_short = program.replace('Flex Online ', '')
                    logger.info(f"  - {program_short}: {inquiries} inquiries (as of {final_date})")
        
        logger.info(f"Last update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        logger.error(f"Error in state snapshot ETL pipeline: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    load_all_data()
