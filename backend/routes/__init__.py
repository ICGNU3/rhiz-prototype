"""
Routes Package - Blueprint Registration
"""
from flask import Blueprint

# Import all route blueprints
from .auth_routes import auth_bp
from .contact_routes import contact_bp
from .goal_routes import goal_bp
from .trust_routes import trust_bp
from .dashboard_routes import dashboard_bp


def register_blueprints(app):
    """Register all application blueprints"""
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(contact_bp, url_prefix='/api/contacts')
    app.register_blueprint(goal_bp, url_prefix='/api/goals')
    app.register_blueprint(trust_bp, url_prefix='/api/trust')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    
    # Register core routes without prefix for compatibility
    from .core_routes import core_bp
    app.register_blueprint(core_bp)