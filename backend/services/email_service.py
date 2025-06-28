"""
Email service for sending magic link authentication emails via Resend
"""
import os
import logging
from typing import Optional
import resend

logger = logging.getLogger(__name__)

class EmailService:
    """Email service using Resend API for magic link authentication"""
    
    def __init__(self):
        self.api_key = os.environ.get('RESEND_API_KEY')
        if self.api_key:
            resend.api_key = self.api_key
            logger.info("Resend email service initialized")
        else:
            logger.warning("RESEND_API_KEY not found in environment variables")
    
    def is_configured(self) -> bool:
        """Check if the email service is properly configured"""
        return bool(self.api_key)
    
    def send_magic_link(self, email: str, magic_link: str) -> bool:
        """
        Send magic link authentication email
        
        Args:
            email: Recipient email address
            magic_link: The authentication link to send
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.is_configured():
            logger.error("Email service not configured - missing RESEND_API_KEY")
            return False
        
        try:
            # Create the email content
            html_content = self._create_magic_link_html(magic_link)
            text_content = self._create_magic_link_text(magic_link)
            
            # Send email via Resend
            response = resend.Emails.send({
                "from": "Rhiz <auth@rhiz.app>",
                "to": [email],
                "subject": "Your secure login link for Rhiz",
                "html": html_content,
                "text": text_content
            })
            
            logger.info(f"Magic link email sent successfully to {email}. Response: {response}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send magic link email to {email}: {str(e)}")
            return False
    
    def _create_magic_link_html(self, magic_link: str) -> str:
        """Create HTML content for magic link email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your Rhiz Login Link</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ font-size: 32px; font-weight: bold; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 12px; margin: 20px 0; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 16px 32px; text-decoration: none; border-radius: 8px; font-weight: 600; margin: 20px 0; }}
                .footer {{ text-align: center; color: #666; font-size: 14px; margin-top: 30px; }}
                .security-note {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">Rhiz</div>
                </div>
                
                <div class="content">
                    <h2>Welcome back to Rhiz</h2>
                    <p>Click the button below to securely sign in to your relationship intelligence platform:</p>
                    
                    <div style="text-align: center;">
                        <a href="{magic_link}" class="button">Sign In to Rhiz</a>
                    </div>
                    
                    <div class="security-note">
                        <strong>Security Note:</strong> This link will expire in 15 minutes and can only be used once. If you didn't request this login, you can safely ignore this email.
                    </div>
                </div>
                
                <div class="footer">
                    <p>Having trouble? Copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; font-size: 12px; color: #999;">{magic_link}</p>
                    <p>This email was sent to you because you requested access to Rhiz. If you didn't make this request, please ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_magic_link_text(self, magic_link: str) -> str:
        """Create plain text content for magic link email"""
        return f"""
Welcome back to Rhiz!

Click the link below to securely sign in to your relationship intelligence platform:

{magic_link}

This link will expire in 15 minutes and can only be used once.

If you didn't request this login, you can safely ignore this email.

Having trouble? Copy and paste the link above into your browser.

---
Rhiz - Relationship Intelligence Platform
"""

# Global email service instance
email_service = EmailService()