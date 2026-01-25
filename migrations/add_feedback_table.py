"""
Migration: Add feedback table for user response ratings
"""

import sqlite3
import sys


def add_feedback_table(db_path='edulytix.db'):
    """Create feedback table for chat responses."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Creating feedback table...")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_feedback (
                feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                conversation_id TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK(rating IN (-1, 1)),
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (chat_id) REFERENCES chat_history(chat_id)
            )
        """)
        print("✅ Created table: chat_feedback")
        
        # Add index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_user 
            ON chat_feedback(user_id, created_at DESC)
        """)
        print("✅ Added index: idx_feedback_user")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_feedback_rating 
            ON chat_feedback(rating, created_at DESC)
        """)
        print("✅ Added index: idx_feedback_rating")
        
        conn.commit()
        print("\n✅ Feedback table created successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error creating feedback table: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


def rollback_feedback_table(db_path='edulytix.db'):
    """Remove feedback table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("Removing feedback table...")
        
        cursor.execute("DROP TABLE IF EXISTS chat_feedback")
        print("✅ Removed table: chat_feedback")
        
        conn.commit()
        print("\n✅ Feedback table removed successfully!")
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error removing feedback table: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        rollback_feedback_table()
    else:
        add_feedback_table()
