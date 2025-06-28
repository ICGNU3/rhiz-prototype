"""
Contact Intelligence Service
Provides AI-powered contact insights and relationship analysis
"""

import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
from openai import OpenAI

logger = logging.getLogger(__name__)

class ContactIntelligence:
    """Main class for contact intelligence and natural language processing"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        try:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
            else:
                self.openai_client = None
                logger.warning("OpenAI API key not found - AI features will be limited")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {e}")
            self.openai_client = None

    def generate_daily_suggestions(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Generate daily outreach suggestions based on contact data"""
        try:
            if not self.db:
                return []
                
            cursor = self.db.cursor()
            
            # Get contacts with recent interaction patterns
            cursor.execute("""
                SELECT c.id, c.name, c.email, c.company, c.title, c.warmth_status, c.warmth_label,
                       c.last_interaction_date, c.priority_level, c.notes,
                       COUNT(ci.id) as interaction_count,
                       MAX(ci.interaction_date) as last_interaction
                FROM contacts c
                LEFT JOIN contact_interactions ci ON c.id = ci.contact_id
                WHERE c.user_id = %s
                GROUP BY c.id
                ORDER BY last_interaction_date ASC, priority_level DESC
                LIMIT %s
            """, (user_id, limit * 2))
            
            contacts = cursor.fetchall()
            suggestions = []
            
            for contact in contacts:
                contact_id, name, email, company, title, warmth_status, warmth_label = contact[:7]
                last_interaction_date, priority_level, notes = contact[7:10]
                interaction_count, last_interaction = contact[10:12]
                
                # Calculate days since last interaction
                days_since = self._days_since_last_interaction(last_interaction_date)
                
                # Generate suggestion based on patterns
                if days_since > 30 and warmth_status >= 2:  # Warm contacts going cold
                    suggestion_type = "reconnect"
                    priority = 8
                elif days_since > 7 and priority_level == "High":
                    suggestion_type = "follow_up"
                    priority = 7
                elif warmth_status == 1 and interaction_count == 0:  # Cold leads
                    suggestion_type = "initial_outreach"
                    priority = 5
                else:
                    continue
                
                # Generate suggested action
                suggested_action = self._generate_suggested_action(contact, suggestion_type)
                
                suggestion = {
                    'contact_id': contact_id,
                    'name': name,
                    'email': email,
                    'company': company,
                    'title': title,
                    'suggestion_type': suggestion_type,
                    'priority_score': priority,
                    'reason': f"Last contact: {days_since} days ago",
                    'suggested_action': suggested_action,
                    'warmth_level': warmth_label
                }
                
                suggestions.append(suggestion)
            
            # Sort by priority and return top suggestions
            suggestions.sort(key=lambda x: x['priority_score'], reverse=True)
            return suggestions[:limit]
            
        except Exception as e:
            logger.error(f"Error generating daily suggestions: {e}")
            return []

    def _days_since_last_interaction(self, last_date) -> int:
        """Calculate days since last interaction"""
        if not last_date:
            return 365  # No interaction recorded
        
        if isinstance(last_date, str):
            try:
                last_date = datetime.fromisoformat(last_date.replace('Z', '+00:00'))
            except:
                return 365
        
        return (datetime.now() - last_date).days

    def _generate_suggested_action(self, contact, suggestion_type: str) -> str:
        """Generate suggested action based on contact and suggestion type"""
        name = contact[1]
        company = contact[3]
        title = contact[4]
        
        if suggestion_type == "reconnect":
            return f"Send a friendly check-in message to {name} at {company}"
        elif suggestion_type == "follow_up":
            return f"Follow up with {name} on previous conversation"
        elif suggestion_type == "initial_outreach":
            return f"Introduce yourself to {name} ({title} at {company})"
        else:
            return f"Reach out to {name}"

    def summarize_contact_history(self, contact_id: str) -> Dict[str, Any]:
        """Generate natural language summary of contact history"""
        try:
            if not self.db:
                return {"summary": "Database connection not available"}
                
            cursor = self.db.cursor()
            
            # Get contact details and interactions
            cursor.execute("""
                SELECT c.name, c.company, c.title, c.warmth_label, c.notes,
                       COUNT(ci.id) as interaction_count,
                       MAX(ci.interaction_date) as last_interaction,
                       STRING_AGG(ci.summary, '; ') as interaction_summaries
                FROM contacts c
                LEFT JOIN contact_interactions ci ON c.id = ci.contact_id
                WHERE c.id = %s
                GROUP BY c.id, c.name, c.company, c.title, c.warmth_label, c.notes
            """, (contact_id,))
            
            result = cursor.fetchone()
            if not result:
                return {"summary": "Contact not found"}
            
            name, company, title, warmth, notes = result[:5]
            interaction_count, last_interaction, summaries = result[5:8]
            
            # Generate AI summary if OpenAI is available
            if self.openai_client and summaries:
                summary = self._generate_ai_summary(name, company, title, warmth, 
                                                  interaction_count, summaries, notes)
            else:
                # Fallback summary
                summary = f"{name} is a {title} at {company} with {warmth} relationship status. "
                summary += f"You've had {interaction_count} interactions."
                if notes:
                    summary += f" Notes: {notes}"
            
            return {
                "summary": summary,
                "interaction_count": interaction_count,
                "last_interaction": last_interaction,
                "warmth_level": warmth
            }
            
        except Exception as e:
            logger.error(f"Error summarizing contact history: {e}")
            return {"summary": "Error generating summary"}

    def _generate_ai_summary(self, name: str, company: str, title: str, warmth: str,
                           interaction_count: int, summaries: str, notes: str) -> str:
        """Generate AI-powered contact summary"""
        try:
            prompt = f"""
            Summarize this professional relationship in 2-3 sentences:
            
            Contact: {name}, {title} at {company}
            Relationship status: {warmth}
            Total interactions: {interaction_count}
            Interaction history: {summaries}
            Notes: {notes or 'None'}
            
            Focus on the relationship development and key points of connection.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Latest OpenAI model as of knowledge cutoff
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI summary: {e}")
            return f"{name} at {company}. {interaction_count} interactions recorded."

    def process_natural_language_query(self, user_id: str, query: str) -> Dict[str, Any]:
        """Process natural language queries about contacts and relationships"""
        try:
            if not self.openai_client:
                return {"error": "AI assistant not available"}
            
            # Get user's contact data for context
            contacts_context = self._get_contacts_context(user_id)
            
            prompt = f"""
            You are a relationship intelligence assistant. Answer this query about the user's professional network:
            
            Query: {query}
            
            User's contacts context: {contacts_context}
            
            Provide a helpful response based on the available contact data. If you need more specific information,
            suggest what the user should look for or add to their contact records.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            return {
                "response": response.choices[0].message.content.strip(),
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Error processing natural language query: {e}")
            return {"error": "Unable to process query"}

    def _get_contacts_context(self, user_id: str) -> str:
        """Get summarized context of user's contacts for AI queries"""
        try:
            if not self.db:
                return "No contact data available"
                
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT COUNT(*) as total_contacts,
                       COUNT(CASE WHEN warmth_status >= 3 THEN 1 END) as warm_contacts,
                       STRING_AGG(DISTINCT company, ', ') as companies,
                       STRING_AGG(DISTINCT title, ', ') as titles
                FROM contacts 
                WHERE user_id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            if result:
                total, warm, companies, titles = result
                return f"Total contacts: {total}, Warm relationships: {warm}, Companies: {companies}, Roles: {titles}"
            
            return "No contacts found"
            
        except Exception as e:
            logger.error(f"Error getting contacts context: {e}")
            return "Contact data unavailable"

# Global instance for easy importing
contact_intelligence = ContactIntelligence()