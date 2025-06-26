"""
Conference Mode - Smart Contact Capture and Follow-up System
Optimizes networking at conferences with intelligent contact management and AI-powered follow-ups.
"""

import sqlite3
import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from models import Database, Contact, Goal
import openai
import os
import re

class ConferenceMode:
    """Conference Mode for smart contact capture and follow-up management"""
    
    def __init__(self, db: Database):
        self.db = db
        self.contact_model = Contact(db)
        self.goal_model = Goal(db)
        self.openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    def activate_conference_mode(self, user_id: int, conference_name: str, 
                                location: str = None, start_date: str = None, 
                                end_date: str = None) -> str:
        """Activate conference mode for a user"""
        conference_id = str(uuid.uuid4())
        
        conn = self.db.get_connection()
        try:
            conn.execute("""
                INSERT INTO conferences (id, user_id, name, location, start_date, end_date, 
                                       is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (conference_id, user_id, conference_name, location, start_date, 
                  end_date, True, datetime.now().isoformat()))
            
            # Deactivate any other active conferences for this user
            conn.execute("""
                UPDATE conferences SET is_active = FALSE 
                WHERE user_id = ? AND id != ?
            """, (user_id, conference_id))
            
            conn.commit()
            logging.info(f"Activated conference mode: {conference_name} for user {user_id}")
            return conference_id
            
        except Exception as e:
            logging.error(f"Error activating conference mode: {e}")
            raise
        finally:
            conn.close()
    
    def deactivate_conference_mode(self, user_id: int, conference_id: str = None):
        """Deactivate conference mode"""
        conn = self.db.get_connection()
        try:
            if conference_id:
                conn.execute("""
                    UPDATE conferences SET is_active = FALSE 
                    WHERE user_id = ? AND id = ?
                """, (user_id, conference_id))
            else:
                # Deactivate all active conferences for user
                conn.execute("""
                    UPDATE conferences SET is_active = FALSE 
                    WHERE user_id = ?
                """, (user_id,))
            
            conn.commit()
            logging.info(f"Deactivated conference mode for user {user_id}")
            
        except Exception as e:
            logging.error(f"Error deactivating conference mode: {e}")
            raise
        finally:
            conn.close()
    
    def get_active_conference(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get the active conference for a user"""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, location, start_date, end_date, created_at
                FROM conferences 
                WHERE user_id = ? AND is_active = TRUE
                LIMIT 1
            """, (user_id,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'name': result[1],
                    'location': result[2],
                    'start_date': result[3],
                    'end_date': result[4],
                    'created_at': result[5]
                }
            return None
            
        finally:
            conn.close()
    
    def capture_conference_contact(self, user_id: int, conference_id: str, 
                                 name: str, company: str = None, title: str = None,
                                 conversation_notes: str = None, twitter: str = None,
                                 linkedin: str = None, email: str = None,
                                 voice_memo: str = None, badge_photo_text: str = None) -> str:
        """Capture a new contact during conference mode with enhanced context"""
        
        # Create the contact
        contact_id = self.contact_model.create(
            user_id=user_id,
            name=name,
            email=email,
            company=company,
            title=title,
            twitter=twitter,
            linkedin=linkedin,
            notes=conversation_notes,
            relationship_type="Conference Contact"
        )
        
        # Add conference-specific metadata
        conn = self.db.get_connection()
        try:
            # Get conference details for tagging
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM conferences WHERE id = ?", (conference_id,))
            conference_name = cursor.fetchone()[0]
            
            # Create conference contact entry
            conn.execute("""
                INSERT INTO conference_contacts (id, conference_id, contact_id, 
                                               conversation_notes, voice_memo, 
                                               badge_photo_text, captured_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), conference_id, contact_id, conversation_notes,
                  voice_memo, badge_photo_text, datetime.now().isoformat()))
            
            # Auto-tag with conference name and date
            current_tags = conversation_notes or ""
            conference_tag = f"{conference_name}, {datetime.now().strftime('%Y-%m-%d')}"
            updated_tags = f"{current_tags}, {conference_tag}".strip(", ")
            
            # Update contact with conference tags
            conn.execute("""
                UPDATE contacts SET tags = ?, updated_at = ?
                WHERE id = ?
            """, (updated_tags, datetime.now().isoformat(), contact_id))
            
            conn.commit()
            
            # Perform AI enhancement
            self._ai_enhance_conference_contact(contact_id, user_id)
            
            logging.info(f"Captured conference contact: {name} at {conference_name}")
            return contact_id
            
        except Exception as e:
            logging.error(f"Error capturing conference contact: {e}")
            raise
        finally:
            conn.close()
    
    def _ai_enhance_conference_contact(self, contact_id: str, user_id: int):
        """Use AI to enhance the conference contact with tags and priority scoring"""
        try:
            # Get contact details
            contact = self.contact_model.get_by_id(contact_id)
            if not contact:
                return
            
            # Get user goals for relevance analysis
            goals = self.goal_model.get_all(user_id)
            
            # Prepare AI prompt
            contact_context = f"""
            Contact: {contact['name']}
            Company: {contact.get('company', 'Unknown')}
            Title: {contact.get('title', 'Unknown')}
            Conversation Notes: {contact.get('notes', 'No notes')}
            """
            
            goals_context = "\n".join([f"- {goal['title']}: {goal['description']}" for goal in goals])
            
            prompt = f"""
            Analyze this conference contact and provide intelligent enhancements:
            
            {contact_context}
            
            User's Current Goals:
            {goals_context}
            
            Please provide:
            1. Interest tags (3-5 relevant keywords)
            2. Goal relevance score (1-10 for each goal)
            3. Relationship priority (Hot, Warm, Cool)
            4. Follow-up timing (today, 2-3 days, next week)
            5. Key conversation themes
            
            Respond in JSON format:
            {{
                "interest_tags": ["tag1", "tag2", "tag3"],
                "goal_relevance": {{"goal_id": score}},
                "priority": "Hot|Warm|Cool",
                "follow_up_timing": "today|2-3 days|next week",
                "themes": ["theme1", "theme2"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            ai_analysis = json.loads(response.choices[0].message.content)
            
            # Update contact with AI insights
            conn = self.db.get_connection()
            try:
                # Update interest tags
                current_tags = contact.get('tags', '')
                new_tags = ai_analysis.get('interest_tags', [])
                all_tags = f"{current_tags}, {', '.join(new_tags)}".strip(', ')
                
                # Set warmth level based on priority
                priority_map = {'Hot': 'Active', 'Warm': 'Warm', 'Cool': 'Aware'}
                warmth_label = priority_map.get(ai_analysis.get('priority', 'Cool'), 'Aware')
                warmth_status = {'Active': 4, 'Warm': 3, 'Aware': 2}.get(warmth_label, 2)
                
                conn.execute("""
                    UPDATE contacts 
                    SET tags = ?, warmth_label = ?, warmth_status = ?, updated_at = ?
                    WHERE id = ?
                """, (all_tags, warmth_label, warmth_status, datetime.now().isoformat(), contact_id))
                
                # Store AI analysis
                conn.execute("""
                    INSERT INTO conference_ai_analysis (id, contact_id, analysis_data, created_at)
                    VALUES (?, ?, ?, ?)
                """, (str(uuid.uuid4()), contact_id, json.dumps(ai_analysis), 
                      datetime.now().isoformat()))
                
                conn.commit()
                
            finally:
                conn.close()
                
        except Exception as e:
            logging.error(f"Error in AI enhancement: {e}")
    
    def generate_conference_follow_ups(self, user_id: int, conference_id: str) -> List[Dict[str, Any]]:
        """Generate AI-powered follow-up suggestions for conference contacts"""
        try:
            # Get conference details
            conference = self.get_conference_by_id(conference_id)
            if not conference:
                return []
            
            # Get conference contacts
            contacts = self.get_conference_contacts(conference_id)
            if not contacts:
                return []
            
            # Get user goals
            goals = self.goal_model.get_all(user_id)
            goals_context = "\n".join([f"- {goal['title']}: {goal['description']}" for goal in goals])
            
            # Build contacts context
            contacts_context = []
            for contact in contacts:
                context = f"""
                - {contact['name']}, "{contact.get('company', 'Unknown')}, {contact.get('title', 'Unknown')}, {contact.get('conversation_notes', 'No notes')}"
                """
                contacts_context.append(context.strip())
            
            prompt = f"""
            You are an AI embedded in a founder's relationship system. The user just attended a conference.

            Your job is to:
            - Review the list of new contacts they met at this event
            - Analyze who is most relevant to the user's current goal(s)
            - Suggest warm, thoughtful follow-ups personalized to the conversation
            - Prioritize based on timing, opportunity, and depth of connection

            Event: "{conference['name']}"
            User's Goals:
            {goals_context}
            
            Contacts:
            {chr(10).join(contacts_context)}

            For each contact, return:
            - Name
            - Reason to follow up
            - Suggested message (warm and personalized)
            - Suggested timing (e.g., "today", "in 2 days", "next week")

            Respond in JSON format as an array of objects.
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            ai_suggestions = json.loads(response.choices[0].message.content)
            
            # Store follow-up suggestions
            self._store_follow_up_suggestions(conference_id, ai_suggestions)
            
            return ai_suggestions.get('suggestions', ai_suggestions) if isinstance(ai_suggestions, dict) else ai_suggestions
            
        except Exception as e:
            logging.error(f"Error generating follow-ups: {e}")
            return []
    
    def _store_follow_up_suggestions(self, conference_id: str, suggestions: List[Dict]):
        """Store follow-up suggestions in the database"""
        conn = self.db.get_connection()
        try:
            for suggestion in suggestions:
                if isinstance(suggestion, dict) and 'name' in suggestion:
                    conn.execute("""
                        INSERT INTO conference_follow_ups (id, conference_id, contact_name,
                                                         reason, message, timing, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (str(uuid.uuid4()), conference_id, suggestion['name'],
                          suggestion.get('reason', ''), suggestion.get('message', ''),
                          suggestion.get('timing', ''), datetime.now().isoformat()))
            
            conn.commit()
            
        except Exception as e:
            logging.error(f"Error storing follow-up suggestions: {e}")
        finally:
            conn.close()
    
    def get_conference_contacts(self, conference_id: str) -> List[Dict[str, Any]]:
        """Get all contacts captured during a conference"""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.id, c.name, c.email, c.company, c.title, c.notes, c.tags,
                       cc.conversation_notes, cc.voice_memo, cc.captured_at
                FROM contacts c
                JOIN conference_contacts cc ON c.id = cc.contact_id
                WHERE cc.conference_id = ?
                ORDER BY cc.captured_at DESC
            """, (conference_id,))
            
            contacts = []
            for row in cursor.fetchall():
                contacts.append({
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'company': row[3],
                    'title': row[4],
                    'notes': row[5],
                    'tags': row[6],
                    'conversation_notes': row[7],
                    'voice_memo': row[8],
                    'captured_at': row[9]
                })
            
            return contacts
            
        finally:
            conn.close()
    
    def get_conference_by_id(self, conference_id: str) -> Optional[Dict[str, Any]]:
        """Get conference details by ID"""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, location, start_date, end_date, created_at
                FROM conferences WHERE id = ?
            """, (conference_id,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'name': result[1],
                    'location': result[2],
                    'start_date': result[3],
                    'end_date': result[4],
                    'created_at': result[5]
                }
            return None
            
        finally:
            conn.close()
    
    def get_daily_follow_up_summary(self, user_id: int) -> Dict[str, Any]:
        """Get today's most important conference follow-ups"""
        try:
            # Get active conference
            active_conference = self.get_active_conference(user_id)
            if not active_conference:
                return {'contacts': [], 'conference': None}
            
            # Get recent follow-up suggestions
            conn = self.db.get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT contact_name, reason, message, timing
                    FROM conference_follow_ups
                    WHERE conference_id = ? AND created_at >= date('now', '-1 day')
                    ORDER BY 
                        CASE timing 
                            WHEN 'today' THEN 1
                            WHEN 'in 2 days' THEN 2
                            WHEN '2-3 days' THEN 2
                            WHEN 'next week' THEN 3
                            ELSE 4
                        END,
                        created_at DESC
                    LIMIT 3
                """, (active_conference['id'],))
                
                follow_ups = []
                for row in cursor.fetchall():
                    follow_ups.append({
                        'name': row[0],
                        'reason': row[1],
                        'message': row[2],
                        'timing': row[3]
                    })
                
                return {
                    'conference': active_conference,
                    'contacts': follow_ups
                }
                
            finally:
                conn.close()
                
        except Exception as e:
            logging.error(f"Error getting daily summary: {e}")
            return {'contacts': [], 'conference': None}
    
    def process_voice_memo(self, voice_text: str) -> Dict[str, str]:
        """Process voice memo to extract contact information"""
        try:
            prompt = f"""
            Extract contact information from this voice memo:
            "{voice_text}"
            
            Extract and return:
            - Name
            - Company/Organization (if mentioned)
            - What they do/title (if mentioned)
            - Key conversation points
            - Interests or topics discussed
            
            Return as JSON:
            {{
                "name": "extracted name",
                "company": "extracted company",
                "title": "extracted title",
                "conversation_summary": "key points discussed",
                "interests": ["interest1", "interest2"]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logging.error(f"Error processing voice memo: {e}")
            return {}
    
    def mark_follow_up_complete(self, user_id: int, contact_name: str, conference_id: str):
        """Mark a follow-up as completed"""
        conn = self.db.get_connection()
        try:
            conn.execute("""
                UPDATE conference_follow_ups 
                SET completed = TRUE, completed_at = ?
                WHERE conference_id = ? AND contact_name = ?
            """, (datetime.now().isoformat(), conference_id, contact_name))
            
            conn.commit()
            logging.info(f"Marked follow-up complete for {contact_name}")
            
        except Exception as e:
            logging.error(f"Error marking follow-up complete: {e}")
        finally:
            conn.close()