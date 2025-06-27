"""
Email integration for direct sending of generated messages.
Supports SMTP configuration and email sending with tracking.
"""

import smtplib
import os
import logging
from datetime import datetime
from models import ContactInteraction

class EmailSender:
    def __init__(self, db):
        self.db = db
        self.interaction_model = ContactInteraction(db)
        
        # Email configuration from environment variables
        self.smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.email_address = os.environ.get('EMAIL_ADDRESS')
        self.email_password = os.environ.get('EMAIL_PASSWORD')
        self.sender_name = os.environ.get('SENDER_NAME', 'Founder Network')
        
    def validate_configuration(self):
        """Check if email configuration is complete"""
        missing_configs = []
        
        if not self.email_address:
            missing_configs.append('EMAIL_ADDRESS')
        if not self.email_password:
            missing_configs.append('EMAIL_PASSWORD')
        
        return missing_configs
    
    def send_email(self, to_email, subject, message_body, contact_id=None, user_id=None, goal_title=None):
        """Send email and log the interaction"""
        try:
            # Validate configuration
            missing_configs = self.validate_configuration()
            if missing_configs:
                raise ValueError(f"Missing email configuration: {', '.join(missing_configs)}")
            
            # Create message using simple string formatting
            from_header = f"{self.sender_name} <{self.email_address}>"
            
            # Build email message
            email_message = f"""From: {from_header}
To: {to_email}
Subject: {subject}

{message_body}"""
            
            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable security
            server.login(self.email_address, self.email_password)
            
            # Send email
            server.sendmail(self.email_address, [to_email], email_message)
            server.quit()
            
            # Log successful interaction
            if contact_id and user_id:
                self.interaction_model.create(
                    contact_id=contact_id,
                    user_id=user_id,
                    interaction_type='Email',
                    status='sent',
                    direction='outbound',
                    subject=subject,
                    summary=f"Sent outreach email regarding: {goal_title or 'networking'}",
                    notes=f"Email sent to {to_email} successfully"
                )
            
            logging.info(f"Email sent successfully to {to_email}")
            return {
                'success': True,
                'message': f'Email sent successfully to {to_email}',
                'timestamp': datetime.now().isoformat()
            }
            
        except smtplib.SMTPAuthenticationError:
            error_msg = "Email authentication failed. Please check your email credentials."
            logging.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except smtplib.SMTPRecipientsRefused:
            error_msg = f"Invalid recipient email address: {to_email}"
            logging.error(error_msg)
            return {'success': False, 'error': error_msg}
            
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
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
                    summary=f"Failed to send email regarding: {goal_title or 'networking'}",
                    notes=f"Error: {error_msg}"
                )
            
            return {'success': False, 'error': error_msg}
    
    def send_bulk_emails(self, email_list, subject_template, message_template, user_id=None, goal_title=None):
        """Send emails to multiple contacts"""
        results = {
            'total_sent': 0,
            'total_failed': 0,
            'details': []
        }
        
        for email_data in email_list:
            try:
                # Personalize subject and message
                contact_name = email_data.get('contact_name', 'there')
                to_email = email_data.get('email')
                contact_id = email_data.get('contact_id')
                
                if not to_email:
                    results['details'].append({
                        'contact_name': contact_name,
                        'status': 'skipped',
                        'reason': 'No email address'
                    })
                    continue
                
                # Personalize templates
                personalized_subject = subject_template.format(
                    contact_name=contact_name,
                    goal_title=goal_title or ''
                )
                
                personalized_message = message_template.format(
                    contact_name=contact_name,
                    goal_title=goal_title or ''
                )
                
                # Send email
                result = self.send_email(
                    to_email=to_email,
                    subject=personalized_subject,
                    message_body=personalized_message,
                    contact_id=contact_id,
                    user_id=user_id,
                    goal_title=goal_title
                )
                
                if result['success']:
                    results['total_sent'] += 1
                    results['details'].append({
                        'contact_name': contact_name,
                        'email': to_email,
                        'status': 'sent',
                        'timestamp': result['timestamp']
                    })
                else:
                    results['total_failed'] += 1
                    results['details'].append({
                        'contact_name': contact_name,
                        'email': to_email,
                        'status': 'failed',
                        'error': result['error']
                    })
                    
            except Exception as e:
                results['total_failed'] += 1
                results['details'].append({
                    'contact_name': email_data.get('contact_name', 'Unknown'),
                    'status': 'failed',
                    'error': str(e)
                })
        
        return results
    
    def test_email_configuration(self):
        """Test email configuration by sending a test email"""
        try:
            missing_configs = self.validate_configuration()
            if missing_configs:
                return {
                    'success': False,
                    'error': f"Missing configuration: {', '.join(missing_configs)}"
                }
            
            # Test SMTP connection only if we have credentials
            if self.email_address and self.email_password:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.quit()
                
                return {
                    'success': True,
                    'message': f'Email configuration valid. Ready to send from {self.email_address}'
                }
            else:
                return {
                    'success': False,
                    'error': 'Email credentials not configured'
                }
            
        except smtplib.SMTPAuthenticationError:
            return {
                'success': False,
                'error': 'Authentication failed. Please check email credentials.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Configuration test failed: {str(e)}'
            }
    
    def get_email_templates(self):
        """Get common email templates for different scenarios"""
        templates = {
            'networking': {
                'subject': 'Introduction and Potential Collaboration - {goal_title}',
                'body': """Hi {contact_name},

I hope this email finds you well. I'm reaching out because I'm currently {goal_title} and thought you might have valuable insights or potential interest in collaborating.

Would you be open to a brief conversation to explore potential synergies?

Best regards,
{sender_name}"""
            },
            'fundraising': {
                'subject': 'Investment Opportunity - {goal_title}',
                'body': """Dear {contact_name},

I hope you're doing well. I'm reaching out because I'm currently {goal_title} and believe this opportunity might align with your investment focus.

Would you be available for a brief call to discuss the opportunity?

Best regards,
{sender_name}"""
            },
            'partnership': {
                'subject': 'Partnership Opportunity - {goal_title}',
                'body': """Hi {contact_name},

I hope this message finds you well. I'm working on {goal_title} and think there could be interesting partnership opportunities between our organizations.

Would you be open to exploring potential collaboration?

Best regards,
{sender_name}"""
            },
            'advisory': {
                'subject': 'Advisory Opportunity - {goal_title}',
                'body': """Dear {contact_name},

I hope you're doing well. I'm currently {goal_title} and would greatly value your expertise and guidance.

Would you be interested in discussing a potential advisory role?

Best regards,
{sender_name}"""
            }
        }
        
        return templates