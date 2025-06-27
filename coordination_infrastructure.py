"""
Coordination Infrastructure Engine
Multi-party goal coordination and collaborative project management for network architects
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
import json

@dataclass
class CoordinationProject:
    id: int
    title: str
    description: str
    project_type: str  # collaboration, joint_venture, event, initiative
    status: str  # planning, active, completed, paused
    coordinator_id: int
    participants: List[int]
    milestones: List[Dict]
    resources_needed: List[str]
    success_criteria: str
    target_completion: datetime
    date_created: datetime

@dataclass
class ProjectParticipant:
    contact_id: int
    role: str  # coordinator, contributor, advisor, connector
    commitment_level: str  # high, medium, low
    skills_contributed: List[str]
    availability: str
    join_date: datetime
    status: str  # active, invited, declined, inactive

class CoordinationInfrastructure:
    """Engine for coordinating multi-party projects and collaborative goals"""
    
    def __init__(self, db_path: str = 'db.sqlite3'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_coordination_tables()
        
    def _init_coordination_tables(self):
        """Initialize coordination infrastructure tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS coordination_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    project_type TEXT NOT NULL,
                    status TEXT DEFAULT 'planning',
                    coordinator_id INTEGER NOT NULL,
                    success_criteria TEXT,
                    target_completion DATE,
                    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (coordinator_id) REFERENCES users (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS project_participants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    contact_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    commitment_level TEXT DEFAULT 'medium',
                    skills_contributed TEXT,
                    availability TEXT,
                    status TEXT DEFAULT 'invited',
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES coordination_projects (id),
                    FOREIGN KEY (contact_id) REFERENCES contacts (id),
                    UNIQUE(project_id, contact_id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS project_milestones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    responsible_contact_id INTEGER,
                    target_date DATE,
                    completion_date DATE,
                    status TEXT DEFAULT 'pending',
                    order_sequence INTEGER DEFAULT 0,
                    FOREIGN KEY (project_id) REFERENCES coordination_projects (id),
                    FOREIGN KEY (responsible_contact_id) REFERENCES contacts (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS project_resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_description TEXT,
                    needed_by_date DATE,
                    provider_contact_id INTEGER,
                    status TEXT DEFAULT 'needed',
                    value_estimate TEXT,
                    FOREIGN KEY (project_id) REFERENCES coordination_projects (id),
                    FOREIGN KEY (provider_contact_id) REFERENCES contacts (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS project_updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    contact_id INTEGER,
                    update_type TEXT NOT NULL,
                    content TEXT,
                    visibility TEXT DEFAULT 'all_participants',
                    date_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES coordination_projects (id),
                    FOREIGN KEY (contact_id) REFERENCES contacts (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS coordination_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_name TEXT UNIQUE NOT NULL,
                    project_type TEXT NOT NULL,
                    description TEXT,
                    default_milestones TEXT,
                    default_resources TEXT,
                    success_criteria_template TEXT,
                    estimated_duration_days INTEGER,
                    recommended_team_size TEXT
                )
            ''')
            
            conn.commit()
            self._seed_coordination_templates()
    
    def _seed_coordination_templates(self):
        """Seed common coordination project templates"""
        templates = [
            {
                'template_name': 'Startup Fundraising Round',
                'project_type': 'collaboration',
                'description': 'Coordinate fundraising efforts with network support',
                'default_milestones': json.dumps([
                    {'title': 'Pitch Deck Finalization', 'days_offset': 7},
                    {'title': 'Investor Introduction Phase', 'days_offset': 14},
                    {'title': 'Due Diligence Preparation', 'days_offset': 30},
                    {'title': 'Term Sheet Negotiation', 'days_offset': 45},
                    {'title': 'Round Closing', 'days_offset': 60}
                ]),
                'default_resources': json.dumps([
                    'Legal counsel introductions',
                    'Investor warm introductions',
                    'Pitch deck review',
                    'Financial model validation',
                    'Reference customers'
                ]),
                'success_criteria_template': 'Successfully raise target amount with favorable terms',
                'estimated_duration_days': 90,
                'recommended_team_size': '3-5 key contributors'
            },
            {
                'template_name': 'Industry Event Organization',
                'project_type': 'event',
                'description': 'Coordinate industry event with multiple stakeholders',
                'default_milestones': json.dumps([
                    {'title': 'Venue Selection', 'days_offset': 7},
                    {'title': 'Speaker Recruitment', 'days_offset': 21},
                    {'title': 'Sponsorship Secured', 'days_offset': 35},
                    {'title': 'Registration Launch', 'days_offset': 42},
                    {'title': 'Event Execution', 'days_offset': 90}
                ]),
                'default_resources': json.dumps([
                    'Venue connections',
                    'Speaker network',
                    'Sponsor relationships',
                    'Marketing channels',
                    'Event production support'
                ]),
                'success_criteria_template': 'Successful event with target attendance and positive feedback',
                'estimated_duration_days': 120,
                'recommended_team_size': '4-8 organizers'
            },
            {
                'template_name': 'Strategic Partnership Development',
                'project_type': 'joint_venture',
                'description': 'Develop strategic partnership between organizations',
                'default_milestones': json.dumps([
                    {'title': 'Partnership Framework', 'days_offset': 14},
                    {'title': 'Stakeholder Alignment', 'days_offset': 28},
                    {'title': 'Legal Structure', 'days_offset': 42},
                    {'title': 'Pilot Program Launch', 'days_offset': 60},
                    {'title': 'Full Partnership Activation', 'days_offset': 90}
                ]),
                'default_resources': json.dumps([
                    'Business development contacts',
                    'Legal partnership expertise',
                    'Executive introductions',
                    'Market research',
                    'Integration support'
                ]),
                'success_criteria_template': 'Mutually beneficial partnership with clear value creation',
                'estimated_duration_days': 120,
                'recommended_team_size': '2-4 key stakeholders per side'
            }
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            for template in templates:
                conn.execute('''
                    INSERT OR IGNORE INTO coordination_templates 
                    (template_name, project_type, description, default_milestones, 
                     default_resources, success_criteria_template, estimated_duration_days, recommended_team_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    template['template_name'],
                    template['project_type'],
                    template['description'],
                    template['default_milestones'],
                    template['default_resources'],
                    template['success_criteria_template'],
                    template['estimated_duration_days'],
                    template['recommended_team_size']
                ))
            conn.commit()
    
    def create_coordination_project(self, coordinator_id: int, title: str, description: str,
                                  project_type: str, template_id: Optional[int] = None,
                                  target_completion: Optional[datetime] = None) -> int:
        """Create a new coordination project"""
        
        if target_completion is None:
            target_completion = datetime.now() + timedelta(days=90)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                INSERT INTO coordination_projects 
                (title, description, project_type, coordinator_id, target_completion)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, description, project_type, coordinator_id, target_completion))
            
            project_id = cursor.lastrowid
            
            # If using a template, create default milestones and resources
            if template_id:
                self._apply_project_template(project_id, template_id)
            
            conn.commit()
            
        self.logger.info(f"Created coordination project {project_id}: {title}")
        return project_id
    
    def _apply_project_template(self, project_id: int, template_id: int):
        """Apply a project template to create default milestones and resources"""
        
        with sqlite3.connect(self.db_path) as conn:
            template = conn.execute('''
                SELECT default_milestones, default_resources, success_criteria_template
                FROM coordination_templates WHERE id = ?
            ''', (template_id,)).fetchone()
            
            if not template:
                return
            
            milestones_data = json.loads(template[0])
            resources_data = json.loads(template[1])
            success_criteria = template[2]
            
            # Update project with success criteria
            conn.execute('''
                UPDATE coordination_projects SET success_criteria = ? WHERE id = ?
            ''', (success_criteria, project_id))
            
            # Create milestones
            for i, milestone in enumerate(milestones_data):
                target_date = datetime.now() + timedelta(days=milestone['days_offset'])
                conn.execute('''
                    INSERT INTO project_milestones 
                    (project_id, title, target_date, order_sequence)
                    VALUES (?, ?, ?, ?)
                ''', (project_id, milestone['title'], target_date, i))
            
            # Create resource needs
            for resource in resources_data:
                conn.execute('''
                    INSERT INTO project_resources 
                    (project_id, resource_type, resource_description)
                    VALUES (?, ?, ?)
                ''', (project_id, 'network_connection', resource))
            
            conn.commit()
    
    def add_project_participant(self, project_id: int, contact_id: int, role: str,
                              commitment_level: str = 'medium', skills: List[str] = None,
                              availability: str = '') -> bool:
        """Add a participant to a coordination project"""
        
        skills_json = json.dumps(skills or [])
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO project_participants 
                    (project_id, contact_id, role, commitment_level, skills_contributed, availability)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (project_id, contact_id, role, commitment_level, skills_json, availability))
                
                # Log the addition
                conn.execute('''
                    INSERT INTO project_updates 
                    (project_id, contact_id, update_type, content)
                    VALUES (?, ?, ?, ?)
                ''', (project_id, contact_id, 'participant_added', f"Joined as {role}"))
                
                conn.commit()
                
            return True
            
        except sqlite3.IntegrityError:
            self.logger.warning(f"Contact {contact_id} already participant in project {project_id}")
            return False
    
    def update_participant_status(self, project_id: int, contact_id: int, status: str) -> bool:
        """Update participant status (invited, active, declined, inactive)"""
        
        valid_statuses = ['invited', 'active', 'declined', 'inactive']
        if status not in valid_statuses:
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE project_participants 
                SET status = ? 
                WHERE project_id = ? AND contact_id = ?
            ''', (status, project_id, contact_id))
            
            # Log status change
            conn.execute('''
                INSERT INTO project_updates 
                (project_id, contact_id, update_type, content)
                VALUES (?, ?, ?, ?)
            ''', (project_id, contact_id, 'status_change', f"Status changed to {status}"))
            
            conn.commit()
        
        return True
    
    def complete_milestone(self, milestone_id: int, completing_contact_id: int, notes: str = '') -> bool:
        """Mark a milestone as completed"""
        
        with sqlite3.connect(self.db_path) as conn:
            # Get milestone and project info
            milestone_info = conn.execute('''
                SELECT pm.project_id, pm.title, cp.title as project_title
                FROM project_milestones pm
                JOIN coordination_projects cp ON pm.project_id = cp.id
                WHERE pm.id = ?
            ''', (milestone_id,)).fetchone()
            
            if not milestone_info:
                return False
            
            project_id, milestone_title, project_title = milestone_info
            
            # Update milestone
            conn.execute('''
                UPDATE project_milestones 
                SET status = 'completed', completion_date = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (milestone_id,))
            
            # Log completion
            content = f"Completed milestone: {milestone_title}"
            if notes:
                content += f" - {notes}"
            
            conn.execute('''
                INSERT INTO project_updates 
                (project_id, contact_id, update_type, content)
                VALUES (?, ?, ?, ?)
            ''', (project_id, completing_contact_id, 'milestone_completed', content))
            
            conn.commit()
        
        return True
    
    def get_project_dashboard(self, project_id: int) -> Dict[str, Any]:
        """Get comprehensive project dashboard data"""
        
        with sqlite3.connect(self.db_path) as conn:
            # Project info
            project = conn.execute('''
                SELECT id, title, description, project_type, status, coordinator_id,
                       success_criteria, target_completion, date_created
                FROM coordination_projects WHERE id = ?
            ''', (project_id,)).fetchone()
            
            if not project:
                return {}
            
            # Participants
            participants = conn.execute('''
                SELECT pp.contact_id, c.name, c.title, c.company, pp.role, 
                       pp.commitment_level, pp.skills_contributed, pp.status
                FROM project_participants pp
                JOIN contacts c ON pp.contact_id = c.id
                WHERE pp.project_id = ?
            ''', (project_id,)).fetchall()
            
            # Milestones
            milestones = conn.execute('''
                SELECT id, title, description, responsible_contact_id, target_date,
                       completion_date, status, order_sequence
                FROM project_milestones 
                WHERE project_id = ?
                ORDER BY order_sequence, target_date
            ''', (project_id,)).fetchall()
            
            # Resources
            resources = conn.execute('''
                SELECT id, resource_type, resource_description, needed_by_date,
                       provider_contact_id, status, value_estimate
                FROM project_resources 
                WHERE project_id = ?
            ''', (project_id,)).fetchall()
            
            # Recent updates
            updates = conn.execute('''
                SELECT pu.update_type, pu.content, pu.date_posted, c.name
                FROM project_updates pu
                LEFT JOIN contacts c ON pu.contact_id = c.id
                WHERE pu.project_id = ?
                ORDER BY pu.date_posted DESC
                LIMIT 10
            ''', (project_id,)).fetchall()
            
            # Progress calculation
            total_milestones = len(milestones)
            completed_milestones = len([m for m in milestones if m[6] == 'completed'])
            progress_percentage = (completed_milestones / total_milestones * 100) if total_milestones > 0 else 0
            
            return {
                'project': {
                    'id': project[0],
                    'title': project[1],
                    'description': project[2],
                    'type': project[3],
                    'status': project[4],
                    'coordinator_id': project[5],
                    'success_criteria': project[6],
                    'target_completion': project[7],
                    'date_created': project[8],
                    'progress_percentage': progress_percentage
                },
                'participants': [
                    {
                        'contact_id': p[0],
                        'name': p[1],
                        'title': p[2],
                        'company': p[3],
                        'role': p[4],
                        'commitment_level': p[5],
                        'skills': json.loads(p[6]) if p[6] else [],
                        'status': p[7]
                    } for p in participants
                ],
                'milestones': [
                    {
                        'id': m[0],
                        'title': m[1],
                        'description': m[2],
                        'responsible_contact_id': m[3],
                        'target_date': m[4],
                        'completion_date': m[5],
                        'status': m[6],
                        'order': m[7]
                    } for m in milestones
                ],
                'resources': [
                    {
                        'id': r[0],
                        'type': r[1],
                        'description': r[2],
                        'needed_by': r[3],
                        'provider_id': r[4],
                        'status': r[5],
                        'value_estimate': r[6]
                    } for r in resources
                ],
                'recent_updates': [
                    {
                        'type': u[0],
                        'content': u[1],
                        'date': u[2],
                        'author': u[3]
                    } for u in updates
                ]
            }
    
    def get_user_coordination_overview(self, user_id: int) -> Dict[str, Any]:
        """Get coordination overview for a user"""
        
        with sqlite3.connect(self.db_path) as conn:
            # Projects as coordinator
            coordinated_projects = conn.execute('''
                SELECT id, title, project_type, status, target_completion
                FROM coordination_projects 
                WHERE coordinator_id = ?
                ORDER BY date_created DESC
            ''', (user_id,)).fetchall()
            
            # Projects as participant (need to join through contacts)
            participating_projects = conn.execute('''
                SELECT DISTINCT cp.id, cp.title, cp.project_type, cp.status, pp.role
                FROM coordination_projects cp
                JOIN project_participants pp ON cp.id = pp.project_id
                JOIN contacts c ON pp.contact_id = c.id
                WHERE c.user_id = ? AND cp.coordinator_id != ?
                ORDER BY cp.date_created DESC
            ''', (user_id, user_id)).fetchall()
            
            # Upcoming milestones
            upcoming_milestones = conn.execute('''
                SELECT pm.id, pm.title, pm.target_date, cp.title as project_title
                FROM project_milestones pm
                JOIN coordination_projects cp ON pm.project_id = cp.id
                WHERE (cp.coordinator_id = ? OR pm.responsible_contact_id IN (
                    SELECT id FROM contacts WHERE user_id = ?
                )) AND pm.status = 'pending' AND pm.target_date >= date('now')
                ORDER BY pm.target_date
                LIMIT 5
            ''', (user_id, user_id)).fetchall()
            
            # Active coordination stats
            stats = conn.execute('''
                SELECT 
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_projects,
                    COUNT(CASE WHEN status = 'planning' THEN 1 END) as planning_projects,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_projects
                FROM coordination_projects 
                WHERE coordinator_id = ?
            ''', (user_id,)).fetchone()
        
        return {
            'coordinated_projects': [
                {
                    'id': p[0],
                    'title': p[1],
                    'type': p[2],
                    'status': p[3],
                    'target_completion': p[4]
                } for p in coordinated_projects
            ],
            'participating_projects': [
                {
                    'id': p[0],
                    'title': p[1],
                    'type': p[2],
                    'status': p[3],
                    'role': p[4]
                } for p in participating_projects
            ],
            'upcoming_milestones': [
                {
                    'id': m[0],
                    'title': m[1],
                    'target_date': m[2],
                    'project_title': m[3]
                } for m in upcoming_milestones
            ],
            'stats': {
                'active_projects': stats[0] if stats else 0,
                'planning_projects': stats[1] if stats else 0,
                'completed_projects': stats[2] if stats else 0
            }
        }
    
    def suggest_project_participants(self, project_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Suggest potential participants for a project based on skills and network"""
        
        # Get project details and current participants
        with sqlite3.connect(self.db_path) as conn:
            project = conn.execute('''
                SELECT title, description, project_type FROM coordination_projects WHERE id = ?
            ''', (project_id,)).fetchone()
            
            if not project:
                return []
            
            # Get current participants to exclude
            current_participants = conn.execute('''
                SELECT contact_id FROM project_participants WHERE project_id = ?
            ''', (project_id,)).fetchall()
            
            current_participant_ids = [p[0] for p in current_participants]
            
            # Get user's contacts with relevant skills/experience
            # This is a simplified version - in practice would use AI to match skills to project needs
            exclude_clause = ""
            params = [user_id]
            
            if current_participant_ids:
                exclude_clause = f"AND c.id NOT IN ({','.join(['?' for _ in current_participant_ids])})"
                params.extend(current_participant_ids)
            
            potential_participants = conn.execute(f'''
                SELECT c.id, c.name, c.title, c.company, c.notes, c.warmth
                FROM contacts c
                WHERE c.user_id = ? {exclude_clause}
                ORDER BY 
                    CASE c.warmth 
                        WHEN 'hot' THEN 3 
                        WHEN 'warm' THEN 2 
                        ELSE 1 
                    END DESC,
                    c.name
                LIMIT 10
            ''', params).fetchall()
            
            return [
                {
                    'contact_id': p[0],
                    'name': p[1],
                    'title': p[2],
                    'company': p[3],
                    'notes': p[4],
                    'warmth': p[5],
                    'suggested_role': self._suggest_role_for_contact(p[2], project[2])
                } for p in potential_participants
            ]
    
    def _suggest_role_for_contact(self, contact_title: str, project_type: str) -> str:
        """Suggest an appropriate role for a contact based on their title and project type"""
        
        title_lower = (contact_title or '').lower()
        
        # Role mapping based on titles and project types
        if any(word in title_lower for word in ['ceo', 'founder', 'president', 'director']):
            return 'advisor'
        elif any(word in title_lower for word in ['manager', 'lead', 'head']):
            return 'contributor'
        elif any(word in title_lower for word in ['consultant', 'expert', 'specialist']):
            return 'advisor'
        elif any(word in title_lower for word in ['coordinator', 'organizer']):
            return 'contributor'
        else:
            return 'contributor'
    
    def get_coordination_templates(self) -> List[Dict[str, Any]]:
        """Get available project templates"""
        
        with sqlite3.connect(self.db_path) as conn:
            templates = conn.execute('''
                SELECT id, template_name, project_type, description, 
                       estimated_duration_days, recommended_team_size
                FROM coordination_templates
                ORDER BY template_name
            ''').fetchall()
            
            return [
                {
                    'id': t[0],
                    'name': t[1],
                    'type': t[2],
                    'description': t[3],
                    'duration_days': t[4],
                    'team_size': t[5]
                } for t in templates
            ]