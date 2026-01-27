"""
Migration: Update program names to official display names
Run this once to standardize all program names in the database
"""
import sqlite3
import sys
sys.path.append('.')
from utils.program_mapping import PROGRAM_CODE_TO_NAME

def update_programs_table():
    """Update the programs lookup table with official names"""
    conn = sqlite3.connect('edulytix.db')
    
    print("🔄 Updating programs table...")
    
    for code, name in PROGRAM_CODE_TO_NAME.items():
        conn.execute('''
            UPDATE programs 
            SET program_name = ? 
            WHERE program_code = ?
        ''', (name, code))
        print(f"   ✅ {code} → {name}")
    
    conn.commit()
    
    # Verify
    cursor = conn.execute('SELECT program_code, program_name FROM programs ORDER BY program_code')
    print("\n📊 Updated programs table:")
    for row in cursor:
        print(f"   {row[0]:10} → {row[1]}")
    
    conn.close()
    print("\n✅ Programs table updated successfully")

if __name__ == '__main__':
    update_programs_table()
