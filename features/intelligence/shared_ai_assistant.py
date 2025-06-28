"""
Shared AI Assistant - Ambient Intelligence for Root Members
Provides missed connections, daily micro-actions, and weekly collective insights
using non-intrusive analysis of user actions and goals.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
import os
from openai import OpenAI


@dataclass
class MissedConnection:
    """Represents a potential connection between two members"""
    user_a_id: int
    user_b_id: int
    connection_reason: str
    confidence_score: float
    suggested_intro: str
    common_interests: List[str]
    relevance_context: str


@dataclass
class MicroAction:
    """Represents a daily micro-action suggestion"""
    user_id: int
    action_type: str
    suggestion: str
    context: str
    goal_relevance: str
    priority_score: float
    estimated_time: str


@dataclass
class CollectiveInsight:
    """Represents a weekly collective insight"""
    insight_type: str
    title: str
    description: str
    data_points: List[Dict[str, Any]]
    trend_direction: str
    impact_level: str
    actionable_recommendation: str


class SharedAIAssistant:
    """Ambient AI assistant providing network intelligence and micro-actions"""
    
    def __init__(self, db_path: str = 'db.sqlite3'):
        self.db_path = db_path
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self._init_database()

    def _init_database(self):
        """Initialize AI assistant database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Missed connections tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS missed_connections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_a_id INTEGER NOT NULL,
                    user_b_id INTEGER NOT NULL,
                    connection_reason TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    suggested_intro TEXT NOT NULL,
                    common_interests TEXT,
                    relevance_context TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    acted_on_at TEXT,
                    UNIQUE(user_a_id, user_b_id, connection_reason)
                )
            ''')
            
            # Daily micro-actions
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS micro_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    action_type TEXT NOT NULL,
                    suggestion TEXT NOT NULL,
                    context TEXT,
                    goal_relevance TEXT,
                    priority_score REAL NOT NULL,
                    estimated_time TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    completed_at TEXT
                )
            ''')
            
            # Weekly collective insights
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS collective_insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    week_start_date TEXT NOT NULL,
                    insight_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    data_points TEXT,
                    trend_direction TEXT,
                    impact_level TEXT,
                    actionable_recommendation TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Assistant interaction tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assistant_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    interaction_type TEXT NOT NULL,
                    content TEXT,
                    response TEXT,
                    satisfaction_rating INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()

    def surface_missed_connections(self, user_id: int) -> List[MissedConnection]:
        """Identify potential connections between members based on goals and activities"""
        connections = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get user's goals and interests
                cursor.execute('''
                    SELECT id, title, description FROM goals 
                    WHERE user_id = ? AND status != 'completed'
                ''', (user_id,))
                user_goals = cursor.fetchall()
                
                if not user_goals:
                    return connections
                
                # Get other users with similar goals or complementary needs
                cursor.execute('''
                    SELECT DISTINCT g.user_id, g.title, g.description, c.name, c.company, c.title as job_title
                    FROM goals g
                    LEFT JOIN contacts c ON c.user_id = g.user_id
                    WHERE g.user_id != ? AND g.status != 'completed'
                    ORDER BY g.created_at DESC
                    LIMIT 20
                ''', (user_id,))
                other_users = cursor.fetchall()
                
                # Analyze potential connections using AI
                for other_user_id, other_goal_title, other_goal_desc, name, company, job_title in other_users:
                    if other_user_id == user_id:
                        continue
                    
                    # Check if connection already suggested recently
                    cursor.execute('''
                        SELECT id FROM missed_connections 
                        WHERE ((user_a_id = ? AND user_b_id = ?) OR (user_a_id = ? AND user_b_id = ?))
                        AND created_at > date('now', '-7 days')
                    ''', (user_id, other_user_id, other_user_id, user_id))
                    
                    if cursor.fetchone():
                        continue
                    
                    connection = self._analyze_connection_potential(
                        user_goals, other_user_id, other_goal_title, other_goal_desc, 
                        name, company, job_title
                    )
                    
                    if connection and connection.confidence_score > 0.7:
                        connections.append(connection)
                        
                        # Store the connection suggestion
                        cursor.execute('''
                            INSERT OR IGNORE INTO missed_connections 
                            (user_a_id, user_b_id, connection_reason, confidence_score, 
                             suggested_intro, common_interests, relevance_context)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (user_id, other_user_id, connection.connection_reason,
                              connection.confidence_score, connection.suggested_intro,
                              json.dumps(connection.common_interests), connection.relevance_context))
                
                conn.commit()
                
        except Exception as e:
            logging.error(f"Error surfacing missed connections: {e}")
        
        return sorted(connections, key=lambda x: x.confidence_score, reverse=True)[:3]

    def _analyze_connection_potential(self, user_goals: List[Tuple], other_user_id: int, 
                                    other_goal_title: str, other_goal_desc: str,
                                    name: str, company: str, job_title: str) -> Optional[MissedConnection]:
        """Use AI to analyze connection potential between two members"""
        try:
            user_goals_text = "\n".join([f"- {title}: {desc}" for _, title, desc in user_goals])
            other_context = f"Goal: {other_goal_title}\nDescription: {other_goal_desc}\nRole: {job_title} at {company}"
            
            prompt = f"""Analyze potential connection between two Root Members:

MEMBER A GOALS:
{user_goals_text}

MEMBER B CONTEXT:
{other_context}

Determine if there's valuable connection potential. Look for:
- Complementary expertise (one needs what the other offers)
- Similar industries or challenges
- Potential collaboration opportunities
- Mutual benefit scenarios

Respond with JSON:
{{
    "has_potential": boolean,
    "confidence_score": float (0-1),
    "connection_reason": "brief reason",
    "suggested_intro": "natural introduction message",
    "common_interests": ["list", "of", "shared", "interests"],
    "relevance_context": "why this connection matters now"
}}

Only suggest high-value connections that could lead to meaningful collaboration."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            if result.get("has_potential", False):
                return MissedConnection(
                    user_a_id=0,  # Will be set by caller
                    user_b_id=other_user_id,
                    connection_reason=result.get("connection_reason", ""),
                    confidence_score=result.get("confidence_score", 0.0),
                    suggested_intro=result.get("suggested_intro", ""),
                    common_interests=result.get("common_interests", []),
                    relevance_context=result.get("relevance_context", "")
                )
                
        except Exception as e:
            logging.error(f"Error analyzing connection potential: {e}")
        
        return None

    def generate_daily_micro_actions(self, user_id: int) -> List[MicroAction]:
        """Generate personalized daily micro-actions based on goals and recent activity"""
        actions = []
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get user's active goals
                cursor.execute('''
                    SELECT id, title, description, target_date FROM goals 
                    WHERE user_id = ? AND status != 'completed'
                    ORDER BY created_at DESC
                ''', (user_id,))
                goals = cursor.fetchall()
                
                # Get recent contacts and interactions
                cursor.execute('''
                    SELECT c.id, c.name, c.company, c.title, c.warmth, c.relationship_type,
                           MAX(ci.created_at) as last_interaction
                    FROM contacts c
                    LEFT JOIN contact_interactions ci ON c.id = ci.contact_id
                    WHERE c.user_id = ?
                    GROUP BY c.id
                    ORDER BY last_interaction DESC NULLS LAST
                    LIMIT 15
                ''', (user_id,))
                contacts = cursor.fetchall()
                
                # Get user's recent activity patterns
                cursor.execute('''
                    SELECT interaction_type, COUNT(*) as count
                    FROM contact_interactions ci
                    JOIN contacts c ON ci.contact_id = c.id
                    WHERE c.user_id = ? AND ci.created_at > date('now', '-7 days')
                    GROUP BY interaction_type
                ''', (user_id,))
                recent_activity = cursor.fetchall()
                
                # Generate AI-powered micro-actions
                for goal_id, goal_title, goal_desc, target_date in goals:
                    goal_actions = self._generate_goal_specific_actions(
                        goal_id, goal_title, goal_desc, target_date, contacts, recent_activity
                    )
                    actions.extend(goal_actions)
                
                # Store micro-actions
                for action in actions:
                    cursor.execute('''
                        INSERT INTO micro_actions 
                        (user_id, action_type, suggestion, context, goal_relevance, 
                         priority_score, estimated_time)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (user_id, action.action_type, action.suggestion, action.context,
                          action.goal_relevance, action.priority_score, action.estimated_time))
                
                conn.commit()
                
        except Exception as e:
            logging.error(f"Error generating micro-actions: {e}")
        
        return sorted(actions, key=lambda x: x.priority_score, reverse=True)[:3]

    def _generate_goal_specific_actions(self, goal_id: int, goal_title: str, goal_desc: str,
                                      target_date: str, contacts: List[Tuple], 
                                      recent_activity: List[Tuple]) -> List[MicroAction]:
        """Generate micro-actions specific to a goal using AI analysis"""
        try:
            contacts_context = "\n".join([
                f"- {name} ({title} at {company}) - {warmth} warmth, {rel_type}, last contact: {last_int or 'never'}"
                for _, name, company, title, warmth, rel_type, last_int in contacts[:10]
            ])
            
            activity_context = "\n".join([
                f"- {interaction_type}: {count} times this week"
                for interaction_type, count in recent_activity
            ])
            
            prompt = f"""Generate 1-2 specific daily micro-actions for this goal:

GOAL: {goal_title}
DESCRIPTION: {goal_desc}
TARGET DATE: {target_date}

AVAILABLE CONTACTS:
{contacts_context}

RECENT ACTIVITY:
{activity_context}

Generate actionable, specific micro-actions (5-15 minutes each) that:
- Move this goal forward today
- Leverage existing contacts when relevant
- Are realistic and non-overwhelming
- Focus on relationship building or information gathering

Respond with JSON array:
[{{
    "action_type": "outreach|research|follow_up|planning",
    "suggestion": "specific action to take",
    "context": "why this action matters",
    "goal_relevance": "how this advances the goal",
    "priority_score": float (0-1),
    "estimated_time": "5-15 minutes"
}}]"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.4
            )
            
            # Parse the response - it should contain an array
            result = json.loads(response.choices[0].message.content)
            actions_data = result.get("actions", [])
            
            # If the response is directly an array, use it
            if isinstance(result, list):
                actions_data = result
            
            actions = []
            for action_data in actions_data:
                action = MicroAction(
                    user_id=0,  # Will be set by caller
                    action_type=action_data.get("action_type", "planning"),
                    suggestion=action_data.get("suggestion", ""),
                    context=action_data.get("context", ""),
                    goal_relevance=action_data.get("goal_relevance", ""),
                    priority_score=action_data.get("priority_score", 0.5),
                    estimated_time=action_data.get("estimated_time", "10 minutes")
                )
                actions.append(action)
            
            return actions
            
        except Exception as e:
            logging.error(f"Error generating goal-specific actions: {e}")
            return []

    def generate_weekly_collective_insights(self) -> List[CollectiveInsight]:
        """Generate weekly insights based on aggregated community data"""
        insights = []
        
        try:
            week_start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if insights already generated for this week
                cursor.execute('''
                    SELECT id FROM collective_insights 
                    WHERE week_start_date = ?
                ''', (week_start,))
                
                if cursor.fetchone():
                    # Return existing insights
                    cursor.execute('''
                        SELECT insight_type, title, description, data_points, 
                               trend_direction, impact_level, actionable_recommendation
                        FROM collective_insights 
                        WHERE week_start_date = ?
                        ORDER BY created_at DESC
                    ''', (week_start,))
                    
                    for row in cursor.fetchall():
                        insights.append(CollectiveInsight(
                            insight_type=row[0],
                            title=row[1],
                            description=row[2],
                            data_points=json.loads(row[3]) if row[3] else [],
                            trend_direction=row[4],
                            impact_level=row[5],
                            actionable_recommendation=row[6]
                        ))
                    
                    return insights
                
                # Generate new insights
                funding_insight = self._generate_funding_trends_insight(cursor, week_start)
                if funding_insight:
                    insights.append(funding_insight)
                
                networking_insight = self._generate_networking_patterns_insight(cursor, week_start)
                if networking_insight:
                    insights.append(networking_insight)
                
                collaboration_insight = self._generate_collaboration_trends_insight(cursor, week_start)
                if collaboration_insight:
                    insights.append(collaboration_insight)
                
                # Store insights
                for insight in insights:
                    cursor.execute('''
                        INSERT INTO collective_insights 
                        (week_start_date, insight_type, title, description, data_points,
                         trend_direction, impact_level, actionable_recommendation)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (week_start, insight.insight_type, insight.title, insight.description,
                          json.dumps(insight.data_points), insight.trend_direction,
                          insight.impact_level, insight.actionable_recommendation))
                
                conn.commit()
                
        except Exception as e:
            logging.error(f"Error generating collective insights: {e}")
        
        return insights

    def _generate_funding_trends_insight(self, cursor, week_start: str) -> Optional[CollectiveInsight]:
        """Analyze funding-related trends in the community"""
        try:
            # Get funding-related goals and activities
            cursor.execute('''
                SELECT g.title, g.description, COUNT(ci.id) as activity_count
                FROM goals g
                LEFT JOIN contacts c ON c.user_id = g.user_id
                LEFT JOIN contact_interactions ci ON ci.contact_id = c.id
                WHERE (g.title LIKE '%fund%' OR g.title LIKE '%raise%' OR g.title LIKE '%investor%'
                       OR g.description LIKE '%fund%' OR g.description LIKE '%raise%')
                AND g.created_at > date('now', '-7 days')
                GROUP BY g.id
                ORDER BY activity_count DESC
                LIMIT 10
            ''')
            funding_goals = cursor.fetchall()
            
            if not funding_goals:
                return None
            
            # Analyze with AI
            goals_context = "\n".join([
                f"- {title}: {desc} ({activity_count} interactions)"
                for title, desc, activity_count in funding_goals
            ])
            
            prompt = f"""Analyze funding trends from Root Member activities:

