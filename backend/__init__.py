"""
Backend Package - Flask Application Factory
"""
import os
import logging
from flask import Flask
from flask_cors import CORS
from backend.extensions import db, migrate
# Direct blueprint imports will be done in register_blueprints function


def create_app(config_name=None):
    """
    Application factory pattern for Flask app creation
    """
    app = Flask(__name__, 
                static_folder='../static',
                template_folder='../templates')
    
    # Configure CORS for React frontend
    CORS(app, supports_credentials=True, origins=['http://localhost:5173', 'https://*.replit.app'])
    
    # Load configuration
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
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logging.info("Environment variables loaded from .env file")
    except ImportError:
        logging.info("Loading environment variables from system")
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Additional configuration
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'uploads')


def initialize_extensions(app):
    """Initialize Flask extensions"""
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()


def register_blueprints(app):
    """Register all application blueprints"""
    # Temporarily disable auth_bp to use simple demo authentication
    # from backend.routes.auth_routes import auth_bp
    from backend.routes.contact_routes import contact_bp
    from backend.routes.goal_routes import goal_bp
    from backend.routes.trust_routes import trust_bp
    from backend.routes.dashboard_routes import dashboard_bp
    from backend.routes.core_routes import core_bp
    from backend.routes.simple_health_routes import health_bp
    
    # app.register_blueprint(auth_bp, url_prefix='/api/auth')  # Disabled for demo
    app.register_blueprint(contact_bp, url_prefix='/api/contacts')
    app.register_blueprint(goal_bp, url_prefix='/api/goals')
    app.register_blueprint(trust_bp, url_prefix='/api/trust')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(health_bp, url_prefix='/api')
    
    # Register core routes without prefix for compatibility
    app.register_blueprint(core_bp)


def configure_logging(app):
    """Configure application logging"""
    if not app.debug:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s: %(message)s'
        )
    else:
        logging.basicConfig(level=logging.DEBUG)