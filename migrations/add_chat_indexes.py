"""
Migration: Add indexes for chat performance optimization
"""

import sqlite3
import sys


def add_chat_indexes(db_path='edulytix.db'):
    """Add indexes for common chat query patterns."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Adding chat performance indexes...")
        
        # Index for chat history queries by user and conversation
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_history_user_conversation 
            ON chat_history(user_id, conversation_id, timestamp DESC)
        """)
        print("✅ Added index: idx_chat_history_user_conversation")
        
        # Index for chat history queries by user only
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_history_user_timestamp 
            ON chat_history(user_id, timestamp DESC)
        """)
        print("✅ Added index: idx_chat_history_user_timestamp")
        
        # Index for chat metrics queries by user
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_metrics_user_timestamp 
            ON chat_metrics(user_id, timestamp DESC)
        """)
        print("✅ Added index: idx_chat_metrics_user_timestamp")
        
        # Index for chat metrics queries by query type
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_metrics_query_type 
            ON chat_metrics(query_type, timestamp DESC)
        """)
        print("✅ Added index: idx_chat_metrics_query_type")
        
        # Index for admissions_metrics common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_admissions_program_metric_year 
            ON admissions_metrics(program, metric_name, cohort_year, report_date DESC)
        """)
        print("✅ Added index: idx_admissions_program_metric_year")
        
        # Index for marketing_spend queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_marketing_program_date 
            ON marketing_spend(program, month_date DESC)
        """)
        print("✅ Added index: idx_marketing_program_date")
        
        conn.commit()
        print("\n✅ All indexes added successfully!")
        
        # Analyze query performance
        print("\n📊 Analyzing index effectiveness...")
        
        # Test query performance
        test_queries = [
            ("Chat history by user", "SELECT * FROM chat_history WHERE user_id = 1 ORDER BY timestamp DESC LIMIT 10"),
            ("Chat metrics by user", "SELECT * FROM chat_metrics WHERE user_id = 1 ORDER BY timestamp DESC LIMIT 10"),
            ("Admissions by program", "SELECT * FROM admissions_metrics WHERE program = 'MBA' AND metric_name = 'total_applications' ORDER BY report_date DESC LIMIT 10")
        ]
        
        for name, query in test_queries:
            cursor.execute(f"EXPLAIN QUERY PLAN {query}")
            plan = cursor.fetchall()
            uses_index = any('INDEX' in str(row) for row in plan)
            print(f"   {name}: {'✅ Uses index' if uses_index else '⚠️  No index'}")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error adding indexes: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


def rollback_indexes(db_path='edulytix.db'):
    """Remove added indexes."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Removing chat performance indexes...")
        
        indexes = [
            'idx_chat_history_user_conversation',
            'idx_chat_history_user_timestamp',
            'idx_chat_metrics_user_timestamp',
            'idx_chat_metrics_query_type',
            'idx_admissions_program_metric_year',
            'idx_marketing_program_date'
        ]
        
        for index in indexes:
            cursor.execute(f"DROP INDEX IF EXISTS {index}")
            print(f"✅ Removed index: {index}")
        
        conn.commit()
        print("\n✅ All indexes removed successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error removing indexes: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        rollback_indexes()
    else:
        add_chat_indexes()
