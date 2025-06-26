"""
Integration & Automation module for external service connections.
Handles calendar integration, CRM sync, social media monitoring, and team collaboration.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from models import Database, Contact, ContactInteraction
try:
    from telegram_integration import TelegramNetworkingBot
    TELEGRAM_INTEGRATION_AVAILABLE = True
except ImportError:
    from telegram_fallback import MockTelegramBot as TelegramNetworkingBot
    TELEGRAM_INTEGRATION_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SlackIntegration:
    """Slack integration for team collaboration and networking updates"""
    
    def __init__(self, db: Database):
        self.db = db
        self.slack_token = os.environ.get('SLACK_BOT_TOKEN')
        self.slack_channel_id = os.environ.get('SLACK_CHANNEL_ID')
        self.client = None
        
        if self.slack_token:
            self.client = WebClient(token=self.slack_token)
            logger.info("Slack client initialized")
        else:
            logger.warning("SLACK_BOT_TOKEN not found - Slack features disabled")
    
    def is_configured(self) -> bool:
        """Check if Slack integration is properly configured"""
        return self.client is not None and self.slack_channel_id is not None
    
    def send_networking_update(self, message: str, contact_name: str = None) -> bool:
        """Send networking update to Slack channel"""
        if not self.is_configured():
            logger.warning("Slack not configured - skipping notification")
            return False
        
        try:
            # Format message with context
            if contact_name:
                formatted_message = f"🤝 *Networking Update*\n📧 {message}\n👤 Contact: {contact_name}"
            else:
                formatted_message = f"🤝 *Networking Update*\n{message}"
            
            response = self.client.chat_postMessage(
                channel=self.slack_channel_id,
                text=formatted_message,
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": formatted_message
                        }
                    }
                ]
            )
            logger.info(f"Slack message sent: {response['ts']}")
            return True
            
        except SlackApiError as e:
            logger.error(f"Slack API error: {e.response['error']}")
            return False
        except Exception as e:
            logger.error(f"Slack integration error: {str(e)}")
            return False
    
    def send_daily_digest(self, user_id: int) -> bool:
        """Send daily networking digest to Slack"""
        if not self.is_configured():
            return False
        
        try:
            # Get recent interactions
            interaction_model = ContactInteraction(self.db)
            recent_interactions = interaction_model.get_timeline(user_id, days_back=1)
            
            # Get contacts needing follow-up
            contact_model = Contact(self.db)
            follow_ups = contact_model.get_follow_ups_due(user_id, days_ahead=1)
            
            # Build digest message
            digest_parts = ["📊 *Daily Networking Digest*"]
            
            if recent_interactions:
                digest_parts.append(f"\n✅ *Recent Activity* ({len(recent_interactions)} interactions)")
                for interaction in recent_interactions[:3]:  # Show top 3
                    digest_parts.append(f"• {interaction.get('summary', 'Contact interaction')}")
            
            if follow_ups:
                digest_parts.append(f"\n⏰ *Follow-ups Due* ({len(follow_ups)} contacts)")
                for contact in follow_ups[:3]:  # Show top 3
                    digest_parts.append(f"• {contact['name']} - {contact.get('follow_up_action', 'Follow up')}")
            
            if not recent_interactions and not follow_ups:
                digest_parts.append("\n💤 Quiet day - consider reaching out to warm contacts")
            
            digest_message = "\n".join(digest_parts)
            
            response = self.client.chat_postMessage(
                channel=self.slack_channel_id,
                text=digest_message,
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": digest_message
                        }
                    }
                ]
            )
            
            logger.info("Daily digest sent to Slack")
            return True
            
        except Exception as e:
            logger.error(f"Daily digest error: {str(e)}")
            return False

class CalendarIntegration:
    """Calendar integration for meeting scheduling and follow-up automation"""
    
    def __init__(self, db: Database):
        self.db = db
        # Calendar integration would require OAuth setup
        # For now, we'll provide the structure and mock functionality
        logger.info("Calendar integration initialized (mock mode)")
    
    def schedule_follow_up(self, contact_id: int, days_ahead: int = 7, note: str = "") -> Dict[str, Any]:
        """Schedule a follow-up reminder"""
        try:
            contact_model = Contact(self.db)
            contact = contact_model.get_by_id(contact_id)
            
            if not contact:
                return {"success": False, "error": "Contact not found"}
            
            follow_up_date = (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
            
            # Update contact with follow-up information
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE contacts 
                SET follow_up_due_date = ?, follow_up_action = ?
                WHERE id = ?
            """, (follow_up_date, note or "Follow up on previous conversation", contact_id))
            
            conn.commit()
            
            return {
                "success": True,
                "message": f"Follow-up scheduled for {contact['name']} on {follow_up_date}",
                "contact_name": contact['name'],
                "follow_up_date": follow_up_date,
                "note": note
            }
            
        except Exception as e:
            logger.error(f"Calendar scheduling error: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_upcoming_networking_events(self, user_id: int, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get upcoming networking-related calendar events (mock data for structure)"""
        # This would integrate with Google Calendar, Outlook, etc.
        # For now, return structured data showing what this would provide
        
        mock_events = [
            {
                "title": "Coffee with Sarah Chen",
                "date": (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                "time": "10:00 AM",
                "contact_name": "Sarah Chen",
                "location": "Blue Bottle Coffee, SOMA",
                "type": "networking_meeting"
            },
            {
                "title": "TechStars Demo Day",
                "date": (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
                "time": "6:00 PM",
                "location": "Pier 27, San Francisco",
                "type": "networking_event"
            }
        ]
        
        return mock_events

class CRMSync:
    """CRM synchronization for external platform integration"""
    
    def __init__(self, db: Database):
        self.db = db
        self.supported_crms = ['hubspot', 'salesforce', 'airtable', 'pipedrive']
        logger.info("CRM sync module initialized")
    
    def export_contacts_to_csv(self, user_id: int) -> str:
        """Export contacts in standard CRM format"""
        try:
            contact_model = Contact(self.db)
            contacts = contact_model.get_all(user_id)
            
            if not contacts:
                return ""
            
            # Generate CSV content
            csv_lines = ["Name,Email,Phone,Company,Title,LinkedIn,Relationship Type,Warmth Level,Priority,Notes,Last Contact,Follow Up Due"]
            
            for contact in contacts:
                line_parts = [
                    contact.get('name', ''),
                    contact.get('email', ''),
                    contact.get('phone', ''),
                    contact.get('company', ''),
                    contact.get('title', ''),
                    contact.get('linkedin', ''),
                    contact.get('relationship_type', ''),
                    contact.get('warmth_label', ''),
                    contact.get('priority_level', ''),
                    contact.get('notes', '').replace(',', ';'),  # Escape commas
                    contact.get('last_interaction_date', ''),
                    contact.get('follow_up_due_date', '')
                ]
                csv_lines.append(','.join(f'"{part}"' for part in line_parts))
            
            return '\n'.join(csv_lines)
            
        except Exception as e:
            logger.error(f"CSV export error: {str(e)}")
            return ""
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status with external CRMs"""
        return {
            "supported_crms": self.supported_crms,
            "active_syncs": [],  # Would list active integrations
            "last_sync": None,
            "export_available": True
        }

class SocialMediaMonitoring:
    """Social media monitoring for contact updates and networking opportunities"""
    
    def __init__(self, db: Database):
        self.db = db
        logger.info("Social media monitoring initialized")
    
    def get_contact_social_updates(self, contact_id: int) -> List[Dict[str, Any]]:
        """Get recent social media updates for a contact (mock structure)"""
        # This would integrate with Twitter API, LinkedIn API, etc.
        # Showing the data structure for what this would provide
        
        contact_model = Contact(self.db)
        contact = contact_model.get_by_id(contact_id)
        
        if not contact:
            return []
        
        # Mock social updates structure
        mock_updates = [
            {
                "platform": "twitter",
                "type": "tweet",
                "content": f"Just closed our Series A! Grateful for all the support from the founder community.",
                "date": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                "engagement": {"likes": 47, "retweets": 12},
                "relevance_score": 0.9,
                "action_suggestion": "Congratulate on Series A funding"
            },
            {
                "platform": "linkedin",
                "type": "job_change",
                "content": f"Excited to announce I'm joining as Head of Product",
                "date": (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
                "relevance_score": 0.8,
                "action_suggestion": "Congratulate on new role"
            }
        ]
        
        return mock_updates
    
    def get_networking_opportunities(self, user_id: int) -> List[Dict[str, Any]]:
        """Find networking opportunities from social media mentions"""
        # Mock networking opportunities
        opportunities = [
            {
                "type": "event_mention",
                "source": "twitter",
                "content": "Speaking at SF Founders Meetup next week - come say hi!",
                "contact_name": "Alex Rodriguez",
                "event_date": (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d'),
                "action_suggestion": "Attend event and connect in person"
            },
            {
                "type": "industry_discussion",
                "source": "linkedin",
                "content": "Great discussion on AI in fintech - looking for more perspectives",
                "contact_name": "Maria Garcia",
                "relevance_score": 0.85,
                "action_suggestion": "Share insights on AI in fintech"
            }
        ]
        
        return opportunities

class AutomationEngine:
    """Central automation engine coordinating all integrations"""
    
    def __init__(self, db: Database):
        self.db = db
        self.slack = SlackIntegration(db)
        
        # Initialize Telegram bot if available
        if TELEGRAM_INTEGRATION_AVAILABLE:
            try:
                self.telegram = TelegramNetworkingBot(db)
            except Exception as e:
                logger.warning(f"Failed to initialize Telegram bot: {e}")
                self.telegram = None
        else:
            self.telegram = None
            
        self.calendar = CalendarIntegration(db)
        self.crm_sync = CRMSync(db)
        self.social_monitor = SocialMediaMonitoring(db)
        logger.info("Automation engine initialized")
    
    def process_interaction_automation(self, contact_id: int, interaction_type: str, user_id: int):
        """Process automation triggers after an interaction"""
        try:
            contact_model = Contact(self.db)
            contact = contact_model.get_by_id(contact_id)
            
            if not contact:
                return
            
            contact_name = contact['name']
            
            # Send notifications
            if interaction_type == 'email_sent':
                self.slack.send_networking_update(
                    f"Email sent successfully", 
                    contact_name
                )
                
                # Send Telegram notification  
                import asyncio
                try:
                    asyncio.create_task(self.telegram.send_notification(
                        f"Email sent successfully", 
                        contact_name
                    ))
                except Exception as e:
                    logger.warning(f"Telegram notification failed: {e}")
                
                # Schedule follow-up reminder
                self.calendar.schedule_follow_up(
                    contact_id, 
                    days_ahead=7, 
                    note="Follow up on email response"
                )
            
            elif interaction_type == 'meeting_scheduled':
                self.slack.send_networking_update(
                    f"Meeting scheduled", 
                    contact_name
                )
            
            elif interaction_type == 'introduction_made':
                self.slack.send_networking_update(
                    f"Introduction facilitated", 
                    contact_name
                )
            
            logger.info(f"Automation processed for {contact_name}: {interaction_type}")
            
        except Exception as e:
            logger.error(f"Automation processing error: {str(e)}")
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations"""
        return {
            "slack": {
                "configured": self.slack.is_configured(),
                "status": "active" if self.slack.is_configured() else "needs_setup"
            },
            "telegram": {
                "configured": self.telegram.is_configured(),
                "status": "active" if self.telegram.is_configured() else "needs_setup"
            },
            "calendar": {
                "configured": False,
                "status": "mock_mode"
            },
            "crm_sync": {
                "configured": True,
                "status": "export_ready",
                "supported_platforms": self.crm_sync.supported_crms
            },
            "social_monitoring": {
                "configured": False,
                "status": "mock_mode"
            }
        }
    
    def run_daily_automation(self, user_id: int):
        """Run daily automation tasks"""
        try:
            # Send daily Slack digest
            self.slack.send_daily_digest(user_id)
            
            # Process follow-up reminders
            contact_model = Contact(self.db)
            overdue_followups = contact_model.get_follow_ups_due(user_id, days_ahead=0)
            
            if overdue_followups:
                overdue_names = [contact['name'] for contact in overdue_followups[:3]]
                self.slack.send_networking_update(
                    f"⚠️ Overdue follow-ups: {', '.join(overdue_names)}"
                )
            
            logger.info(f"Daily automation completed for user {user_id}")
            
        except Exception as e:
            logger.error(f"Daily automation error: {str(e)}")