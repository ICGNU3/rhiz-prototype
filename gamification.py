"""
Gamification Engine for Founder Network AI
Handles XP, titles, daily quests, achievements, and streaks to make networking engaging.
"""

import sqlite3
import uuid
import json
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from models import Database
import openai
import os

class GamificationEngine:
    """Main gamification system for tracking user progress and engagement"""
    
    def __init__(self, db: Database):
        self.db = db
        self.openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # XP values for different actions
        self.xp_rewards = {
            'add_contact': 15,
            'add_note': 10,
            'follow_up': 20,
            'email_sent': 25,
            'meeting_scheduled': 30,
            'goal_matched': 15,
            'relationship_created': 20,
            'conference_contact': 25,
            'daily_login': 5,
            'quest_completed': 50,
            'achievement_unlocked': 100
        }
        
        # Title progression based on XP
        self.titles = [
            (0, 'Contact Seeker'),
            (100, 'Connector'),
            (250, 'Network Weaver'),
            (500, 'Intent Architect'),
            (1000, 'Rhizomatic Operator'),
            (2000, 'Network Sage'),
            (5000, 'Connection Master')
        ]
    
    def award_xp(self, user_id: int, action: str, points: Optional[int] = None) -> Dict[str, Any]:
        """Award XP for an action and check for level/title changes"""
        if points is None:
            points = self.xp_rewards.get(action, 10)
        
        conn = self.db.get_connection()
        try:
            # Get current XP and title
            cursor = conn.cursor()
            cursor.execute("SELECT xp, title FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            
            if not result:
                return {'success': False, 'error': 'User not found'}
            
            old_xp, old_title = result
            new_xp = old_xp + points
            
            # Update XP
            conn.execute("UPDATE users SET xp = ? WHERE id = ?", (new_xp, user_id))
            
            # Check for title upgrade
            new_title = self.get_title_for_xp(new_xp)
            title_upgraded = False
            
            if new_title != old_title:
                conn.execute("UPDATE users SET title = ? WHERE id = ?", (new_title, user_id))
                title_upgraded = True
                
                # Award achievement for title upgrade
                self.unlock_achievement(
                    user_id, 
                    'title_upgrade', 
                    f'Title Upgraded: {new_title}',
                    f'Reached the title of {new_title}',
                    50
                )
            
            # Log streak
            self.log_daily_streak(user_id)
            
            conn.commit()
            
            logging.info(f"Awarded {points} XP to user {user_id} for {action}")
            
            return {
                'success': True,
                'points_awarded': points,
                'old_xp': old_xp,
                'new_xp': new_xp,
                'title_upgraded': title_upgraded,
                'old_title': old_title,
                'new_title': new_title
            }
            
        except Exception as e:
            logging.error(f"Error awarding XP: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def get_title_for_xp(self, xp: int) -> str:
        """Get the appropriate title for an XP amount"""
        for required_xp, title in reversed(self.titles):
            if xp >= required_xp:
                return title
        return 'Contact Seeker'
    
    def get_user_progress(self, user_id: int) -> Dict[str, Any]:
        """Get complete user progress including XP, title, streaks, and next milestone"""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT xp, title, streak_count FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            
            if not result:
                return {}
            
            xp, title, streak_count = result
            
            # Find next title milestone
            next_title = None
            next_xp_needed = None
            
            for required_xp, title_name in self.titles:
                if required_xp > xp:
                    next_title = title_name
                    next_xp_needed = required_xp - xp
                    break
            
            # Get recent achievements
            cursor.execute("""
                SELECT achievement_name, description, xp_awarded, unlocked_at
                FROM user_achievements 
                WHERE user_id = ? 
                ORDER BY unlocked_at DESC 
                LIMIT 3
            """, (user_id,))
            
            recent_achievements = []
            for row in cursor.fetchall():
                recent_achievements.append({
                    'name': row[0],
                    'description': row[1],
                    'xp_awarded': row[2],
                    'unlocked_at': row[3]
                })
            
            return {
                'xp': xp,
                'title': title,
                'streak_count': streak_count or 0,
                'next_title': next_title,
                'next_xp_needed': next_xp_needed,
                'recent_achievements': recent_achievements
            }
            
        finally:
            conn.close()
    
    def log_daily_streak(self, user_id: int):
        """Log daily activity and update streak count"""
        today = date.today()
        
        conn = self.db.get_connection()
        try:
            # Check if already logged today
            cursor = conn.cursor()
            cursor.execute("""
                SELECT actions_count FROM user_streaks 
                WHERE user_id = ? AND date = ?
            """, (user_id, today))
            
            existing = cursor.fetchone()
            
            if existing:
                # Increment action count for today
                conn.execute("""
                    UPDATE user_streaks 
                    SET actions_count = actions_count + 1 
                    WHERE user_id = ? AND date = ?
                """, (user_id, today))
            else:
                # New day - insert record
                conn.execute("""
                    INSERT INTO user_streaks (user_id, date, actions_count)
                    VALUES (?, ?, 1)
                """, (user_id, today))
                
                # Update streak count
                self.update_streak_count(user_id)
            
            conn.commit()
            
        except Exception as e:
            logging.error(f"Error logging daily streak: {e}")
        finally:
            conn.close()
    
    def update_streak_count(self, user_id: int):
        """Calculate and update the user's current streak"""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            
            # Get all streak dates for user in descending order
            cursor.execute("""
                SELECT date FROM user_streaks 
                WHERE user_id = ? 
                ORDER BY date DESC
            """, (user_id,))
            
            dates = [datetime.strptime(row[0], '%Y-%m-%d').date() for row in cursor.fetchall()]
            
            if not dates:
                conn.execute("UPDATE users SET streak_count = 0 WHERE id = ?", (user_id,))
                conn.commit()
                return
            
            # Calculate consecutive days from today
            streak = 0
            today = date.today()
            current_date = today
            
            for streak_date in dates:
                if streak_date == current_date:
                    streak += 1
                    current_date -= timedelta(days=1)
                elif streak_date == current_date - timedelta(days=1):
                    # Allow for one day gap (yesterday)
                    current_date = streak_date
                    streak += 1
                    current_date -= timedelta(days=1)
                else:
                    break
            
            # Update streak count
            conn.execute("UPDATE users SET streak_count = ? WHERE id = ?", (streak, user_id))
            
            # Check for streak achievements
            if streak >= 7:
                self.unlock_achievement(user_id, 'week_streak', 'Week Warrior', 'Maintained 7-day streak', 25)
            if streak >= 30:
                self.unlock_achievement(user_id, 'month_streak', 'Monthly Master', 'Maintained 30-day streak', 100)
            
            conn.commit()
            
        except Exception as e:
            logging.error(f"Error updating streak count: {e}")
        finally:
            conn.close()
    
    def generate_daily_quests(self, user_id: int) -> List[Dict[str, Any]]:
        """Generate personalized daily quests using AI"""
        try:
            # Get user context
            user_progress = self.get_user_progress(user_id)
            
            # Get user goals and recent contacts
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT title, description FROM goals WHERE user_id = ? LIMIT 3", (user_id,))
            goals = [{'title': row[0], 'description': row[1]} for row in cursor.fetchall()]
            
            cursor.execute("""
                SELECT name, company, warmth_label, last_interaction_date 
                FROM contacts 
                WHERE user_id = ? 
                ORDER BY last_interaction_date DESC 
                LIMIT 5
            """, (user_id,))
            
            recent_contacts = []
            for row in cursor.fetchall():
                recent_contacts.append({
                    'name': row[0],
                    'company': row[1],
                    'warmth': row[2],
                    'last_interaction': row[3]
                })
            
            conn.close()
            
            # Generate quests with AI
            prompt = f"""
            You are a gamification AI for a founder networking platform. Generate 3 personalized daily quests for a user.

            User Context:
            - Title: {user_progress.get('title', 'Contact Seeker')}
            - XP: {user_progress.get('xp', 0)}
            - Streak: {user_progress.get('streak_count', 0)} days
            
            Goals: {json.dumps(goals)}
            Recent Contacts: {json.dumps(recent_contacts)}
            
            Create quests that are:
            1. Actionable today
            2. Aligned with their goals
            3. Progressive (harder for higher-level users)
            4. Engaging and motivating
            
            Quest types to choose from:
            - follow_up (reach out to specific contacts)
            - add_contact (meet new people)
            - relationship_building (strengthen existing connections)
            - goal_alignment (connect contacts to goals)
            - conference_networking (if applicable)
            
            Return JSON format:
            {{
                "quests": [
                    {{
                        "text": "Quest description",
                        "type": "quest_type",
                        "target_value": 1,
                        "xp_reward": 20
                    }}
                ],
                "contact_of_the_day": "Name of contact to focus on",
                "motivational_message": "Encouraging message for the user"
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            ai_response = json.loads(response.choices[0].message.content)
            
            # Store quests in database
            today = date.today()
            generated_quests = []
            
            conn = self.db.get_connection()
            try:
                for quest_data in ai_response.get('quests', []):
                    quest_id = str(uuid.uuid4())
                    
                    conn.execute("""
                        INSERT INTO daily_quests (id, user_id, quest_text, quest_type, 
                                                target_value, xp_reward, date_created)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        quest_id,
                        user_id,
                        quest_data['text'],
                        quest_data['type'],
                        quest_data.get('target_value', 1),
                        quest_data.get('xp_reward', 20),
                        today
                    ))
                    
                    generated_quests.append({
                        'id': quest_id,
                        'text': quest_data['text'],
                        'type': quest_data['type'],
                        'target_value': quest_data.get('target_value', 1),
                        'current_progress': 0,
                        'xp_reward': quest_data.get('xp_reward', 20),
                        'completed': False
                    })
                
                conn.commit()
                
                return {
                    'quests': generated_quests,
                    'contact_of_the_day': ai_response.get('contact_of_the_day', ''),
                    'motivational_message': ai_response.get('motivational_message', 'Keep building your network!')
                }
                
            finally:
                conn.close()
                
        except Exception as e:
            logging.error(f"Error generating daily quests: {e}")
            return {
                'quests': [],
                'contact_of_the_day': '',
                'motivational_message': 'Keep networking and growing your connections!'
            }
    
    def get_daily_quests(self, user_id: int) -> Dict[str, Any]:
        """Get today's quests for a user, generating them if they don't exist"""
        today = date.today()
        
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, quest_text, quest_type, target_value, current_progress, 
                       xp_reward, completed
                FROM daily_quests 
                WHERE user_id = ? AND date_created = ?
            """, (user_id, today))
            
            existing_quests = []
            for row in cursor.fetchall():
                existing_quests.append({
                    'id': row[0],
                    'text': row[1],
                    'type': row[2],
                    'target_value': row[3],
                    'current_progress': row[4],
                    'xp_reward': row[5],
                    'completed': bool(row[6])
                })
            
            if existing_quests:
                return {
                    'quests': existing_quests,
                    'contact_of_the_day': 'Focus on your warm connections',
                    'motivational_message': 'Great job staying consistent with your networking!'
                }
            else:
                # Generate new quests
                return self.generate_daily_quests(user_id)
                
        finally:
            conn.close()
    
    def complete_quest(self, user_id: int, quest_id: str) -> Dict[str, Any]:
        """Mark a quest as completed and award XP"""
        conn = self.db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT xp_reward, completed FROM daily_quests 
                WHERE id = ? AND user_id = ?
            """, (quest_id, user_id))
            
            result = cursor.fetchone()
            if not result:
                return {'success': False, 'error': 'Quest not found'}
            
            xp_reward, completed = result
            
            if completed:
                return {'success': False, 'error': 'Quest already completed'}
            
            # Mark as completed
            conn.execute("""
                UPDATE daily_quests 
                SET completed = TRUE, current_progress = target_value, date_completed = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), quest_id))
            
            conn.commit()
            
            # Award XP
            xp_result = self.award_xp(user_id, 'quest_completed', xp_reward)
            
            return {
                'success': True,
                'xp_awarded': xp_reward,
                'xp_result': xp_result
            }
            
        except Exception as e:
            logging.error(f"Error completing quest: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def unlock_achievement(self, user_id: int, achievement_type: str, name: str, description: str, xp_reward: int = 0):
        """Unlock an achievement for a user"""
        conn = self.db.get_connection()
        try:
            # Check if achievement already exists
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM user_achievements 
                WHERE user_id = ? AND achievement_type = ?
            """, (user_id, achievement_type))
            
            if cursor.fetchone():
                return  # Achievement already unlocked
            
            # Create achievement
            achievement_id = str(uuid.uuid4())
            conn.execute("""
                INSERT INTO user_achievements (id, user_id, achievement_type, achievement_name,
                                             description, xp_awarded, unlocked_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                achievement_id,
                user_id,
                achievement_type,
                name,
                description,
                xp_reward,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            
            # Award XP for achievement
            if xp_reward > 0:
                self.award_xp(user_id, 'achievement_unlocked', xp_reward)
            
            logging.info(f"Achievement unlocked for user {user_id}: {name}")
            
        except Exception as e:
            logging.error(f"Error unlocking achievement: {e}")
        finally:
            conn.close()
    
    def update_last_action(self, contact_id: str):
        """Update the last action timestamp for a contact"""
        conn = self.db.get_connection()
        try:
            conn.execute("""
                UPDATE contacts 
                SET last_action = ? 
                WHERE id = ?
            """, (datetime.now().isoformat(), contact_id))
            conn.commit()
        except Exception as e:
            logging.error(f"Error updating last action: {e}")
        finally:
            conn.close()