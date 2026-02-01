"""
Marketing Data ETL Pipeline - Enhanced Version
Load marketing ad spend data from the new cleaner Excel file
Handles dynamic sheets, months, and programs with state tracking
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
EXCEL_FILE = 'Dataset/Mays Flex Online Ad Spend.xlsx'

def create_marketing_tables():
    """Create marketing tables with proper schema"""
    conn = sqlite3.connect(DB_PATH)
    
    # Main spend table - individual channel spend by month (NO notes here)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS marketing_spend (
            spend_id INTEGER PRIMARY KEY AUTOINCREMENT,
            program TEXT NOT NULL,
            channel TEXT NOT NULL,
            fiscal_year TEXT NOT NULL,
            month_date TEXT NOT NULL,
            spend_amount REAL DEFAULT 0,
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
    
    # Incremental notes table - one note per program-channel-fiscal_year
    conn.execute('''
        CREATE TABLE IF NOT EXISTS marketing_incremental_notes (
            note_id INTEGER PRIMARY KEY AUTOINCREMENT,
            program TEXT NOT NULL,
            channel TEXT NOT NULL,
            fiscal_year TEXT NOT NULL,
            incremental_note TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(program, channel, fiscal_year)
        )
    ''')
    
    # State tracking table - track what we've processed
    conn.execute('''
        CREATE TABLE IF NOT EXISTS marketing_etl_state (
            state_id INTEGER PRIMARY KEY AUTOINCREMENT,
            fiscal_year TEXT NOT NULL,
            sheet_name TEXT NOT NULL,
            programs TEXT NOT NULL,  -- JSON array of programs
            channels TEXT NOT NULL,  -- JSON array of channels  
            months TEXT NOT NULL,    -- JSON array of months
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(fiscal_year, sheet_name)
        )
    ''')
    
    # Create indexes for performance
    conn.execute('CREATE INDEX IF NOT EXISTS idx_spend_program ON marketing_spend(program)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_spend_date ON marketing_spend(month_date)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_spend_fiscal ON marketing_spend(fiscal_year)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_totals_program ON marketing_spend_totals(program)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_notes_program_channel ON marketing_incremental_notes(program, channel)')
    
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

def get_current_state(conn):
    """Get current ETL state from database"""
    try:
        state_df = pd.read_sql("SELECT * FROM marketing_etl_state", conn)
        state_dict = {}
        for _, row in state_df.iterrows():
            state_dict[row['fiscal_year']] = {
                'sheet_name': row['sheet_name'],
                'programs': json.loads(row['programs']),
                'channels': json.loads(row['channels']),
                'months': json.loads(row['months']),
                'last_updated': row['last_updated']
            }
        return state_dict
    except:
        return {}

def update_state(conn, fiscal_year, sheet_name, programs, channels, months):
    """Update ETL state in database"""
    conn.execute('''
        INSERT OR REPLACE INTO marketing_etl_state 
        (fiscal_year, sheet_name, programs, channels, months, last_updated)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (
        fiscal_year, 
        sheet_name, 
        json.dumps(sorted(programs)), 
        json.dumps(sorted(channels)), 
        json.dumps(months)
    ))
    conn.commit()

def detect_sheet_structure(df, sheet_name):
    """
    Detect the structure of a sheet dynamically
    Returns: (programs, channels, month_columns, notes_column)
    """
    print(f"\n📊 Analyzing sheet: {sheet_name}")
    
    # Assume first row is headers
    headers = df.iloc[0].tolist()
    
    # Find Program and Channel columns (should be first two)
    program_col = 0  # Column A
    channel_col = 1  # Column B
    
    print(f"   Program column: {headers[program_col]} (Column {program_col})")
    print(f"   Channel column: {headers[channel_col]} (Column {channel_col})")
    
    # Find month columns (start from column 2, exclude notes column)
    month_columns = []
    notes_column = None
    
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    for i, header in enumerate(headers[2:], start=2):  # Start from column 2
        header_str = str(header).strip()
        
        # Check if it's a notes column
        if 'note' in header_str.lower() or 'incremental' in header_str.lower():
            notes_column = i
            print(f"   Notes column: {header_str} (Column {i})")
            continue
        
        # Check if it's a month column
        if any(month in header_str for month in month_names):
            month_name = next((m for m in month_names if m in header_str), header_str)
            month_columns.append((i, month_name, header_str))
            print(f"   Month column: {month_name} (Column {i})")
    
    # Extract unique programs and channels from data
    programs = set()
    channels = set()
    
    for idx in range(1, len(df)):  # Skip header row
        program_val = df.iloc[idx, program_col]
        channel_val = df.iloc[idx, channel_col]
        
        if pd.notna(program_val) and str(program_val).strip():
            standardized = standardize_program_name(str(program_val).strip())
            if standardized:
                programs.add(standardized)
        
        if pd.notna(channel_val) and str(channel_val).strip():
            channels.add(str(channel_val).strip())
    
    print(f"   Programs found: {len(programs)}")
    print(f"   Channels found: {len(channels)}")
    print(f"   Months found: {len(month_columns)}")
    
    return list(programs), list(channels), month_columns, notes_column

def convert_month_to_date(month_name, fiscal_year):
    """Convert month name to proper date based on fiscal year"""
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    if month_name not in month_names:
        return None
    
    month_num = month_names.index(month_name) + 1
    
    # Determine year based on fiscal year and month
    # Fiscal year runs from September to August of the following year
    if fiscal_year == 'FY25':
        if month_name in ['September', 'October', 'November', 'December']:
            year = 2024  # Fall semester of FY25
        else:  # Jan-Aug (Spring/Summer of FY25)
            year = 2025
    elif fiscal_year == 'FY26':
        # Special case: FY26 data only includes August-December 2025
        # August 2025 is the END of FY25, but it's included in FY26 sheet
        if month_name == 'August':
            year = 2025  # August 2025 (end of FY25, but in FY26 sheet)
        elif month_name in ['September', 'October', 'November', 'December']:
            year = 2025  # Fall semester of FY26
        else:  # Jan-July (Spring/Summer of FY26) - not present in current data
            year = 2026
    else:
        # For future fiscal years, extract year from FY format
        try:
            fy_num = int(fiscal_year[2:])  # Get '27' from 'FY27'
            base_year = 2000 + fy_num
            if month_name in ['September', 'October', 'November', 'December']:
                year = base_year - 1  # Fall semester
            else:
                year = base_year  # Spring/Summer semester
        except:
            return None
    
    return f"{year}-{month_num:02d}-01"

def parse_sheet_data(df, sheet_name, fiscal_year):
    """
    Parse data from a single sheet
    Returns: (spend_records, totals_records, notes_records)
    """
    print(f"\n📊 Processing sheet: {sheet_name} ({fiscal_year})")
    
    # Detect sheet structure
    programs, channels, month_columns, notes_column = detect_sheet_structure(df, sheet_name)
    
    if not month_columns:
        print("   ❌ No month columns detected!")
        return [], [], []
    
    spend_records = []
    totals_records = []
    notes_records = []
    current_program = None
    
    # Track notes we've already processed to avoid duplicates
    processed_notes = set()
    
    # Process data rows (skip header row)
    for idx in range(1, len(df)):
        row = df.iloc[idx]
        
        program_cell = str(row[0]).strip() if pd.notna(row[0]) else ''
        channel_cell = str(row[1]).strip() if pd.notna(row[1]) else ''
        
        # Skip completely empty rows
        if not program_cell and not channel_cell:
            continue
        
        # Update current program if we have a new one
        if program_cell and program_cell not in ['', 'nan', 'NaN']:
            current_program = standardize_program_name(program_cell)
            if current_program:
                print(f"   Processing program: {current_program}")
        
        # Skip if no current program
        if not current_program:
            continue
        
        # Process channel data
        if channel_cell and channel_cell not in ['', 'nan', 'NaN']:
            # Check for incremental notes (only once per program-channel-fiscal_year)
            note_key = (current_program, channel_cell, fiscal_year)
            if note_key not in processed_notes and notes_column and pd.notna(row[notes_column]):
                note = str(row[notes_column]).strip()
                if note and note not in ['', 'nan', 'NaN']:
                    notes_records.append({
                        'program': current_program,
                        'channel': channel_cell,
                        'fiscal_year': fiscal_year,
                        'incremental_note': note
                    })
                    processed_notes.add(note_key)
                    print(f"     📝 Note for {current_program} - {channel_cell}: {note[:50]}...")
            
            # Process each month for spend data
            for col_idx, month_name, header_str in month_columns:
                value = row[col_idx]
                month_date = convert_month_to_date(month_name, fiscal_year)
                
                if not month_date:
                    continue
                
                # Parse value - handle various formats
                spend_amount = 0.0
                if pd.notna(value):
                    value_str = str(value).strip().lower()
                    if value_str not in ['', '-', 'no ad spend', 'nan', '0']:
                        try:
                            spend_amount = float(value)
                        except (ValueError, TypeError):
                            spend_amount = 0.0
                
                spend_records.append({
                    'program': current_program,
                    'channel': channel_cell,
                    'fiscal_year': fiscal_year,
                    'month_date': month_date,
                    'spend_amount': spend_amount
                })
    
    # Calculate totals by program and month
    if spend_records:
        spend_df = pd.DataFrame(spend_records)
        totals_df = spend_df.groupby(['program', 'fiscal_year', 'month_date'])['spend_amount'].sum().reset_index()
        
        for _, row in totals_df.iterrows():
            totals_records.append({
                'program': row['program'],
                'fiscal_year': row['fiscal_year'],
                'month_date': row['month_date'],
                'total_spend': row['spend_amount']
            })
    
    print(f"   ✅ Extracted {len(spend_records)} spend records")
    print(f"   ✅ Extracted {len(totals_records)} totals records")
    print(f"   ✅ Extracted {len(notes_records)} incremental notes")
    
    return spend_records, totals_records, notes_records


def load_marketing_spend():
    """Load marketing spend data from the new Excel file with dynamic detection"""
    conn = sqlite3.connect(DB_PATH)
    
    # Get current state
    current_state = get_current_state(conn)
    
    # Read Excel file and get all sheets
    try:
        excel_file = pd.ExcelFile(EXCEL_FILE)
        available_sheets = excel_file.sheet_names
        print(f"\n📋 Available sheets: {available_sheets}")
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        conn.close()
        return
    
    all_spend_records = []
    all_totals_records = []
    all_notes_records = []
    
    # Process each sheet
    for sheet_name in available_sheets:
        try:
            # Determine fiscal year from sheet name
            if 'FY25' in sheet_name.upper():
                fiscal_year = 'FY25'
            elif 'FY26' in sheet_name.upper():
                fiscal_year = 'FY26'
            else:
                # Try to extract FY from sheet name (e.g., "FY27", "27", etc.)
                import re
                fy_match = re.search(r'(?:FY)?(\d{2})', sheet_name.upper())
                if fy_match:
                    fiscal_year = f"FY{fy_match.group(1)}"
                else:
                    print(f"⚠️ Cannot determine fiscal year for sheet: {sheet_name}")
                    continue
            
            print(f"\n📊 Processing sheet: {sheet_name} → {fiscal_year}")
            
            # Read sheet data
            df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name, header=None)
            
            # Detect current structure
            programs, channels, month_columns, notes_column = detect_sheet_structure(df, sheet_name)
            
            # Check if this is new or changed
            is_new_or_changed = True
            if fiscal_year in current_state:
                old_state = current_state[fiscal_year]
                if (set(programs) == set(old_state['programs']) and 
                    set(channels) == set(old_state['channels']) and
                    len(month_columns) == len(old_state['months'])):
                    print(f"   ℹ️ No changes detected for {fiscal_year}")
                    is_new_or_changed = False
            
            if is_new_or_changed:
                print(f"   🔄 Processing changes for {fiscal_year}")
                
                # Parse the sheet data
                spend_records, totals_records, notes_records = parse_sheet_data(df, sheet_name, fiscal_year)
                
                all_spend_records.extend(spend_records)
                all_totals_records.extend(totals_records)
                all_notes_records.extend(notes_records)
                
                # Update state
                month_list = [f"{month_name}:{header}" for _, month_name, header in month_columns]
                update_state(conn, fiscal_year, sheet_name, programs, channels, month_list)
            
        except Exception as e:
            print(f"❌ Error processing sheet {sheet_name}: {e}")
            continue
    
    if not all_spend_records and not all_totals_records and not all_notes_records:
        print("ℹ️ No new data to load")
        conn.close()
        return
    
    # Load spend data to database (INSERT OR REPLACE for updates)
    if all_spend_records:
        print(f"\n💾 Loading {len(all_spend_records)} spend records to database...")
        for record in all_spend_records:
            conn.execute('''
                INSERT OR REPLACE INTO marketing_spend 
                (program, channel, fiscal_year, month_date, spend_amount)
                VALUES (?, ?, ?, ?, ?)
            ''', (record['program'], record['channel'], record['fiscal_year'], 
                  record['month_date'], record['spend_amount']))
    
    # Load totals data to database
    if all_totals_records:
        print(f"💾 Loading {len(all_totals_records)} totals records to database...")
        for record in all_totals_records:
            conn.execute('''
                INSERT OR REPLACE INTO marketing_spend_totals 
                (program, fiscal_year, month_date, total_spend)
                VALUES (?, ?, ?, ?)
            ''', (record['program'], record['fiscal_year'], record['month_date'], record['total_spend']))
    
    # Load notes data to database (separate table)
    if all_notes_records:
        print(f"💾 Loading {len(all_notes_records)} incremental notes to database...")
        for record in all_notes_records:
            conn.execute('''
                INSERT OR REPLACE INTO marketing_incremental_notes 
                (program, channel, fiscal_year, incremental_note)
                VALUES (?, ?, ?, ?)
            ''', (record['program'], record['channel'], record['fiscal_year'], record['incremental_note']))
    
    conn.commit()
    
    print(f"\n✅ Successfully loaded:")
    print(f"   • {len(all_spend_records)} spend records")
    print(f"   • {len(all_totals_records)} totals records")
    print(f"   • {len(all_notes_records)} incremental notes")
    
    # Show summary if we have data
    if all_spend_records:
        df_spend = pd.DataFrame(all_spend_records)
        
        print("\n📊 Summary by Program:")
        summary = df_spend.groupby('program')['spend_amount'].agg(['count', 'sum']).round(2)
        summary.columns = ['Records', 'Total Spend ($)']
        print(summary.to_string())
        
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
    
    # Check for incremental notes (separate table now)
    try:
        notes_count = pd.read_sql(
            "SELECT COUNT(*) as count FROM marketing_incremental_notes",
            conn
        )['count'].iloc[0]
        print(f"\n✅ Incremental notes: {notes_count} unique program-channel combinations")
        
        # Show sample notes
        sample_notes = pd.read_sql(
            "SELECT program, channel, fiscal_year, LEFT(incremental_note, 50) as note_preview FROM marketing_incremental_notes LIMIT 5",
            conn
        )
        if not sample_notes.empty:
            print("\n📝 Sample incremental notes:")
            for _, row in sample_notes.iterrows():
                print(f"   • {row['program']} - {row['channel']} ({row['fiscal_year']}): {row['note_preview']}...")
    except:
        print("\n✅ Incremental notes: 0 (table may not exist yet)")
    
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
    print("🚀 Marketing Data ETL Pipeline - Enhanced Dynamic Version")
    print("=" * 80)
    print(f"📁 Source file: {EXCEL_FILE}")
    
    # Step 1: Create tables
    create_marketing_tables()
    
    # Step 2: Load marketing spend data (with dynamic detection)
    load_marketing_spend()
    
    # Step 3: Validate data
    validate_data()
    
    # Step 4: Update metadata
    update_metadata()
    
    print("\n" + "=" * 80)
    print("✅ Marketing ETL Complete!")
    print("=" * 80)
    print("\n💡 Enhanced Features:")
    print("   ✅ Dynamic sheet detection (FY25, FY26, FY27+)")
    print("   ✅ Flexible month column detection")
    print("   ✅ State tracking for incremental updates")
    print("   ✅ Automatic program name standardization")
    print("   ✅ Smart change detection")
    print("   ✅ Separate incremental notes table (no duplication)")
    print("   ✅ Month-wise spend tracking")
    print("   ✅ Robust error handling")
    print("\n💡 Next steps:")
    print("   1. Run main_app.py to view the dashboard")
    print("   2. Check Data Explorer for updated tables:")
    print("      • marketing_spend (channel-level, month-wise)")
    print("      • marketing_spend_totals (program-level, month-wise)")
    print("      • marketing_incremental_notes (program-channel notes)")
    print("      • marketing_etl_state (tracking)")
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
