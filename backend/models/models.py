import sqlite3
import uuid
from datetime import datetime
import json
import logging

class Database:
    def __init__(self, db_path='db.sqlite3'):
        self.db_path = db_path
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

class User:
    def __init__(self, db):
        self.db = db
    
    def create(self, email):
        user_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        try:
            conn.execute(
                "INSERT INTO users (id, email) VALUES (?, ?)",
                (user_id, email)
            )
            conn.commit()
            logging.info(f"Created user: {user_id}")
            return user_id
        except Exception as e:
            logging.error(f"Failed to create user: {e}")
            return None
        finally:
            conn.close()
    
    def get_or_create_default(self):
        """Get or create a default user for demo purposes"""
        conn = self.db.get_connection()
        try:
            user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
            if user:
                return user['id']
            else:
                return self.create("demo@founder-network.ai")
        finally:
            conn.close()

class Contact:
    def __init__(self, db):
        self.db = db
    
    def create(self, user_id, name, email=None, phone=None, twitter=None, linkedin=None, 
               handle=None, relationship_type='Contact', warmth_status=1, warmth_label='Cold',
               priority_level='Medium', notes=None, narrative_thread=None, tags=None,
               introduced_by=None, location=None, company=None, title=None, interests=None,
               follow_up_action=None, follow_up_due_date=None):
        contact_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        try:
            conn.execute(
                """INSERT INTO contacts 
                   (id, user_id, name, email, phone, twitter, linkedin, handle, relationship_type,
                    warmth_status, warmth_label, priority_level, notes, narrative_thread, tags,
                    introduced_by, location, company, title, interests, follow_up_action, follow_up_due_date) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (contact_id, user_id, name, email, phone, twitter, linkedin, handle, relationship_type,
                 warmth_status, warmth_label, priority_level, notes, narrative_thread, tags,
                 introduced_by, location, company, title, interests, follow_up_action, follow_up_due_date)
            )
            conn.commit()
            logging.info(f"Created contact: {contact_id}")
            return contact_id
        except Exception as e:
            logging.error(f"Failed to create contact: {e}")
            return None
        finally:
            conn.close()
    
    def get_all(self, user_id):
        conn = self.db.get_connection()
        try:
            contacts = conn.execute(
                "SELECT * FROM contacts WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()
            return [dict(contact) for contact in contacts]
        finally:
            conn.close()
    
    def get_by_id(self, contact_id):
        conn = self.db.get_connection()
        try:
            contact = conn.execute(
                "SELECT * FROM contacts WHERE id = ?",
                (contact_id,)
            ).fetchone()
            return dict(contact) if contact else None
        finally:
            conn.close()
    
    def update_last_interaction(self, contact_id, interaction_method='Email'):
        conn = self.db.get_connection()
        try:
            conn.execute(
                "UPDATE contacts SET last_interaction_date = datetime('now'), last_contact_method = ?, interaction_count = interaction_count + 1, updated_at = datetime('now') WHERE id = ?",
                (interaction_method, contact_id)
            )
            conn.commit()
        finally:
            conn.close()
    
    def update_warmth_status(self, contact_id, warmth_status, warmth_label):
        conn = self.db.get_connection()
        try:
            conn.execute(
                "UPDATE contacts SET warmth_status = ?, warmth_label = ?, updated_at = datetime('now') WHERE id = ?",
                (warmth_status, warmth_label, contact_id)
            )
            conn.commit()
        finally:
            conn.close()
    
    def get_by_filters(self, user_id, warmth_status=None, priority_level=None, relationship_type=None, days_since_contact=None):
        """Get contacts with advanced filtering for CRM views"""
        conn = self.db.get_connection()
        try:
            query = "SELECT * FROM contacts WHERE user_id = ?"
            params = [user_id]
            
            if warmth_status:
                query += " AND warmth_status = ?"
                params.append(warmth_status)
            
            if priority_level:
                query += " AND priority_level = ?"
                params.append(priority_level)
            
            if relationship_type:
                query += " AND relationship_type = ?"
                params.append(relationship_type)
            
            if days_since_contact:
                query += " AND (last_interaction_date IS NULL OR last_interaction_date < datetime('now', '-' || ? || ' days'))"
                params.append(days_since_contact)
            
            query += " ORDER BY priority_level DESC, last_interaction_date ASC"
            
            contacts = conn.execute(query, params).fetchall()
            return [dict(contact) for contact in contacts]
        finally:
            conn.close()
    
    def get_follow_ups_due(self, user_id, days_ahead=7):
        """Get contacts with follow-ups due in the next N days"""
        conn = self.db.get_connection()
        try:
            contacts = conn.execute(
                """SELECT * FROM contacts WHERE user_id = ? 
                   AND follow_up_due_date IS NOT NULL 
                   AND follow_up_due_date <= datetime('now', '+' || ? || ' days')
                   ORDER BY follow_up_due_date ASC""",
                (user_id, days_ahead)
            ).fetchall()
            return [dict(contact) for contact in contacts]
        finally:
            conn.close()
    
    def get_pipeline_view(self, user_id):
        """Get contacts organized by warmth pipeline stages"""
        conn = self.db.get_connection()
        try:
            pipeline = {}
            warmth_stages = ['Cold', 'Aware', 'Warm', 'Active', 'Contributor']
            
            for stage in warmth_stages:
                contacts = conn.execute(
                    "SELECT * FROM contacts WHERE user_id = ? AND warmth_label = ? ORDER BY updated_at DESC",
                    (user_id, stage)
                ).fetchall()
                pipeline[stage] = [dict(contact) for contact in contacts]
            
            return pipeline
        finally:
            conn.close()
    
    @staticmethod
    def get_warmth_options():
        """Get available warmth status options"""
        return [
            ('cold', 'Cold'),
            ('aware', 'Aware'),
            ('warm', 'Warm'),
            ('active', 'Active'),
            ('contributor', 'Contributor')
        ]
    
    @staticmethod
    def get_relationship_types():
        """Get available relationship types"""
        return [
            ('colleague', 'Colleague'),
            ('client', 'Client'),
            ('advisor', 'Advisor'),
            ('investor', 'Investor'),
            ('mentor', 'Mentor'),
            ('friend', 'Friend'),
            ('acquaintance', 'Acquaintance'),
            ('lead', 'Lead')
        ]
    
    def get_company_options(self, user_id):
        """Get list of unique companies for a user"""
        conn = self.db.get_connection()
        try:
            companies = conn.execute(
                "SELECT DISTINCT company FROM contacts WHERE user_id = ? AND company IS NOT NULL AND company != '' ORDER BY company",
                (user_id,)
            ).fetchall()
            return [company['company'] for company in companies]
        except Exception as e:
            logging.error(f"Error getting company options: {e}")
            return []
        finally:
            conn.close()

class Goal:
    def __init__(self, db):
        self.db = db
    
    def create(self, user_id, title, description, embedding=None):
        goal_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        try:
            conn.execute(
                "INSERT INTO goals (id, user_id, title, description, embedding) VALUES (?, ?, ?, ?, ?)",
                (goal_id, user_id, title, description, embedding)
            )
            conn.commit()
            logging.info(f"Created goal: {goal_id}")
            return goal_id
        except Exception as e:
            logging.error(f"Failed to create goal: {e}")
            return None
        finally:
            conn.close()
    
    def get_all(self, user_id):
        conn = self.db.get_connection()
        try:
            goals = conn.execute(
                "SELECT * FROM goals WHERE user_id = ? ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()
            return [dict(goal) for goal in goals]
        finally:
            conn.close()
    
    def get_by_id(self, goal_id):
        conn = self.db.get_connection()
        try:
            goal = conn.execute(
                "SELECT * FROM goals WHERE id = ?",
                (goal_id,)
            ).fetchone()
            return dict(goal) if goal else None
        finally:
            conn.close()
    
    def update_embedding(self, goal_id, embedding):
        conn = self.db.get_connection()
        try:
            conn.execute(
                "UPDATE goals SET embedding = ? WHERE id = ?",
                (embedding, goal_id)
            )
            conn.commit()
        finally:
            conn.close()

class AISuggestion:
    def __init__(self, db):
        self.db = db
    
    def create(self, contact_id, goal_id, suggestion, confidence):
        suggestion_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        try:
            conn.execute(
                "INSERT INTO ai_suggestions (id, contact_id, goal_id, suggestion, confidence) VALUES (?, ?, ?, ?, ?)",
                (suggestion_id, contact_id, goal_id, suggestion, confidence)
            )
            conn.commit()
            return suggestion_id
        finally:
            conn.close()
    
    def get_recent(self, user_id, limit=5):
        """Get recent AI suggestions for a user"""
        conn = self.db.get_connection()
        try:
            suggestions = conn.execute(
                """SELECT ai.*, c.name as contact_name, g.title as goal_title 
                   FROM ai_suggestions ai
                   JOIN contacts c ON ai.contact_id = c.id
                   JOIN goals g ON ai.goal_id = g.id
                   WHERE g.user_id = ? 
                   ORDER BY ai.created_at DESC 
                   LIMIT ?""",
                (user_id, limit)
            ).fetchall()
            return [dict(suggestion) for suggestion in suggestions]
        except Exception as e:
            logging.error(f"Error getting recent AI suggestions: {e}")
            return []
        finally:
            conn.close()

class ContactInteraction:
    def __init__(self, db):
        self.db = db
    
    def create(self, contact_id, user_id, interaction_type='Email', status='sent', direction='outbound', 
               subject=None, summary=None, sentiment='neutral', notes=None, follow_up_needed=False,
               follow_up_action=None, follow_up_date=None, duration_minutes=None):
        interaction_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        try:
            conn.execute(
                """INSERT INTO contact_interactions 
                   (id, contact_id, user_id, interaction_type, status, direction, subject, summary, 
                    sentiment, notes, follow_up_needed, follow_up_action, follow_up_date, duration_minutes) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (interaction_id, contact_id, user_id, interaction_type, status, direction, subject, 
                 summary, sentiment, notes, follow_up_needed, follow_up_action, follow_up_date, duration_minutes)
            )
            conn.commit()
            return interaction_id
        finally:
            conn.close()
    
    def get_by_contact(self, contact_id):
        conn = self.db.get_connection()
        try:
            interactions = conn.execute(
                "SELECT * FROM contact_interactions WHERE contact_id = ? ORDER BY timestamp DESC",
                (contact_id,)
            ).fetchall()
            return [dict(interaction) for interaction in interactions]
        finally:
            conn.close()
    
    def get_timeline(self, user_id, days_back=30):
        """Get interaction timeline for the user"""
        conn = self.db.get_connection()
        try:
            interactions = conn.execute(
                """SELECT ci.*, c.name as contact_name 
                   FROM contact_interactions ci 
                   JOIN contacts c ON ci.contact_id = c.id 
                   WHERE ci.user_id = ? AND ci.timestamp >= datetime('now', '-' || ? || ' days')
                   ORDER BY ci.timestamp DESC""",
                (user_id, days_back)
            ).fetchall()
            return [dict(interaction) for interaction in interactions]
        finally:
            conn.close()
    
    def get_recent(self, user_id, limit=5):
        """Get recent contact interactions for a user"""
        conn = self.db.get_connection()
        try:
            interactions = conn.execute(
                """SELECT ci.*, c.name as contact_name 
                   FROM contact_interactions ci 
                   JOIN contacts c ON ci.contact_id = c.id 
                   WHERE ci.user_id = ? 
                   ORDER BY ci.timestamp DESC 
                   LIMIT ?""",
                (user_id, limit)
            ).fetchall()
            return [dict(interaction) for interaction in interactions]
        except Exception as e:
            logging.error(f"Error getting recent interactions: {e}")
            return []
        finally:
            conn.close()
    
    def count_pending_follow_ups(self, user_id):
        """Count pending follow-ups for a user"""
        conn = self.db.get_connection()
        try:
            count = conn.execute(
                """SELECT COUNT(*) as count 
                   FROM contact_interactions 
                   WHERE user_id = ? AND follow_up_needed = 1 
                   AND (follow_up_date IS NULL OR follow_up_date <= datetime('now'))""",
                (user_id,)
            ).fetchone()
            return count['count'] if count else 0
        except Exception as e:
            logging.error(f"Error counting pending follow-ups: {e}")
            return 0
        finally:
            conn.close()
    
    def count_this_month(self, user_id):
        """Count interactions this month for a user"""
        conn = self.db.get_connection()
        try:
            count = conn.execute(
                """SELECT COUNT(*) as count 
                   FROM contact_interactions 
                   WHERE user_id = ? 
                   AND timestamp >= datetime('now', 'start of month')""",
                (user_id,)
            ).fetchone()
            return count['count'] if count else 0
        except Exception as e:
            logging.error(f"Error counting this month's interactions: {e}")
            return 0
        finally:
            conn.close()

