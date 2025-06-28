"""
Application configuration management
"""
import os
from typing import Optional

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SESSION_SECRET', 'dev-secret-key')
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///rhiz.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # API Keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # Email settings
    FROM_EMAIL = os.environ.get('FROM_EMAIL', 'noreply@rhiz.app')
    
    # Application settings
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # Security settings
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_SECURE = not DEBUG
    SESSION_COOKIE_HTTPONLY = True
    
    @classmethod
    def validate_config(cls) -> list[str]:
        """Validate required configuration and return missing items"""
        missing = []
        required_vars = ['OPENAI_API_KEY', 'DATABASE_URL']
        
        for var in required_vars:
            if not getattr(cls, var):
                missing.append(var)
        
        return missing

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///rhiz_dev.db')

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    @classmethod
    def validate_config(cls) -> list[str]:
        """Enhanced validation for production"""
        missing = super().validate_config()
        production_required = ['RESEND_API_KEY', 'STRIPE_SECRET_KEY']
        
        for var in production_required:
            if not getattr(cls, var):
                missing.append(var)
        
        return missing

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}