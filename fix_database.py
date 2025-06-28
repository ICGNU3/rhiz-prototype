#!/usr/bin/env python3

import sqlite3
import uuid

def fix_database():
    """Fix the database by ensuring proper user IDs and associations"""
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    try:
        # Fix the users table - update NULL IDs to proper UUIDs
        print("Fixing user IDs...")
        
        # Update the demo user to have a proper UUID
        cursor.execute("UPDATE users SET id = ? WHERE email = ?", ('demo_user', 'demo@rhiz.app'))
        cursor.execute("UPDATE users SET id = ? WHERE email = ?", ('2', 'demo_user'))
        
        # Update all associated records to use the correct user_id
        print("Updating associated records...")
        
        # Update goals to use the demo_user ID
        cursor.execute("UPDATE goals SET user_id = ? WHERE user_id = ?", ('demo_user', '2'))
        
        # Update contacts to use the demo_user ID
        cursor.execute("UPDATE contacts SET user_id = ? WHERE user_id = ?", ('demo_user', '2'))
        
        # Update ai_suggestions to use the demo_user ID
        cursor.execute("UPDATE ai_suggestions SET user_id = ? WHERE user_id = ?", ('demo_user', '2'))
        
        # Update contact_interactions to use the demo_user ID
        cursor.execute("UPDATE contact_interactions SET user_id = ? WHERE user_id = ?", ('demo_user', '2'))
        
        conn.commit()
        
        # Verify the fix
        print("Verifying fix...")
        users = cursor.execute('SELECT id, email FROM users').fetchall()
        print("Users:", users)
        
        goals = cursor.execute('SELECT DISTINCT user_id FROM goals').fetchall()
        print("Goal user_ids:", [g[0] for g in goals])
        
        contacts = cursor.execute('SELECT DISTINCT user_id FROM contacts').fetchall()
        print("Contact user_ids:", [c[0] for c in contacts])
        
        print("Database fixed successfully!")
        
    except Exception as e:
        print(f"Error fixing database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database()