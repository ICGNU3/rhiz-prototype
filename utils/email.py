"""
Resend Email Service for Rhiz
Handles all transactional emails using Resend API
"""
import os
import logging
import resend
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ResendEmailService:
    """Production email service using Resend"""
    
    def __init__(self):
        self.api_key = os.environ.get('RESEND_API_KEY')
        self.from_email = os.environ.get('FROM_EMAIL', 'info@ourhizome.com')
        self.is_configured = False
        
        if self.api_key:
            try:
                resend.api_key = self.api_key
                self.is_configured = True
                logger.info("Resend email service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Resend: {e}")
        else:
            logger.warning("RESEND_API_KEY not found - email features will be disabled")
    
    def send_email(self, to_email: str, subject: str, html_content: str, 
                   text_content: str = None, reply_to: str = None) -> Dict[str, Any]:
        """Send email using Resend API"""
        if not self.is_configured:
            logger.error("Resend not configured - cannot send email")
            return {
                'success': False,
                'error': 'Email service not configured',
                'method': 'resend'
            }
        
        try:
            email_data = {
                "from": f"Rhiz <{self.from_email}>",
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }
            
            if text_content:
                email_data["text"] = text_content
                
            if reply_to:
                email_data["reply_to"] = reply_to
            
            response = resend.Emails.send(email_data)
            
            logger.info(f"Email sent successfully to {to_email} via Resend - ID: {response.get('id', 'unknown')}")
            
            return {
                'success': True,
                'message': 'Email sent successfully via Resend',
                'method': 'resend',
                'email_id': response.get('id'),
                'response': response
            }
            
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                    error_msg = f"HTTP {e.response.status_code}: {error_details.get('message', error_msg)}"
                except:
                    error_msg = f"HTTP {e.response.status_code}: {error_msg}"
            
            logger.error(f"Resend email error: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'method': 'resend'
            }
    
    def send_magic_link_email(self, to_email: str, magic_token: str, base_url: str = None) -> bool:
        """Send magic link email for passwordless authentication"""
        if not self.is_configured:
            logger.error("Email service not configured - cannot send magic link")
            return False
            
        try:
            # Use current domain or fallback
            if not base_url:
                base_url = os.environ.get('REPLIT_DEV_DOMAIN', 'https://ourhizome.com')
                if not base_url.startswith('http'):
                    base_url = f"https://{base_url}"
            
            magic_link = f"{base_url}/auth/verify?token={magic_token}"
            
            # Create email content
            subject = "Sign in to Rhiz"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Sign in to Rhiz</title>
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
                        <h1>Rhiz</h1>
                    </div>
                    <div class="content">
                        <h2>Welcome to Root Membership</h2>
                        <p>Click the button below to sign in to your Rhiz account:</p>
                        <a href="{magic_link}" class="button">Sign In to Rhiz</a>
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
            Welcome to Rhiz Root Membership
            
            Click this link to sign in: {magic_link}
            
            This link will expire in 1 hour for security.
            
            Goal in mind. People in reach. Moves in motion.
            
            If you didn't request this email, you can safely ignore it.
            """
            
            result = self.send_email(to_email, subject, html_content, text_content)
            return result['success']
                
        except Exception as e:
            logger.error(f"Error sending magic link email: {e}")
            return False
    
    def send_welcome_email(self, to_email: str, user_name: str = None) -> bool:
        """Send welcome email for new Root Members"""
        if not self.is_configured:
            return False
            
        try:
            subject = "Welcome to Rhiz Root Membership"
            greeting = f"Welcome {user_name}!" if user_name else "Welcome to Root Membership!"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Welcome to Rhiz</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 0; background: #0a0a0f; color: #ffffff; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
                    .header {{ text-align: center; margin-bottom: 40px; }}
                    .content {{ background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 40px; }}
                    .feature {{ margin: 20px 0; padding: 20px; background: rgba(255, 255, 255, 0.02); border-radius: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">🌱</div>
                        <h1>Rhiz</h1>
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
            
            result = self.send_email(to_email, subject, html_content)
            return result['success']
            
        except Exception as e:
            logger.error(f"Error sending welcome email: {e}")
            return False
    
    def send_goal_confirmation_email(self, to_email: str, goal_title: str, goal_description: str) -> bool:
        """Send goal creation confirmation email"""
        if not self.is_configured:
            return False
            
        try:
            subject = f"Goal Created: {goal_title}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Goal Created - Rhiz</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 0; background: #0a0a0f; color: #ffffff; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
                    .content {{ background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 40px; }}
                    .goal-box {{ background: rgba(79, 172, 254, 0.1); border: 1px solid rgba(79, 172, 254, 0.3); border-radius: 12px; padding: 20px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="content">
                        <h2>🎯 Your Goal is Set!</h2>
                        <p>You've successfully created a new goal in Rhiz. Our AI is now analyzing your network to find relevant connections.</p>
                        
                        <div class="goal-box">
                            <h3>{goal_title}</h3>
                            <p>{goal_description}</p>
                        </div>
                        
                        <p><strong>What happens next?</strong></p>
                        <ul>
                            <li>AI will analyze your contacts for relevant matches</li>
                            <li>You'll receive personalized outreach suggestions</li>
                            <li>Smart recommendations will appear in your dashboard</li>
                        </ul>
                        
                        <p>Check your Rhiz dashboard for AI-powered insights!</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            result = self.send_email(to_email, subject, html_content)
            return result['success']
            
        except Exception as e:
            logger.error(f"Error sending goal confirmation email: {e}")
            return False
    
    def send_outreach_message(self, to_email: str, subject: str, message_body: str,
                            contact_id: Optional[int] = None, user_id: Optional[int] = None,
                            goal_title: Optional[str] = None) -> Dict[str, Any]:
        """Send AI-generated outreach message"""
        if not self.is_configured:
            return {
                'success': False,
                'error': 'Email service not configured',
                'method': 'resend'
            }
        
        try:
            # Create formatted HTML email
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{subject}</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .message {{ background: #f8f9fa; padding: 30px; border-radius: 8px; margin: 20px 0; }}
                    .footer {{ text-align: center; padding: 15px; font-size: 12px; color: #6c757d; border-top: 1px solid #dee2e6; margin-top: 30px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="message">
                        {message_body.replace(chr(10), '<br>')}
                    </div>
                    <div class="footer">
                        Sent via Rhiz - Connecting founders with the right people
                    </div>
                </div>
            </body>
            </html>
            """
            
            result = self.send_email(to_email, subject, html_content, message_body)
            
            # Log the interaction if IDs provided
            if contact_id and user_id:
                self._log_email_interaction(contact_id, user_id, to_email, subject, 
                                          message_body, goal_title, 'resend', result['success'])
            
            return result
            
        except Exception as e:
            logger.error(f"Error sending outreach message: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'resend'
            }
    
    def _log_email_interaction(self, contact_id: int, user_id: int, to_email: str,
                              subject: str, message: str, goal_title: str,
                              method: str, success: bool):
        """Log email interaction to database"""
        try:
            from database_utils import get_db_connection
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO contact_interactions 
                (contact_id, user_id, interaction_type, details, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                contact_id,
                user_id,
                'email_sent',
                f"Email sent via {method}: {subject} ({'Success' if success else 'Failed'})",
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to log email interaction: {e}")
    
    def send_application_confirmation(self, to_email: str, first_name: str) -> bool:
        """Send application confirmation email for Root Membership"""
        try:
            subject = "Root Membership Application Received - Rhiz"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{subject}</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 8px 8px; }}
                    .footer {{ text-align: center; padding: 15px; font-size: 12px; color: #6c757d; border-top: 1px solid #dee2e6; margin-top: 30px; }}
                    .highlight {{ background: rgba(102, 126, 234, 0.1); padding: 15px; border-radius: 6px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="margin: 0; font-size: 24px;">Application Received</h1>
                        <p style="margin: 10px 0 0 0; opacity: 0.9;">Welcome to the Root Member application process</p>
                    </div>
                    <div class="content">
                        <p>Hello {first_name},</p>
                        
                        <p>Thank you for applying to become one of our One Hundred Root Members. Your application has been received and will be carefully reviewed by our founding team.</p>
                        
                        <div class="highlight">
                            <h3 style="margin-top: 0;">What happens next:</h3>
                            <ul style="margin-bottom: 0;">
                                <li>Review within 48 hours</li>
                                <li>If selected, you'll receive access instructions</li>
                                <li>Lifetime access to the exclusive Root Member community</li>
                                <li>Direct connection to other founding entrepreneurs</li>
                            </ul>
                        </div>
                        
                        <p>We're building something special together - a deep, connected community of ambitious founders who believe in collaboration over competition.</p>
                        
                        <p>Best,<br>The Rhiz Team</p>
                    </div>
                    <div class="footer">
                        Rhiz - Connecting founders with the right people
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Hello {first_name},

            Thank you for applying to become one of our One Hundred Root Members. Your application has been received and will be carefully reviewed by our founding team.

            What happens next:
            - Review within 48 hours
            - If selected, you'll receive access instructions
            - Lifetime access to the exclusive Root Member community
            - Direct connection to other founding entrepreneurs

            We're building something special together - a deep, connected community of ambitious founders who believe in collaboration over competition.

            Best,
            The Rhiz Team

            Rhiz - Connecting founders with the right people
            """
            
            result = self.send_email(to_email, subject, html_content, text_content)
            return result.get('success', False)
            
        except Exception as e:
            logging.error(f"Failed to send application confirmation email: {e}")
            return False

# Initialize global email service
email_service = ResendEmailService()