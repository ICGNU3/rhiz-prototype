"""
Contact Intelligence Engine
AI-powered relationship signal analysis and insights generation
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import sys
sys.path.append('.')
from database_helpers import DatabaseHelper
from openai import OpenAI

logger = logging.getLogger(__name__)

class ContactIntelligence:
    """AI-powered contact intelligence and relationship signal analysis"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
    def analyze_relationship_signals(self, user_id: str, contact_id: str) -> Dict[str, Any]:
        """Analyze relationship signals for a specific contact"""
        try:
            # Get contact data
            contact = DatabaseHelper.execute_query(
                'SELECT * FROM contacts WHERE id = %s AND user_id = %s',
                (contact_id, user_id),
                fetch_one=True
            )
            
            if not contact:
                return {'error': 'Contact not found'}
            
            # Get interaction history
            interactions = DatabaseHelper.execute_query(
                'SELECT * FROM contact_interactions WHERE contact_id = %s ORDER BY interaction_date DESC LIMIT 10',
                (contact_id,),
                fetch_all=True
            ) or []
            
            # Calculate relationship signals
            signals = self._calculate_relationship_signals(contact, interactions)
            
            # Generate AI insights
            ai_insights = self._generate_ai_insights(contact, interactions, signals)
            
            return {
                'contact_id': contact_id,
                'signals': signals,
                'ai_insights': ai_insights,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing relationship signals: {e}")
            return {'error': 'Failed to analyze relationship signals'}
    
    def _calculate_relationship_signals(self, contact: Dict, interactions: List[Dict]) -> Dict[str, Any]:
        """Calculate quantitative relationship signals"""
        now = datetime.now()
        
        # Recency analysis
        last_interaction = None
        if interactions:
            last_interaction_str = interactions[0].get('interaction_date')
            if last_interaction_str:
                try:
                    last_interaction = datetime.fromisoformat(last_interaction_str.replace('Z', '+00:00'))
                except:
                    last_interaction = None
        
        days_since_last_contact = None
        if last_interaction:
            days_since_last_contact = (now - last_interaction).days
        
        # Frequency analysis
        interaction_frequency = len(interactions) / max(1, (now - datetime.fromisoformat(contact.get('created_at', now.isoformat()))).days / 30)
        
        # Response time analysis
        avg_response_time = None
        if interactions:
            response_times = [i.get('response_time_hours', 24) for i in interactions if i.get('response_time_hours')]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
        
        # Engagement depth
        interaction_types = [i.get('interaction_type') for i in interactions]
        deep_interactions = len([t for t in interaction_types if t in ['meeting', 'call', 'video_call']])
        engagement_depth = deep_interactions / max(1, len(interactions))
        
        # Trust indicators
        trust_score = self._calculate_trust_score(contact, interactions)
        
        return {
            'recency': {
                'days_since_last_contact': days_since_last_contact,
                'last_interaction_date': last_interaction.isoformat() if last_interaction else None
            },
            'frequency': {
                'interactions_per_month': round(interaction_frequency, 2),
                'total_interactions': len(interactions)
            },
            'responsiveness': {
                'avg_response_time_hours': round(avg_response_time, 1) if avg_response_time else None
            },
            'engagement': {
                'depth_score': round(engagement_depth, 2),
                'deep_interactions': deep_interactions
            },
            'trust': {
                'trust_score': trust_score,
                'warmth_status': contact.get('warmth_status', 'unknown')
            }
        }
    
    def _calculate_trust_score(self, contact: Dict, interactions: List[Dict]) -> float:
        """Calculate basic trust score based on relationship factors"""
        base_score = 0.5
        
        # Warmth status influence
        warmth_multipliers = {
            'cold': 0.3,
            'warm': 0.6,
            'active': 0.8,
            'contributor': 1.0
        }
        warmth_score = warmth_multipliers.get(contact.get('warmth_status'), 0.5)
        
        # Interaction consistency
        if len(interactions) >= 3:
            consistency_bonus = 0.2
        else:
            consistency_bonus = 0.0
        
        # Recent activity
        recent_bonus = 0.0
        if interactions:
            last_interaction_str = interactions[0].get('interaction_date')
            if last_interaction_str:
                try:
                    last_interaction = datetime.fromisoformat(last_interaction_str.replace('Z', '+00:00'))
                    days_ago = (datetime.now() - last_interaction).days
                    if days_ago <= 7:
                        recent_bonus = 0.3
                    elif days_ago <= 30:
                        recent_bonus = 0.1
                except:
                    pass
        
        trust_score = min(1.0, warmth_score + consistency_bonus + recent_bonus)
        return round(trust_score, 2)
    
    def _generate_ai_insights(self, contact: Dict, interactions: List[Dict], signals: Dict) -> Dict[str, Any]:
        """Generate AI-powered insights about the relationship"""
        try:
            if not self.openai_client:
                return {'insights': ['AI insights unavailable - OpenAI not configured']}
            
            # Prepare context for AI
            context = f"""
            Contact: {contact.get('name', 'Unknown')}
            Company: {contact.get('company', 'Unknown')}
            Title: {contact.get('title', 'Unknown')}
            Warmth Status: {contact.get('warmth_status', 'Unknown')}
            Recent Interactions: {len(interactions)}
            Trust Score: {signals.get('trust', {}).get('trust_score', 0)}
            Days Since Last Contact: {signals.get('recency', {}).get('days_since_last_contact', 'Unknown')}
            """
            
            # Generate insights using OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a relationship intelligence assistant. Analyze the contact data and provide 2-3 brief, actionable insights about strengthening this relationship. Focus on practical next steps and relationship opportunities."
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            insights_text = response.choices[0].message.content
            insights = [insight.strip() for insight in insights_text.split('\n') if insight.strip()]
            
            return {
                'insights': insights[:3],  # Limit to 3 insights
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {e}")
            return {
                'insights': ['Schedule a follow-up to strengthen the relationship'],
                'generated_at': datetime.now().isoformat()
            }
    
    def get_priority_contacts(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get priority contacts that need attention"""
        try:
            # Get contacts with interaction analysis
            contacts = DatabaseHelper.execute_query(
                '''
                SELECT c.*, 
                       COUNT(ci.id) as interaction_count,
                       MAX(ci.interaction_date) as last_interaction
                FROM contacts c
                LEFT JOIN contact_interactions ci ON c.id = ci.contact_id
                WHERE c.user_id = %s
                GROUP BY c.id
                ORDER BY 
                    CASE WHEN MAX(ci.interaction_date) IS NULL THEN 1 ELSE 0 END,
                    MAX(ci.interaction_date) ASC
                LIMIT %s
                ''',
                (user_id, limit),
                fetch_all=True
            ) or []
            
            priority_contacts = []
            for contact in contacts:
                # Calculate priority score
                priority_score = self._calculate_priority_score(contact)
                
                priority_contacts.append({
                    'contact': dict(contact),
                    'priority_score': priority_score,
                    'reason': self._get_priority_reason(contact)
                })
            
            return sorted(priority_contacts, key=lambda x: x['priority_score'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting priority contacts: {e}")
            return []
    
    def _calculate_priority_score(self, contact: Dict) -> float:
        """Calculate priority score for contact attention"""
        score = 0.0
        
        # Base score by warmth status
        warmth_scores = {
            'contributor': 0.9,
            'active': 0.7,
            'warm': 0.5,
            'cold': 0.3
        }
        score += warmth_scores.get(contact.get('warmth_status'), 0.3)
        
        # Penalty for no interactions
        if contact.get('interaction_count', 0) == 0:
            score += 0.5  # New contacts get attention
        
        # Penalty for old last interaction
        if contact.get('last_interaction'):
            try:
                last_interaction = datetime.fromisoformat(contact['last_interaction'].replace('Z', '+00:00'))
                days_ago = (datetime.now() - last_interaction).days
                if days_ago > 30:
                    score += 0.4
                elif days_ago > 14:
                    score += 0.2
            except:
                pass
        
        return min(1.0, score)
    
    def _get_priority_reason(self, contact: Dict) -> str:
        """Get human-readable reason for contact priority"""
        if contact.get('interaction_count', 0) == 0:
            return "New contact - reach out to establish connection"
        
        if contact.get('last_interaction'):
            try:
                last_interaction = datetime.fromisoformat(contact['last_interaction'].replace('Z', '+00:00'))
                days_ago = (datetime.now() - last_interaction).days
                if days_ago > 30:
                    return f"No contact for {days_ago} days - relationship may be cooling"
                elif days_ago > 14:
                    return f"Overdue for follow-up ({days_ago} days ago)"
                else:
                    return "Active relationship - continue nurturing"
            except:
                pass
        
        return "Strengthen relationship with regular touchpoints"
    
    def process_natural_language_query(self, user_id: str, query: str) -> Dict[str, Any]:
        """Process natural language queries about contacts and relationships"""
        try:
            if not self.openai_client:
                return {'error': 'AI chat unavailable - OpenAI not configured'}
            
            # Get user's contacts and goals for context
            contacts = DatabaseHelper.execute_query(
                'SELECT name, company, title, warmth_status FROM contacts WHERE user_id = %s LIMIT 10',
                (user_id,),
                fetch_all=True
            ) or []
            
            goals = DatabaseHelper.execute_query(
                'SELECT title, description FROM goals WHERE user_id = %s LIMIT 5',
                (user_id,),
                fetch_all=True
            ) or []
            
            # Prepare context
            context = f"""
            User's Recent Contacts: {[dict(c) for c in contacts]}
            User's Goals: {[dict(g) for g in goals]}
            Query: {query}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a relationship intelligence assistant. Answer questions about the user's network, contacts, and relationship building strategies. Provide specific, actionable advice based on their contacts and goals."
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return {
                'response': response.choices[0].message.content,
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing natural language query: {e}")
            return {
                'response': "I'm here to help with relationship insights. Try asking about your contacts, goals, or networking strategies.",
                'query': query,
                'timestamp': datetime.now().isoformat()
            }