FUNDING-RELATED GOALS AND ACTIVITY:
{goals_context}

Generate insights about:
- Common fundraising patterns or strategies
- Market trends reflected in member goals
- Networking patterns for fundraising
- Actionable recommendations

Respond with JSON:
{{
    "title": "compelling insight title",
    "description": "detailed analysis",
    "trend_direction": "increasing|decreasing|stable",
    "impact_level": "high|medium|low",
    "actionable_recommendation": "specific advice for members",
    "data_points": [
        {{"metric": "name", "value": "insight", "trend": "+/-X%"}}
    ]
}}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return CollectiveInsight(
                insight_type="funding_trends",
                title=result.get("title", "Funding Activity Trends"),
                description=result.get("description", ""),
                data_points=result.get("data_points", []),
                trend_direction=result.get("trend_direction", "stable"),
                impact_level=result.get("impact_level", "medium"),
                actionable_recommendation=result.get("actionable_recommendation", "")
            )
            
        except Exception as e:
            logging.error(f"Error generating funding trends insight: {e}")
            return None

    def _generate_networking_patterns_insight(self, cursor, week_start: str) -> Optional[CollectiveInsight]:
        """Analyze networking patterns across the community"""
        try:
            # Get networking activity data
            cursor.execute('''
                SELECT interaction_type, COUNT(*) as count,
                       COUNT(DISTINCT ci.contact_id) as unique_contacts
                FROM contact_interactions ci
                JOIN contacts c ON ci.contact_id = c.id
                WHERE ci.created_at > date('now', '-7 days')
                GROUP BY interaction_type
                ORDER BY count DESC
            ''')
            interaction_patterns = cursor.fetchall()
            
            cursor.execute('''
                SELECT c.warmth, COUNT(*) as count
                FROM contacts c
                JOIN contact_interactions ci ON c.id = ci.contact_id
                WHERE ci.created_at > date('now', '-7 days')
                GROUP BY c.warmth
            ''')
            warmth_patterns = cursor.fetchall()
            
            if not interaction_patterns:
                return None
            
            patterns_context = "\n".join([
                f"- {int_type}: {count} interactions with {unique_contacts} unique contacts"
                for int_type, count, unique_contacts in interaction_patterns
            ])
            
            warmth_context = "\n".join([
                f"- {warmth} contacts: {count} interactions"
                for warmth, count in warmth_patterns
            ])
            
            prompt = f"""Analyze networking patterns from Root Member activity:

INTERACTION PATTERNS:
{patterns_context}

RELATIONSHIP WARMTH PATTERNS:
{warmth_context}

Generate insights about:
- Most effective relationship behaviors
- Relationship building patterns
- Communication trends
- Strategic recommendations

Respond with JSON format for relationship insights."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return CollectiveInsight(
                insight_type="relationship_patterns",
                title=result.get("title", "Community Relationship Patterns"),
                description=result.get("description", ""),
                data_points=result.get("data_points", []),
                trend_direction=result.get("trend_direction", "stable"),
                impact_level=result.get("impact_level", "medium"),
                actionable_recommendation=result.get("actionable_recommendation", "")
            )
            
        except Exception as e:
            logging.error(f"Error generating relationship patterns insight: {e}")
            return None

    def _generate_collaboration_trends_insight(self, cursor, week_start: str) -> Optional[CollectiveInsight]:
        """Analyze collaboration trends from collective actions and shared goals"""
        try:
            # Get collective action participation
            cursor.execute('''
                SELECT ca.title, COUNT(cap.user_id) as participants,
                       AVG(JSON_EXTRACT(cap.progress_data, '$.progress_percentage')) as avg_progress
                FROM collective_actions ca
                JOIN collective_action_participants cap ON ca.id = cap.action_id
                WHERE cap.joined_at > date('now', '-7 days')
                GROUP BY ca.id
                ORDER BY participants DESC
            ''')
            collaboration_data = cursor.fetchall()
            
            if not collaboration_data:
                return None
            
            collab_context = "\n".join([
                f"- {title}: {participants} participants, {avg_progress:.1f}% avg progress"
                for title, participants, avg_progress in collaboration_data
            ])
            
            prompt = f"""Analyze collaboration trends from Root Member collective actions:

