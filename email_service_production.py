"""
Production Email Service using Resend
Handles magic link authentication and transactional emails for launch
"""
import os
import logging
import resend

logger = logging.getLogger(__name__)

class ProductionEmailService:
    """Production-ready email service using Resend"""
    
    def __init__(self):
        self.api_key = os.environ.get('RESEND_API_KEY')
        self.from_email = os.environ.get('FROM_EMAIL', 'info@ourhizome.com')
        self._configured = False
        
        if self.api_key:
            try:
                resend.api_key = self.api_key
                self._configured = True
                logger.info("Resend email service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Resend: {e}")
        else:
            logger.warning("RESEND_API_KEY not found - email features will be disabled")
    
    def is_configured(self) -> bool:
        """Check if email service is properly configured"""
        return self._configured
    
    def send_magic_link_email(self, to_email: str, magic_token: str, base_url: str = None) -> bool:
        """Send magic link email for passwordless authentication"""
        if not self.is_configured():
            logger.error("Email service not configured - cannot send magic link")
            return False
            
        try:
            # Use current domain or fallback
            if not base_url:
                base_url = os.environ.get('REPLIT_DEV_DOMAIN', 'https://ourhizome.app')
                if not base_url.startswith('http'):
                    base_url = f"https://{base_url}"
            
            magic_link = f"{base_url}/auth/verify?token={magic_token}"
            
            # Create email content
            subject = "Sign in to OuRhizome"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Sign in to OuRhizome</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 0; background: #0a0a0f; color: #ffffff; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
                    .header {{ text-align: center; margin-bottom: 40px; }}
                    .logo {{ width: 64px; height: 64px; margin: 0 auto 20px; }}
                    .content {{ background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 40px; text-align: center; }}
                    .button {{ display: inline-block; background: linear-gradient(135deg, #4facfe 0%, #8b5cf6 100%); color: white; padding: 16px 32px; text-decoration: none; border-radius: 12px; font-weight: 600; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 40px; color: rgba(255, 255, 255, 0.7); font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">🌱</div>
                        <h1>OuRhizome</h1>
                    </div>
                    <div class="content">
                        <h2>Welcome to Root Membership</h2>
                        <p>Click the button below to sign in to your OuRhizome account:</p>
                        <a href="{magic_link}" class="button">Sign In to OuRhizome</a>
                        <p><small>This link will expire in 1 hour for security.</small></p>
                    </div>
                    <div class="footer">
                        <p>Goal in mind. People in reach. Moves in motion.</p>
                        <p>If you didn't request this email, you can safely ignore it.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Welcome to OuRhizome Root Membership
            
            Click this link to sign in: {magic_link}
            
            This link will expire in 1 hour for security.
            
            Goal in mind. People in reach. Moves in motion.
            
            If you didn't request this email, you can safely ignore it.
            """
            
            # Create and send email
            message = Mail(
                from_email=Email(self.from_email, "OuRhizome"),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content),
                plain_text_content=Content("text/plain", text_content)
            )
            
            response = self.sg.send(message)
            
            if response.status_code in [200, 202]:
                logger.info(f"Magic link email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email: {response.status_code} {response.body}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending magic link email: {e}")
            return False
    
    def send_welcome_email(self, to_email: str, user_name: str = None) -> bool:
        """Send welcome email for new Root Members"""
        if not self.is_configured():
            return False
            
        try:
            subject = "Welcome to OuRhizome Root Membership"
            
            greeting = f"Welcome {user_name}!" if user_name else "Welcome to Root Membership!"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Welcome to OuRhizome</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 0; background: #0a0a0f; color: #ffffff; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
                    .header {{ text-align: center; margin-bottom: 40px; }}
                    .logo {{ width: 64px; height: 64px; margin: 0 auto 20px; }}
                    .content {{ background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 40px; }}
                    .feature {{ margin: 20px 0; padding: 20px; background: rgba(255, 255, 255, 0.02); border-radius: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">🌱</div>
                        <h1>OuRhizome</h1>
                    </div>
                    <div class="content">
                        <h2>{greeting}</h2>
                        <p>You're now part of the exclusive community of One Hundred Root Members.</p>
                        
                        <div class="feature">
                            <h3>🎯 Goal-First Networking</h3>
                            <p>Start with your goals and let AI find the right people in your network.</p>
                        </div>
                        
                        <div class="feature">
                            <h3>🤖 AI-Powered Matching</h3>
                            <p>Advanced semantic analysis connects your objectives with relevant contacts.</p>
                        </div>
                        
                        <div class="feature">
                            <h3>📧 Smart Outreach</h3>
                            <p>Generate personalized messages that resonate with your contacts.</p>
                        </div>
                        
                        <p><strong>Ready to get started?</strong> Log in and create your first goal to begin building meaningful connections.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=Email(self.from_email, "OuRhizome"),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            response = self.sg.send(message)
            return response.status_code in [200, 202]
            
        except Exception as e:
            logger.error(f"Error sending welcome email: {e}")
            return False

# Initialize global email service
production_email_service = ProductionEmailService()