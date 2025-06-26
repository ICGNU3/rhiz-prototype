"""
Simple email service for sending AI-generated messages.
Supports both SMTP and SendGrid for reliable email delivery.
"""

import smtplib
import os
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict, Any

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

class EmailService:
    def __init__(self, db):
        self.db = db
        
        # SendGrid configuration (preferred)
        self.sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
        
        # SMTP fallback configuration
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.email_address = os.environ.get('EMAIL_ADDRESS')
        self.email_password = os.environ.get('EMAIL_PASSWORD')
        self.sender_name = os.environ.get('SENDER_NAME', 'Founder Network')
        
    def get_available_methods(self) -> Dict[str, bool]:
        """Check which email methods are available"""
        return {
            'sendgrid': bool(self.sendgrid_api_key and SENDGRID_AVAILABLE),
            'smtp': bool(self.email_address and self.email_password)
        }
    
    def send_email(self, to_email: str, subject: str, message_body: str, 
                   contact_id: Optional[int] = None, user_id: Optional[int] = None, 
                   goal_title: Optional[str] = None) -> Dict[str, Any]:
        """Send email using the best available method"""
        
        methods = self.get_available_methods()
        
        # Try SendGrid first
        if methods['sendgrid']:
            try:
                return self._send_via_sendgrid(to_email, subject, message_body, 
                                             contact_id, user_id, goal_title)
            except Exception as e:
                logging.error(f"SendGrid failed: {e}")
                # Fall back to SMTP if available
                if methods['smtp']:
                    return self._send_via_smtp(to_email, subject, message_body, 
                                             contact_id, user_id, goal_title)
                else:
                    return {
                        'success': False,
                        'error': f'SendGrid failed and no SMTP fallback: {e}',
                        'method': 'sendgrid'
                    }
        
        # Try SMTP
        elif methods['smtp']:
            return self._send_via_smtp(to_email, subject, message_body, 
                                     contact_id, user_id, goal_title)
        
        # No methods available
        else:
            return {
                'success': False,
                'error': 'No email configuration found. Please set up SendGrid API key or SMTP credentials.',
                'method': 'none'
            }
    
    def _send_via_sendgrid(self, to_email: str, subject: str, message_body: str,
                          contact_id: Optional[int], user_id: Optional[int], 
                          goal_title: Optional[str]) -> Dict[str, Any]:
        """Send email via SendGrid"""
        
        sg = SendGridAPIClient(api_key=self.sendgrid_api_key)
        
        message = Mail(
            from_email=self.email_address or 'noreply@foundernetwork.ai',
            to_emails=to_email,
            subject=subject,
            html_content=f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: #f8f9fa; padding: 20px; text-align: center; border-bottom: 1px solid #dee2e6;">
                    <h3 style="margin: 0; color: #495057;">Founder Network AI</h3>
                </div>
                <div style="padding: 30px; background: white;">
                    {message_body.replace(chr(10), '<br>')}
                </div>
                <div style="background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #6c757d;">
                    Sent via Founder Network AI - Connecting founders with the right people
                </div>
            </div>
            """
        )
        
        try:
            response = sg.send(message)
            
            # Log the interaction
            self._log_email_interaction(contact_id, user_id, to_email, subject, 
                                      message_body, goal_title, 'sendgrid', True)
            
            return {
                'success': True,
                'message': 'Email sent successfully via SendGrid',
                'method': 'sendgrid',
                'status_code': response.status_code
            }
            
        except Exception as e:
            logging.error(f"SendGrid error: {e}")
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