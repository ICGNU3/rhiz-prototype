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

# Register intelligence and advanced feature blueprints
try:
    from routes.intelligence_routes import intelligence_bp
    app.register_blueprint(intelligence_bp)
    print("Intelligence routes loaded successfully")
except ImportError as e:
    print(f"Intelligence routes not available: {e}")

# Legacy routes compatibility (temporary)
try:
    import routes as legacy_routes
    print("Legacy routes still active - migration in progress")
except ImportError as e:
    print(f"Legacy routes disabled: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)