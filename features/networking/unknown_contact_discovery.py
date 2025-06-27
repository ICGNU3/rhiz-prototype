"""
Unknown Contact Discovery Engine
Proactive system to identify and suggest valuable unknown contacts based on goals and network analysis
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from openai_utils import OpenAIUtils
import json

class UnknownContactDiscovery:
    """Engine for discovering and suggesting unknown contacts that could be valuable"""
    
    def __init__(self, db_path: str = 'db.sqlite3'):
        self.db_path = db_path
        self.openai = OpenAIUtils()
        self.logger = logging.getLogger(__name__)
        self._init_discovery_tables()
        
    def _init_discovery_tables(self):
        """Initialize tables for unknown contact discovery"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS unknown_contact_suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    suggested_name TEXT,
                    suggested_title TEXT,
                    suggested_company TEXT,
                    suggested_industry TEXT,
                    reasoning TEXT,
                    relevance_score REAL,
                    goal_alignment TEXT,
                    discovery_method TEXT,
                    status TEXT DEFAULT 'suggested',
                    date_suggested TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    date_actioned TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS contact_discovery_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT,
                    success_rate REAL DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS network_expansion_opportunities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    opportunity_type TEXT NOT NULL,
                    description TEXT,
                    potential_contacts TEXT,
                    priority_score REAL,
                    action_suggested TEXT,
                    date_identified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
    
    def discover_unknown_contacts_for_goal(self, user_id: int, goal_id: int) -> List[Dict[str, Any]]:
        """Discover unknown contacts that could help with a specific goal"""
        
        # Get goal details
        goal = self._get_goal_details(goal_id)
        if not goal:
            return []
        
        # Get user's current network for gap analysis
        current_contacts = self._get_user_contacts(user_id)
        
        # Analyze network gaps using AI
        suggestions = self._ai_generate_contact_suggestions(goal, current_contacts)
        
        # Store suggestions in database
        stored_suggestions = []
        for suggestion in suggestions:
            suggestion_id = self._store_contact_suggestion(user_id, suggestion, goal_id)
            suggestion['id'] = suggestion_id
            stored_suggestions.append(suggestion)
        
        return stored_suggestions
    
    def _ai_generate_contact_suggestions(self, goal: Dict, current_contacts: List[Dict]) -> List[Dict[str, Any]]:
        """Use AI to generate suggestions for unknown contacts"""
        
        # Build context about current network
        network_context = self._build_network_context(current_contacts)
        
        prompt = f"""
        Analyze this professional goal and current network to suggest 3-5 specific types of unknown contacts that would be most valuable to connect with.

        GOAL: {goal['title']} - {goal['description']}

        CURRENT NETWORK ANALYSIS:
        {network_context}

        For each suggested contact type, provide:
        1. Specific title/role (be precise, not generic)
        2. Ideal company type or industry
        3. Why this contact would be valuable for the goal
        4. Suggested approach method
        5. Relevance score (0.0-1.0)

        Focus on identifying specific gaps in the network that prevent goal achievement.
        Suggest contacts that would provide unique value not available in current network.

        Respond in JSON format:
        {{
            "suggestions": [
                {{
                    "suggested_title": "specific title",
                    "suggested_company_type": "type of company",
                    "suggested_industry": "industry",
                    "reasoning": "specific reason why valuable",
                    "approach_method": "how to find/connect",
                    "relevance_score": 0.0-1.0,
                    "goal_alignment": "how this helps the goal"
                }}
            ]
        }}
        """
        
        try:
            response = self.openai.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('suggestions', [])
            
        except Exception as e:
            self.logger.error(f"AI contact suggestion failed: {e}")
            return []
    
    def _build_network_context(self, contacts: List[Dict]) -> str:
        """Build a summary of the current network for AI analysis"""
        
        if not contacts:
            return "No existing contacts in network."
        
        # Analyze current network composition
        industries = {}
        titles = {}
        companies = {}
        
        for contact in contacts:
            industry = contact.get('industry', 'Unknown')
            title = contact.get('title', 'Unknown')
            company = contact.get('company', 'Unknown')
            
            industries[industry] = industries.get(industry, 0) + 1
            titles[title] = titles.get(title, 0) + 1
            companies[company] = companies.get(company, 0) + 1
        
        context_parts = [
            f"Total contacts: {len(contacts)}",
            f"Top industries: {', '.join([f'{k} ({v})' for k, v in sorted(industries.items(), key=lambda x: x[1], reverse=True)[:5]])}",
            f"Common titles: {', '.join([f'{k} ({v})' for k, v in sorted(titles.items(), key=lambda x: x[1], reverse=True)[:5]])}",
            f"Company diversity: {len(companies)} different companies"
        ]
        
        return "\n".join(context_parts)
    
    def discover_network_expansion_opportunities(self, user_id: int) -> List[Dict[str, Any]]:
        """Identify broader network expansion opportunities"""
        
        user_goals = self._get_user_goals(user_id)
        current_contacts = self._get_user_contacts(user_id)
        
        opportunities = []
        
        # Analyze each goal for network gaps
        for goal in user_goals:
            goal_opportunities = self._identify_goal_network_gaps(goal, current_contacts)
            opportunities.extend(goal_opportunities)
        
        # Identify industry/vertical gaps
        industry_opportunities = self._identify_industry_gaps(current_contacts, user_goals)
        opportunities.extend(industry_opportunities)
        
        # Identify relationship strength gaps
        strength_opportunities = self._identify_relationship_strength_gaps(current_contacts)
        opportunities.extend(strength_opportunities)
        
        # Store opportunities
        for opp in opportunities:
            self._store_expansion_opportunity(user_id, opp)
        
        return opportunities
    
    def _identify_goal_network_gaps(self, goal: Dict, contacts: List[Dict]) -> List[Dict[str, Any]]:
        """Identify network gaps for a specific goal"""
        
        # Use AI to analyze goal and suggest network composition
        prompt = f"""
        Analyze this professional goal and suggest what types of people should be in someone's network to achieve it successfully.

        GOAL: {goal['title']} - {goal.get('description', '')}

        Current network size: {len(contacts)}

        What specific types of professional relationships are missing or under-represented that would significantly help achieve this goal?

        Respond in JSON format:
        {{
            "network_gaps": [
                {{
                    "gap_type": "missing role/expertise",
                    "description": "why this gap matters",
                    "priority": 0.0-1.0,
                    "suggested_action": "how to address this gap"
                }}
            ]
        }}
        """
        
        try:
            response = self.openai.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            gaps = result.get('network_gaps', [])
            
            return [{
                'opportunity_type': 'goal_network_gap',
                'description': gap['description'],
                'priority_score': gap['priority'],
                'action_suggested': gap['suggested_action'],
                'goal_id': goal['id']
            } for gap in gaps]
            
        except Exception as e:
            self.logger.error(f"Goal network gap analysis failed: {e}")
            return []
    
    def _identify_industry_gaps(self, contacts: List[Dict], goals: List[Dict]) -> List[Dict[str, Any]]:
        """Identify industry/vertical gaps in network"""
        
        current_industries = set()
        for contact in contacts:
            industry = contact.get('industry')
            if industry:
                current_industries.add(industry.lower())
        
        # Common valuable industries for professional networks
        valuable_industries = {
            'technology', 'finance', 'healthcare', 'media', 'education',
            'government', 'nonprofit', 'consulting', 'legal', 'real estate'
        }
        
        missing_industries = valuable_industries - current_industries
        
        opportunities = []
        for industry in missing_industries:
            opportunities.append({
                'opportunity_type': 'industry_gap',
                'description': f'No contacts in {industry} industry',
                'priority_score': 0.6,
                'action_suggested': f'Seek connections in {industry} through events or mutual contacts'
            })
        
        return opportunities
    
    def _identify_relationship_strength_gaps(self, contacts: List[Dict]) -> List[Dict[str, Any]]:
        """Identify gaps in relationship strength distribution"""
        
        warmth_distribution = {}
        for contact in contacts:
            warmth = contact.get('warmth', 'cold')
            warmth_distribution[warmth] = warmth_distribution.get(warmth, 0) + 1
        
        total_contacts = len(contacts)
        if total_contacts == 0:
            return []
        
        opportunities = []
        
        # Check for lack of warm relationships
        warm_contacts = warmth_distribution.get('warm', 0)
        if warm_contacts / total_contacts < 0.3:
            opportunities.append({
                'opportunity_type': 'relationship_strength_gap',
                'description': 'Low percentage of warm relationships in network',
                'priority_score': 0.8,
                'action_suggested': 'Focus on deepening existing relationships before adding new contacts'
            })
        
        # Check for lack of hot relationships
        hot_contacts = warmth_distribution.get('hot', 0)
        if hot_contacts / total_contacts < 0.1:
            opportunities.append({
                'opportunity_type': 'relationship_strength_gap',
                'description': 'Few close/hot relationships for referrals and support',
                'priority_score': 0.7,
                'action_suggested': 'Identify 3-5 existing contacts to develop into closer relationships'
            })
        
        return opportunities
    
    def get_discovery_insights(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive discovery insights for a user"""
        
        with sqlite3.connect(self.db_path) as conn:
            # Recent suggestions
            recent_suggestions = conn.execute('''
                SELECT suggested_name, suggested_title, suggested_company, reasoning, relevance_score
                FROM unknown_contact_suggestions
                WHERE user_id = ? AND date_suggested >= datetime('now', '-30 days')
                ORDER BY relevance_score DESC
                LIMIT 5
            ''', (user_id,)).fetchall()
            
            # Expansion opportunities
            opportunities = conn.execute('''
                SELECT opportunity_type, description, priority_score, action_suggested
                FROM network_expansion_opportunities
                WHERE user_id = ? 
                ORDER BY priority_score DESC
                LIMIT 10
            ''', (user_id,)).fetchall()
            
            # Discovery success rate
            success_stats = conn.execute('''
                SELECT 
                    COUNT(*) as total_suggestions,
                    COUNT(CASE WHEN status = 'connected' THEN 1 END) as successful_connections,
                    AVG(relevance_score) as avg_relevance
                FROM unknown_contact_suggestions
                WHERE user_id = ?
            ''', (user_id,)).fetchone()
        
        return {
            'recent_suggestions': [
                {
                    'name': row[0],
                    'title': row[1],
                    'company': row[2],
                    'reasoning': row[3],
                    'relevance_score': row[4]
                } for row in recent_suggestions
            ],
            'expansion_opportunities': [
                {
                    'type': row[0],
                    'description': row[1],
                    'priority': row[2],
                    'action': row[3]
                } for row in opportunities
            ],
            'success_metrics': {
                'total_suggestions': success_stats[0] if success_stats else 0,
                'successful_connections': success_stats[1] if success_stats else 0,
                'avg_relevance_score': success_stats[2] if success_stats else 0.0,
                'success_rate': (success_stats[1] / success_stats[0] * 100) if success_stats and success_stats[0] > 0 else 0
            }
        }
    
    def mark_suggestion_status(self, suggestion_id: int, status: str, notes: str = "") -> bool:
        """Mark a suggestion as connected, ignored, or in progress"""
        
        valid_statuses = ['suggested', 'in_progress', 'connected', 'ignored', 'not_relevant']
        if status not in valid_statuses:
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE unknown_contact_suggestions 
                SET status = ?, date_actioned = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, suggestion_id))
            
            conn.commit()
        
        return True
    
    def _store_contact_suggestion(self, user_id: int, suggestion: Dict, goal_id: int) -> int:
        """Store a contact suggestion in the database"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                INSERT INTO unknown_contact_suggestions 
                (user_id, suggested_name, suggested_title, suggested_company, 
                 suggested_industry, reasoning, relevance_score, goal_alignment, discovery_method)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                suggestion.get('suggested_name', ''),
                suggestion.get('suggested_title', ''),
                suggestion.get('suggested_company_type', ''),
                suggestion.get('suggested_industry', ''),
                suggestion.get('reasoning', ''),
                suggestion.get('relevance_score', 0.0),
                suggestion.get('goal_alignment', ''),
                'ai_goal_analysis'
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def _store_expansion_opportunity(self, user_id: int, opportunity: Dict) -> int:
        """Store a network expansion opportunity"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                INSERT INTO network_expansion_opportunities 
                (user_id, opportunity_type, description, priority_score, action_suggested)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user_id,
                opportunity['opportunity_type'],
                opportunity['description'],
                opportunity['priority_score'],
                opportunity['action_suggested']
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    def _get_goal_details(self, goal_id: int) -> Optional[Dict]:
        """Get goal details for analysis"""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute('''
                SELECT id, title, description FROM goals WHERE id = ?
            ''', (goal_id,)).fetchone()
            
            if row:
                return {'id': row[0], 'title': row[1], 'description': row[2]}
        return None
    
    def _get_user_contacts(self, user_id: int) -> List[Dict]:
        """Get user's current contacts for analysis"""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute('''
                SELECT id, name, title, company, industry, warmth
                FROM contacts WHERE user_id = ?
            ''', (user_id,)).fetchall()
            
            return [
                {
                    'id': row[0],
                    'name': row[1],
                    'title': row[2],
                    'company': row[3],
                    'industry': row[4],
                    'warmth': row[5]
                } for row in rows
            ]
    
    def _get_user_goals(self, user_id: int) -> List[Dict]:
        """Get user's goals for analysis"""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute('''
                SELECT id, title, description FROM goals WHERE user_id = ?
            ''', (user_id,)).fetchall()
            
            return [
                {'id': row[0], 'title': row[1], 'description': row[2]}
                for row in rows
            ]