#!/usr/bin/env python3
"""
Script to add an authorized user to the Rhiz platform
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Database
from auth import AuthManager

def add_authorized_user():
    """Add isrealdeep@gmail.com as an authorized user"""
    db = Database()
    auth_manager = AuthManager(db)
    
    email = "isrealdeep@gmail.com"
    
    # Check if user already exists
    existing_user = auth_manager.get_user_by_email(email)
    if existing_user:
        print(f"User {email} already exists with ID: {existing_user['id']}")
        current_tier = existing_user.get('subscription_tier', 'explorer')
        print(f"Current subscription tier: {current_tier}")
        
        # Upgrade to founder_plus if not already
        if current_tier != 'founder_plus':
            conn = db.get_connection()
            try:
                conn.execute(
                    "UPDATE users SET subscription_tier = 'founder_plus', updated_at = datetime('now') WHERE email = ?",
                    (email,)
                )
                conn.commit()
                print(f"Upgraded {email} to founder_plus tier with full platform access")
            except Exception as e:
                print(f"Failed to upgrade user: {e}")
                return False
            finally:
                conn.close()
        else:
            print("User already has founder_plus tier")
        return True
    
    # Create new user with founder_plus tier for full access
    user_id = auth_manager.create_user(
        email=email,
        subscription_tier='founder_plus'  # Full access tier
    )
    
    if user_id:
        print(f"Successfully created user {email} with ID: {user_id}")
        print("User has founder_plus tier with full platform access")
        return True
    else:
        print(f"Failed to create user {email}")
        return False

if __name__ == "__main__":
    success = add_authorized_user()
    sys.exit(0 if success else 1)