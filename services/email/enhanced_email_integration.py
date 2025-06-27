"""
Enhanced Email Integration for Direct Sending of AI-Generated Messages
Provides seamless email sending with personalized templates and tracking
"""

import os
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Dict, List, Optional
from models import ContactInteraction

class EnhancedEmailIntegration:
    """Enhanced email service for direct message sending with AI integration"""
    
    def __init__(self, db):
        self.db = db
        self.interaction_model = ContactInteraction(db)
        
        # Enhanced SMTP configurations
        self.smtp_configs = {
            'gmail': {
                'server': 'smtp.gmail.com',
                'port': 587,
                'use_tls': True,
                'auth_required': True
            },
            'outlook': {
                'server': 'smtp-mail.outlook.com', 
                'port': 587,
                'use_tls': True,
                'auth_required': True
            },
            'yahoo': {
                'server': 'smtp.mail.yahoo.com',
                'port': 587,
                'use_tls': True,
                'auth_required': True
            },
            'custom': {
                'server': os.environ.get('CUSTOM_SMTP_SERVER'),
                'port': int(os.environ.get('CUSTOM_SMTP_PORT', 587)),
                'use_tls': os.environ.get('CUSTOM_SMTP_TLS', 'true').lower() == 'true',
                'auth_required': os.environ.get('CUSTOM_SMTP_AUTH', 'true').lower() == 'true'
            }
        }
        
        # Get email configuration
        self.email_address = os.environ.get('EMAIL_ADDRESS')
        self.email_password = os.environ.get('EMAIL_PASSWORD')  # App password for Gmail
        self.sender_name = os.environ.get('SENDER_NAME', 'OuRhizome Network')
        
        # Auto-detect provider
        self.provider = self._detect_email_provider()
        self.smtp_config = self.smtp_configs.get(self.provider, self.smtp_configs['gmail'])
        
    def _detect_email_provider(self) -> str:
        """Auto-detect email provider from email address"""
        if not self.email_address:
            return 'custom'
            
        domain = self.email_address.split('@')[1].lower()
        
        if 'gmail' in domain:
            return 'gmail'
        elif 'outlook' in domain or 'hotmail' in domain or 'live' in domain:
            return 'outlook'
        elif 'yahoo' in domain:
            return 'yahoo'
        else:
            return 'custom'
    
    def is_configured(self) -> bool:
        """Check if email is properly configured"""
        return bool(self.email_address and self.email_password and self.smtp_config['server'])
    
    def get_configuration_status(self) -> Dict[str, any]:
        """Get detailed configuration status for setup assistance"""
        status = {
            'configured': self.is_configured(),
            'email_address': self.email_address,
            'provider': self.provider,
            'smtp_server': self.smtp_config['server'],
            'smtp_port': self.smtp_config['port'],
            'missing_fields': []
        }
        
        if not self.email_address:
            status['missing_fields'].append('EMAIL_ADDRESS')
        if not self.email_password:
            status['missing_fields'].append('EMAIL_PASSWORD')
        if not self.smtp_config['server']:
            status['missing_fields'].append('SMTP_SERVER')
            
        return status
    
    def send_ai_generated_message(self, contact_data: Dict, message_data: Dict, 
                                 user_id: int, goal_data: Optional[Dict] = None) -> Dict[str, any]:
        """Send AI-generated message with enhanced tracking and personalization"""
        
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Email not configured. Please configure your email settings.',
                'config_url': '/email_setup'
            }
        
        # Validate inputs
        if not contact_data.get('email'):
            return {
                'success': False,
                'error': f"No email address found for {contact_data.get('name', 'contact')}"
            }
        
        # Prepare email content
        subject = message_data.get('subject', f"Introduction from {self.sender_name}")
        message_body = message_data.get('message', message_data.get('body', ''))
        
        # Add personalization footer
        footer = self._generate_email_footer(contact_data, goal_data)
        full_message = f"{message_body}\n\n{footer}"
        
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.sender_name} <{self.email_address}>"
            msg['To'] = contact_data['email']
            msg['Subject'] = subject
            
            # Create both plain text and HTML versions
            text_part = MIMEText(full_message, 'plain', 'utf-8')
            html_part = MIMEText(self._convert_to_html(full_message), 'html', 'utf-8')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            result = self._send_email_message(msg, contact_data['email'])
            
            if result['success']:
                # Log successful interaction
                interaction_id = self._log_email_interaction(
                    contact_id=contact_data.get('id'),
                    user_id=user_id,
                    subject=subject,
                    message_body=message_body,
                    status='sent',
                    goal_data=goal_data
                )
                
                result['interaction_id'] = interaction_id
                result['contact_name'] = contact_data.get('name')
                
            return result
            
        except Exception as e:
            logging.error(f"Enhanced email send failed: {e}")
            
            # Log failed interaction
            self._log_email_interaction(
                contact_id=contact_data.get('id'),
                user_id=user_id,
                subject=subject,
                message_body=message_body,
                status='failed',
                error_details=str(e),
                goal_data=goal_data
            )
            
            return {
                'success': False,
                'error': f"Failed to send email: {str(e)}"
            }
    
    def _send_email_message(self, msg: MIMEMultipart, to_email: str) -> Dict[str, any]:
        """Send the prepared email message via SMTP"""
        try:
            # Create secure connection
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                if self.smtp_config['use_tls']:
                    server.starttls(context=context)
                
                if self.smtp_config['auth_required']:
                    server.login(self.email_address, self.email_password)
                
                # Send email
                server.send_message(msg)
                
            logging.info(f"Email sent successfully to {to_email}")
            return {
                'success': True,
                'message': f'Email sent successfully to {to_email}',
                'timestamp': datetime.now().isoformat()
            }
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = "Authentication failed. Check your email credentials."
            if 'gmail' in self.provider:
                error_msg += " For Gmail, use an App Password instead of your regular password."
            logging.error(f"SMTP authentication failed: {e}")
            return {'success': False, 'error': error_msg}
            
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"Recipient email address rejected: {to_email}"
            logging.error(f"SMTP recipients refused: {e}")
            return {'success': False, 'error': error_msg}
            
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error occurred: {str(e)}"
            logging.error(f"SMTP error: {e}")
            return {'success': False, 'error': error_msg}
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logging.error(f"Email send error: {e}")
            return {'success': False, 'error': error_msg}
    
    def _generate_email_footer(self, contact_data: Dict, goal_data: Optional[Dict]) -> str:
        """Generate personalized email footer"""
        footer_lines = [
            "Best regards,",
            self.sender_name
        ]
        
        if goal_data:
            footer_lines.append(f"\nSent via OuRhizome - Goal: {goal_data.get('title', 'Network Expansion')}")
        else:
            footer_lines.append("\nSent via OuRhizome Network Intelligence")
            
        return "\n".join(footer_lines)
    
    def _convert_to_html(self, text_content: str) -> str:
        """Convert plain text to basic HTML format"""
        # Simple conversion - replace line breaks with <br> and wrap in basic HTML
        html_content = text_content.replace('\n', '<br>\n')
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            {html_content}
        </body>
        </html>
        """
    
    def _log_email_interaction(self, contact_id: Optional[int], user_id: int, 
                              subject: str, message_body: str, status: str,
                              goal_data: Optional[Dict] = None, error_details: str = None) -> Optional[int]:
        """Log email interaction with enhanced metadata"""
        try:
            if not contact_id:
                return None
                
            notes = f"Email {status}: {subject}"
            if error_details:
                notes += f" | Error: {error_details}"
            if goal_data:
                notes += f" | Goal: {goal_data.get('title', 'Unknown')}"
            
            return self.interaction_model.create(
                contact_id=contact_id,
                user_id=user_id,
                interaction_type='Email',
                status=status,
                direction='outbound',
                subject=subject,
                summary=message_body[:200] + "..." if len(message_body) > 200 else message_body,
                notes=notes
            )
            
        except Exception as e:
            logging.error(f"Failed to log email interaction: {e}")
            return None
    
    def test_connection(self) -> Dict[str, any]:
        """Test email configuration and connection"""
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Email configuration incomplete',
                'status': self.get_configuration_status()
            }
        
        try:
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_config['server'], self.smtp_config['port']) as server:
                if self.smtp_config['use_tls']:
                    server.starttls(context=context)
                
                if self.smtp_config['auth_required']:
                    server.login(self.email_address, self.email_password)
                
            return {
                'success': True,
                'message': f'Email configuration test successful for {self.email_address}',
                'provider': self.provider
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Connection test failed: {str(e)}',
                'provider': self.provider
            }
    
    def bulk_send_messages(self, message_batch: List[Dict]) -> Dict[str, any]:
        """Send multiple AI-generated messages in batch"""
        results = {
            'total': len(message_batch),
            'sent': 0,
            'failed': 0,
            'details': []
        }
        
        for message_data in message_batch:
            result = self.send_ai_generated_message(
                contact_data=message_data['contact'],
                message_data=message_data['message'],
                user_id=message_data['user_id'],
                goal_data=message_data.get('goal')
            )
            
            if result['success']:
                results['sent'] += 1
            else:
                results['failed'] += 1
            
            results['details'].append({
                'contact': message_data['contact'].get('name'),
                'success': result['success'],
                'error': result.get('error')
            })
        
        return results
    
    def get_email_templates(self) -> List[Dict[str, str]]:
        """Get pre-defined email templates for different scenarios"""
        return [
            {
                'name': 'Warm Introduction',
                'subject': 'Quick introduction - {goal_title}',
                'template': '''Hi {contact_name},

I hope this message finds you well. I came across your profile and was impressed by your work at {company}.

{personalized_message}

I'd love to connect and learn more about your experience in {industry}. Would you be open to a brief coffee chat or call in the coming weeks?

Looking forward to hearing from you.'''
            },
            {
                'name': 'Collaboration Request',
                'subject': 'Potential collaboration opportunity',
                'template': '''Hello {contact_name},

I've been following your work in {industry} and am reaching out regarding a potential collaboration opportunity.

{personalized_message}

I believe there could be strong synergies between our initiatives. Would you be interested in exploring this further?

I'd be happy to share more details over a brief call at your convenience.'''
            },
            {
                'name': 'Expert Advice Request',
                'subject': 'Seeking your expertise on {topic}',
                'template': '''Hi {contact_name},

I hope you're doing well. I'm reaching out because of your expertise in {field}.

{personalized_message}

I would greatly value your perspective on this and would be honored if you'd be willing to share some insights over a brief conversation.

Thank you for considering this request.'''
            }
        ]