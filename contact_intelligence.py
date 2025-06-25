import re
import json
from datetime import datetime, timedelta
from models import Database, Contact, ContactInteraction, ContactRelationship, OutreachSuggestion, ContactIntelligence
from openai_utils import OpenAIUtils
import logging

class ContactNLP:
    """Natural Language Processing for contact queries and commands"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.db = Database()
        self.contact_intel = ContactIntelligence(self.db)
        self.openai_utils = OpenAIUtils()
    
    def process_command(self, command_text):
        """Process natural language commands and return appropriate responses"""
        command = command_text.lower().strip()
        
        # Pattern matching for common commands
        if self._matches_pattern(command, ["show", "list", "get"], ["warm", "allies", "ally"]):
            return self._get_warm_allies(command)
        
        elif self._matches_pattern(command, ["show", "list", "get"], ["follow up", "follow-up", "due"]):
            return self._get_follow_ups_due(command)
        
        elif self._matches_pattern(command, ["tell me about", "summarize", "summary"], []):
            return self._summarize_contact(command)
        
        elif self._matches_pattern(command, ["who should i", "suggest", "recommend"], ["reach out", "contact", "follow up"]):
            return self._get_outreach_suggestions()
        
        elif self._matches_pattern(command, ["pipeline", "kanban", "stages"], []):
            return self._get_pipeline_view()
        
        elif self._matches_pattern(command, ["cold", "contacts"], []):
            return self._get_contacts_by_warmth("Cold")
        
        elif self._matches_pattern(command, ["high priority", "priority"], []):
            return self._get_high_priority_contacts()
        
        elif self._matches_pattern(command, ["investors", "investor"], []):
            return self._get_contacts_by_type("Investor")
        
        elif self._matches_pattern(command, ["collaborators", "collaborator"], []):
            return self._get_contacts_by_type("Collaborator")
        
        elif self._matches_pattern(command, ["timeline", "history", "recent"], []):
            return self._get_interaction_timeline(command)
        
        elif self._matches_pattern(command, ["introduction", "introduce"], []):
            return self._suggest_introductions(command)
        
        else:
            return self._fallback_ai_response(command)
    
    def _matches_pattern(self, command, action_words, context_words):
        """Check if command matches pattern with action and context words"""
        has_action = any(word in command for word in action_words)
        has_context = not context_words or any(word in command for word in context_words)
        return has_action and has_context
    
    def _get_warm_allies(self, command):
        """Get warm allies with optional time filter"""
        days_filter = self._extract_days_from_command(command)
        
        contacts = Contact(self.db).get_by_filters(
            self.user_id,
            warmth_status=3,  # Warm contacts
            relationship_type="Ally",
            days_since_contact=days_filter
        )
        
        if not contacts:
            return "No warm allies found matching your criteria."
        
        response = f"Found {len(contacts)} warm allies"
        if days_filter:
            response += f" you haven't contacted in {days_filter}+ days"
        response += ":\n\n"
        
        for contact in contacts[:10]:
            last_contact = contact.get('last_interaction_date', 'Never')
            if last_contact and last_contact != 'Never':
                last_contact = last_contact[:10]
            response += f"• **{contact['name']}** - Last contact: {last_contact}\n"
            if contact.get('company'):
                response += f"  {contact['company']}"
            if contact.get('title'):
                response += f" - {contact['title']}"
            response += "\n"
        
        return response
    
    def _get_follow_ups_due(self, command):
        """Get contacts with follow-ups due"""
        days_ahead = self._extract_days_from_command(command) or 7
        
        contacts = Contact(self.db).get_follow_ups_due(self.user_id, days_ahead)
        
        if not contacts:
            return f"No follow-ups due in the next {days_ahead} days."
        
        response = f"Follow-ups due in the next {days_ahead} days ({len(contacts)} contacts):\n\n"
        
        for contact in contacts:
            due_date = contact['follow_up_due_date'][:10] if contact.get('follow_up_due_date') else 'TBD'
            action = contact.get('follow_up_action', 'Follow up')
            response += f"• **{contact['name']}** - Due: {due_date}\n"
            response += f"  Action: {action}\n\n"
        
        return response
    
    def _summarize_contact(self, command):
        """Summarize a specific contact's history"""
        # Extract contact name from command
        name_match = re.search(r'(?:tell me about|summarize|summary of)\s+(.+?)(?:\s|$)', command, re.IGNORECASE)
        if not name_match:
            return "Please specify which contact you'd like to know about (e.g., 'Tell me about John Smith')."
        
        contact_name = name_match.group(1).strip()
        
        # Find contact by name
        contacts = Contact(self.db).get_all(self.user_id)
        matching_contact = None
        
        for contact in contacts:
            if contact_name.lower() in contact['name'].lower():
                matching_contact = contact
                break
        
        if not matching_contact:
            return f"Contact '{contact_name}' not found. Please check the spelling or try a different name."
        
        return self.contact_intel.summarize_contact_history(matching_contact['id'])
    
    def _get_outreach_suggestions(self):
        """Get AI-generated outreach suggestions"""
        # Generate fresh suggestions
        self.contact_intel.generate_daily_suggestions(self.user_id)
        
        suggestions = OutreachSuggestion(self.db).get_daily_suggestions(self.user_id, limit=5)
        
        if not suggestions:
            return "No outreach suggestions at the moment. All your contacts are up to date!"
        
        response = f"Top {len(suggestions)} contacts to reach out to:\n\n"
        
        for i, suggestion in enumerate(suggestions, 1):
            response += f"{i}. **{suggestion['contact_name']}** ({suggestion['warmth_label']})\n"
            response += f"   Reason: {suggestion['reason']}\n"
            response += f"   Action: {suggestion['suggested_action']}\n\n"
        
        return response
    
    def _get_pipeline_view(self):
        """Get kanban-style pipeline view"""
        pipeline = Contact(self.db).get_pipeline_view(self.user_id)
        
        response = "Contact Warming Pipeline:\n\n"
        
        for stage, contacts in pipeline.items():
            response += f"**{stage}** ({len(contacts)} contacts)\n"
            for contact in contacts[:3]:  # Show top 3 per stage
                response += f"• {contact['name']}"
                if contact.get('company'):
                    response += f" ({contact['company']})"
                response += "\n"
            if len(contacts) > 3:
                response += f"  ... and {len(contacts) - 3} more\n"
            response += "\n"
        
        return response
    
    def _get_contacts_by_warmth(self, warmth_label):
        """Get contacts by warmth status"""
        warmth_map = {'Cold': 1, 'Aware': 2, 'Warm': 3, 'Active': 4, 'Contributor': 5}
        warmth_status = warmth_map.get(warmth_label, 1)
        
        contacts = Contact(self.db).get_by_filters(self.user_id, warmth_status=warmth_status)
        
        if not contacts:
            return f"No {warmth_label.lower()} contacts found."
        
        response = f"{warmth_label} contacts ({len(contacts)}):\n\n"
        
        for contact in contacts[:10]:
            response += f"• **{contact['name']}**"
            if contact.get('company'):
                response += f" - {contact['company']}"
            if contact.get('title'):
                response += f" ({contact['title']})"
            response += "\n"
        
        if len(contacts) > 10:
            response += f"\n... and {len(contacts) - 10} more contacts"
        
        return response
    
    def _get_high_priority_contacts(self):
        """Get high priority contacts"""
        contacts = Contact(self.db).get_by_filters(self.user_id, priority_level="High")
        
        if not contacts:
            return "No high priority contacts found."
        
        response = f"High Priority Contacts ({len(contacts)}):\n\n"
        
        for contact in contacts:
            response += f"• **{contact['name']}** ({contact['warmth_label']})"
            if contact.get('company'):
                response += f" - {contact['company']}"
            
            last_contact = contact.get('last_interaction_date')
            if last_contact:
                days_ago = (datetime.now() - datetime.fromisoformat(last_contact)).days
                response += f" - Last contact: {days_ago} days ago"
            response += "\n"
        
        return response
    
    def _get_contacts_by_type(self, relationship_type):
        """Get contacts by relationship type"""
        contacts = Contact(self.db).get_by_filters(self.user_id, relationship_type=relationship_type)
        
        if not contacts:
            return f"No {relationship_type.lower()} contacts found."
        
        response = f"{relationship_type} Contacts ({len(contacts)}):\n\n"
        
        for contact in contacts[:10]:
            response += f"• **{contact['name']}** ({contact['warmth_label']})"
            if contact.get('company'):
                response += f" - {contact['company']}"
            response += "\n"
        
        return response
    
    def _get_interaction_timeline(self, command):
        """Get recent interaction timeline"""
        days_back = self._extract_days_from_command(command) or 30
        
        interactions = ContactInteraction(self.db).get_timeline(self.user_id, days_back)
        
        if not interactions:
            return f"No interactions recorded in the last {days_back} days."
        
        response = f"Interaction Timeline (Last {days_back} days - {len(interactions)} interactions):\n\n"
        
        current_date = None
        for interaction in interactions[:20]:  # Show last 20
            interaction_date = interaction['timestamp'][:10]
            
            if interaction_date != current_date:
                response += f"**{interaction_date}**\n"
                current_date = interaction_date
            
            response += f"• {interaction['contact_name']} - {interaction['interaction_type']}"
            if interaction.get('subject'):
                response += f": {interaction['subject']}"
            response += "\n"
        
        return response
    
    def _suggest_introductions(self, command):
        """Suggest potential introductions"""
        # Extract contact name if specified
        name_match = re.search(r'(?:introduce|introduction)\s+(?:for\s+)?(.+?)(?:\s+to|\s|$)', command, re.IGNORECASE)
        
        if name_match:
            contact_name = name_match.group(1).strip()
            contacts = Contact(self.db).get_all(self.user_id)
            
            target_contact = None
            for contact in contacts:
                if contact_name.lower() in contact['name'].lower():
                    target_contact = contact
                    break
            
            if not target_contact:
                return f"Contact '{contact_name}' not found."
            
            intros = ContactRelationship(self.db).get_potential_introductions(self.user_id, target_contact['id'])
            
            if not intros:
                return f"No potential introductions found for {target_contact['name']}."
            
            response = f"Potential introductions for **{target_contact['name']}**:\n\n"
            
            for intro in intros[:5]:
                response += f"• **{intro['name']}**"
                if intro.get('company'):
                    response += f" - {intro['company']}"
                if intro.get('tags'):
                    common_tags = self._find_common_interests(target_contact.get('tags', ''), intro.get('tags', ''))
                    if common_tags:
                        response += f" (Common: {', '.join(common_tags)})"
                response += "\n"
            
            return response
        else:
            return "Please specify which contact you'd like introduction suggestions for."
    
    def _extract_days_from_command(self, command):
        """Extract number of days from command text"""
        day_patterns = [
            r'(\d+)\s*days?',
            r'(\d+)\s*d\b',
            r'(\d+)\+\s*days?',
            r'in\s+(\d+)\s*days?'
        ]
        
        for pattern in day_patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _find_common_interests(self, tags1, tags2):
        """Find common tags/interests between two contacts"""
        if not tags1 or not tags2:
            return []
        
        tags1_list = [tag.strip().lower() for tag in tags1.split(',')]
        tags2_list = [tag.strip().lower() for tag in tags2.split(',')]
        
        return list(set(tags1_list) & set(tags2_list))
    
    def _fallback_ai_response(self, command):
        """Use AI to interpret and respond to complex queries"""
        try:
            # Get context about user's contacts
            contacts_summary = self._get_contacts_context()
            
            prompt = f"""You are a smart CRM assistant. Based on the user's query and their contact database context, provide a helpful response.

User Query: "{command}"

Contact Database Context:
{contacts_summary}

Available actions you can suggest:
- View contacts by warmth level (Cold, Aware, Warm, Active, Contributor)
- View contacts by relationship type (Ally, Investor, Collaborator, Press, etc.)
- View contacts by priority (High, Medium, Low)
- View follow-ups due
- View interaction timeline
- Get outreach suggestions
- Summarize specific contacts

Provide a concise, actionable response. If the query is unclear, ask for clarification."""

            # Use GPT-4o for intelligent response
            response = self.openai_utils.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"AI fallback error: {e}")
            return "I'm not sure how to help with that request. Try asking about your contacts, follow-ups, or outreach suggestions."
    
    def _get_contacts_context(self):
        """Get summarized context about user's contacts for AI"""
        contacts = Contact(self.db).get_all(self.user_id)
        
        if not contacts:
            return "No contacts in database."
        
        # Count by categories
        warmth_counts = {}
        type_counts = {}
        priority_counts = {}
        
        for contact in contacts:
            warmth = contact.get('warmth_label', 'Cold')
            warmth_counts[warmth] = warmth_counts.get(warmth, 0) + 1
            
            rel_type = contact.get('relationship_type', 'Contact')
            type_counts[rel_type] = type_counts.get(rel_type, 0) + 1
            
            priority = contact.get('priority_level', 'Medium')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        context = f"Total contacts: {len(contacts)}\n"
        context += f"Warmth levels: {dict(warmth_counts)}\n"
        context += f"Relationship types: {dict(type_counts)}\n"
        context += f"Priority levels: {dict(priority_counts)}"
        
        return context