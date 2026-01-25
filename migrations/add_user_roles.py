"""
Migration: Add role field to users table
Created: January 24, 2026
"""
import sqlite3
from datetime import datetime


def upgrade():
    """Add role field to users table and set first user as admin"""
    conn = sqlite3.connect('edulytix.db')
    cursor = conn.cursor()
    
    try:
        # Check if role column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'role' not in columns:
            # Add role column
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
            print("✅ Added 'role' column to users table")
            
            # Create index on role
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
            print("✅ Created index on role column")
            
            # Set first user as admin
            cursor.execute("SELECT user_id, email FROM users ORDER BY created_at LIMIT 1")
            first_user = cursor.fetchone()
            
            if first_user:
                cursor.execute("UPDATE users SET role = 'admin' WHERE user_id = ?", (first_user[0],))
                print(f"✅ Set first user ({first_user[1]}) as admin")
            
            conn.commit()
            print("✅ Migration completed successfully")
        else:
            print("ℹ️  Role column already exists, skipping migration")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    
    finally:
        conn.close()


def downgrade():
    """Remove role field from users table (not recommended)"""
    conn = sqlite3.connect('edulytix.db')
    cursor = conn.cursor()
    
    try:
        # SQLite doesn't support DROP COLUMN directly
        # We need to recreate the table without the role column
        print("⚠️  Downgrade not implemented for SQLite")
        print("⚠️  To remove role column, you would need to recreate the table")
        
    finally:
        conn.close()


if __name__ == '__main__':
    print("Running migration: Add user roles")
    print("-" * 50)
    upgrade()
    print("-" * 50)
    print("Migration completed!")
