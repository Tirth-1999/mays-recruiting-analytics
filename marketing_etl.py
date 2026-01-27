"""
Marketing Data ETL Pipeline
Load marketing ad spend data from Ologie into the database
Handles dynamic month detection and incremental updates
"""

import pandas as pd
import sqlite3
from datetime import datetime
import numpy as np
import json
import re
import sys
sys.path.append('.')
from utils.program_mapping import get_program_display_name

# Database connection
DB_PATH = 'edulytix.db'

def create_marketing_tables():
    """Create marketing tables with proper schema"""
    conn = sqlite3.connect(DB_PATH)
    
    # Main spend table - individual channel spend by month
    conn.execute('''
        CREATE TABLE IF NOT EXISTS marketing_spend (
            spend_id INTEGER PRIMARY KEY AUTOINCREMENT,
            program TEXT NOT NULL,
            channel TEXT NOT NULL,
            fiscal_year TEXT NOT NULL,
            month_date TEXT NOT NULL,
            spend_amount REAL DEFAULT 0,
            extra_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(program, channel, fiscal_year, month_date)
        )
    ''')
    
    # Totals table - program-level totals by month
    conn.execute('''
        CREATE TABLE IF NOT EXISTS marketing_spend_totals (
            total_id INTEGER PRIMARY KEY AUTOINCREMENT,
            program TEXT NOT NULL,
            fiscal_year TEXT NOT NULL,
            month_date TEXT NOT NULL,
            total_spend REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(program, fiscal_year, month_date)
        )
    ''')
    
    # Create indexes for performance
    conn.execute('CREATE INDEX IF NOT EXISTS idx_spend_program ON marketing_spend(program)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_spend_date ON marketing_spend(month_date)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_totals_program ON marketing_spend_totals(program)')
    
    conn.commit()
    conn.close()
    print("✅ Marketing tables created/verified")

def standardize_program_name(program_name):
    """
    Standardize program names using central mapping utility.
    Handles variations like 'Flex Online Mba', 'Flex Online MBA', etc.
    """
    if not program_name or program_name == 'nan':
        return None
    
    # Use the central mapping utility
    standardized = get_program_display_name(program_name)
    
    return standardized

def detect_fiscal_year_columns(df):
    """
    Detect FY25 and FY26 columns dynamically
    Returns: (fy25_months, fy26_months, fy25_notes_col, fy26_notes_col, header_row_idx)
    """
    # Row 0 has FY headers, Row 1 has month names
    fy_header_row = df.iloc[0]
    month_header_row = df.iloc[1]
    
    # Month name mapping
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    fy25_months = []
    fy26_months = []
    fy25_notes_col = None
    fy26_notes_col = None
    
    # Find FY25 and FY26 start columns by scanning row 0
    fy25_start = None
    fy26_start = None
    
    for col_idx in range(len(fy_header_row)):
        cell_value = str(fy_header_row[col_idx]).strip()
        
        if ('FY25' in cell_value or 'Year 1' in cell_value) and 'note' not in cell_value.lower():
            fy25_start = col_idx
            print(f"   FY25 section starts at column: {col_idx}")
        elif ('FY26' in cell_value or 'Year 2' in cell_value) and 'note' not in cell_value.lower():
            fy26_start = col_idx
            print(f"   FY26 section starts at column: {col_idx}")
        
        # Find notes columns
        if 'note' in cell_value.lower() or 'incremental' in cell_value.lower():
            if 'FY25' in cell_value or 'Y1' in cell_value:
                fy25_notes_col = col_idx
                print(f"   FY25 notes column: {col_idx}")
            elif 'FY26' in cell_value or 'Y2' in cell_value:
                fy26_notes_col = col_idx
                print(f"   FY26 notes column: {col_idx}")
    
    # Now scan month names in row 1 and assign to FY25 or FY26
    for col_idx in range(len(month_header_row)):
        cell_value = str(month_header_row[col_idx]).strip()
        
        # Check if it's a month name
        if any(month in cell_value for month in month_names):
            month_name = next((m for m in month_names if m in cell_value), None)
            
            # Determine if it's FY25 or FY26 based on column position
            if fy25_start is not None and col_idx >= fy25_start:
                # Check if we've entered FY26 territory
                if fy26_start is not None and col_idx >= fy26_start:
                    # This is FY26
                    if month_name in ['August', 'September', 'October', 'November', 'December']:
                        year = 2025
                    else:
                        year = 2026
                    month_num = month_names.index(month_name) + 1
                    month_date = f"{year}-{month_num:02d}-01"
                    fy26_months.append((col_idx, month_name, month_date))
                else:
                    # This is FY25
                    if month_name in ['September', 'October', 'November', 'December']:
                        year = 2024
                    else:
                        year = 2025
                    month_num = month_names.index(month_name) + 1
                    month_date = f"{year}-{month_num:02d}-01"
                    fy25_months.append((col_idx, month_name, month_date))
    
    return fy25_months, fy26_months, fy25_notes_col, fy26_notes_col, 1  # header_row_idx = 1

