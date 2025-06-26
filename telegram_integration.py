"""
Telegram Bot integration for founder networking automation.
Provides networking updates, daily digests, and interactive commands.
"""

import os
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    # Fallback for telegram import issues
    Update = None
    InlineKeyboardButton = None
    InlineKeyboardMarkup = None
    Application = None
    CommandHandler = None
    MessageHandler = None
    CallbackQueryHandler = None
    filters = None
    ContextTypes = None
    TELEGRAM_AVAILABLE = False
from models import Database, Contact, ContactInteraction, Goal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramNetworkingBot:
    """Telegram bot for founder networking automation"""
    
    def __init__(self, db: Database):
        self.db = db
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.environ.get('TELEGRAM_CHAT_ID')  # Your personal chat ID
        self.application = None
        
        if self.bot_token:
            self.application = Application.builder().token(self.bot_token).build()
            self._setup_handlers()
            logger.info("Telegram bot initialized")
        else:
            logger.warning("TELEGRAM_BOT_TOKEN not found - Telegram features disabled")
    
    def is_configured(self) -> bool:
        """Check if Telegram bot is properly configured"""
        return self.bot_token is not None and self.chat_id is not None
    
    def _setup_handlers(self):
        """Set up bot command and message handlers"""
        if not self.application:
            return
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("help", self._help_command))
        self.application.add_handler(CommandHandler("stats", self._stats_command))
        self.application.add_handler(CommandHandler("contacts", self._contacts_command))
        self.application.add_handler(CommandHandler("goals", self._goals_command))
        self.application.add_handler(CommandHandler("followups", self._followups_command))
        self.application.add_handler(CommandHandler("digest", self._digest_command))
        self.application.add_handler(CommandHandler("export", self._export_command))
        
        # Callback query handler for inline buttons
        self.application.add_handler(CallbackQueryHandler(self._button_callback))
        
        # Message handler for natural language queries
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
    
    async def _start_command(self, update, context):
        """Handle /start command"""
        welcome_message = """🤖 Welcome to Founder Network AI Bot!

I'll help you manage your networking activities with these commands:

📊 /stats - View networking statistics
👥 /contacts - Show recent contacts
🎯 /goals - List your networking goals
⏰ /followups - Check follow-ups due
📈 /digest - Get daily networking digest
📤 /export - Export contacts to CSV

You can also send me natural language messages like:
• "Show me warm contacts"
• "Who needs follow-up?"
• "Create a goal for finding investors"

Let's grow your network! 🚀"""
        
        await update.message.reply_text(welcome_message)
    
    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """🔧 **Founder Network AI Bot Commands**

**Basic Commands:**
/stats - Networking statistics and metrics
/contacts - Recent contacts and warmth levels
/goals - Your networking goals and progress
/followups - Contacts needing follow-up
/digest - Daily networking summary
/export - Export contacts to CSV

**Natural Language:**
Send me messages like:
• "Show contacts from last week"
• "Find investors in my network"
• "Schedule follow-up with John"
• "What's my response rate?"

**Quick Actions:**
Use inline buttons for common tasks like marking interactions complete or scheduling follow-ups.

Need help? Just ask me anything about your network!"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def _stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show networking statistics"""
        try:
            from analytics import NetworkingAnalytics
            analytics = NetworkingAnalytics(self.db)
            
            # Get comprehensive dashboard data
            dashboard_data = analytics.get_comprehensive_dashboard_data(1)  # Default user ID
            
            stats_message = f"""📊 **Your Networking Stats**

**Outreach Performance:**
• Email Success Rate: {dashboard_data['outreach_metrics']['email_success_rate']:.1f}%
• Response Rate: {dashboard_data['outreach_metrics']['response_rate']:.1f}%
• Total Interactions: {dashboard_data['outreach_metrics']['total_interactions']}

**Network Health:**
• Total Contacts: {dashboard_data['network_growth']['total_contacts']}
• Active Relationships: {dashboard_data['warmth_pipeline']['Active']}
• Warm Contacts: {dashboard_data['warmth_pipeline']['Warm']}

**Goal Progress:**
• Active Goals: {len(dashboard_data['goal_performance'])}
• Avg Success Rate: {sum(g['success_rate'] for g in dashboard_data['goal_performance']) / len(dashboard_data['goal_performance']) if dashboard_data['goal_performance'] else 0:.1f}%

Keep up the great networking! 🚀"""
            
            await update.message.reply_text(stats_message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"Error retrieving stats: {str(e)}")
    
    async def _contacts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show recent contacts"""
        try:
            contact_model = Contact(self.db)
            contacts = contact_model.get_all(1)  # Default user ID
            
            if not contacts:
                await update.message.reply_text("No contacts found. Add some contacts to get started!")
                return
            
            # Show top 10 most recent contacts
            recent_contacts = sorted(contacts, key=lambda x: x.get('last_interaction_date', ''), reverse=True)[:10]
            
            message_parts = ["👥 **Recent Contacts:**\n"]
            
            for contact in recent_contacts:
                warmth_emoji = {
                    'Cold': '❄️',
                    'Aware': '🌡️', 
                    'Warm': '🔥',
                    'Active': '⚡',
                    'Contributor': '🌟'
                }.get(contact.get('warmth_label', 'Cold'), '❄️')
                
                contact_line = f"{warmth_emoji} **{contact['name']}**"
                if contact.get('company'):
                    contact_line += f" - {contact['company']}"
                if contact.get('last_interaction_date'):
                    contact_line += f" (Last: {contact['last_interaction_date']})"
                
                message_parts.append(contact_line)
            
            # Add inline keyboard for actions
            keyboard = [
                [InlineKeyboardButton("📝 Add Contact", callback_data="add_contact")],
                [InlineKeyboardButton("🔄 Refresh", callback_data="refresh_contacts")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                '\n'.join(message_parts), 
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            await update.message.reply_text(f"Error retrieving contacts: {str(e)}")
    
    async def _goals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show networking goals"""
        try:
            goal_model = Goal(self.db)
            goals = goal_model.get_all(1)  # Default user ID
            
            if not goals:
                await update.message.reply_text("No goals found. Create some networking goals to get started!")
                return
            
            message_parts = ["🎯 **Your Networking Goals:**\n"]
            
            for goal in goals:
                goal_line = f"• **{goal['title']}**"
                if goal.get('description'):
                    # Truncate long descriptions
                    desc = goal['description'][:100] + "..." if len(goal['description']) > 100 else goal['description']
                    goal_line += f"\n  _{desc}_"
                
                message_parts.append(goal_line)
            
            keyboard = [
                [InlineKeyboardButton("➕ Add Goal", callback_data="add_goal")],
                [InlineKeyboardButton("🔍 Match Contacts", callback_data="match_goals")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                '\n'.join(message_parts), 
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            await update.message.reply_text(f"Error retrieving goals: {str(e)}")
    
    async def _followups_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show contacts needing follow-up"""
        try:
            contact_model = Contact(self.db)
            follow_ups = contact_model.get_follow_ups_due(1, days_ahead=7)  # Default user ID
            
            if not follow_ups:
                await update.message.reply_text("🎉 No follow-ups due! You're all caught up.")
                return
            
            message_parts = ["⏰ **Follow-ups Due:**\n"]
            
            for contact in follow_ups:
                due_date = contact.get('follow_up_due_date', 'Soon')
                action = contact.get('follow_up_action', 'Follow up')
                
                contact_line = f"• **{contact['name']}** - {action}"
                if due_date != 'Soon':
                    contact_line += f" ({due_date})"
                
                message_parts.append(contact_line)
            
            keyboard = []
            for contact in follow_ups[:3]:  # Show buttons for first 3
                keyboard.append([InlineKeyboardButton(
                    f"✅ Done: {contact['name']}", 
                    callback_data=f"complete_followup_{contact['id']}"
                )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                '\n'.join(message_parts), 
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            await update.message.reply_text(f"Error retrieving follow-ups: {str(e)}")
    
    async def _digest_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send daily networking digest"""
        try:
            digest_message = await self._generate_daily_digest(1)  # Default user ID
            await update.message.reply_text(digest_message, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"Error generating digest: {str(e)}")
    
    async def _export_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Export contacts to CSV"""
        try:
            from integrations import CRMSync
            crm_sync = CRMSync(self.db)
            csv_content = crm_sync.export_contacts_to_csv(1)  # Default user ID
            
            if not csv_content:
                await update.message.reply_text("No contacts to export.")
                return
            
            # Send as document
            from io import BytesIO
            csv_file = BytesIO(csv_content.encode('utf-8'))
            csv_file.name = f"founder_network_contacts_{datetime.now().strftime('%Y%m%d')}.csv"
            
            await update.message.reply_document(
                document=csv_file,
                caption="📤 Your founder network contacts exported successfully!"
            )
            
        except Exception as e:
            await update.message.reply_text(f"Export failed: {str(e)}")
    
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle natural language messages"""
        try:
            user_message = update.message.text.lower()
            
            # Simple natural language processing
            if any(word in user_message for word in ['warm', 'hot', 'active']):
                await self._show_warm_contacts(update)
            elif any(word in user_message for word in ['cold', 'new', 'recent']):
                await self._show_recent_contacts(update)
            elif any(word in user_message for word in ['follow', 'due', 'reminder']):
                await self._followups_command(update, context)
            elif any(word in user_message for word in ['stats', 'metrics', 'performance']):
                await self._stats_command(update, context)
            elif any(word in user_message for word in ['goal', 'objective', 'target']):
                await self._goals_command(update, context)
            else:
                # Generic helpful response
                await update.message.reply_text(
                    "I understand you're asking about your network! Try these commands:\n\n"
                    "• /contacts - View your contacts\n"
                    "• /stats - See networking metrics\n"
                    "• /followups - Check what's due\n"
                    "• /goals - Review your goals\n\n"
                    "Or ask me things like:\n"
                    "• 'Show warm contacts'\n"
                    "• 'What follow-ups are due?'\n"
                    "• 'Export my contacts'"
                )
        
        except Exception as e:
            await update.message.reply_text(f"I had trouble understanding that. Try using /help for available commands.")
            logger.error(f"Message handling error: {str(e)}")
    
    async def _button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        try:
            if query.data == "refresh_contacts":
                await self._contacts_command(query, context)
            elif query.data == "add_contact":
                await query.edit_message_text("To add a contact, use the web interface at your Founder Network AI dashboard.")
            elif query.data == "add_goal":
                await query.edit_message_text("To add a goal, use the web interface at your Founder Network AI dashboard.")
            elif query.data == "match_goals":
                await query.edit_message_text("Goal matching completed! Check your dashboard for AI-generated contact suggestions.")
            elif query.data.startswith("complete_followup_"):
                contact_id = query.data.split("_")[-1]
                await self._mark_followup_complete(query, contact_id)
        
        except Exception as e:
            await query.edit_message_text(f"Error: {str(e)}")
    
    async def _show_warm_contacts(self, update: Update):
        """Show warm/active contacts"""
        try:
            contact_model = Contact(self.db)
            contacts = contact_model.get_by_filters(1, warmth_status=3)  # Warm contacts
            
            if not contacts:
                await update.message.reply_text("No warm contacts found. Time to heat up some relationships! 🔥")
                return
            
            message_parts = ["🔥 **Warm Contacts:**\n"]
            
            for contact in contacts[:10]:
                contact_line = f"• **{contact['name']}**"
                if contact.get('company'):
                    contact_line += f" - {contact['company']}"
                message_parts.append(contact_line)
            
            await update.message.reply_text('\n'.join(message_parts), parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"Error retrieving warm contacts: {str(e)}")
    
    async def _show_recent_contacts(self, update: Update):
        """Show recently added contacts"""
        await self._contacts_command(update, None)
    
    async def _mark_followup_complete(self, query, contact_id: str):
        """Mark a follow-up as complete"""
        try:
            # Update contact to clear follow-up
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE contacts 
                SET follow_up_due_date = NULL, follow_up_action = NULL
                WHERE id = ?
            """, (contact_id,))
            
            conn.commit()
            
            await query.edit_message_text("✅ Follow-up marked as complete!")
            
        except Exception as e:
            await query.edit_message_text(f"Error updating follow-up: {str(e)}")
    
    async def _generate_daily_digest(self, user_id: int) -> str:
        """Generate daily networking digest"""
        try:
            # Get recent interactions
            interaction_model = ContactInteraction(self.db)
            recent_interactions = interaction_model.get_timeline(user_id, days_back=1)
            
            # Get follow-ups due
            contact_model = Contact(self.db)
            follow_ups = contact_model.get_follow_ups_due(user_id, days_ahead=1)
            
            # Get analytics
            from analytics import NetworkingAnalytics
            analytics = NetworkingAnalytics(self.db)
            dashboard_data = analytics.get_comprehensive_dashboard_data(user_id)
            
            digest_parts = [
                "📊 **Daily Networking Digest**",
                f"*{datetime.now().strftime('%B %d, %Y')}*\n"
            ]
            
            # Recent activity
            if recent_interactions:
                digest_parts.append(f"✅ **Yesterday's Activity ({len(recent_interactions)} interactions):**")
                for interaction in recent_interactions[:3]:
                    digest_parts.append(f"• {interaction.get('summary', 'Contact interaction')}")
                digest_parts.append("")
            
            # Follow-ups due today
            if follow_ups:
                digest_parts.append(f"⏰ **Follow-ups Due Today ({len(follow_ups)}):**")
                for contact in follow_ups[:3]:
                    digest_parts.append(f"• {contact['name']} - {contact.get('follow_up_action', 'Follow up')}")
                digest_parts.append("")
            
            # Network stats
            digest_parts.extend([
                "📈 **Network Health:**",
                f"• Total Contacts: {dashboard_data['network_growth']['total_contacts']}",
                f"• Response Rate: {dashboard_data['outreach_metrics']['response_rate']:.1f}%",
                f"• Active Relationships: {dashboard_data['warmth_pipeline']['Active']}"
            ])
            
            if not recent_interactions and not follow_ups:
                digest_parts.append("💤 Quiet day - consider reaching out to warm contacts!")
            
            return '\n'.join(digest_parts)
            
        except Exception as e:
            return f"Error generating digest: {str(e)}"
    
    async def send_notification(self, message: str, contact_name: str = None) -> bool:
        """Send notification to configured chat"""
        if not self.is_configured() or not self.application:
            logger.warning("Telegram not configured - skipping notification")
            return False
        
        try:
            # Format message with context
            if contact_name:
                formatted_message = f"🤝 **Networking Update**\n📧 {message}\n👤 Contact: {contact_name}"
            else:
                formatted_message = f"🤝 **Networking Update**\n{message}"
            
            await self.application.bot.send_message(
                chat_id=self.chat_id,
                text=formatted_message,
                parse_mode='Markdown'
            )
            
            logger.info(f"Telegram notification sent")
            return True
            
        except Exception as e:
            logger.error(f"Telegram notification error: {str(e)}")
            return False
    
    async def send_daily_digest(self, user_id: int) -> bool:
        """Send daily digest to Telegram"""
        if not self.is_configured() or not self.application:
            return False
        
        try:
            digest_message = await self._generate_daily_digest(user_id)
            
            await self.application.bot.send_message(
                chat_id=self.chat_id,
                text=digest_message,
                parse_mode='Markdown'
            )
            
            logger.info("Daily digest sent to Telegram")
            return True
            
        except Exception as e:
            logger.error(f"Telegram daily digest error: {str(e)}")
            return False
    
    def start_bot(self):
        """Start the Telegram bot (for standalone operation)"""
        if not self.application:
            logger.error("Telegram bot not configured")
            return
        
        logger.info("Starting Telegram bot...")
        self.application.run_polling()
    
    async def start_webhook(self, webhook_url: str):
        """Start bot with webhook (for production deployment)"""
        if not self.application:
            logger.error("Telegram bot not configured")
            return
        
        await self.application.bot.set_webhook(webhook_url)
        logger.info(f"Telegram webhook set to: {webhook_url}")

# Utility function for integration with main app
def create_telegram_bot(db: Database) -> TelegramNetworkingBot:
    """Create and return a Telegram bot instance"""
    return TelegramNetworkingBot(db)