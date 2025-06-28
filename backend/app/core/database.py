"""
Database configuration and initialization
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Base model class with common attributes"""
    pass

# Initialize SQLAlchemy with custom base
db = SQLAlchemy(model_class=Base)

def init_database(app):
    """Initialize database with application context"""
    db.init_app(app)
    
    with app.app_context():
        # Import all models to ensure tables are created
        from backend.app.models.user import User
        from backend.app.models.contact import Contact
        from backend.app.models.goal import Goal
        from backend.app.models.interaction import ContactInteraction, AISuggestion
        
        # Create all tables
        db.create_all()
        
        return db