def parse_ad_spend_file(file_path):
    """
    Parse the marketing spend file with dynamic month detection
    Returns: (spend_records, totals_records)
    """
    print(f"\n📊 Processing: {file_path}")
    
    # Read the raw file
    df = pd.read_excel(file_path, header=None)
    
    # Detect fiscal year columns (row 0 has FY headers, row 1 has months)
    fy25_months, fy26_months, fy25_notes_col, fy26_notes_col, header_row_idx = detect_fiscal_year_columns(df)
    
    print(f"   FY25 months detected: {len(fy25_months)}")
    print(f"   FY26 months detected: {len(fy26_months)}")
    
    all_months = fy25_months + fy26_months
    
    if not all_months:
        print("   ❌ No months detected!")
        return [], []
    
    # Parse data rows (start from row 2, which is index 2)
    spend_records = []
    totals_records = []
    current_program = None
    
    for idx in range(2, min(len(df), 57)):  # Rows 2-56 (data rows)
        row = df.iloc[idx]
        
        program_cell = str(row[0]).strip() if pd.notna(row[0]) else ''
        channel_cell = str(row[1]).strip() if pd.notna(row[1]) else ''
        
        # Skip completely empty rows
        if not program_cell and not channel_cell:
            continue
        
        # Check if this is a Totals row (Program='Totals', Channel is empty)
        if program_cell.lower() == 'totals' and not channel_cell:
            # This is a totals row for the current program
            if current_program:
                # Get notes if available
                notes_list = []
                if fy25_notes_col and pd.notna(row[fy25_notes_col]):
                    note = str(row[fy25_notes_col]).strip()
                    if note and note not in ['', 'nan', 'NaN']:
                        notes_list.append(f"FY25: {note}")
                if fy26_notes_col and pd.notna(row[fy26_notes_col]):
                    note = str(row[fy26_notes_col]).strip()
                    if note and note not in ['', 'nan', 'NaN']:
                        notes_list.append(f"FY26: {note}")
                
                # Process each month for totals
                for col_idx, month_name, month_date in all_months:
                    value = row[col_idx]
                    
                    # Determine fiscal year
                    fiscal_year = 'FY25' if (col_idx, month_name, month_date) in fy25_months else 'FY26'
                    
                    # Parse value - "No Ad Spend" or "-" = 0
                    spend_amount = 0.0
                    if pd.notna(value):
                        value_str = str(value).strip().lower()
                        if value_str not in ['', '-', 'no ad spend', 'nan']:
                            try:
                                spend_amount = float(value)
                            except (ValueError, TypeError):
                                spend_amount = 0.0
                    
                    totals_records.append({
                        'program': current_program,
                        'fiscal_year': fiscal_year,
                        'month_date': month_date,
                        'total_spend': spend_amount
                    })
            continue
        
        # Check if this is a new program row
        if program_cell and program_cell not in ['', 'nan', 'NaN', 'Totals']:
            current_program = standardize_program_name(program_cell)
            print(f"   Processing program: {current_program}")
        
        # Skip if no current program
        if not current_program:
            continue
        
        # This is a channel row
        if channel_cell and channel_cell not in ['', 'nan', 'NaN']:
            # Get notes if available
            notes_list = []
            if fy25_notes_col and pd.notna(row[fy25_notes_col]):
                note = str(row[fy25_notes_col]).strip()
                if note and note not in ['', 'nan', 'NaN']:
                    notes_list.append(f"FY25: {note}")
            if fy26_notes_col and pd.notna(row[fy26_notes_col]):
                note = str(row[fy26_notes_col]).strip()
                if note and note not in ['', 'nan', 'NaN']:
                    notes_list.append(f"FY26: {note}")
            
            notes_json = json.dumps(notes_list) if notes_list else None
            
            # Process each month
            for col_idx, month_name, month_date in all_months:
                value = row[col_idx]
                
                # Determine fiscal year
                fiscal_year = 'FY25' if (col_idx, month_name, month_date) in fy25_months else 'FY26'
                
                # Parse value - "No Ad Spend" or "-" = 0
                spend_amount = 0.0
                if pd.notna(value):
                    value_str = str(value).strip().lower()
                    if value_str not in ['', '-', 'no ad spend', 'nan']:
                        try:
                            spend_amount = float(value)
                        except (ValueError, TypeError):
                            spend_amount = 0.0
                
                spend_records.append({
                    'program': current_program,
                    'channel': channel_cell,
                    'fiscal_year': fiscal_year,
                    'month_date': month_date,
                    'spend_amount': spend_amount,
                    'extra_notes': notes_json
                })
    
    print(f"   ✅ Extracted {len(spend_records)} spend records")
    print(f"   ✅ Extracted {len(totals_records)} totals records")
    
    return spend_records, totals_records

