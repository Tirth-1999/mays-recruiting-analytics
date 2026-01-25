"""
Migration: Add users table for Google OAuth authentication
Created: January 24, 2026
"""
import sqlite3
from datetime import datetime


def upgrade():
    """Add users table to database"""
    conn = sqlite3.connect('edulytix.db')
    cursor = conn.cursor()
    
    try:
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                google_id TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                profile_picture_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                preferences TEXT
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        
        conn.commit()
        print("✅ Users table created successfully")
        print("✅ Indexes created on google_id and email")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating users table: {e}")
        raise
    
    finally:
        conn.close()


def downgrade():
    """Remove users table (rollback)"""
    conn = sqlite3.connect('edulytix.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('DROP TABLE IF EXISTS users')
        conn.commit()
        print("✅ Users table dropped successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error dropping users table: {e}")
        raise
    
    finally:
        conn.close()


if __name__ == '__main__':
    print("Running migration: Add users table")
    print("-" * 50)
    upgrade()
    print("-" * 50)
    print("Migration completed!")
