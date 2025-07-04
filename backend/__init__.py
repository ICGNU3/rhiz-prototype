"""
Backend Package - Flask Application Factory
"""
import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# Import extensions
from .extensions import db, migrate, cors

def create_app(config_name=None):
    """
    Application factory pattern for Flask app creation
    """
    # Create Flask app with template and static folders relative to project root
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configure the app
    configure_app(app, config_name)
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Configure logging
    configure_logging(app)
    
    return app

def configure_app(app, config_name=None):
    """Configure Flask application"""
    
    # Basic Flask configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Database configuration - PostgreSQL via DATABASE_URL
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Environment-specific configuration
    environment = os.environ.get('REPLIT_DEPLOYMENT', 'development')
    if environment == 'production':
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
    else:
        app.config['DEBUG'] = True
        app.config['TESTING'] = False

def initialize_extensions(app):
    """Initialize Flask extensions"""
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins=["*"], supports_credentials=True)
    
    # Import models to ensure they're registered with Flask-Migrate
    with app.app_context():
        try:
            from .models import User, Contact, Goal, AISuggestion, ContactInteraction, AuthToken
            logging.info("Models imported successfully for Flask-Migrate")
        except Exception as e:
            logging.error(f"Model import error: {e}")

def register_blueprints(app):
    """Register all application blueprints"""
    from .routes.auth_routes import auth_bp
    from .routes.api_routes import api_bp
    from .routes.contact_routes import contact_bp
    from .routes.goal_routes import goal_bp
    from .routes.core_routes import core_bp
    from .routes.service_routes import service_bp
    from .routes.intelligence_routes import intelligence_bp
    from .routes.trust_routes import trust_bp
    
    # Register blueprints with URL prefixes
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(contact_bp, url_prefix='/api/contacts')
    app.register_blueprint(goal_bp, url_prefix='/api/goals')
    app.register_blueprint(service_bp, url_prefix='/api/services')
    app.register_blueprint(trust_bp, url_prefix='/api/trust')
    app.register_blueprint(intelligence_bp)  # Already has /api/intelligence prefix
    app.register_blueprint(core_bp)  # Core routes (/, /health, etc.)

def configure_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        # Production logging
        from logging.handlers import RotatingFileHandler
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler('logs/rhiz.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Rhiz application startup')
    else:
        # Development logging - use app logger instead
        app.logger.setLevel(logging.DEBUG)