def get_existing_data(conn):
    """Get existing data from database to detect new records"""
    try:
        existing_spend = pd.read_sql(
            "SELECT program, channel, fiscal_year, month_date FROM marketing_spend",
            conn
        )
        existing_totals = pd.read_sql(
            "SELECT program, fiscal_year, month_date FROM marketing_spend_totals",
            conn
        )
        return existing_spend, existing_totals
    except:
        return pd.DataFrame(), pd.DataFrame()

def load_marketing_spend():
    """Load marketing spend data into database with incremental updates"""
    conn = sqlite3.connect(DB_PATH)
    
    # Parse the ad spend file
    file_path = 'Dataset/Mays Flex Online Ad Spend Year 1.xlsx'
    spend_records, totals_records = parse_ad_spend_file(file_path)
    
    if not spend_records and not totals_records:
        print("⚠️  No records to load")
        conn.close()
        return
    
    # Get existing data
    existing_spend, existing_totals = get_existing_data(conn)
    
    # Convert to DataFrames
    df_spend = pd.DataFrame(spend_records)
    df_totals = pd.DataFrame(totals_records)
    
    # Detect new records
    if not existing_spend.empty:
        # Merge to find new records
        df_spend_merged = df_spend.merge(
            existing_spend,
            on=['program', 'channel', 'fiscal_year', 'month_date'],
            how='left',
            indicator=True
        )
        new_spend = df_spend_merged[df_spend_merged['_merge'] == 'left_only'].drop('_merge', axis=1)
        updated_spend = df_spend_merged[df_spend_merged['_merge'] == 'both'].drop('_merge', axis=1)
        
        print(f"\n📊 Spend Records: {len(new_spend)} new, {len(updated_spend)} existing")
    else:
        new_spend = df_spend
        print(f"\n📊 Spend Records: {len(new_spend)} new (first load)")
    
    if not existing_totals.empty:
        df_totals_merged = df_totals.merge(
            existing_totals,
            on=['program', 'fiscal_year', 'month_date'],
            how='left',
            indicator=True
        )
        new_totals = df_totals_merged[df_totals_merged['_merge'] == 'left_only'].drop('_merge', axis=1)
        updated_totals = df_totals_merged[df_totals_merged['_merge'] == 'both'].drop('_merge', axis=1)
        
        print(f"📊 Totals Records: {len(new_totals)} new, {len(updated_totals)} existing")
    else:
        new_totals = df_totals
        print(f"📊 Totals Records: {len(new_totals)} new (first load)")
    
    # Load to database (INSERT OR REPLACE for updates)
    for _, row in df_spend.iterrows():
        conn.execute('''
            INSERT OR REPLACE INTO marketing_spend 
            (program, channel, fiscal_year, month_date, spend_amount, extra_notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (row['program'], row['channel'], row['fiscal_year'], 
              row['month_date'], row['spend_amount'], row['extra_notes']))
    
    for _, row in df_totals.iterrows():
        conn.execute('''
            INSERT OR REPLACE INTO marketing_spend_totals 
            (program, fiscal_year, month_date, total_spend)
            VALUES (?, ?, ?, ?)
        ''', (row['program'], row['fiscal_year'], row['month_date'], row['total_spend']))
    
    conn.commit()
    
    print(f"\n✅ Loaded {len(df_spend)} spend records to database")
    print(f"✅ Loaded {len(df_totals)} totals records to database")
    
    # Show summary
    print("\n📊 Summary by Program:")
    summary = df_spend.groupby('program')['spend_amount'].agg(['count', 'sum']).round(2)
    summary.columns = ['Records', 'Total Spend ($)']
    print(summary.to_string())
    
    print("\n📊 Summary by Channel:")
    channel_summary = df_spend.groupby('channel')['spend_amount'].agg(['count', 'sum']).round(2)
    channel_summary.columns = ['Records', 'Total Spend ($)']
    print(channel_summary.to_string())
    
    print("\n📊 Summary by Fiscal Year:")
    fy_summary = df_spend.groupby('fiscal_year')['spend_amount'].agg(['count', 'sum']).round(2)
    fy_summary.columns = ['Records', 'Total Spend ($)']
    print(fy_summary.to_string())
    
    conn.close()

def validate_data():
    """Validate loaded data for consistency"""
    print("\n🔍 Validating data...")
    
    conn = sqlite3.connect(DB_PATH)
    
    # Check for programs
    programs = pd.read_sql("SELECT DISTINCT program FROM marketing_spend ORDER BY program", conn)
    print(f"\n✅ Programs found: {len(programs)}")
    for prog in programs['program']:
        print(f"   • {prog}")
    
    # Check for channels
    channels = pd.read_sql("SELECT DISTINCT channel FROM marketing_spend ORDER BY channel", conn)
    print(f"\n✅ Channels found: {len(channels)}")
    for ch in channels['channel']:
        print(f"   • {ch}")
    
    # Check date range
    date_range = pd.read_sql(
        "SELECT MIN(month_date) as earliest, MAX(month_date) as latest FROM marketing_spend",
        conn
    )
    print(f"\n✅ Date range: {date_range['earliest'].iloc[0]} to {date_range['latest'].iloc[0]}")
    
    # Check for notes
    notes_count = pd.read_sql(
        "SELECT COUNT(*) as count FROM marketing_spend WHERE extra_notes IS NOT NULL",
        conn
    )['count'].iloc[0]
    print(f"\n✅ Records with notes: {notes_count}")
    
    # Verify totals match
    print("\n🔍 Verifying totals...")
    verification = pd.read_sql('''
        SELECT 
            s.program,
            s.fiscal_year,
            s.month_date,
            SUM(s.spend_amount) as calculated_total,
            t.total_spend as stored_total,
            ABS(SUM(s.spend_amount) - t.total_spend) as difference
        FROM marketing_spend s
        LEFT JOIN marketing_spend_totals t 
            ON s.program = t.program 
            AND s.fiscal_year = t.fiscal_year 
            AND s.month_date = t.month_date
        GROUP BY s.program, s.fiscal_year, s.month_date
        HAVING difference > 0.01
    ''', conn)
    
    if verification.empty:
        print("✅ All totals match calculated sums")
    else:
        print(f"⚠️  Found {len(verification)} mismatches:")
        print(verification.to_string())
    
    conn.close()

def update_metadata():
    """Update metadata with last update timestamp"""
    conn = sqlite3.connect(DB_PATH)
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    conn.execute('''
        INSERT OR REPLACE INTO metadata (key, value, updated_at)
        VALUES ('last_marketing_update', ?, CURRENT_TIMESTAMP)
    ''', (today,))
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Updated metadata: last_marketing_update = {today}")

def main():
    """Main ETL process"""
    print("=" * 80)
    print("🚀 Marketing Data ETL Pipeline - Enhanced Version")
    print("=" * 80)
    
    # Step 1: Create tables
    create_marketing_tables()
    
    # Step 2: Load marketing spend data (with auto-detection)
    load_marketing_spend()
    
    # Step 3: Validate data
    validate_data()
    
    # Step 4: Update metadata
    update_metadata()
    
    print("\n" + "=" * 80)
    print("✅ Marketing ETL Complete!")
    print("=" * 80)
    print("\n💡 Features:")
    print("   ✅ Auto-detects new months in Excel file")
    print("   ✅ Handles both FY25 and FY26 data")
    print("   ✅ Stores notes as JSON lists")
    print("   ✅ Separate totals table")
    print("   ✅ Standardized program names")
    print("   ✅ 'No Ad Spend' = 0 (not NULL)")
    print("\n💡 Next steps:")
    print("   1. Run main_app.py to view the dashboard")
    print("   2. Check Data Explorer for new tables:")
    print("      • marketing_spend (channel-level)")
    print("      • marketing_spend_totals (program-level)")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
