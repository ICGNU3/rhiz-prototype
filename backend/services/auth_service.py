"""
Authentication Service
Handles Magic-Link authentication with JWT tokens and Resend email integration
"""

import os
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import resend
from flask import current_app
from backend.extensions import db
from backend.models import User, AuthToken

class AuthService:
    """Magic-Link authentication service"""
    
    def __init__(self):
        self.jwt_secret = os.environ.get('JWT_SECRET_KEY')
        self.resend_api_key = os.environ.get('RESEND_API_KEY')
        if self.resend_api_key:
            resend.api_key = self.resend_api_key
    
    def generate_magic_link_token(self, email: str) -> str:
        """Generate a secure JWT token for magic link authentication"""
        payload = {
            'email': email,
            'type': 'magic_link',
            'exp': datetime.utcnow() + timedelta(minutes=15),  # 15-minute expiry
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(32)  # Unique token ID
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
        
        # Store token in database for tracking and revocation
        auth_token = AuthToken()
        auth_token.email = email
        auth_token.token = token
        auth_token.expires = payload['exp']
        
        db.session.add(auth_token)
        db.session.commit()
        
        return token
    
    def verify_magic_link_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a magic link JWT token"""
        try:
            # Check if token exists in database and is not used
            auth_token = AuthToken.query.filter_by(token=token).first()
            if not auth_token or auth_token.used_at:
                return None
            
            # Verify JWT token
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            
            # Check if token is expired
            if auth_token.is_expired():
                return None
            
            # Mark token as used
            auth_token.mark_used()
            db.session.commit()
            
            return payload
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def send_magic_link(self, email: str, token: str) -> bool:
        """Send magic link email via Resend"""
        try:
            # Generate magic link URL
            base_url = os.environ.get('REPLIT_DEV_DOMAIN', 'http://localhost:5000')
            if base_url.startswith('https://'):
                magic_link = f"{base_url}/api/auth/verify?token={token}"
            else:
                magic_link = f"http://localhost:5000/api/auth/verify?token={token}"
            
            # HTML email template
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Your Rhiz Magic Link</title>
            </head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 12px; margin-bottom: 30px;">
                    <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 700;">
                        🌱 Rhiz
                    </h1>
                    <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0; font-size: 16px;">
                        Your secure login link is ready
                    </p>
                </div>
                
                <div style="background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2 style="color: #333; margin-top: 0;">Access Your Account</h2>
                    <p>Click the button below to securely log in to your Rhiz account:</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{magic_link}" 
                           style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                  color: white; 
                                  padding: 14px 28px; 
                                  text-decoration: none; 
                                  border-radius: 8px; 
                                  font-weight: 600; 
                                  display: inline-block;
                                  transition: all 0.3s ease;">
                            🔐 Secure Login
                        </a>
                    </div>
                    
                    <p style="color: #666; font-size: 14px; margin-top: 30px;">
                        <strong>Security Note:</strong> This link expires in 15 minutes and can only be used once.
                        If you didn't request this login, you can safely ignore this email.
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 30px; color: #888; font-size: 12px;">
                    <p>Rhiz - High-context relationship intelligence</p>
                </div>
            </body>
            </html>
            """
            
            # Text fallback
            text_content = f"""
            Rhiz - Secure Login
            
            Click the link below to log in to your account:
            {magic_link}
            
            This link expires in 15 minutes and can only be used once.
            If you didn't request this login, you can safely ignore this email.
            
            ---
            Rhiz - High-context relationship intelligence
            """
            
            # Send email via Resend
            if self.resend_api_key:
                try:
                    params = {
                        "from": "Rhiz <noreply@rhiz.app>",
                        "to": [email],
                        "subject": "🔐 Your Rhiz Login Link",
                        "html": html_content,
                        "text": text_content
                    }
                    
                    email_response = resend.Emails.send(params)
                    return True
                except Exception as e:
                    current_app.logger.error(f"Resend email error: {e}")
                    # Fallback to development mode
                    current_app.logger.info(f"Magic link for {email}: {magic_link}")
                    return True
            else:
                # Development fallback - log the magic link
                current_app.logger.info(f"Development Magic link for {email}: {magic_link}")
                return True
                
        except Exception as e:
            current_app.logger.error(f"Failed to send magic link: {e}")
            return False
    
    def get_or_create_user(self, email: str) -> User:
        """Get existing user or create new one"""
        user = User.query.filter_by(email=email).first()
        
        if not user:
            user = User()
            user.email = email
            user.subscription_tier = 'explorer'  # Default tier for new users
            user.is_guest = False
            
            db.session.add(user)
            db.session.commit()
        
        return user
    
    def cleanup_expired_tokens(self):
        """Remove expired tokens from database"""
        expired_tokens = AuthToken.query.filter(
            AuthToken.expires < datetime.utcnow()
        ).all()
        
        for token in expired_tokens:
            db.session.delete(token)
        
        db.session.commit()
        return len(expired_tokens)