"""
Collective Actions - Cohort-based Collaboration System
Enables users to join predefined collaborative initiatives with shared goals, resources, and progress tracking.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class CollectiveAction:
    """Represents a collective action with goals, timeline, and resources"""
    id: str
    title: str
    description: str
    goal_amount: str
    timeline_days: int
    category: str
    max_participants: int
    current_participants: int
    status: str  # 'active', 'full', 'completed', 'archived'
    start_date: str
    end_date: str
    resources: Dict[str, Any]
    created_at: str


class CollectiveActionsManager:
    """Manages collective actions and user participation"""
    
    # Predefined collective actions
    PREDEFINED_ACTIONS = {
        'raise_together': {
            'title': 'Raise Together',
            'description': 'Collaborative fundraising cohort for early-stage founders',
            'goal_amount': '$250K in 30 days',
            'timeline_days': 30,
            'category': 'fundraising',
            'max_participants': 20,
            'resources': {
                'templates': [
                    'Pitch Deck Template (Series A)',
                    'Financial Model Template',
                    'Investor Email Templates',
                    'Due Diligence Checklist'
                ],
                'advisors': [
                    'Sarah Chen - Former VC Partner',
                    'Marcus Rodriguez - Serial Entrepreneur',
                    'Dr. Patricia Wu - Finance Expert'
                ],
                'intro_opportunities': [
                    'Warm intros to 50+ VCs',
                    'Angel investor network access',
                    'Founder-to-founder referrals'
                ],
                'milestones': [
                    'Week 1: Pitch deck finalized',
                    'Week 2: 10 investor meetings scheduled',
                    'Week 3: First term sheet received',
                    'Week 4: Round closed'
                ]
            }
        },
        'hire_smart': {
            'title': 'Hire Smart',
            'description': 'Strategic hiring cohort for scaling teams effectively',
            'goal_amount': '5 key hires in 45 days',
            'timeline_days': 45,
            'category': 'hiring',
            'max_participants': 15,
            'resources': {
                'templates': [
                    'Job Description Templates',
                    'Interview Question Banks',
                    'Offer Letter Templates',
                    'Onboarding Checklists'
                ],
                'advisors': [
                    'David Kim - Head of Talent at TechCorp',
                    'Lisa Thompson - HR Consultant',
                    'James Park - Startup Recruiter'
                ],
                'intro_opportunities': [
                    'Access to vetted candidate pools',
                    'Recruiter network introductions',
                    'Cross-cohort talent sharing'
                ],
                'milestones': [
                    'Week 1: Job descriptions optimized',
                    'Week 2: Candidate pipeline established',
                    'Week 4: First offers extended',
                    'Week 6: Key positions filled'
                ]
            }
        },
        'find_beta_users': {
            'title': 'Find Beta Users',
            'description': 'Customer acquisition cohort for product validation',
            'goal_amount': '100 beta users in 21 days',
            'timeline_days': 21,
            'category': 'customer_acquisition',
            'max_participants': 25,
            'resources': {
                'templates': [
                    'Beta User Outreach Templates',
                    'Product Demo Scripts',
                    'Feedback Collection Forms',
                    'User Interview Guides'
                ],
                'advisors': [
                    'Rachel Green - Growth Marketing Expert',
                    'Tom Wilson - Product Manager',
                    'Elena Rodriguez - Customer Success'
                ],
                'intro_opportunities': [
                    'Early adopter communities',
                    'Product hunt launch support',
                    'Influencer network access'
                ],
                'milestones': [
                    'Week 1: Outreach strategy defined',
                    'Week 2: 25 beta users onboarded',
                    'Week 3: 100 users goal achieved'
                ]
            }
        },
        'scale_operations': {
            'title': 'Scale Operations',
            'description': 'Operational excellence cohort for growing businesses',
            'goal_amount': '50% efficiency gain in 60 days',
            'timeline_days': 60,
            'category': 'operations',
            'max_participants': 12,
            'resources': {
                'templates': [
                    'Process Documentation Templates',
                    'KPI Dashboards',
                    'Automation Playbooks',
                    'Team Structure Charts'
                ],
                'advisors': [
                    'Michael Chen - Operations Consultant',
                    'Susan Davis - Process Optimization Expert',
                    'Alex Martinez - Technology Integration'
                ],
                'intro_opportunities': [
                    'SaaS tool partnerships',
                    'Automation expert network',
                    'Efficiency consultant referrals'
                ],
                'milestones': [
                    'Week 2: Current processes audited',
                    'Week 4: Automation tools implemented',
                    'Week 6: Team training completed',
                    'Week 8: Efficiency targets met'
                ]
            }
        }
    }

    def __init__(self, db_path: str = 'db.sqlite3'):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize collective actions database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Collective actions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS collective_actions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    goal_amount TEXT,
                    timeline_days INTEGER,
                    category TEXT,
                    max_participants INTEGER,
                    current_participants INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    start_date TEXT,
                    end_date TEXT,
                    resources TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User participation table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS collective_action_participants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_id TEXT,
                    user_id TEXT,
                    joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    progress_data TEXT,
                    last_check_in TEXT,
                    completion_status TEXT DEFAULT 'active',
                    individual_goal TEXT,
                    FOREIGN KEY (action_id) REFERENCES collective_actions (id)
                )
            ''')
            
            # Progress updates table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS collective_action_updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_id TEXT,
                    user_id TEXT,
                    update_type TEXT,
                    content TEXT,
                    milestone_achieved TEXT,
                    progress_percentage REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    is_public BOOLEAN DEFAULT 1,
                    FOREIGN KEY (action_id) REFERENCES collective_actions (id)
                )
            ''')
            
            # Chat/check-in messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS collective_action_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_id TEXT,
                    user_id TEXT,
                    message_type TEXT,
                    content TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    is_system_message BOOLEAN DEFAULT 0,
                    FOREIGN KEY (action_id) REFERENCES collective_actions (id)
                )
            ''')
            
            # Reminders and nudges table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS collective_action_reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action_id TEXT,
                    user_id TEXT,
                    reminder_type TEXT,
                    content TEXT,
                    scheduled_for TEXT,
                    sent_at TEXT,
                    status TEXT DEFAULT 'pending',
                    FOREIGN KEY (action_id) REFERENCES collective_actions (id)
                )
            ''')
            
            conn.commit()

    def create_predefined_actions(self):
        """Create all predefined collective actions"""
        for action_key, action_data in self.PREDEFINED_ACTIONS.items():
            # Check if action already exists
            existing = self.get_action_by_id(action_key)
            if not existing:
                start_date = datetime.now()
                end_date = start_date + timedelta(days=action_data['timeline_days'])
                
                self.create_action(
                    action_id=action_key,
                    title=action_data['title'],
                    description=action_data['description'],
                    goal_amount=action_data['goal_amount'],
                    timeline_days=action_data['timeline_days'],
                    category=action_data['category'],
                    max_participants=action_data['max_participants'],
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat(),
                    resources=action_data['resources']
                )

    def create_action(self, action_id: str, title: str, description: str, 
                     goal_amount: str, timeline_days: int, category: str,
                     max_participants: int, start_date: str, end_date: str,
                     resources: Dict[str, Any]) -> str:
        """Create a new collective action"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO collective_actions 
                (id, title, description, goal_amount, timeline_days, category,
                 max_participants, start_date, end_date, resources)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (action_id, title, description, goal_amount, timeline_days,
                  category, max_participants, start_date, end_date,
                  json.dumps(resources)))
            conn.commit()
        return action_id

    def get_all_actions(self) -> List[Dict[str, Any]]:
        """Get all collective actions"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM collective_actions 
                WHERE status = 'active' 
                ORDER BY created_at DESC
            ''')
            
            actions = []
            for row in cursor.fetchall():
                action = dict(zip([col[0] for col in cursor.description], row))
                action['resources'] = json.loads(action['resources'] or '{}')
                actions.append(action)
            
            return actions

    def get_action_by_id(self, action_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific collective action by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM collective_actions WHERE id = ?', (action_id,))
            row = cursor.fetchone()
            
            if row:
                action = dict(zip([col[0] for col in cursor.description], row))
                action['resources'] = json.loads(action['resources'] or '{}')
                return action
            return None

    def join_action(self, action_id: str, user_id: str, individual_goal: str = None) -> bool:
        """User joins a collective action"""
        # Check if action exists and has space
        action = self.get_action_by_id(action_id)
        if not action:
            return False
            
        if action['current_participants'] >= action['max_participants']:
            return False
            
        # Check if user already joined
        if self.is_user_participating(action_id, user_id):
            return False
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Add user to participants
            cursor.execute('''
                INSERT INTO collective_action_participants 
                (action_id, user_id, individual_goal, progress_data)
                VALUES (?, ?, ?, ?)
            ''', (action_id, user_id, individual_goal or action['goal_amount'], 
                  json.dumps({'milestones_completed': [], 'progress_percentage': 0})))
            
            # Update participant count
            cursor.execute('''
                UPDATE collective_actions 
                SET current_participants = current_participants + 1 
                WHERE id = ?
            ''', (action_id,))
            
            # Add welcome message
            cursor.execute('''
                INSERT INTO collective_action_messages 
                (action_id, user_id, message_type, content, is_system_message)
                VALUES (?, ?, ?, ?, ?)
            ''', (action_id, user_id, 'welcome', 
                  f'Welcome to {action["title"]}! Your journey begins now.', True))
            
            conn.commit()
            
        # Schedule initial reminders
        self._schedule_reminders(action_id, user_id)
        return True

    def is_user_participating(self, action_id: str, user_id: str) -> bool:
        """Check if user is participating in an action"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 1 FROM collective_action_participants 
                WHERE action_id = ? AND user_id = ? AND completion_status = 'active'
            ''', (action_id, user_id))
            return cursor.fetchone() is not None

    def get_user_actions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all actions user is participating in"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ca.*, cap.joined_at, cap.progress_data, cap.individual_goal,
                       cap.completion_status, cap.last_check_in
                FROM collective_actions ca
                JOIN collective_action_participants cap ON ca.id = cap.action_id
                WHERE cap.user_id = ? AND cap.completion_status = 'active'
                ORDER BY cap.joined_at DESC
            ''', (user_id,))
            
            actions = []
            for row in cursor.fetchall():
                action = dict(zip([col[0] for col in cursor.description], row))
                action['resources'] = json.loads(action['resources'] or '{}')
                action['progress_data'] = json.loads(action['progress_data'] or '{}')
                actions.append(action)
            
            return actions

    def update_progress(self, action_id: str, user_id: str, update_type: str,
                       content: str, milestone_achieved: str = None,
                       progress_percentage: float = None) -> bool:
        """Update user progress in collective action"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Add progress update
            cursor.execute('''
                INSERT INTO collective_action_updates 
                (action_id, user_id, update_type, content, milestone_achieved, progress_percentage)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (action_id, user_id, update_type, content, milestone_achieved, progress_percentage))
            
            # Update participant progress data
            if progress_percentage is not None:
                cursor.execute('''
                    SELECT progress_data FROM collective_action_participants 
                    WHERE action_id = ? AND user_id = ?
                ''', (action_id, user_id))
                
                row = cursor.fetchone()
                if row:
                    progress_data = json.loads(row[0] or '{}')
                    progress_data['progress_percentage'] = progress_percentage
                    
                    if milestone_achieved:
                        if 'milestones_completed' not in progress_data:
                            progress_data['milestones_completed'] = []
                        progress_data['milestones_completed'].append({
                            'milestone': milestone_achieved,
                            'completed_at': datetime.now().isoformat()
                        })
                    
                    cursor.execute('''
                        UPDATE collective_action_participants 
                        SET progress_data = ?, last_check_in = CURRENT_TIMESTAMP
                        WHERE action_id = ? AND user_id = ?
                    ''', (json.dumps(progress_data), action_id, user_id))
            
            conn.commit()
            return True

    def get_action_feed(self, action_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent updates and messages for an action"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get recent updates
            cursor.execute('''
                SELECT 'update' as type, cau.*, u.email as user_email
                FROM collective_action_updates cau
                LEFT JOIN users u ON cau.user_id = u.id
                WHERE cau.action_id = ? AND cau.is_public = 1
                UNION ALL
                SELECT 'message' as type, cam.id, cam.action_id, cam.user_id,
                       cam.message_type as update_type, cam.content,
                       NULL as milestone_achieved, NULL as progress_percentage,
                       cam.created_at, cam.is_system_message as is_public,
                       u.email as user_email
                FROM collective_action_messages cam
                LEFT JOIN users u ON cam.user_id = u.id
                WHERE cam.action_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (action_id, action_id, limit))
            
            feed = []
            for row in cursor.fetchall():
                item = dict(zip([col[0] for col in cursor.description], row))
                feed.append(item)
            
            return feed

    def get_group_progress(self, action_id: str) -> Dict[str, Any]:
        """Get aggregated progress for the entire group"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get action details
            action = self.get_action_by_id(action_id)
            if not action:
                return {}
            
            # Get participant progress
            cursor.execute('''
                SELECT progress_data FROM collective_action_participants 
                WHERE action_id = ? AND completion_status = 'active'
            ''', (action_id,))
            
            participants = cursor.fetchall()
            total_participants = len(participants)
            total_progress = 0
            milestones_completed = 0
            
            for (progress_data,) in participants:
                data = json.loads(progress_data or '{}')
                total_progress += data.get('progress_percentage', 0)
                milestones_completed += len(data.get('milestones_completed', []))
            
            avg_progress = total_progress / total_participants if total_participants > 0 else 0
            
            # Calculate days remaining
            end_date = datetime.fromisoformat(action['end_date'])
            days_remaining = max(0, (end_date - datetime.now()).days)
            
            return {
                'action_id': action_id,
                'total_participants': total_participants,
                'avg_progress': round(avg_progress, 1),
                'milestones_completed': milestones_completed,
                'days_remaining': days_remaining,
                'target_goal': action['goal_amount'],
                'completion_rate': round(avg_progress, 1)
            }

    def _schedule_reminders(self, action_id: str, user_id: str):
        """Schedule automated reminders for user"""
        action = self.get_action_by_id(action_id)
        if not action:
            return
            
        now = datetime.now()
        timeline_days = action['timeline_days']
        
        # Schedule reminders at key intervals
        reminder_schedule = [
            (3, "check_in", "How's your progress going? Share an update with the group!"),
            (7, "milestone", "Week 1 milestone check - are you on track?"),
            (timeline_days // 2, "midpoint", "You're halfway through! Keep the momentum going."),
            (timeline_days - 3, "final_push", "Final push! Just 3 days left to reach your goal."),
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for days_offset, reminder_type, content in reminder_schedule:
                if days_offset < timeline_days:
                    scheduled_for = (now + timedelta(days=days_offset)).isoformat()
                    cursor.execute('''
                        INSERT INTO collective_action_reminders 
                        (action_id, user_id, reminder_type, content, scheduled_for)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (action_id, user_id, reminder_type, content, scheduled_for))
            
            conn.commit()

    def get_pending_reminders(self) -> List[Dict[str, Any]]:
        """Get reminders that need to be sent"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM collective_action_reminders 
                WHERE status = 'pending' AND scheduled_for <= CURRENT_TIMESTAMP
                ORDER BY scheduled_for ASC
            ''')
            
            reminders = []
            for row in cursor.fetchall():
                reminder = dict(zip([col[0] for col in cursor.description], row))
                reminders.append(reminder)
            
            return reminders

    def mark_reminder_sent(self, reminder_id: int):
        """Mark a reminder as sent"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE collective_action_reminders 
                SET status = 'sent', sent_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (reminder_id,))
            conn.commit()

    def post_message(self, action_id: str, user_id: str, message_type: str, content: str) -> bool:
        """Post a message to the action's chat/check-in thread"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO collective_action_messages 
                (action_id, user_id, message_type, content)
                VALUES (?, ?, ?, ?)
            ''', (action_id, user_id, message_type, content))
            conn.commit()
            return True

    def get_action_messages(self, action_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat messages for an action"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT cam.*, u.email as user_email
                FROM collective_action_messages cam
                LEFT JOIN users u ON cam.user_id = u.id
                WHERE cam.action_id = ?
                ORDER BY cam.created_at DESC
                LIMIT ?
            ''', (action_id, limit))
            
            messages = []
            for row in cursor.fetchall():
                message = dict(zip([col[0] for col in cursor.description], row))
                messages.append(message)
            
            return messages

    def get_user_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard data for user's collective actions"""
        user_actions = self.get_user_actions(user_id)
        
        dashboard_data = {
            'active_actions': len(user_actions),
            'actions': [],
            'total_progress': 0,
            'upcoming_deadlines': [],
            'recent_updates': []
        }
        
        for action in user_actions:
            progress_data = action.get('progress_data', {})
            progress_percentage = progress_data.get('progress_percentage', 0)
            dashboard_data['total_progress'] += progress_percentage
            
            # Calculate days until deadline
            end_date = datetime.fromisoformat(action['end_date'])
            days_remaining = (end_date - datetime.now()).days
            
            action_summary = {
                'id': action['id'],
                'title': action['title'],
                'progress': progress_percentage,
                'days_remaining': days_remaining,
                'individual_goal': action.get('individual_goal', action['goal_amount']),
                'milestones_completed': len(progress_data.get('milestones_completed', [])),
                'group_progress': self.get_group_progress(action['id'])
            }
            
            dashboard_data['actions'].append(action_summary)
            
            if days_remaining <= 7:
                dashboard_data['upcoming_deadlines'].append(action_summary)
        
        if dashboard_data['active_actions'] > 0:
            dashboard_data['avg_progress'] = dashboard_data['total_progress'] / dashboard_data['active_actions']
        else:
            dashboard_data['avg_progress'] = 0
            
        return dashboard_data