"""
Migration: Add chat_history table for AI chatbot assistant
Created: January 25, 2026
Description: Creates chat_history table to store user conversations with the AI assistant
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path to import database utilities
sys.path.append(str(Path(__file__).parent.parent))

def migrate_up(db_path='edulytix.db'):
    """Create chat_history table and indexes."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create chat_history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                conversation_id TEXT NOT NULL,
                message TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tokens_used INTEGER DEFAULT 0,
                query_type TEXT,
                sql_query TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_chat_user 
            ON chat_history(user_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_chat_conversation 
            ON chat_history(conversation_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_chat_timestamp 
            ON chat_history(timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_chat_user_conversation 
            ON chat_history(user_id, conversation_id)
        ''')
        
        conn.commit()
        print("✅ Migration successful: chat_history table created")
        print("   - Table: chat_history")
        print("   - Indexes: idx_chat_user, idx_chat_conversation, idx_chat_timestamp, idx_chat_user_conversation")
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    
    finally:
        conn.close()

def migrate_down(db_path='edulytix.db'):
    """Rollback: Drop chat_history table and indexes."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Drop indexes first
        cursor.execute('DROP INDEX IF EXISTS idx_chat_user_conversation')
        cursor.execute('DROP INDEX IF EXISTS idx_chat_timestamp')
        cursor.execute('DROP INDEX IF EXISTS idx_chat_conversation')
        cursor.execute('DROP INDEX IF EXISTS idx_chat_user')
        
        # Drop table
        cursor.execute('DROP TABLE IF EXISTS chat_history')
        
        conn.commit()
        print("✅ Rollback successful: chat_history table dropped")
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"❌ Rollback failed: {e}")
        raise
    
    finally:
        conn.close()

def verify_migration(db_path='edulytix.db'):
    """Verify the migration was successful."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='chat_history'
        ''')
        table_exists = cursor.fetchone() is not None
        
        # Check if indexes exist
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='chat_history'
        ''')
        indexes = [row[0] for row in cursor.fetchall()]
        
        print("\n📊 Migration Verification:")
        print(f"   Table exists: {'✅' if table_exists else '❌'}")
        print(f"   Indexes created: {len(indexes)}")
        for idx in indexes:
            print(f"      - {idx}")
        
        # Get table schema
        if table_exists:
            cursor.execute('PRAGMA table_info(chat_history)')
            columns = cursor.fetchall()
            print(f"\n   Columns ({len(columns)}):")
            for col in columns:
                print(f"      - {col[1]} ({col[2]})")
        
        return table_exists and len(indexes) >= 4
        
    finally:
        conn.close()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate chat_history table')
    parser.add_argument('action', choices=['up', 'down', 'verify'], 
                       help='Migration action: up (create), down (drop), verify (check)')
    parser.add_argument('--db', default='edulytix.db', 
                       help='Database path (default: edulytix.db)')
    
    args = parser.parse_args()
    
    if args.action == 'up':
        migrate_up(args.db)
        verify_migration(args.db)
    elif args.action == 'down':
        migrate_down(args.db)
    elif args.action == 'verify':
        success = verify_migration(args.db)
        sys.exit(0 if success else 1)
