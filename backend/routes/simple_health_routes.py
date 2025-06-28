"""
Simple health check routes
"""
from flask import Blueprint, jsonify
from backend.models import User, Contact, Goal
from backend.extensions import db

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        user_count = User.query.count()
        contact_count = Contact.query.count()
        goal_count = Goal.query.count()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'stats': {
                'users': user_count,
                'contacts': contact_count,
                'goals': goal_count
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@health_bp.route('/status', methods=['GET'])
def status():
    """Application status"""
    return jsonify({
        'application': 'Rhiz',
        'version': '2.0.0',
        'status': 'running',
        'backend_structure': 'modular'
    })