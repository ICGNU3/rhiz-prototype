"""
Refactored main application file
Clean, modular structure with separated route blueprints
"""

from app import app
from routes.core_routes import core_bp
from routes.auth_routes import auth_bp  
from routes.contact_routes import contact_bp
from routes.goal_routes import goal_bp

# Register all blueprint modules
app.register_blueprint(core_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(goal_bp)

# Register advanced feature blueprints (these need to be created)
try:
    from routes.intelligence_routes import intelligence_bp
    app.register_blueprint(intelligence_bp)
except ImportError:
    print("Intelligence routes not yet migrated")

try:
    from routes.advanced_routes import advanced_bp
    app.register_blueprint(advanced_bp)
except ImportError:
    print("Advanced routes not yet migrated")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)