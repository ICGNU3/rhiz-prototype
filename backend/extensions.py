"""
Flask Extensions
Initialize Flask extensions to avoid circular imports
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

# Initialize extensions - will be bound to app in create_app
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()