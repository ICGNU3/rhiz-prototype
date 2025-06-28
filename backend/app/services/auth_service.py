"""
Authentication service integrating modernized User model with existing auth system
"""
import os
import uuid
import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
try:
    from backend.app.core.database import db
    from backend.app.models.user import User
    from backend.app.core.exceptions import AuthenticationError, ValidationError
    modern_db_available = True
except ImportError:
    # Fallback to existing Flask app database
    from app import db
    modern_db_available = False
    
    # Create simplified User model for compatibility
    class User:
        def __init__(self, id, email, **kwargs):
            self.id = id
            self.email = email
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    class AuthenticationError(Exception):
        pass
    
    class ValidationError(Exception):
        pass

class ModernAuthService:
    """Modern authentication service using SQLAlchemy User model"""
    
    def __init__(self):
        self.magic_link_expiry = timedelta(minutes=30)
        self._magic_links = {}  # In-memory store for demo, should use Redis in production
    
    def create_user(self, email: str, google_id: str = None, subscription_tier: str = 'explorer') -> Optional[User]:
        """Create a new user with database compatibility"""
        try:
            # Check if user already exists
            existing_user = self.get_user_by_email(email)
            if existing_user:
                logging.warning(f"User creation failed - email already exists: {email}")
                return existing_user
            
            if modern_db_available:
                # Use modernized model
                user = User.create_user(
                    email=email,
                    google_id=google_id,
                    subscription_tier=subscription_tier
                )
            else:
                # Use direct database access for compatibility
                import sqlite3
                user_id = str(uuid.uuid4())
                
                # Get the database path from app config
                with db.engine.connect() as conn:
                    conn.execute(
                        """INSERT OR IGNORE INTO users 
                           (id, email, google_id, subscription_tier, subscription_status, created_at, updated_at) 
                           VALUES (?, ?, ?, ?, 'active', datetime('now'), datetime('now'))""",
                        (user_id, email, google_id, subscription_tier)
                    )
                    conn.commit()
                
                # Create user object
                user = User(id=user_id, email=email, google_id=google_id, 
                           subscription_tier=subscription_tier, subscription_status='active')
            
            logging.info(f"Created user: {user.id} with tier: {subscription_tier}")
            return user
            
        except Exception as e:
            logging.error(f"Failed to create user: {e}")
            # Return None instead of raising exception for graceful fallback
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email with database compatibility"""
        try:
            if modern_db_available:
                return User.get_by_email(email)
            else:
                # Use direct database access
                with db.engine.connect() as conn:
                    result = conn.execute(
                        "SELECT * FROM users WHERE email = ?",
                        (email,)
                    ).fetchone()
                    
                    if result:
                        # Convert row to User object
                        return User(
                            id=result[0],
                            email=result[1],
                            google_id=result[2] if len(result) > 2 else None,
                            subscription_tier=result[3] if len(result) > 3 else 'explorer'
                        )
                    return None
        except Exception as e:
            logging.error(f"Failed to get user by email: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID with database compatibility"""
        try:
            if modern_db_available:
                return User.get_by_id(user_id)
            else:
                # Use direct database access
                with db.engine.connect() as conn:
                    result = conn.execute(
                        "SELECT * FROM users WHERE id = ?",
                        (user_id,)
                    ).fetchone()
                    
                    if result:
                        # Convert row to User object
                        return User(
                            id=result[0],
                            email=result[1],
                            google_id=result[2] if len(result) > 2 else None,
                            subscription_tier=result[3] if len(result) > 3 else 'explorer'
                        )
                    return None
        except Exception as e:
            logging.error(f"Failed to get user by ID: {e}")
            return None
    
    def create_magic_link(self, email: str) -> str:
        """Create a magic link token for passwordless authentication"""
        if not email or '@' not in email:
            raise ValidationError("Valid email address required")
        
        # Generate secure token
        token = secrets.token_urlsafe(32)
        
        # Store token with expiry (in production, use Redis)
        self._magic_links[token] = {
            'email': email,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + self.magic_link_expiry
        }
        
        logging.info(f"Created magic link for {email}")
        return token
    
    def verify_magic_link(self, token: str) -> Optional[str]:
        """Verify magic link token and return email if valid"""
        try:
            link_data = self._magic_links.get(token)
            if not link_data:
                return None
            
            # Check if token has expired
            if datetime.utcnow() > link_data['expires_at']:
                del self._magic_links[token]
                return None
            
            email = link_data['email']
            
            # Clean up used token
            del self._magic_links[token]
            
            return email
            
        except Exception as e:
            logging.error(f"Magic link verification failed: {e}")
            return None
    
    def authenticate_user(self, email: str, create_if_not_exists: bool = True) -> Optional[User]:
        """Authenticate user and create if needed"""
        try:
            user = self.get_user_by_email(email)
            
            if not user and create_if_not_exists:
                user = self.create_user(email)
            
            if user:
                logging.info(f"User authenticated: {user.id}")
            
            return user
            
        except Exception as e:
            logging.error(f"Authentication failed: {e}")
            return None
    
    def create_demo_user(self) -> User:
        """Create or get demo user for testing"""
        try:
            demo_email = "demo@rhiz.app"
            user = self.get_user_by_email(demo_email)
            
            if not user:
                user = self.create_user(
                    email=demo_email,
                    subscription_tier='founder_plus'  # Give demo user full access
                )
                
                if not user:
                    # Create simple demo user if database creation fails
                    user = User(
                        id="demo_user_id",
                        email=demo_email,
                        subscription_tier='founder_plus'
                    )
            
            return user
            
        except Exception as e:
            logging.error(f"Demo user creation failed: {e}")
            # Return simple demo user as fallback
            return User(
                id="demo_user_fallback",
                email="demo@rhiz.app",
                subscription_tier='founder_plus'
            )
    
    def validate_session(self, user_id: str) -> Optional[User]:
        """Validate user session and return user if valid"""
        try:
            user = self.get_user_by_id(user_id)
            if user:
                logging.debug(f"Session validated for user: {user_id}")
            return user
        except Exception as e:
            logging.error(f"Session validation failed: {e}")
            return None

# Global auth service instance
auth_service = ModernAuthService()