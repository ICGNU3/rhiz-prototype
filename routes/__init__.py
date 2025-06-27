"""
Routes package initialization
Provides shared utilities and dependencies for all route modules
"""

from flask import session, redirect, url_for, flash
from functools import wraps
from models import Database, User, Contact, Goal, AISuggestion, ContactInteraction
from openai_utils import OpenAIUtils
from gamification import GamificationEngine
from auth import AuthManager, SubscriptionManager
from utils.validation import validate_session_user_id, safe_get_user_id, ValidationError
import logging

# Initialize shared dependencies
db = Database()
user_model = User(db)
contact_model = Contact(db)
goal_model = Goal(db)
ai_suggestion_model = AISuggestion(db)
interaction_model = ContactInteraction(db)
openai_utils = OpenAIUtils()
gamification = GamificationEngine(db)
auth_manager = AuthManager(db)
subscription_manager = SubscriptionManager(db)

def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            validate_session_user_id()
            return f(*args, **kwargs)
        except ValidationError:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('auth_routes.login'))
        except Exception as e:
            logging.error(f"Authentication error: {e}")
            flash('Authentication error', 'error')
            return redirect(url_for('auth_routes.login'))
    return decorated_function

def get_current_user():
    """Get current authenticated user or None"""
    try:
        user_id = validate_session_user_id()
        return user_model.get_by_id(user_id)
    except ValidationError:
        return None

def get_current_user_id():
    """Get current user ID from session"""
    try:
        return validate_session_user_id()
    except ValidationError:
        return None

class RouteBase:
    """Base class for route modules providing shared functionality"""
    
    def __init__(self):
        self.db = db
        self.user_model = user_model
        self.contact_model = contact_model
        self.goal_model = goal_model
        self.ai_suggestion_model = ai_suggestion_model
        self.interaction_model = interaction_model
        self.openai_utils = openai_utils
        self.gamification = gamification
        self.auth_manager = auth_manager
        self.subscription_manager = subscription_manager
        
    def get_current_user_id(self):
        """Get current user ID with validation"""
        return get_current_user_id()
    
    def award_xp(self, action: str, points: int = 5, metadata: dict = None):
        """Award XP to current user"""
        try:
            user_id = safe_get_user_id()
            if user_id and points:
                self.gamification.award_xp(user_id, action, points, metadata or {})
        except Exception as e:
            logging.error(f"Failed to award XP for action '{action}': {e}")
    
    def flash_success(self, message: str):
        """Flash a success message"""
        flash(message, 'success')
    
    def flash_error(self, message: str):
        """Flash an error message"""
        flash(message, 'error')