class ContactRelationship:
    def __init__(self, db):
        self.db = db
    
    def create(self, user_id, contact_a_id, contact_b_id, relationship_type='knows', strength=1, notes=None):
        relationship_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        try:
            conn.execute(
                "INSERT INTO contact_relationships (id, user_id, contact_a_id, contact_b_id, relationship_type, strength, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (relationship_id, user_id, contact_a_id, contact_b_id, relationship_type, strength, notes)
            )
            conn.commit()
            return relationship_id
        finally:
            conn.close()
    
    def get_potential_introductions(self, user_id, contact_id):
        """Find contacts who might be good introductions for the given contact"""
        conn = self.db.get_connection()
        try:
            # Find contacts with similar tags or interests
            contact = conn.execute("SELECT tags, interests FROM contacts WHERE id = ?", (contact_id,)).fetchone()
            if not contact:
                return []
            
            tags = contact['tags'] or ''
            interests = contact['interests'] or ''
            
            # Simple matching based on tags and interests
            potential_matches = conn.execute(
                """SELECT DISTINCT c.*, cr.relationship_type, cr.strength 
                   FROM contacts c 
                   LEFT JOIN contact_relationships cr ON (c.id = cr.contact_b_id OR c.id = cr.contact_a_id)
                   WHERE c.user_id = ? AND c.id != ? 
                   AND (c.tags LIKE ? OR c.interests LIKE ? OR c.tags LIKE ? OR c.interests LIKE ?)
                   ORDER BY cr.strength DESC""",
                (user_id, contact_id, f'%{tags}%', f'%{interests}%', f'%{interests}%', f'%{tags}%')
            ).fetchall()
            
            return [dict(match) for match in potential_matches]
        finally:
            conn.close()