COLLECTIVE ACTION PARTICIPATION:
{collab_context}

Generate insights about:
- Most engaging collaboration types
- Group progress patterns
- Community momentum indicators
- Recommendations for future initiatives

Respond with JSON format for collaboration insights."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return CollectiveInsight(
                insight_type="collaboration_trends",
                title=result.get("title", "Community Collaboration Trends"),
                description=result.get("description", ""),
                data_points=result.get("data_points", []),
                trend_direction=result.get("trend_direction", "stable"),
                impact_level=result.get("impact_level", "medium"),
                actionable_recommendation=result.get("actionable_recommendation", "")
            )
            
        except Exception as e:
            logging.error(f"Error generating collaboration trends insight: {e}")
            return None

    def mark_connection_acted_on(self, connection_id: int, user_id: int) -> bool:
        """Mark a missed connection as acted upon"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE missed_connections 
                    SET status = 'acted_on', acted_on_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND user_a_id = ?
                ''', (connection_id, user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error marking connection as acted on: {e}")
            return False

    def mark_micro_action_completed(self, action_id: int, user_id: int) -> bool:
        """Mark a micro-action as completed"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE micro_actions 
                    SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND user_id = ?
                ''', (action_id, user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logging.error(f"Error marking micro-action as completed: {e}")
            return False

    def get_user_assistant_summary(self, user_id: int) -> Dict[str, Any]:
        """Get personalized AI assistant summary for user dashboard"""
        try:
            connections = self.surface_missed_connections(user_id)
            actions = self.generate_daily_micro_actions(user_id)
            insights = self.generate_weekly_collective_insights()
            
            return {
                'missed_connections': [
                    {
                        'id': conn.user_b_id,
                        'reason': conn.connection_reason,
                        'suggestion': conn.suggested_intro,
                        'confidence': conn.confidence_score
                    } for conn in connections
                ],
                'daily_actions': [
                    {
                        'type': action.action_type,
                        'suggestion': action.suggestion,
                        'context': action.context,
                        'time': action.estimated_time,
                        'priority': action.priority_score
                    } for action in actions
                ],
                'weekly_insights': [
                    {
                        'type': insight.insight_type,
                        'title': insight.title,
                        'description': insight.description[:200] + "..." if len(insight.description) > 200 else insight.description,
                        'recommendation': insight.actionable_recommendation
                    } for insight in insights[:2]  # Show top 2 insights
                ]
            }
            
        except Exception as e:
            logging.error(f"Error getting user assistant summary: {e}")
            return {
                'missed_connections': [],
                'daily_actions': [],
                'weekly_insights': []
            }