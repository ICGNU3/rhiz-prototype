"""
Simple email service for sending AI-generated messages.
Supports both SMTP and Resend for reliable email delivery.
"""

import smtplib
import os
import logging
import resend
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict, Any

try:
    resend_available = True
except ImportError:
    resend_available = False

class EmailService:
    def __init__(self, db):
        self.db = db
        
        # Resend configuration (preferred)
        self.resend_api_key = os.environ.get('RESEND_API_KEY')
        self.from_email = os.environ.get('FROM_EMAIL', 'info@ourhizome.com')
        
        # SMTP fallback configuration
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.email_address = os.environ.get('EMAIL_ADDRESS')
        self.email_password = os.environ.get('EMAIL_PASSWORD')
        self.sender_name = os.environ.get('SENDER_NAME', 'OuRhizome')
        
        # Initialize Resend if API key is available
        if self.resend_api_key:
            resend.api_key = self.resend_api_key
        
    def get_available_methods(self) -> Dict[str, bool]:
        """Check which email methods are available"""
        return {
            'resend': bool(self.resend_api_key and resend_available),
            'smtp': bool(self.email_address and self.email_password)
        }
    
    def send_email(self, to_email: str, subject: str, message_body: str, 
                   contact_id: Optional[int] = None, user_id: Optional[int] = None, 
                   goal_title: Optional[str] = None) -> Dict[str, Any]:
        """Send email using the best available method"""
        
        methods = self.get_available_methods()
        
        # Try Resend first
        if methods['resend']:
            try:
                return self._send_via_resend(to_email, subject, message_body, 
                                           contact_id, user_id, goal_title)
            except Exception as e:
                logging.error(f"Resend failed: {e}")
                # Fall back to SMTP if available
                if methods['smtp']:
                    return self._send_via_smtp(to_email, subject, message_body, 
                                             contact_id, user_id, goal_title)
                else:
                    return {
                        'success': False,
                        'error': f'Resend failed and no SMTP fallback: {e}',
                        'method': 'resend'
                    }
        
        # Try SMTP
        elif methods['smtp']:
            return self._send_via_smtp(to_email, subject, message_body, 
                                     contact_id, user_id, goal_title)
        
        # No methods available
        else:
            return {
                'success': False,
                'error': 'No email configuration found. Please set up RESEND_API_KEY or SMTP credentials.',
                'method': 'none'
            }
    
    def _send_via_resend(self, to_email: str, subject: str, message_body: str,
                        contact_id: Optional[int], user_id: Optional[int], 
                        goal_title: Optional[str]) -> Dict[str, Any]:
        """Send email via Resend"""
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #f8f9fa; padding: 20px; text-align: center; border-bottom: 1px solid #dee2e6;">
                <h3 style="margin: 0; color: #495057;">OuRhizome</h3>
            </div>
            <div style="padding: 30px; background: white;">
                {message_body.replace(chr(10), '<br>')}
            </div>
            <div style="background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #6c757d;">
                Sent via OuRhizome - Connecting founders with the right people
            </div>
        </div>
        """
        
        email_data = {
            "from": f"OuRhizome <{self.from_email}>",
            "to": [to_email],
            "subject": subject,
            "html": html_content,
            "text": message_body
        }
        
        try:
            response = resend.Emails.send(email_data)
            
            # Log the interaction
            self._log_email_interaction(contact_id, user_id, to_email, subject, 
                                      message_body, goal_title or '', 'resend', True)
            
            return {
                'success': True,
                'message': 'Email sent successfully via Resend',
                'method': 'resend',
                'email_id': response.get('id'),
                'response': response
            }
            
        except Exception as e:
            logging.error(f"Resend error: {e}")
            raise e
    
    def _send_via_smtp(self, to_email: str, subject: str, message_body: str,
                      contact_id: Optional[int], user_id: Optional[int], 
                      goal_title: Optional[str]) -> Dict[str, Any]:
        """Send email via SMTP"""
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.sender_name} <{self.email_address}>"
            msg['To'] = to_email
            
            # Create HTML and plain text versions
            text_content = message_body
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    {message_body.replace(chr(10), '<br>')}
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                    <p style="font-size: 12px; color: #999; text-align: center;">
                        Sent via Founder Network AI
                    </p>
                </div>
            </body>
            </html>
            """
            
            # Attach parts
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.send_message(msg)
            server.quit()
            
            # Log the interaction
            self._log_email_interaction(contact_id, user_id, to_email, subject, 
                                      message_body, goal_title, 'smtp', True)
            
            return {
                'success': True,
                'message': 'Email sent successfully via SMTP',
                'method': 'smtp'
            }
            
        except Exception as e:
            logging.error(f"SMTP error: {e}")
            
            # Log failed attempt
            self._log_email_interaction(contact_id, user_id, to_email, subject, 
                                      message_body, goal_title, 'smtp', False, str(e))
            
            return {
                'success': False,
                'error': f'SMTP error: {e}',
                'method': 'smtp'
            }
    
    def _log_email_interaction(self, contact_id: Optional[int], user_id: Optional[int], 
                              to_email: str, subject: str, message_body: str,
                              goal_title: Optional[str], method: str, 
                              success: bool, error: Optional[str] = None):
        """Log email interaction to database"""
        
        try:
            cursor = self.db.cursor()
            
            interaction_type = 'email_sent' if success else 'email_failed'
            notes = f"Email via {method}"
            if goal_title:
                notes += f" for goal: {goal_title}"
            if error:
                notes += f" | Error: {error}"
            
            cursor.execute("""
                INSERT INTO contact_interactions 
                (contact_id, user_id, interaction_type, notes, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                contact_id, 
                user_id or 1,  # Default user
                interaction_type,
                notes,
                datetime.now().isoformat()
            ))
            
            self.db.commit()
            
        except Exception as e:
            logging.error(f"Failed to log email interaction: {e}")
    
    def get_email_templates(self) -> Dict[str, Dict[str, str]]:
        """Get common email templates"""
        return {
            'warm_intro': {
                'subject': 'Quick connection from {sender_name}',
                'template': """Hi {contact_name},

I hope this message finds you well. I came across your profile and was impressed by your work at {company}.

{personalized_message}

I'd love to connect and explore potential synergies between our work. Would you be open to a brief conversation?

Best regards,
{sender_name}"""
            },
            'collaboration': {
                'subject': 'Collaboration opportunity - {goal_title}',
                'template': """Hello {contact_name},

I'm reaching out regarding an exciting collaboration opportunity that aligns with your expertise in {industry}.

{personalized_message}

I believe there could be mutual value in connecting. Would you be interested in exploring this further?

Best,
{sender_name}"""
            },
            'follow_up': {
                'subject': 'Following up on our {goal_title} discussion',
                'template': """Hi {contact_name},

Following up on our recent conversation about {goal_title}.

{personalized_message}

Looking forward to continuing our discussion.

Best regards,
{sender_name}"""
            }
        }
    
    def test_email_configuration(self) -> Dict[str, Any]:
        """Test email configuration"""
        methods = self.get_available_methods()
        
        if not any(methods.values()):
            return {
                'success': False,
                'message': 'No email configuration found',
                'methods': methods
            }
        
        # Test with a dummy email (won't actually send)
        test_subject = "Founder Network AI - Configuration Test"
        test_message = "This is a test message to verify email configuration."
        
        return {
            'success': True,
            'message': 'Email configuration is valid',
            'methods': methods,
            'available_templates': list(self.get_email_templates().keys())
        }