class OutreachSuggestion:
    def __init__(self, db):
        self.db = db
    
    def create(self, user_id, contact_id, suggestion_type, priority_score, reason, suggested_action, suggested_message=None):
        suggestion_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        try:
            conn.execute(
                "INSERT INTO outreach_suggestions (id, user_id, contact_id, suggestion_type, priority_score, reason, suggested_action, suggested_message) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (suggestion_id, user_id, contact_id, suggestion_type, priority_score, reason, suggested_action, suggested_message)
            )
            conn.commit()
            return suggestion_id
        finally:
            conn.close()
    
    def get_daily_suggestions(self, user_id, limit=10):
        """Get daily outreach suggestions ordered by priority"""
        conn = self.db.get_connection()
        try:
            suggestions = conn.execute(
                """SELECT os.*, c.name as contact_name, c.warmth_label, c.last_interaction_date
                   FROM outreach_suggestions os 
                   JOIN contacts c ON os.contact_id = c.id 
                   WHERE os.user_id = ? AND os.acted_on = FALSE 
                   ORDER BY os.priority_score DESC LIMIT ?""",
                (user_id, limit)
            ).fetchall()
            return [dict(suggestion) for suggestion in suggestions]
        finally:
            conn.close()
    
    def mark_acted_on(self, suggestion_id):
        conn = self.db.get_connection()
        try:
            conn.execute(
                "UPDATE outreach_suggestions SET acted_on = TRUE WHERE id = ?",
                (suggestion_id,)
            )
            conn.commit()
        finally:
            conn.close()

