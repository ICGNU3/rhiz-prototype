"""
Simplified email integration for direct sending of generated messages.
Uses basic SMTP without complex MIME handling to ensure compatibility.
"""

import smtplib
import os
import logging
from datetime import datetime
from models import ContactInteraction

class SimpleEmailSender:
    def __init__(self, db):
        self.db = db
        self.interaction_model = ContactInteraction(db)
        
        # Email configuration - defaults for common providers
        self.smtp_configs = {
            'gmail': {'server': 'smtp.gmail.com', 'port': 587},
            'outlook': {'server': 'smtp-mail.outlook.com', 'port': 587},
            'yahoo': {'server': 'smtp.mail.yahoo.com', 'port': 587}
        }
        
        # Get configuration from environment or use defaults
        self.email_address = os.environ.get('EMAIL_ADDRESS')
        self.email_password = os.environ.get('EMAIL_PASSWORD')
        self.sender_name = os.environ.get('SENDER_NAME', 'Founder Network')
        
        # Auto-detect provider or use custom settings
        self.smtp_server = os.environ.get('SMTP_SERVER')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        
        # Auto-configure based on email domain if not specified
        if not self.smtp_server and self.email_address:
            domain = self.email_address.split('@')[1].lower()
            if 'gmail' in domain:
                self.smtp_server = self.smtp_configs['gmail']['server']
                self.smtp_port = self.smtp_configs['gmail']['port']
            elif 'outlook' in domain or 'hotmail' in domain:
                self.smtp_server = self.smtp_configs['outlook']['server']
                self.smtp_port = self.smtp_configs['outlook']['port']
            elif 'yahoo' in domain:
                self.smtp_server = self.smtp_configs['yahoo']['server']
                self.smtp_port = self.smtp_configs['yahoo']['port']
            else:
                self.smtp_server = 'smtp.gmail.com'  # Default fallback
                self.smtp_port = 587
    
    def is_configured(self):
        """Check if basic email configuration is present"""
        return bool(self.email_address and self.email_password)
    
    def send_email(self, to_email, subject, message_body, contact_id=None, user_id=None, goal_title=None):
        """Send email using simple SMTP"""
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Email not configured. Please set EMAIL_ADDRESS and EMAIL_PASSWORD environment variables.'
            }
        
        try:
            # Create simple email message
            email_content = f"""From: {self.sender_name} <{self.email_address}>
To: {to_email}
Subject: {subject}
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8

{message_body}
"""
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.sendmail(self.email_address, [to_email], email_content.encode('utf-8'))
            
            # Log successful interaction
            if contact_id and user_id:
                self.interaction_model.create(
                    contact_id=contact_id,
                    user_id=user_id,
                    interaction_type='Email',
                    status='sent',
                    direction='outbound',
                    subject=subject,
                    summary=f"Sent outreach email: {goal_title or 'networking'}",
                    notes=f"Email sent to {to_email}"
                )
            
            logging.info(f"Email sent successfully to {to_email}")
            return {
                'success': True,
                'message': f'Email sent to {to_email}',
                'timestamp': datetime.now().isoformat()
            }
            
        except smtplib.SMTPAuthenticationError:
            error_msg = "Email authentication failed. Check credentials."
            logging.error(f"SMTP auth failed for {self.email_address}")
            return {'success': False, 'error': error_msg}
            
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            logging.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except Exception as e:
            error_msg = f"Email send failed: {str(e)}"
            logging.error(error_msg)
            
            # Log failed interaction
            if contact_id and user_id:
                self.interaction_model.create(
                    contact_id=contact_id,
                    user_id=user_id,
                    interaction_type='Email',
                    status='failed',
                    direction='outbound',
                    subject=subject,
                    summary=f"Failed email: {goal_title or 'networking'}",
                    notes=f"Error: {error_msg}"
                )
            
            return {'success': False, 'error': error_msg}
    
    def test_connection(self):
        """Test email configuration"""
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Email not configured'
            }
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
            
            return {
                'success': True,
                'message': f'Email ready: {self.email_address}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Connection failed: {str(e)}'
            }
    
    def get_configuration_status(self):
        """Get current email configuration status"""
        status = {
            'configured': self.is_configured(),
            'email_address': self.email_address,
            'smtp_server': self.smtp_server,
            'smtp_port': self.smtp_port,
            'sender_name': self.sender_name
        }
        
        if self.is_configured():
            test_result = self.test_connection()
            status['connection_valid'] = test_result['success']
            status['connection_message'] = test_result.get('message', test_result.get('error'))
        
        return status