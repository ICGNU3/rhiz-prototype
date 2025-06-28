"""
Routes package initialization
Provides shared utilities and dependencies for all route modules
"""

from flask import session, redirect, url_for, flash
from functools import wraps
from models import Database, User, Contact, Goal, AISuggestion, ContactInteraction
import logging

# Initialize shared dependencies
db = Database()

def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('auth_routes.login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current authenticated user or None"""
    user_id = session.get('user_id')
    if user_id:
        return User.get_by_id(user_id)
    return None

def get_current_user_id():
    """Get current user ID from session"""
    return session.get('user_id')

class RouteBase:
    """Base class for route modules providing shared functionality"""
    
    def __init__(self):
        self.db = db
        
    def get_current_user_id(self):
        """Get current user ID with validation"""
        return get_current_user_id()
    
    def award_xp(self, action: str, points: int = 5, metadata: dict = None):
        """Award XP to current user (placeholder for gamification)"""
        pass
    
    def flash_success(self, message: str):
        """Flash a success message"""
        flash(message, 'success')
    
    def flash_error(self, message: str):
        """Flash an error message"""
        flash(message, 'error')