"""
Authentication and subscription management for Founder Network AI
Handles user signup, magic links, Google OAuth, and tier enforcement
"""

import sqlite3
import uuid
import secrets
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import os

class AuthManager:
    def __init__(self, db):
        self.db = db
    
    def create_user(self, email: str, google_id: str = None, subscription_tier: str = 'explorer') -> Optional[str]:
        """Create a new user with email or Google authentication"""
        user_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        try:
            conn.execute(
                """INSERT INTO users 
                   (id, email, google_id, subscription_tier, subscription_status, created_at, updated_at) 
                   VALUES (?, ?, ?, ?, 'active', datetime('now'), datetime('now'))""",
                (user_id, email, google_id, subscription_tier)
            )
            conn.commit()
            logging.info(f"Created user: {user_id} with tier: {subscription_tier}")
            return user_id
        except sqlite3.IntegrityError:
            # User already exists
            logging.warning(f"User creation failed - email already exists: {email}")
            return None
        except Exception as e:
            logging.error(f"Failed to create user: {e}")
            return None
        finally:
            conn.close()
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address"""
        conn = self.db.get_connection()
        try:
            user = conn.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            ).fetchone()
            return dict(user) if user else None
        finally:
            conn.close()
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        conn = self.db.get_connection()
        try:
            user = conn.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()
            return dict(user) if user else None
        finally:
            conn.close()
    
    def create_magic_link(self, email: str) -> str:
        """Create a magic link token for passwordless authentication"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(minutes=15)  # 15 minute expiry
        
        conn = self.db.get_connection()
        try:
            # Clean up old tokens for this email
            conn.execute("DELETE FROM magic_links WHERE email = ?", (email,))
            
            # Create new token
            conn.execute(
                """INSERT INTO magic_links (id, email, token, expires_at) 
                   VALUES (?, ?, ?, ?)""",
                (str(uuid.uuid4()), email, token, expires_at)
            )
            conn.commit()
            return token
        finally:
            conn.close()
    
    def verify_magic_link(self, token: str) -> Optional[str]:
        """Verify magic link token and return email if valid"""
        conn = self.db.get_connection()
        try:
            link = conn.execute(
                """SELECT email FROM magic_links 
                   WHERE token = ? AND expires_at > datetime('now') AND used = FALSE""",
                (token,)
            ).fetchone()
            
            if link:
                # Mark token as used
                conn.execute(
                    "UPDATE magic_links SET used = TRUE WHERE token = ?",
                    (token,)
                )
                conn.commit()
                return link['email']
            return None
        finally:
            conn.close()
    
    def create_guest_session(self) -> str:
        """Create a guest session for unauthenticated users"""
        session_token = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(hours=24)  # 24 hour guest session
        
        conn = self.db.get_connection()
        try:
            conn.execute(
                """INSERT INTO guest_sessions (id, session_token, expires_at) 
                   VALUES (?, ?, ?)""",
                (str(uuid.uuid4()), session_token, expires_at)
            )
            conn.commit()
            return session_token
        finally:
            conn.close()
    
    def get_guest_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get guest session data"""
        conn = self.db.get_connection()
        try:
            session = conn.execute(
                """SELECT * FROM guest_sessions 
                   WHERE session_token = ? AND expires_at > datetime('now')""",
                (session_token,)
            ).fetchone()
            return dict(session) if session else None
        finally:
            conn.close()
    
    def increment_guest_action(self, session_token: str, action_type: str = 'general'):
        """Increment guest action counter"""
        conn = self.db.get_connection()
        try:
            if action_type == 'goal':
                conn.execute(
                    "UPDATE guest_sessions SET goals_created = goals_created + 1, actions_count = actions_count + 1 WHERE session_token = ?",
                    (session_token,)
                )
            elif action_type == 'contact':
                conn.execute(
                    "UPDATE guest_sessions SET contacts_added = contacts_added + 1, actions_count = actions_count + 1 WHERE session_token = ?",
                    (session_token,)
                )
            else:
                conn.execute(
                    "UPDATE guest_sessions SET actions_count = actions_count + 1 WHERE session_token = ?",
                    (session_token,)
                )
            conn.commit()
        finally:
            conn.close()

class SubscriptionManager:
    """Manage subscription tiers and usage limits"""
    
    TIER_LIMITS = {
        'explorer': {
            'max_goals': 1,
            'max_contacts': 50,
            'max_ai_suggestions': 3,
            'features': ['basic_goals', 'basic_contacts', 'limited_ai'],
            'price_monthly': 0,
            'price_yearly': 0
        },
        'founder_plus': {
            'max_goals': -1,  # Unlimited
            'max_contacts': 1000,
            'max_ai_suggestions': -1,  # Unlimited
            'features': ['unlimited_goals', 'advanced_contacts', 'unlimited_ai', 'email_integration', 
                        'calendar_sync', 'network_map', 'analytics', 'conference_mode', 'gamification'],
            'price_monthly': 1900,  # $19.00 in cents
            'price_yearly': 18000   # $180.00 in cents
        }
    }
    
    def __init__(self, db):
        self.db = db
    
    def check_usage_limit(self, user_id: str, action_type: str) -> bool:
        """Check if user can perform action based on their tier limits"""
        user = self.get_user_with_usage(user_id)
        if not user:
            return False
        
        tier = user['subscription_tier']
        limits = self.TIER_LIMITS.get(tier, self.TIER_LIMITS['explorer'])
        
        if action_type == 'goal_creation':
            if limits['max_goals'] == -1:
                return True
            return user['goals_count'] < limits['max_goals']
        
        elif action_type == 'contact_import':
            if limits['max_contacts'] == -1:
                return True
            return user['contacts_count'] < limits['max_contacts']
        
        elif action_type == 'ai_suggestion':
            if limits['max_ai_suggestions'] == -1:
                return True
            return user['ai_suggestions_used'] < limits['max_ai_suggestions']
        
        return True
    
    def has_feature_access(self, user_id: str, feature: str) -> bool:
        """Check if user has access to a specific feature"""
        user = self.get_user_with_usage(user_id)
        if not user:
            return False
        
        tier = user['subscription_tier']
        limits = self.TIER_LIMITS.get(tier, self.TIER_LIMITS['explorer'])
        
        return feature in limits['features']
    
    def track_usage(self, user_id: str, action_type: str, metadata: Dict = None):
        """Track user action and update usage counters"""
        conn = self.db.get_connection()
        try:
            # Log usage tracking
            conn.execute(
                """INSERT INTO usage_tracking (id, user_id, action_type, metadata) 
                   VALUES (?, ?, ?, ?)""",
                (str(uuid.uuid4()), user_id, action_type, json.dumps(metadata or {}))
            )
            
            # Update user counters
            if action_type == 'goal_created':
                conn.execute(
                    "UPDATE users SET goals_count = goals_count + 1, updated_at = datetime('now') WHERE id = ?",
                    (user_id,)
                )
            elif action_type == 'contact_imported':
                conn.execute(
                    "UPDATE users SET contacts_count = contacts_count + 1, updated_at = datetime('now') WHERE id = ?",
                    (user_id,)
                )
            elif action_type == 'ai_suggestion_generated':
                conn.execute(
                    "UPDATE users SET ai_suggestions_used = ai_suggestions_used + 1, updated_at = datetime('now') WHERE id = ?",
                    (user_id,)
                )
            
            conn.commit()
        finally:
            conn.close()
    
    def get_user_with_usage(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user with current usage statistics"""
        conn = self.db.get_connection()
        try:
            user = conn.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,)
            ).fetchone()
            return dict(user) if user else None
        finally:
            conn.close()
    
    def upgrade_user_subscription(self, user_id: str, new_tier: str, stripe_customer_id: str = None, 
                                stripe_subscription_id: str = None):
        """Upgrade user to a higher subscription tier"""
        conn = self.db.get_connection()
        try:
            old_user = conn.execute("SELECT subscription_tier FROM users WHERE id = ?", (user_id,)).fetchone()
            old_tier = old_user['subscription_tier'] if old_user else 'explorer'
            
            # Update user subscription
            conn.execute(
                """UPDATE users SET 
                   subscription_tier = ?, stripe_customer_id = ?, stripe_subscription_id = ?, 
                   subscription_status = 'active', updated_at = datetime('now')
                   WHERE id = ?""",
                (new_tier, stripe_customer_id, stripe_subscription_id, user_id)
            )
            
            # Log subscription history
            conn.execute(
                """INSERT INTO subscription_history (id, user_id, action, from_tier, to_tier) 
                   VALUES (?, ?, 'upgraded', ?, ?)""",
                (str(uuid.uuid4()), user_id, old_tier, new_tier)
            )
            
            conn.commit()
            logging.info(f"Upgraded user {user_id} from {old_tier} to {new_tier}")
        finally:
            conn.close()
    
    def get_tier_info(self, tier: str) -> Dict[str, Any]:
        """Get information about a subscription tier"""
        return self.TIER_LIMITS.get(tier, self.TIER_LIMITS['explorer'])
    
    def get_usage_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive usage summary for user"""
        user = self.get_user_with_usage(user_id)
        if not user:
            return {}
        
        tier_info = self.get_tier_info(user['subscription_tier'])
        
        return {
            'tier': user['subscription_tier'],
            'tier_display': 'Explorer' if user['subscription_tier'] == 'explorer' else 'Founder+',
            'goals_used': user['goals_count'],
            'goals_limit': tier_info['max_goals'],
            'contacts_used': user['contacts_count'],
            'contacts_limit': tier_info['max_contacts'],
            'ai_suggestions_used': user['ai_suggestions_used'],
            'ai_suggestions_limit': tier_info['max_ai_suggestions'],
            'features': tier_info['features'],
            'can_upgrade': user['subscription_tier'] == 'explorer'
        }

class EmailService:
    """Handle magic link email sending"""
    
    def __init__(self):
        self.from_email = "noreply@founder-network.ai"
    
    def send_magic_link(self, to_email: str, magic_token: str, base_url: str = None) -> bool:
        """Send magic link email for passwordless authentication"""
        if not base_url:
            base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
        
        magic_url = f"{base_url}/auth/verify?token={magic_token}"
        
        subject = "Sign in to Founder Network AI"
        html_content = f"""
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #6366f1;">Welcome to Founder Network AI</h2>
                <p>Click the button below to sign in to your account:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{magic_url}" style="background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; display: inline-block; font-weight: 600;">
                        Sign In
                    </a>
                </div>
                <p style="color: #666; font-size: 14px;">This link will expire in 15 minutes. If you didn't request this, you can safely ignore this email.</p>
                <p style="color: #666; font-size: 14px;">Or copy and paste this URL into your browser:<br>
                <a href="{magic_url}" style="color: #6366f1;">{magic_url}</a></p>
            </div>
        </body>
        </html>
        """
        
        try:
            # For now, log the magic link (in production, use SendGrid or similar)
            logging.info(f"Magic link for {to_email}: {magic_url}")
            print(f"MAGIC LINK: {magic_url}")  # Development convenience
            return True
        except Exception as e:
            logging.error(f"Failed to send magic link email: {e}")
            return False