# Monica-Inspired CRM Features

class Reminder:
    def __init__(self, db):
        self.db = db
    
    def create(self, user_id, contact_id, title, description=None, reminder_type='follow_up', 
               due_date=None, is_recurring=False, recurrence_pattern=None):
        reminder_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        try:
            conn.execute(
                """INSERT INTO reminders 
                   (id, user_id, contact_id, title, description, reminder_type, due_date, 
                    is_recurring, recurrence_pattern) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (reminder_id, user_id, contact_id, title, description, reminder_type, 
                 due_date, is_recurring, recurrence_pattern)
            )
            conn.commit()
            return reminder_id
        finally:
            conn.close()
    
    def get_due_reminders(self, user_id, days_ahead=7):
        """Get reminders due in the next N days"""
        conn = self.db.get_connection()
        try:
            reminders = conn.execute(
                """SELECT r.*, c.name as contact_name 
                   FROM reminders r 
                   JOIN contacts c ON r.contact_id = c.id 
                   WHERE r.user_id = ? AND r.is_completed = FALSE 
                   AND r.due_date <= datetime('now', '+' || ? || ' days')
                   ORDER BY r.due_date ASC""",
                (user_id, days_ahead)
            ).fetchall()
            return [dict(reminder) for reminder in reminders]
        finally:
            conn.close()
    
    def mark_completed(self, reminder_id):
        conn = self.db.get_connection()
        try:
            conn.execute(
                "UPDATE reminders SET is_completed = TRUE, completed_at = datetime('now') WHERE id = ?",
                (reminder_id,)
            )
            conn.commit()
        finally:
            conn.close()
    
    def get_all(self, user_id):
        conn = self.db.get_connection()
        try:
            reminders = conn.execute(
                """SELECT r.*, c.name as contact_name 
                   FROM reminders r 
                   JOIN contacts c ON r.contact_id = c.id 
                   WHERE r.user_id = ? 
                   ORDER BY r.due_date ASC""",
                (user_id,)
            ).fetchall()
            return [dict(reminder) for reminder in reminders]
        finally:
            conn.close()

class JournalEntry:
    def __init__(self, db):
        self.db = db
    
    def create(self, user_id, contact_id, content, title=None, entry_type='note'):
        entry_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        try:
            conn.execute(
                """INSERT INTO journal_entries 
                   (id, user_id, contact_id, title, content, entry_type) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (entry_id, user_id, contact_id, title, content, entry_type)
            )
            conn.commit()
            return entry_id
        finally:
            conn.close()
    
    def get_by_contact(self, contact_id):
        conn = self.db.get_connection()
        try:
            entries = conn.execute(
                "SELECT * FROM journal_entries WHERE contact_id = ? ORDER BY created_at DESC",
                (contact_id,)
            ).fetchall()
            return [dict(entry) for entry in entries]
        finally:
            conn.close()
    
    def update(self, entry_id, title=None, content=None):
        conn = self.db.get_connection()
        try:
            if title and content:
                conn.execute(
                    "UPDATE journal_entries SET title = ?, content = ?, updated_at = datetime('now') WHERE id = ?",
                    (title, content, entry_id)
                )
            elif content:
                conn.execute(
                    "UPDATE journal_entries SET content = ?, updated_at = datetime('now') WHERE id = ?",
                    (content, entry_id)
                )
            conn.commit()
        finally:
            conn.close()

