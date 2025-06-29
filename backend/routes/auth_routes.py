"""
Authentication routes module
Magic link authentication with JWT tokens and Resend email integration
"""
from flask import Blueprint, request, jsonify, session, redirect
from backend.extensions import db
from backend.models import User
from backend.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
auth_service = AuthService()


@auth_bp.route('/request-link', methods=['POST'])
@auth_bp.route('/magic-link', methods=['POST'])  # Alias for backward compatibility
def request_magic_link():
    """Generate and send magic link via email"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Please enter a valid email address'}), 400
        
        # Generate JWT magic link token
        token = auth_service.generate_magic_link_token(email)
        
        # Send magic link email
        email_sent = auth_service.send_magic_link(email, token)
        
        if email_sent:
            return jsonify({
                'success': True,
                'message': 'Magic link sent to your email address'
            })
        else:
            return jsonify({
                'error': 'Failed to send email. Please try again.'
            }), 500
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred. Please try again.'}), 500


@auth_bp.route('/verify', methods=['GET'])
def verify_magic_link():
    """Verify magic link token and authenticate user"""
    try:
        token = request.args.get('token')
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        # Verify JWT token
        payload = auth_service.verify_magic_link_token(token)
        
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        email = payload.get('email')
        
        # Get or create user
        user = auth_service.get_or_create_user(email)
        
        # Create session
        session['user_id'] = user.id
        session['authenticated'] = True
        session['email'] = user.email
        
        # Cleanup expired tokens
        auth_service.cleanup_expired_tokens()
        
        # Check if request expects JSON response
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'success': True,
                'message': 'Successfully authenticated',
                'user': user.to_dict()
            })
        
        # Redirect to dashboard for browser requests
        return redirect('/app/dashboard')
        
    except Exception as e:
        return jsonify({'error': 'Authentication failed'}), 401

@auth_bp.route('/profile', methods=['GET'])
def get_user_profile():
    """Get current user profile"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': user.to_dict(),
            'profile': {
                'name': user.email.split('@')[0].title(),
                'email': user.email,
                'subscription_tier': user.subscription_tier,
                'member_since': user.created_at.strftime('%B %Y'),
                'is_guest': user.is_guest
            }
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to load profile'}), 500


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current authenticated user"""
    if not session.get('authenticated'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'No user session'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'success': True,
        'user': user.to_dict()
    })


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout current user"""
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Successfully logged out'
    })


@auth_bp.route('/demo-login', methods=['POST'])
def demo_login():
    """Demo login for testing without email verification"""
    try:
        # Create demo user session
        demo_email = 'demo@rhiz.app'
        
        # Get or create demo user
        user = auth_service.get_or_create_user(demo_email)
        
        # Create session
        session['user_id'] = user.id
        session['authenticated'] = True
        session['email'] = user.email
        
        return jsonify({
            'success': True,
            'message': 'Demo authentication successful',
            'user': user.to_dict(),
            'redirect': '/app/dashboard'
        })
        
    except Exception as e:
        return jsonify({'error': 'Demo login failed'}), 500


@auth_bp.route('/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    return jsonify({
        'authenticated': session.get('authenticated', False),
        'user_id': session.get('user_id'),
        'email': session.get('email')
    })