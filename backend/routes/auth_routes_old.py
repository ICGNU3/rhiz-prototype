"""
Authentication Routes - Magic link and session management
"""
from flask import Blueprint, request, jsonify, session

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current authenticated user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # TODO: Implement user lookup
    return jsonify({
        'id': user_id,
        'authenticated': True
    })


@auth_bp.route('/demo-login', methods=['POST'])
def demo_login():
    """Demo login for development"""
    session['user_id'] = 'demo_user'
    return jsonify({'success': True, 'user_id': 'demo_user'})


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout current user"""
    session.clear()
    return jsonify({'success': True})