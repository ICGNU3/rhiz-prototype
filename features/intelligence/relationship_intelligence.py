"""
Relationship Intelligence Layer for Rhiz
Advanced contact intelligence, timeline management, and relationship insights
"""

import json
import uuid
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging
from openai_utils import OpenAIUtils

class RelationshipIntelligence:
    """Advanced relationship intelligence and contact management"""
    
    def __init__(self, db):
        self.db = db
        self.openai_utils = OpenAIUtils()
    
    # ==================== Unknown but Important Contacts ====================
    
    def add_unknown_contact(self, user_id: str, identifier: str, identifier_type: str, 
                           context_clues: List[str] = None) -> str:
        """Add an unknown but potentially important contact"""
        unknown_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        
        try:
            conn.execute("""
                INSERT INTO unknown_contacts 
                (id, user_id, identifier, identifier_type, context_clues, ai_suggestions, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                unknown_id, user_id, identifier, identifier_type,
                json.dumps(context_clues or []), json.dumps([]),
                datetime.now().isoformat()
            ))
            conn.commit()
            
            # Generate AI suggestions for this contact
            self._generate_ai_suggestions_for_unknown(unknown_id, user_id, identifier, context_clues)
            
            logging.info(f"Added unknown contact: {unknown_id}")
            return unknown_id
            
        except Exception as e:
            logging.error(f"Failed to add unknown contact: {e}")
            return None
        finally:
            conn.close()
    
    def get_unknown_contacts(self, user_id: str, status: str = None) -> List[Dict[str, Any]]:
        """Get all unknown contacts for a user"""
        conn = self.db.get_connection()
        try:
            query = "SELECT * FROM unknown_contacts WHERE user_id = ?"
            params = [user_id]
            
            if status:
                query += " AND status = ?"
                params.append(status)
                
            query += " ORDER BY created_at DESC"
            
            unknowns = conn.execute(query, params).fetchall()
            
            result = []
            for unknown in unknowns:
                unknown_dict = dict(unknown)
                unknown_dict['context_clues'] = json.loads(unknown_dict['context_clues'] or '[]')
                unknown_dict['ai_suggestions'] = json.loads(unknown_dict['ai_suggestions'] or '[]')
                result.append(unknown_dict)
                
            return result
        finally:
            conn.close()
    
    def _generate_ai_suggestions_for_unknown(self, unknown_id: str, user_id: str, 
                                           identifier: str, context_clues: List[str]):
        """Generate AI suggestions for identifying unknown contacts"""
        try:
            # Get user's existing contacts for context
            conn = self.db.get_connection()
            contacts = conn.execute(
                "SELECT name, company, title, email FROM contacts WHERE user_id = ?",
                (user_id,)
            ).fetchall()
            conn.close()
            
            context_text = f"Unknown identifier: {identifier}\n"
            if context_clues:
                context_text += f"Context clues: {', '.join(context_clues)}\n"
            
            # Create prompt for AI analysis
            prompt = f"""
            Analyze this unknown contact and provide suggestions for identification:
            
            {context_text}
            
            Existing contact network includes people from these organizations:
            {', '.join(set([c['company'] for c in contacts if c['company']]))}
            
            Please suggest:
            1. Possible events or conferences where they might have met
            2. Industry connections or mutual contacts
            3. Questions to help identify them
            4. Potential relationship context
            
            Return as JSON with keys: events, connections, questions, context
            """
            
            response = self.openai_utils.get_completion(prompt)
            
            try:
                suggestions = json.loads(response)
            except:
                # Fallback structured suggestions
                suggestions = {
                    "events": ["Recent conference or networking event", "Industry meetup"],
                    "connections": ["Mutual professional contact", "Shared industry connection"],
                    "questions": [f"Did you meet {identifier} at a recent event?", 
                                 f"Is {identifier} connected to your professional network?"],
                    "context": "Professional networking contact"
                }
            
            # Update the unknown contact with AI suggestions
            conn = self.db.get_connection()
            try:
                conn.execute("""
                    UPDATE unknown_contacts 
                    SET ai_suggestions = ?, updated_at = ?
                    WHERE id = ?
                """, (json.dumps(suggestions), datetime.now().isoformat(), unknown_id))
                conn.commit()
            finally:
                conn.close()
                
        except Exception as e:
            logging.error(f"Failed to generate AI suggestions: {e}")
    
    def review_unknown_contact(self, unknown_id: str, action: str, notes: str = None,
                              contact_id: str = None) -> bool:
        """Review and update unknown contact status"""
        conn = self.db.get_connection()
        try:
            # Update review count and status
            conn.execute("""
                UPDATE unknown_contacts 
                SET status = ?, notes = ?, potential_contact_id = ?, 
                    review_count = review_count + 1, last_reviewed = ?, updated_at = ?
                WHERE id = ?
            """, (
                action, notes, contact_id, datetime.now().isoformat(),
                datetime.now().isoformat(), unknown_id
            ))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"Failed to review unknown contact: {e}")
            return False
        finally:
            conn.close()
    
    # ==================== Contact Timeline & History ====================
    
    def add_timeline_event(self, contact_id: str, user_id: str, event_type: str,
                          title: str, description: str = None, event_date: datetime = None,
                          metadata: Dict[str, Any] = None) -> str:
        """Add an event to contact's timeline"""
        event_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        
        try:
            conn.execute("""
                INSERT INTO contact_timeline_events 
                (id, contact_id, user_id, event_type, title, description, event_date, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id, contact_id, user_id, event_type, title, description,
                (event_date or datetime.now()).isoformat(),
                json.dumps(metadata or {}), datetime.now().isoformat()
            ))
            conn.commit()
            
            logging.info(f"Added timeline event: {event_id}")
            return event_id
            
        except Exception as e:
            logging.error(f"Failed to add timeline event: {e}")
            return None
        finally:
            conn.close()
    
    def get_contact_timeline(self, contact_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get full timeline for a contact"""
        conn = self.db.get_connection()
        try:
            # Get timeline events
            events = conn.execute("""
                SELECT * FROM contact_timeline_events 
                WHERE contact_id = ? 
                ORDER BY event_date DESC, created_at DESC 
                LIMIT ?
            """, (contact_id, limit)).fetchall()
            
            # Also get existing interaction logs for compatibility
            interactions = conn.execute("""
                SELECT * FROM contact_interactions 
                WHERE contact_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (contact_id, limit)).fetchall()
            
            # Also get journal entries
            journals = conn.execute("""
                SELECT * FROM journal_entries 
                WHERE contact_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (contact_id, limit)).fetchall()
            
            # Also get tasks
            tasks = conn.execute("""
                SELECT * FROM tasks 
                WHERE contact_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (contact_id, limit)).fetchall()
            
            # Combine and format all timeline items
            timeline = []
            
            # Add timeline events
            for event in events:
                event_dict = dict(event)
                event_dict['metadata'] = json.loads(event_dict['metadata'] or '{}')
                event_dict['source'] = 'timeline_event'
                timeline.append(event_dict)
            
            # Add interactions
            for interaction in interactions:
                interaction_dict = dict(interaction)
                interaction_dict['event_type'] = 'interaction'
                interaction_dict['event_date'] = interaction_dict['created_at']
                interaction_dict['title'] = interaction_dict['interaction_type']
                interaction_dict['description'] = interaction_dict['notes']
                interaction_dict['source'] = 'interaction_log'
                timeline.append(interaction_dict)
            
            # Add journal entries
            for journal in journals:
                journal_dict = dict(journal)
                journal_dict['event_type'] = 'journal'
                journal_dict['event_date'] = journal_dict['created_at']
                journal_dict['title'] = journal_dict.get('title', 'Journal Entry')
                journal_dict['description'] = journal_dict['content']
                journal_dict['source'] = 'journal'
                timeline.append(journal_dict)
            
            # Add tasks
            for task in tasks:
                task_dict = dict(task)
                task_dict['event_type'] = 'task'
                task_dict['event_date'] = task_dict['created_at']
                task_dict['title'] = task_dict['title']
                task_dict['description'] = task_dict['description']
                task_dict['source'] = 'task'
                timeline.append(task_dict)
            
            # Sort by event_date
            timeline.sort(key=lambda x: x['event_date'], reverse=True)
            
            return timeline[:limit]
            
        finally:
            conn.close()
    
    # ==================== Mass Messaging ====================
    
    def create_mass_message_campaign(self, user_id: str, title: str, message_template: str,
                                   message_type: str, target_criteria: Dict[str, Any] = None,
                                   target_contact_ids: List[str] = None) -> str:
        """Create a new mass message campaign"""
        campaign_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        
        try:
            # If no specific contact IDs, determine targets based on criteria
            if not target_contact_ids and target_criteria:
                target_contact_ids = self._get_contacts_by_criteria(user_id, target_criteria)
            
            conn.execute("""
                INSERT INTO mass_message_campaigns 
                (id, user_id, title, message_template, message_type, target_criteria, 
                 target_contact_ids, total_recipients, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                campaign_id, user_id, title, message_template, message_type,
                json.dumps(target_criteria or {}), json.dumps(target_contact_ids or []),
                len(target_contact_ids or []), 'draft', datetime.now().isoformat()
            ))
            conn.commit()
            
            # Create recipient records
            if target_contact_ids:
                self._create_campaign_recipients(campaign_id, user_id, target_contact_ids, message_template)
            
            logging.info(f"Created mass message campaign: {campaign_id}")
            return campaign_id
            
        except Exception as e:
            logging.error(f"Failed to create campaign: {e}")
            return None
        finally:
            conn.close()
    
    def _get_contacts_by_criteria(self, user_id: str, criteria: Dict[str, Any]) -> List[str]:
        """Get contact IDs based on filtering criteria"""
        conn = self.db.get_connection()
        try:
            query = "SELECT id FROM contacts WHERE user_id = ?"
            params = [user_id]
            
            # Add filters based on criteria
            if criteria.get('warmth_status'):
                query += " AND warmth_status = ?"
                params.append(criteria['warmth_status'])
            
            if criteria.get('relationship_type'):
                query += " AND relationship_type = ?"
                params.append(criteria['relationship_type'])
            
            if criteria.get('tags'):
                # Filter by tags (stored as JSON)
                for tag in criteria['tags']:
                    query += " AND (tags LIKE ? OR tags LIKE ? OR tags LIKE ?)"
                    params.extend([f'%"{tag}"%', f'%["{tag}"%', f'%,"{tag}"%'])
            
            if criteria.get('company'):
                query += " AND company = ?"
                params.append(criteria['company'])
            
            if criteria.get('location'):
                query += " AND location = ?"
                params.append(criteria['location'])
            
            contacts = conn.execute(query, params).fetchall()
            return [contact['id'] for contact in contacts]
            
        finally:
            conn.close()
    
    def _create_campaign_recipients(self, campaign_id: str, user_id: str, 
                                  contact_ids: List[str], message_template: str):
        """Create recipient records for campaign"""
        conn = self.db.get_connection()
        try:
            for contact_id in contact_ids:
                # Get contact details for personalization
                contact = conn.execute(
                    "SELECT * FROM contacts WHERE id = ?", (contact_id,)
                ).fetchone()
                
                if contact:
                    # Personalize message
                    personalized_message = self._personalize_message(message_template, dict(contact))
                    
                    recipient_id = str(uuid.uuid4())
                    conn.execute("""
                        INSERT INTO mass_message_recipients 
                        (id, campaign_id, contact_id, user_id, personalized_message, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        recipient_id, campaign_id, contact_id, user_id,
                        personalized_message, datetime.now().isoformat()
                    ))
            
            conn.commit()
        finally:
            conn.close()
    
    def _personalize_message(self, template: str, contact: Dict[str, Any]) -> str:
        """Personalize message template with contact data"""
        try:
            # Simple template replacement
            personalized = template
            
            # Replace common placeholders
            replacements = {
                '{name}': contact.get('name', ''),
                '{first_name}': contact.get('name', '').split()[0] if contact.get('name') else '',
                '{company}': contact.get('company', ''),
                '{title}': contact.get('title', ''),
                '{location}': contact.get('location', '')
            }
            
            for placeholder, value in replacements.items():
                personalized = personalized.replace(placeholder, value)
            
            return personalized
            
        except Exception as e:
            logging.error(f"Failed to personalize message: {e}")
            return template
    
    def get_mass_message_campaigns(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all campaigns for a user"""
        conn = self.db.get_connection()
        try:
            campaigns = conn.execute("""
                SELECT * FROM mass_message_campaigns 
                WHERE user_id = ? 
                ORDER BY created_at DESC
            """, (user_id,)).fetchall()
            
            result = []
            for campaign in campaigns:
                campaign_dict = dict(campaign)
                campaign_dict['target_criteria'] = json.loads(campaign_dict['target_criteria'] or '{}')
                campaign_dict['target_contact_ids'] = json.loads(campaign_dict['target_contact_ids'] or '[]')
                
                # Get recipient stats
                stats = conn.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN send_status = 'sent' THEN 1 ELSE 0 END) as sent,
                        SUM(CASE WHEN send_status = 'failed' THEN 1 ELSE 0 END) as failed,
                        SUM(CASE WHEN opened_at IS NOT NULL THEN 1 ELSE 0 END) as opened,
                        SUM(CASE WHEN replied_at IS NOT NULL THEN 1 ELSE 0 END) as replied
                    FROM mass_message_recipients 
                    WHERE campaign_id = ?
                """, (campaign_dict['id'],)).fetchone()
                
                if stats:
                    campaign_dict['stats'] = dict(stats)
                else:
                    campaign_dict['stats'] = {
                        'total': 0, 'sent': 0, 'failed': 0, 'opened': 0, 'replied': 0
                    }
                
                result.append(campaign_dict)
            
            return result
        finally:
            conn.close()
    
    # ==================== Contact Relationships ====================
    
    def add_contact_relationship(self, user_id: str, contact_a_id: str, contact_b_id: str,
                               relationship_type: str, strength: int = 1, 
                               context: str = None) -> str:
        """Add relationship between two contacts"""
        relationship_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        
        try:
            conn.execute("""
                INSERT INTO contact_relationships 
                (id, user_id, contact_a_id, contact_b_id, relationship_type, strength, context, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                relationship_id, user_id, contact_a_id, contact_b_id,
                relationship_type, strength, context, datetime.now().isoformat()
            ))
            conn.commit()
            
            logging.info(f"Added contact relationship: {relationship_id}")
            return relationship_id
            
        except Exception as e:
            logging.error(f"Failed to add relationship: {e}")
            return None
        finally:
            conn.close()
    
    def get_contact_relationships(self, user_id: str, contact_id: str = None) -> List[Dict[str, Any]]:
        """Get relationships for a contact or all relationships"""
        conn = self.db.get_connection()
        try:
            if contact_id:
                relationships = conn.execute("""
                    SELECT r.*, 
                           ca.name as contact_a_name, ca.company as contact_a_company,
                           cb.name as contact_b_name, cb.company as contact_b_company
                    FROM contact_relationships r
                    JOIN contacts ca ON r.contact_a_id = ca.id
                    JOIN contacts cb ON r.contact_b_id = cb.id
                    WHERE r.user_id = ? AND (r.contact_a_id = ? OR r.contact_b_id = ?)
                    ORDER BY r.created_at DESC
                """, (user_id, contact_id, contact_id)).fetchall()
            else:
                relationships = conn.execute("""
                    SELECT r.*, 
                           ca.name as contact_a_name, ca.company as contact_a_company,
                           cb.name as contact_b_name, cb.company as contact_b_company
                    FROM contact_relationships r
                    JOIN contacts ca ON r.contact_a_id = ca.id
                    JOIN contacts cb ON r.contact_b_id = cb.id
                    WHERE r.user_id = ?
                    ORDER BY r.created_at DESC
                """, (user_id,)).fetchall()
            
            return [dict(rel) for rel in relationships]
        finally:
            conn.close()
    
    # ==================== Intelligent Insights ====================
    
    def analyze_relationship_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze patterns in user's relationship network"""
        conn = self.db.get_connection()
        try:
            # Get contact distribution
            contacts = conn.execute("""
                SELECT warmth_status, relationship_type, company, location, tags
                FROM contacts WHERE user_id = ?
            """, (user_id,)).fetchall()
            
            # Get interaction frequency
            interactions = conn.execute("""
                SELECT contact_id, COUNT(*) as interaction_count,
                       MAX(created_at) as last_interaction
                FROM contact_interactions 
                WHERE user_id = ?
                GROUP BY contact_id
            """, (user_id,)).fetchall()
            
            # Analyze patterns
            analysis = {
                'total_contacts': len(contacts),
                'warmth_distribution': {},
                'relationship_distribution': {},
                'company_distribution': {},
                'location_distribution': {},
                'interaction_patterns': {},
                'recommendations': []
            }
            
            # Warmth distribution
            for contact in contacts:
                warmth = contact['warmth_status'] or 'unknown'
                analysis['warmth_distribution'][warmth] = analysis['warmth_distribution'].get(warmth, 0) + 1
            
            # Relationship type distribution
            for contact in contacts:
                rel_type = contact['relationship_type'] or 'Contact'
                analysis['relationship_distribution'][rel_type] = analysis['relationship_distribution'].get(rel_type, 0) + 1
            
            # Company distribution
            for contact in contacts:
                company = contact['company'] or 'Unknown'
                analysis['company_distribution'][company] = analysis['company_distribution'].get(company, 0) + 1
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_relationship_recommendations(analysis, interactions)
            
            return analysis
            
        finally:
            conn.close()
    
    def _generate_relationship_recommendations(self, analysis: Dict[str, Any], 
                                             interactions: List[Dict[str, Any]]) -> List[str]:
        """Generate intelligent recommendations based on relationship analysis"""
        recommendations = []
        
        # Check warmth distribution
        total_contacts = analysis['total_contacts']
        if total_contacts > 0:
            cold_percentage = analysis['warmth_distribution'].get(1, 0) / total_contacts
            if cold_percentage > 0.5:
                recommendations.append("Consider warming up cold contacts with personalized follow-ups")
        
        # Check interaction patterns
        inactive_contacts = len([i for i in interactions if i['interaction_count'] < 2])
        if inactive_contacts > total_contacts * 0.3:
            recommendations.append("Many contacts have minimal interactions - consider regular check-ins")
        
        # Company diversity
        companies = list(analysis['company_distribution'].keys())
        if len(companies) < total_contacts * 0.3:
            recommendations.append("Network is concentrated in few companies - consider diversifying")
        
        # Relationship type diversity
        rel_types = list(analysis['relationship_distribution'].keys())
        if len(rel_types) < 3:
            recommendations.append("Consider expanding relationship types (mentors, advisors, peers)")
        
        return recommendations
    
    def get_weekly_unknown_contacts_summary(self, user_id: str) -> Dict[str, Any]:
        """Get weekly summary of unknown contacts to review"""
        conn = self.db.get_connection()
        try:
            # Get unknown contacts that need review
            unknowns = conn.execute("""
                SELECT * FROM unknown_contacts 
                WHERE user_id = ? AND status = 'unknown' 
                AND (last_reviewed IS NULL OR last_reviewed < ?)
                ORDER BY created_at DESC
                LIMIT 10
            """, (user_id, (datetime.now() - timedelta(days=7)).isoformat())).fetchall()
            
            summary = {
                'total_unknown': len(unknowns),
                'contacts_to_review': [],
                'suggested_actions': []
            }
            
            for unknown in unknowns:
                unknown_dict = dict(unknown)
                unknown_dict['ai_suggestions'] = json.loads(unknown_dict['ai_suggestions'] or '[]')
                summary['contacts_to_review'].append(unknown_dict)
            
            if len(unknowns) > 0:
                summary['suggested_actions'].append("Review unknown contacts to identify potential connections")
            
            if len(unknowns) > 5:
                summary['suggested_actions'].append("Consider adding more context clues to help identification")
            
            return summary
            
        finally:
            conn.close()
    
    # ==================== Reminder System ====================
    
    def check_due_reminders(self, user_id: str) -> List[Dict[str, Any]]:
        """Get reminders that are due"""
        conn = self.db.get_connection()
        try:
            # Check existing reminders table and contact-specific reminders
            due_reminders = []
            
            # Check Monica-style reminders
            reminders = conn.execute("""
                SELECT r.*, c.name as contact_name, c.email as contact_email
                FROM reminders r
                JOIN contacts c ON r.contact_id = c.id
                WHERE r.user_id = ? AND r.due_date <= ? AND r.is_completed = FALSE
                ORDER BY r.due_date ASC
            """, (user_id, datetime.now().isoformat())).fetchall()
            
            for reminder in reminders:
                due_reminders.append(dict(reminder))
            
            # Check for contacts that haven't been contacted recently
            stale_contacts = conn.execute("""
                SELECT c.*, 
                       MAX(ci.created_at) as last_interaction,
                       COUNT(ci.id) as interaction_count
                FROM contacts c
                LEFT JOIN contact_interactions ci ON c.id = ci.contact_id
                WHERE c.user_id = ? 
                GROUP BY c.id
                HAVING (last_interaction IS NULL OR last_interaction < ?)
                AND c.warmth_status >= 3  -- Only warm/active contacts
                ORDER BY last_interaction ASC
                LIMIT 10
            """, (user_id, (datetime.now() - timedelta(days=30)).isoformat())).fetchall()
            
            for contact in stale_contacts:
                due_reminders.append({
                    'id': f"stale_{contact['id']}",
                    'contact_id': contact['id'],
                    'contact_name': contact['name'],
                    'contact_email': contact['email'],
                    'title': f"Follow up with {contact['name']}",
                    'description': f"No recent interaction with {contact['name']}",
                    'reminder_type': 'follow_up',
                    'due_date': datetime.now().isoformat(),
                    'last_interaction': contact['last_interaction']
                })
            
            return due_reminders
            
        finally:
            conn.close()
    
    def schedule_reminder(self, user_id: str, contact_id: str, title: str, 
                         reminder_type: str, due_date: datetime, 
                         description: str = None, is_recurring: bool = False,
                         recurrence_pattern: str = None) -> str:
        """Schedule a new reminder"""
        reminder_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        
        try:
            conn.execute("""
                INSERT INTO reminders 
                (id, user_id, contact_id, title, description, reminder_type, 
                 due_date, is_recurring, recurrence_pattern, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                reminder_id, user_id, contact_id, title, description,
                reminder_type, due_date.isoformat(), is_recurring,
                recurrence_pattern, datetime.now().isoformat()
            ))
            conn.commit()
            
            logging.info(f"Scheduled reminder: {reminder_id}")
            return reminder_id
            
        except Exception as e:
            logging.error(f"Failed to schedule reminder: {e}")
            return None
        finally:
            conn.close()