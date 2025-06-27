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

# React and API blueprints registered in main.py to avoid conflicts

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)