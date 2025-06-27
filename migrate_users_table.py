#!/usr/bin/env python3
"""
Migration script to update users table with authentication columns
"""
import sqlite3
import sys

def migrate_users_table():
    """Add missing authentication columns to users table"""
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Check current structure
        cursor.execute('PRAGMA table_info(users)')
        existing_columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns: {existing_columns}")
        
        # Define required columns
        required_columns = [
            ('google_id', 'TEXT'),
            ('magic_link_token', 'TEXT'),
            ('magic_link_expires', 'TIMESTAMP'),
            ('subscription_tier', 'TEXT DEFAULT "explorer"'),
            ('stripe_customer_id', 'TEXT'),
            ('stripe_subscription_id', 'TEXT'),
            ('subscription_status', 'TEXT DEFAULT "active"'),
            ('subscription_expires', 'TIMESTAMP'),
            ('goals_count', 'INTEGER DEFAULT 0'),
            ('contacts_count', 'INTEGER DEFAULT 0'),
            ('ai_suggestions_used', 'INTEGER DEFAULT 0'),
            ('is_guest', 'BOOLEAN DEFAULT FALSE'),
            ('guest_actions_count', 'INTEGER DEFAULT 0'),
            ('updated_at', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        ]
        
        # Add missing columns
        for column_name, column_definition in required_columns:
            if column_name not in existing_columns:
                alter_sql = f'ALTER TABLE users ADD COLUMN {column_name} {column_definition}'
                try:
                    cursor.execute(alter_sql)
                    print(f"✓ Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    print(f"✗ Error adding {column_name}: {e}")
            else:
                print(f"  Column already exists: {column_name}")
        
        # Commit changes
        conn.commit()
        
        # Verify final structure
        cursor.execute('PRAGMA table_info(users)')
        final_columns = [column[1] for column in cursor.fetchall()]
        print(f"\nFinal columns: {final_columns}")
        
        conn.close()
        print("\nDatabase migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_users_table()
    sys.exit(0 if success else 1)