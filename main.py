from main_refactored import app
from flask import jsonify
import os
import logging
from datetime import datetime
from api_routes import register_api_routes

# Register API routes for React frontend
register_api_routes(app)

# Initialize Trust Insights system
try:
    from trust_insights import TrustInsightsEngine
    trust_engine = TrustInsightsEngine()
    trust_engine.init_trust_tables()
    logging.info("Trust Insights system initialized successfully")
except Exception as e:
    logging.warning(f"Trust Insights initialization warning: {e}")

# Register React integration routes
from react_integration import register_react_integration
register_react_integration(app)

# Monique CRM functionality integrated in organized route blueprints
# CRM features available through Intelligence navigation section

@app.route('/health')
def health_check():
    """Production health monitoring endpoint"""
    try:
        health = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "environment": "production" if os.environ.get('REPLIT_DEPLOYMENT') else "development"
        }
        
        # Check critical services
        checks = {}
        
        # Database check
        try:
            import sqlite3
            conn = sqlite3.connect("db.sqlite3")
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            checks["database"] = "healthy"
        except Exception as e:
            checks["database"] = f"error: {str(e)[:100]}"
            health["status"] = "degraded"
        
        # API keys check
        checks["openai"] = "configured" if os.environ.get('OPENAI_API_KEY') else "missing"
        checks["sendgrid"] = "configured" if os.environ.get('SENDGRID_API_KEY') else "missing"
        checks["stripe"] = "configured" if os.environ.get('STRIPE_SECRET_KEY') else "missing"
        
        health["checks"] = checks
        
        # Return appropriate status code
        status_code = 200 if health["status"] == "healthy" else 503
        return jsonify(health), status_code
        
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return jsonify({
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Health check unavailable"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
