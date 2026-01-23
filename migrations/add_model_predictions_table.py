"""
Database migration script to add model_predictions table.
This table tracks predictions for validation and performance monitoring.
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.database import get_connection


def create_model_predictions_table():
    """
    Create the model_predictions table for tracking ML predictions.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create model_predictions table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS model_predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_type TEXT NOT NULL,
        program TEXT NOT NULL,
        cohort TEXT,
        prediction_date TEXT NOT NULL,
        forecast_date TEXT NOT NULL,
        metric TEXT NOT NULL,
        predicted_value REAL NOT NULL,
        lower_bound REAL,
        upper_bound REAL,
        actual_value REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    cursor.execute(create_table_sql)
    
    # Create indexes for common queries
    create_index_sql = [
        """
        CREATE INDEX IF NOT EXISTS idx_model_predictions_model_metric 
        ON model_predictions(model_type, metric);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_model_predictions_program 
        ON model_predictions(program, forecast_date);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_model_predictions_dates 
        ON model_predictions(prediction_date, forecast_date);
        """
    ]
    
    for index_sql in create_index_sql:
        cursor.execute(index_sql)
    
    conn.commit()
    print("✓ Successfully created model_predictions table and indexes")
    
    # Verify table creation
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='model_predictions';
    """)
    
    if cursor.fetchone():
        print("✓ Table verification successful")
        
        # Show table schema
        cursor.execute("PRAGMA table_info(model_predictions);")
        columns = cursor.fetchall()
        print("\nTable schema:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
    else:
        print("✗ Table verification failed")
        return False
    
    conn.close()
    return True


def rollback_migration():
    """
    Rollback the migration by dropping the model_predictions table.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS model_predictions;")
    conn.commit()
    
    print("✓ Successfully rolled back migration (dropped model_predictions table)")
    conn.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage model_predictions table migration')
    parser.add_argument(
        'action',
        choices=['migrate', 'rollback'],
        help='Action to perform: migrate (create table) or rollback (drop table)'
    )
    
    args = parser.parse_args()
    
    if args.action == 'migrate':
        print("Running migration: Creating model_predictions table...")
        success = create_model_predictions_table()
        sys.exit(0 if success else 1)
    elif args.action == 'rollback':
        print("Rolling back migration: Dropping model_predictions table...")
        rollback_migration()
        sys.exit(0)
