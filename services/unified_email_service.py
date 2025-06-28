"""
Unified Email Service for Rhiz
Consolidates all email functionality into a single, comprehensive service
"""
import os
import logging
import resend
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class UnifiedEmailService:
    """
    Comprehensive email service consolidating all email functionality
    Supports Resend API (primary) with SMTP fallback and magic link authentication
    """
    
    def __init__(self, db=None):
        self.db = db
        
        # Resend configuration (primary method)
        self.resend_api_key = os.environ.get('RESEND_API_KEY')
        self.from_email = os.environ.get('FROM_EMAIL', 'onboarding@resend.dev')
        
        # SMTP fallback configuration
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.email_address = os.environ.get('EMAIL_ADDRESS')
        self.email_password = os.environ.get('EMAIL_PASSWORD')
        
        # Configuration status
        self.resend_configured = False
        self.smtp_configured = False
        
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize available email services"""
        # Initialize Resend
        if self.resend_api_key:
            try:
                resend.api_key = self.resend_api_key
                self.resend_configured = True
                logger.info("Resend email service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Resend: {e}")
        
        # Check SMTP configuration
        if self.email_address and self.email_password:
            self.smtp_configured = True
            logger.info("SMTP fallback configured")
        
        if not self.resend_configured and not self.smtp_configured:
            logger.warning("No email services configured - email features will be disabled")
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get status of all email services"""
        return {
            'resend': {
                'configured': self.resend_configured,
                'api_key_present': bool(self.resend_api_key),
                'from_email': self.from_email
            },
            'smtp': {
                'configured': self.smtp_configured,
                'server': self.smtp_server,
                'port': self.smtp_port,
                'email_present': bool(self.email_address)
            },
            'any_configured': self.resend_configured or self.smtp_configured
        }
    
    def send_email(self, to_email: str, subject: str, html_content: str = None, 
                   text_content: str = None, **kwargs) -> Dict[str, Any]:
        """
        Send email using best available method
        Falls back from Resend → SMTP if needed
        """
        if not html_content and not text_content:
            return {
                'success': False,
                'error': 'No email content provided',
                'method': 'none'
            }
        
        # Try Resend first (preferred)
        if self.resend_configured:
            result = self._send_with_resend(to_email, subject, html_content, text_content, **kwargs)
            if result['success']:
                return result
            logger.warning(f"Resend failed: {result.get('error')}, trying SMTP fallback")
        
        # Fallback to SMTP
        if self.smtp_configured:
            return self._send_with_smtp(to_email, subject, html_content, text_content, **kwargs)
        
        return {
            'success': False,
            'error': 'No email services configured',
            'method': 'none'
        }
    
    def _send_with_resend(self, to_email: str, subject: str, html_content: str = None, 
                         text_content: str = None, **kwargs) -> Dict[str, Any]:
        """Send email using Resend API"""
        try:
            email_data = {
                "from": f"Rhiz <{self.from_email}>",
                "to": [to_email],
                "subject": subject
            }
            
            if html_content:
                email_data["html"] = html_content
            if text_content:
                email_data["text"] = text_content
            
            # Add optional parameters
            if kwargs.get('reply_to'):
                email_data["reply_to"] = kwargs['reply_to']
            
            response = resend.Emails.send(email_data)
            
            # Log success
            if self.db and kwargs.get('contact_id'):
                self._log_email_interaction(kwargs['contact_id'], kwargs.get('user_id'), 
                                          subject, 'sent', 'resend')
            
            return {
                'success': True,
                'message_id': response.get('id'),
                'method': 'resend',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Resend email failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'method': 'resend'
            }
    
    def _send_with_smtp(self, to_email: str, subject: str, html_content: str = None, 
                       text_content: str = None, **kwargs) -> Dict[str, Any]:
        """Send email using SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_address
            msg['To'] = to_email
            
            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            if html_content:
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            # Log success
            if self.db and kwargs.get('contact_id'):
                self._log_email_interaction(kwargs['contact_id'], kwargs.get('user_id'), 
                                          subject, 'sent', 'smtp')
            
            return {
                'success': True,
                'method': 'smtp',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"SMTP email failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'method': 'smtp'
            }
    
    def send_magic_link(self, to_email: str, magic_token: str, base_url: str = None) -> Dict[str, Any]:
        """Send magic link authentication email"""
        if not base_url:
            base_url = os.environ.get('REPLIT_URL', 'http://localhost:5000')
        
        magic_url = f"{base_url}/api/auth/verify?token={magic_token}"
        
        subject = "Sign in to Rhiz"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Sign in to Rhiz</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #2563eb; margin: 0;">Rhiz</h1>
                <p style="color: #6b7280; margin: 5px 0;">Relationship Intelligence Platform</p>
            </div>
            
            <div style="background: #f8fafc; border-radius: 8px; padding: 30px; margin: 20px 0;">
                <h2 style="color: #1f2937; margin-top: 0;">Welcome back!</h2>
                <p style="color: #4b5563; line-height: 1.6;">
                    Click the button below to sign in to your Rhiz account. This link will expire in 15 minutes.
                </p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{magic_url}" 
                       style="background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; 
                              border-radius: 6px; font-weight: 500; display: inline-block;">
                        Sign in to Rhiz
                    </a>
                </div>
                
                <p style="color: #6b7280; font-size: 14px; margin-bottom: 0;">
                    If the button doesn't work, copy and paste this link into your browser:<br>
                    <a href="{magic_url}" style="color: #2563eb; word-break: break-all;">{magic_url}</a>
                </p>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <p style="color: #9ca3af; font-size: 12px;">
                    This email was sent to {to_email}. If you didn't request this, you can safely ignore it.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Sign in to Rhiz
        
        Welcome back!
        
        Click this link to sign in to your Rhiz account:
        {magic_url}
        
        This link will expire in 15 minutes.
        
        If you didn't request this, you can safely ignore this email.
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def send_ai_outreach(self, to_email: str, contact_name: str, subject: str, 
                        message_body: str, contact_id: int = None, user_id: int = None) -> Dict[str, Any]:
        """Send AI-generated outreach email"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{subject}</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: white; border-radius: 8px; padding: 30px;">
                <div style="white-space: pre-wrap; line-height: 1.6; color: #1f2937;">
{message_body}
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <p style="color: #9ca3af; font-size: 12px;">
                    Sent via Rhiz - Relationship Intelligence Platform
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email, subject, html_content, message_body,
            contact_id=contact_id, user_id=user_id
        )
    
    def send_welcome_email(self, to_email: str, user_name: str = None) -> Dict[str, Any]:
        """Send welcome email to new users"""
        subject = "Welcome to Rhiz!"
        
        greeting = f"Hi {user_name}," if user_name else "Welcome!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to Rhiz</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #2563eb; margin: 0;">Rhiz</h1>
                <p style="color: #6b7280; margin: 5px 0;">Relationship Intelligence Platform</p>
            </div>
            
            <div style="background: #f8fafc; border-radius: 8px; padding: 30px; margin: 20px 0;">
                <h2 style="color: #1f2937; margin-top: 0;">{greeting}</h2>
                <p style="color: #4b5563; line-height: 1.6;">
                    Thank you for joining Rhiz! We're excited to help you build and maintain meaningful relationships
                    through intelligent insights and automation.
                </p>
                
                <h3 style="color: #1f2937;">Getting Started:</h3>
                <ul style="color: #4b5563; line-height: 1.6;">
                    <li>Set your first relationship goal</li>
                    <li>Import your existing contacts</li>
                    <li>Discover AI-powered insights about your network</li>
                    <li>Start building meaningful connections</li>
                </ul>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{os.environ.get('REPLIT_URL', 'http://localhost:5000')}" 
                       style="background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; 
                              border-radius: 6px; font-weight: 500; display: inline-block;">
                        Start Building Relationships
                    </a>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <p style="color: #9ca3af; font-size: 12px;">
                    Questions? Just reply to this email - we're here to help!
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to Rhiz!
        
        {greeting}
        
        Thank you for joining Rhiz! We're excited to help you build and maintain meaningful relationships
        through intelligent insights and automation.
        
        Getting Started:
        - Set your first relationship goal
        - Import your existing contacts  
        - Discover AI-powered insights about your network
        - Start building meaningful connections
        
        Visit {os.environ.get('REPLIT_URL', 'http://localhost:5000')} to get started.
        
        Questions? Just reply to this email - we're here to help!
        """
        
        return self.send_email(to_email, subject, html_content, text_content)
    
    def _log_email_interaction(self, contact_id: int, user_id: int, subject: str, 
                              status: str, method: str):
        """Log email interaction to database"""
        if not self.db:
            return
        
        try:
            with self.db.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO contact_interactions 
                    (contact_id, user_id, interaction_type, interaction_date, notes, status)
                    VALUES (%s, %s, 'email', %s, %s, %s)
                ''', (contact_id, user_id, datetime.now(), f"Email: {subject} (via {method})", status))
        except Exception as e:
            logger.error(f"Failed to log email interaction: {e}")

# Global instance for easy import
email_service = None

def get_email_service(db=None):
    """Get or create global email service instance"""
    global email_service
    if email_service is None:
        email_service = UnifiedEmailService(db)
    return email_service