class Task:
    def __init__(self, db):
        self.db = db
    
    def create(self, user_id, title, description=None, contact_id=None, status='todo', 
               priority='medium', due_date=None):
        task_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        try:
            conn.execute(
                """INSERT INTO tasks 
                   (id, user_id, contact_id, title, description, status, priority, due_date) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (task_id, user_id, contact_id, title, description, status, priority, due_date)
            )
            conn.commit()
            return task_id
        finally:
            conn.close()
    
    def get_by_contact(self, contact_id):
        conn = self.db.get_connection()
        try:
            tasks = conn.execute(
                "SELECT * FROM tasks WHERE contact_id = ? ORDER BY created_at DESC",
                (contact_id,)
            ).fetchall()
            return [dict(task) for task in tasks]
        finally:
            conn.close()
    
    def get_all(self, user_id, status=None):
        conn = self.db.get_connection()
        try:
            if status:
                tasks = conn.execute(
                    """SELECT t.*, c.name as contact_name 
                       FROM tasks t 
                       LEFT JOIN contacts c ON t.contact_id = c.id 
                       WHERE t.user_id = ? AND t.status = ? 
                       ORDER BY t.due_date ASC""",
                    (user_id, status)
                ).fetchall()
            else:
                tasks = conn.execute(
                    """SELECT t.*, c.name as contact_name 
                       FROM tasks t 
                       LEFT JOIN contacts c ON t.contact_id = c.id 
                       WHERE t.user_id = ? 
                       ORDER BY t.due_date ASC""",
                    (user_id,)
                ).fetchall()
            return [dict(task) for task in tasks]
        finally:
            conn.close()
    
    def update_status(self, task_id, status):
        conn = self.db.get_connection()
        try:
            if status == 'done':
                conn.execute(
                    "UPDATE tasks SET status = ?, completed_at = datetime('now'), updated_at = datetime('now') WHERE id = ?",
                    (status, task_id)
                )
            else:
                conn.execute(
                    "UPDATE tasks SET status = ?, updated_at = datetime('now') WHERE id = ?",
                    (status, task_id)
                )
            conn.commit()
        finally:
            conn.close()

class Attachment:
    def __init__(self, db):
        self.db = db
    
    def create(self, user_id, contact_id, filename, original_filename, file_path=None, 
               file_url=None, file_size=None, file_type=None, description=None, is_link=False):
        attachment_id = str(uuid.uuid4())
        conn = self.db.get_connection()
        try:
            conn.execute(
                """INSERT INTO attachments 
                   (id, user_id, contact_id, filename, original_filename, file_path, 
                    file_url, file_size, file_type, description, is_link) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (attachment_id, user_id, contact_id, filename, original_filename, file_path,
                 file_url, file_size, file_type, description, is_link)
            )
            conn.commit()
            return attachment_id
        finally:
            conn.close()
    
    def get_by_contact(self, contact_id):
        conn = self.db.get_connection()
        try:
            attachments = conn.execute(
                "SELECT * FROM attachments WHERE contact_id = ? ORDER BY created_at DESC",
                (contact_id,)
            ).fetchall()
            return [dict(attachment) for attachment in attachments]
        finally:
            conn.close()
    
    def delete(self, attachment_id):
        conn = self.db.get_connection()
        try:
            # Get file path for cleanup
            attachment = conn.execute(
                "SELECT file_path FROM attachments WHERE id = ?",
                (attachment_id,)
            ).fetchone()
            
            # Delete database record
            conn.execute("DELETE FROM attachments WHERE id = ?", (attachment_id,))
            conn.commit()
            
            # Return file path for cleanup
            return attachment['file_path'] if attachment else None
        finally:
            conn.close()

