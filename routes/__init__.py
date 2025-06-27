"""
Routes package initialization
Provides shared utilities and dependencies for all route modules
"""

from flask import session, redirect, url_for, flash
from functools import wraps
from models import Database, User, Contact, Goal, AISuggestion, ContactInteraction, ContactIntelligence, OutreachSuggestion
from openai_utils import OpenAIUtils
from gamification import GamificationEngine
from auth import AuthManager, SubscriptionManager
import logging

# Initialize shared dependencies
db = Database()
user_model = User(db)
contact_model = Contact(db)
goal_model = Goal(db)
ai_suggestion_model = AISuggestion(db)
interaction_model = ContactInteraction(db)
outreach_suggestion_model = OutreachSuggestion(db)
contact_intelligence = ContactIntelligence(db)
openai_utils = OpenAIUtils()
gamification = GamificationEngine(db)
auth_manager = AuthManager(db)
subscription_manager = SubscriptionManager(db)

# Get or create default user
DEFAULT_USER_ID = user_model.get_or_create_default()

def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth_routes.signup'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current authenticated user or None"""
    user_id = session.get('user_id')
    if user_id:
        return user_model.get_by_id(user_id)
    return None

def get_current_user_id():
    """Get current user ID or default user ID"""
    return session.get('user_id', DEFAULT_USER_ID)

class RouteBase:
    """Base class for route modules providing shared functionality"""
    
    def __init__(self):
        self.db = db
        self.user_model = user_model
        self.contact_model = contact_model
        self.goal_model = goal_model
        self.ai_suggestion_model = ai_suggestion_model
        self.interaction_model = interaction_model
        self.outreach_suggestion_model = outreach_suggestion_model
        self.contact_intelligence = contact_intelligence
        self.openai_utils = openai_utils
        self.gamification = gamification
        self.auth_manager = auth_manager
        self.subscription_manager = subscription_manager
        
    def get_current_user_id(self):
        """Get current user ID with fallback to default"""
        return get_current_user_id()
    
    def award_xp(self, action: str, points: int = None, metadata: dict = None):
        """Award XP to current user"""
        user_id = self.get_current_user_id()
        if user_id:
            try:
                self.gamification.award_xp(user_id, action, points, metadata)
            except Exception as e:
                logging.error(f"Failed to award XP: {e}")
    
    def flash_success(self, message: str):
        """Flash a success message"""
        flash(message, 'success')
    
    def flash_error(self, message: str):
        """Flash an error message"""
        flash(message, 'error')