"""
Authentication routes module
Magic link authentication with Resend email integration
"""
import secrets
import string
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from backend.extensions import db
from backend.models import User, AuthToken
from backend.services.email_service import email_service

auth_bp = Blueprint('auth', __name__)


def generate_secure_token(length=32):
    """Generate a cryptographically secure random token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


@auth_bp.route('/request-link', methods=['POST'])
def request_magic_link():
    """Generate and send magic link via email"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Generate secure token
        token = generate_secure_token()
        expires = datetime.utcnow() + timedelta(minutes=15)  # 15 minute expiry
        
        # Clean up old tokens for this email
        AuthToken.query.filter_by(email=email).delete()
        
        # Create new auth token
        auth_token = AuthToken(
            email=email,
            token=token,
            expires=expires
        )
        
        db.session.add(auth_token)
        db.session.commit()
        
        # Generate magic link
        base_url = request.host_url.rstrip('/')
        magic_link = f"{base_url}/api/auth/verify?token={token}"
        
        # Send email
        email_sent = email_service.send_magic_link(email, magic_link)
        
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
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/verify', methods=['GET'])
def verify_magic_link():
    """Verify magic link token and authenticate user"""
    try:
        token = request.args.get('token')
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        # Find the auth token
        auth_token = AuthToken.query.filter_by(token=token).first()
        
        if not auth_token:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Check if token is expired
        if auth_token.is_expired():
            db.session.delete(auth_token)
            db.session.commit()
            return jsonify({'error': 'Token has expired'}), 401
        
        # Check if token has already been used
        if auth_token.used_at:
            return jsonify({'error': 'Token has already been used'}), 401
        
        # Find or create user
        user = User.query.filter_by(email=auth_token.email).first()
        if not user:
            # Create new user
            user = User(
                email=auth_token.email,
                subscription_tier='explorer'
            )
            db.session.add(user)
        
        # Mark token as used
        auth_token.mark_used()
        db.session.commit()
        
        # Set session
        session['user_id'] = user.id
        session['authenticated'] = True
        
        # Redirect to app dashboard or return JSON
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'success': True,
                'message': 'Authentication successful',
                'user': user.to_dict()
            })
        else:
            # Redirect to frontend app
            return redirect('/')
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User signup with email (for backward compatibility)"""
    data = request.get_json()
    if not data or not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'User already exists'}), 409
        
        # Create new user
        user = User(email=data['email'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'user_id': str(user.id)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Simple login for development (for backward compatibility)"""
    data = request.get_json()
    if not data or not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
    
    try:
        user = User.query.filter_by(email=data['email']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Set session
        session['user_id'] = user.id
        session['authenticated'] = True
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'})


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current authenticated user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()})