class ContactIntelligence:
    """Main class for contact intelligence and natural language processing"""
    
    def __init__(self, db):
        self.db = db
        self.contact_model = Contact(db)
        self.interaction_model = ContactInteraction(db)
        self.relationship_model = ContactRelationship(db)
        self.suggestion_model = OutreachSuggestion(db)
        # Monica-inspired features
        self.reminder_model = Reminder(db)
        self.journal_model = JournalEntry(db)
        self.task_model = Task(db)
        self.attachment_model = Attachment(db)
    
    def generate_daily_suggestions(self, user_id):
        """Generate daily outreach suggestions based on contact data"""
        conn = self.db.get_connection()
        try:
            # Clear old suggestions
            conn.execute("DELETE FROM outreach_suggestions WHERE user_id = ? AND created_at < datetime('now', '-7 days')", (user_id,))
            
            # Get contacts for analysis
            contacts = self.contact_model.get_all(user_id)
            
            for contact in contacts:
                contact_id = contact['id']
                priority_score = 0
                suggestion_type = 'check_in'
                reason = ''
                
                # Calculate priority based on various factors
                days_since_contact = self._days_since_last_interaction(contact)
                warmth_status = contact.get('warmth_status', 1)
                priority_level = contact.get('priority_level', 'Medium')
                
                # Priority scoring logic
                if days_since_contact is None or days_since_contact > 30:
                    priority_score += 0.6
                    reason = 'No recent contact (30+ days)'
                    suggestion_type = 'follow_up'
                elif days_since_contact > 14:
                    priority_score += 0.4
                    reason = 'Follow-up needed (14+ days)'
                
                if priority_level == 'High':
                    priority_score += 0.3
                elif priority_level == 'Medium':
                    priority_score += 0.1
                
                if warmth_status <= 2:  # Cold or Aware
                    priority_score += 0.2
                    suggestion_type = 'nurture'
                    reason += ' - Contact needs nurturing'
                
                # Check for due follow-ups
                if contact.get('follow_up_due_date'):
                    follow_up_date = datetime.fromisoformat(contact['follow_up_due_date'])
                    if follow_up_date <= datetime.now():
                        priority_score += 0.5
                        suggestion_type = 'follow_up'
                        reason = 'Follow-up action due'
                
                # Only create suggestions for contacts with meaningful priority
                if priority_score >= 0.3:
                    suggested_action = self._generate_suggested_action(contact, suggestion_type)
                    self.suggestion_model.create(
                        user_id, contact_id, suggestion_type, priority_score, reason, suggested_action
                    )
            
            conn.commit()
            
        finally:
            conn.close()
    
    def _days_since_last_interaction(self, contact):
        """Calculate days since last interaction"""
        if not contact.get('last_interaction_date'):
            return None
        
        try:
            last_date = datetime.fromisoformat(contact['last_interaction_date'])
            return (datetime.now() - last_date).days
        except:
            return None
    
    def _generate_suggested_action(self, contact, suggestion_type):
        """Generate suggested action based on contact and suggestion type"""
        name = contact['name']
        
        if suggestion_type == 'follow_up':
            return f"Follow up with {name} about previous conversation"
        elif suggestion_type == 'nurture':
            return f"Send a warm check-in message to {name}"
        elif suggestion_type == 'introduction':
            return f"Consider introducing {name} to relevant contacts"
        else:
            return f"Reach out to {name} for a general check-in"
    
    def summarize_contact_history(self, contact_id):
        """Generate natural language summary of contact history"""
        contact = self.contact_model.get_by_id(contact_id)
        if not contact:
            return "Contact not found"
        
        interactions = self.interaction_model.get_by_contact(contact_id)
        
        summary = f"**{contact['name']}** - {contact['relationship_type']}\n"
        summary += f"Warmth: {contact['warmth_label']} | Priority: {contact['priority_level']}\n\n"
        
        if contact.get('company'):
            summary += f"Company: {contact['company']}\n"
        if contact.get('title'):
            summary += f"Title: {contact['title']}\n"
        if contact.get('location'):
            summary += f"Location: {contact['location']}\n"
        
        if contact.get('narrative_thread'):
            summary += f"\n**Context:** {contact['narrative_thread']}\n"
        
        if interactions:
            summary += f"\n**Recent Interactions ({len(interactions)}):**\n"
            for interaction in interactions[:3]:  # Show last 3
                date = interaction['timestamp'][:10]
                summary += f"• {date}: {interaction['interaction_type']} - {interaction.get('summary', 'No summary')}\n"
        else:
            summary += "\n**No recorded interactions yet**\n"
        
        if contact.get('follow_up_action'):
            summary += f"\n**Next Action:** {contact['follow_up_action']}"
            if contact.get('follow_up_due_date'):
                summary += f" (Due: {contact['follow_up_due_date'][:10]})"
        
        return summary
