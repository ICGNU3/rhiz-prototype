"""
Rhiz Backend Application Package
High-context relationship intelligence platform
"""

from flask import Flask
from backend.app.core.config import Config
from backend.app.core.database import db
from backend.app.core.exceptions import register_error_handlers

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    from backend.app.api.auth import auth_bp
    from backend.app.api.contacts import contacts_bp
    from backend.app.api.goals import goals_bp
    from backend.app.api.intelligence import intelligence_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(contacts_bp, url_prefix='/api/contacts')
    app.register_blueprint(goals_bp, url_prefix='/api/goals')
    app.register_blueprint(intelligence_bp, url_prefix='/api/intelligence')
    
    return app