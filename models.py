"""
Legacy Models Import
This file maintains compatibility for any legacy imports.
All models are now properly organized in backend/models.py
"""

# Import all models from the new modularized backend
from backend.models import (
    User,
    Contact, 
    Goal,
    AISuggestion,
    ContactInteraction,
    JournalEntry,
    AuthToken
)

# Import db from extensions
from backend.extensions import db

# Legacy database class for compatibility
class Database:
    """Legacy database compatibility class"""
    
    def __init__(self):
        from backend.extensions import db as sqlalchemy_db
        self.db = sqlalchemy_db
    
    def get_connection(self):
        """Legacy method - use SQLAlchemy models instead"""
        return self.db