"""
Enhanced Trust Insights Engine
Advanced relationship intelligence with AI-powered trust scoring and recommendations
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

class EnhancedTrustInsights:
    """Advanced trust insights with AI-powered relationship intelligence"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
    def get_comprehensive_trust_insights(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive trust insights for user's network"""
        try:
            # Get all contacts with interaction data
            contacts = DatabaseHelper.execute_query(
                '''
                SELECT c.*, 
                       COUNT(ci.id) as interaction_count,
                       MAX(ci.interaction_date) as last_interaction,
                       AVG(CASE WHEN ci.sentiment_score IS NOT NULL THEN ci.sentiment_score ELSE 0.5 END) as avg_sentiment
                FROM contacts c
                LEFT JOIN contact_interactions ci ON c.id = ci.contact_id
                WHERE c.user_id = %s
                GROUP BY c.id
                ''',
                (user_id,),
                fetch_all=True
            ) or []
            
            # Calculate trust insights
            trust_analysis = self._analyze_network_trust(contacts)
            
            # Generate AI recommendations
            ai_recommendations = self._generate_trust_recommendations(contacts, trust_analysis)
            
            # Weekly digest of priority actions
            weekly_digest = self._generate_weekly_digest(contacts)
            
            return {
                'trust_analysis': trust_analysis,
                'ai_recommendations': ai_recommendations,
                'weekly_digest': weekly_digest,
                'total_contacts': len(contacts),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating trust insights: {e}")
            return {'error': 'Failed to generate trust insights'}
    
    def _analyze_network_trust(self, contacts: List[Dict]) -> Dict[str, Any]:
        """Analyze overall network trust patterns"""
        if not contacts:
            return {
                'trust_distribution': {},
                'network_health': 0.0,
                'relationship_trends': {}
            }
        
        # Trust tier distribution
        trust_tiers = {'rooted': 0, 'growing': 0, 'dormant': 0, 'frayed': 0}
        total_trust_score = 0
        
        # Relationship patterns
        active_relationships = 0
        stale_relationships = 0
        new_relationships = 0
        
        for contact in contacts:
            # Calculate trust tier
            trust_tier = self._calculate_trust_tier(contact)
            trust_tiers[trust_tier] += 1
            
            # Calculate trust score
            trust_score = self._calculate_advanced_trust_score(contact)
            total_trust_score += trust_score
            
            # Analyze relationship state
            interaction_count = contact.get('interaction_count', 0)
            last_interaction = contact.get('last_interaction')
            
            if interaction_count == 0:
                new_relationships += 1
            elif last_interaction:
                try:
                    last_date = datetime.fromisoformat(last_interaction.replace('Z', '+00:00'))
                    days_ago = (datetime.now() - last_date).days
                    if days_ago <= 30:
                        active_relationships += 1
                    else:
                        stale_relationships += 1
                except:
                    stale_relationships += 1
            else:
                stale_relationships += 1
        
        # Calculate network health score
        network_health = total_trust_score / len(contacts) if contacts else 0.0
        
        return {
            'trust_distribution': trust_tiers,
            'network_health': round(network_health, 2),
            'relationship_trends': {
                'active': active_relationships,
                'stale': stale_relationships,
                'new': new_relationships
            },
            'insights': self._generate_network_insights(trust_tiers, network_health, {
                'active': active_relationships,
                'stale': stale_relationships,
                'new': new_relationships
            })
        }
    
    def _calculate_trust_tier(self, contact: Dict) -> str:
        """Calculate trust tier: rooted, growing, dormant, frayed"""
        interaction_count = contact.get('interaction_count', 0)
        last_interaction = contact.get('last_interaction')
        warmth_status = contact.get('warmth_status', 'cold')
        avg_sentiment = contact.get('avg_sentiment', 0.5)
        
        # Base score calculation
        base_score = 0.0
        
        # Warmth status influence
        warmth_scores = {
            'contributor': 0.4,
            'active': 0.3,
            'warm': 0.2,
            'cold': 0.1
        }
        base_score += warmth_scores.get(warmth_status, 0.1)
        
        # Interaction frequency
        if interaction_count >= 5:
            base_score += 0.3
        elif interaction_count >= 2:
            base_score += 0.2
        elif interaction_count >= 1:
            base_score += 0.1
        
        # Recency bonus
        if last_interaction:
            try:
                last_date = datetime.fromisoformat(last_interaction.replace('Z', '+00:00'))
                days_ago = (datetime.now() - last_date).days
                if days_ago <= 7:
                    base_score += 0.2
                elif days_ago <= 30:
                    base_score += 0.1
                elif days_ago > 90:
                    base_score -= 0.1
            except:
                pass
        
        # Sentiment influence
        if avg_sentiment > 0.7:
            base_score += 0.1
        elif avg_sentiment < 0.3:
            base_score -= 0.1
        
        # Determine tier
        if base_score >= 0.7:
            return 'rooted'
        elif base_score >= 0.4:
            return 'growing'
        elif base_score >= 0.2:
            return 'dormant'
        else:
            return 'frayed'
    
    def _calculate_advanced_trust_score(self, contact: Dict) -> float:
        """Calculate advanced trust score (0-1)"""
        score = 0.5  # Base score
        
        # Warmth status
        warmth_multipliers = {
            'contributor': 1.0,
            'active': 0.8,
            'warm': 0.6,
            'cold': 0.4
        }
        warmth_score = warmth_multipliers.get(contact.get('warmth_status'), 0.4)
        score *= warmth_score
        
        # Interaction consistency
        interaction_count = contact.get('interaction_count', 0)
        if interaction_count >= 5:
            score += 0.3
        elif interaction_count >= 2:
            score += 0.2
        elif interaction_count >= 1:
            score += 0.1
        
        # Recency factor
        last_interaction = contact.get('last_interaction')
        if last_interaction:
            try:
                last_date = datetime.fromisoformat(last_interaction.replace('Z', '+00:00'))
                days_ago = (datetime.now() - last_date).days
                if days_ago <= 7:
                    score += 0.2
                elif days_ago <= 30:
                    score += 0.1
                elif days_ago > 90:
                    score -= 0.2
            except:
                pass
        
        # Sentiment quality
        avg_sentiment = contact.get('avg_sentiment', 0.5)
        sentiment_bonus = (avg_sentiment - 0.5) * 0.2
        score += sentiment_bonus
        
        return min(1.0, max(0.0, score))
    
    def _generate_network_insights(self, trust_tiers: Dict, network_health: float, trends: Dict) -> List[str]:
        """Generate insights about network health"""
        insights = []
        
        total_contacts = sum(trust_tiers.values())
        if total_contacts == 0:
            return ["Start building relationships by adding your first contacts"]
        
        # Network health insights
        if network_health >= 0.8:
            insights.append("Your network shows strong relationship health across contacts")
        elif network_health >= 0.6:
            insights.append("Good network foundation with room for deeper connections")
        elif network_health >= 0.4:
            insights.append("Network needs attention - focus on strengthening key relationships")
        else:
            insights.append("Network requires significant relationship building effort")
        
        # Trust tier insights
        rooted_percent = (trust_tiers['rooted'] / total_contacts) * 100
        if rooted_percent >= 30:
            insights.append(f"Strong core network with {rooted_percent:.0f}% deeply rooted relationships")
        elif rooted_percent >= 15:
            insights.append(f"Building solid foundation with {rooted_percent:.0f}% strong relationships")
        else:
            insights.append("Focus on deepening relationships to build stronger network core")
        
        # Activity insights
        if trends['stale'] > trends['active']:
            insights.append("Many relationships need reactivation - schedule follow-ups")
        if trends['new'] > 0:
            insights.append(f"{trends['new']} new connections ready for outreach")
        
        return insights
    
    def _generate_trust_recommendations(self, contacts: List[Dict], trust_analysis: Dict) -> List[Dict[str, Any]]:
        """Generate AI-powered trust recommendations"""
        recommendations = []
        
        # Find contacts needing attention
        stale_contacts = []
        new_contacts = []
        high_potential = []
        
        for contact in contacts:
            interaction_count = contact.get('interaction_count', 0)
            last_interaction = contact.get('last_interaction')
            warmth_status = contact.get('warmth_status', 'cold')
            
            if interaction_count == 0:
                new_contacts.append(contact)
            elif last_interaction:
                try:
                    last_date = datetime.fromisoformat(last_interaction.replace('Z', '+00:00'))
                    days_ago = (datetime.now() - last_date).days
                    if days_ago > 30:
                        stale_contacts.append(contact)
                except:
                    stale_contacts.append(contact)
            
            # High potential: warm/active but low interaction
            if warmth_status in ['warm', 'active'] and interaction_count < 3:
                high_potential.append(contact)
        
        # Generate recommendations
        if stale_contacts:
            recommendations.append({
                'type': 'reactivate',
                'priority': 'high',
                'title': 'Reactivate Stale Relationships',
                'description': f'Reach out to {len(stale_contacts)} contacts you haven\'t spoken with recently',
                'contacts': [c.get('name') for c in stale_contacts[:3]],
                'action': 'Schedule follow-up conversations'
            })
        
        if new_contacts:
            recommendations.append({
                'type': 'initiate',
                'priority': 'medium',
                'title': 'Connect with New Contacts',
                'description': f'Start conversations with {len(new_contacts)} new connections',
                'contacts': [c.get('name') for c in new_contacts[:3]],
                'action': 'Send introductory messages'
            })
        
        if high_potential:
            recommendations.append({
                'type': 'deepen',
                'priority': 'medium',
                'title': 'Deepen High-Potential Relationships',
                'description': f'Strengthen connections with {len(high_potential)} promising contacts',
                'contacts': [c.get('name') for c in high_potential[:3]],
                'action': 'Schedule deeper conversations'
            })
        
        return recommendations
    
    def _generate_weekly_digest(self, contacts: List[Dict]) -> Dict[str, Any]:
        """Generate weekly relationship digest"""
        priority_contacts = []
        
        for contact in contacts:
            trust_score = self._calculate_advanced_trust_score(contact)
            priority_score = self._calculate_priority_score(contact)
            
            if priority_score > 0.6:  # High priority threshold
                priority_contacts.append({
                    'name': contact.get('name'),
                    'company': contact.get('company'),
                    'trust_score': trust_score,
                    'priority_score': priority_score,
                    'reason': self._get_priority_reason(contact)
                })
        
        # Sort by priority score
        priority_contacts.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return {
            'top_priorities': priority_contacts[:3],
            'total_priorities': len(priority_contacts),
            'week_start': datetime.now().strftime('%Y-%m-%d'),
            'digest_summary': self._generate_digest_summary(priority_contacts)
        }
    
    def _calculate_priority_score(self, contact: Dict) -> float:
        """Calculate priority score for weekly attention"""
        score = 0.0
        
        # Warmth status priority
        warmth_scores = {
            'contributor': 0.9,
            'active': 0.7,
            'warm': 0.5,
            'cold': 0.3
        }
        score += warmth_scores.get(contact.get('warmth_status'), 0.3)
        
        # New contact bonus
        if contact.get('interaction_count', 0) == 0:
            score += 0.4
        
        # Stale relationship penalty/priority
        last_interaction = contact.get('last_interaction')
        if last_interaction:
            try:
                last_date = datetime.fromisoformat(last_interaction.replace('Z', '+00:00'))
                days_ago = (datetime.now() - last_date).days
                if days_ago > 30:
                    score += 0.5  # High priority for reactivation
                elif days_ago > 14:
                    score += 0.3
            except:
                pass
        
        return min(1.0, score)
    
    def _get_priority_reason(self, contact: Dict) -> str:
        """Get reason for priority attention"""
        interaction_count = contact.get('interaction_count', 0)
        last_interaction = contact.get('last_interaction')
        
        if interaction_count == 0:
            return "New contact - establish initial connection"
        
        if last_interaction:
            try:
                last_date = datetime.fromisoformat(last_interaction.replace('Z', '+00:00'))
                days_ago = (datetime.now() - last_date).days
                if days_ago > 60:
                    return f"Relationship cooling - {days_ago} days since last contact"
                elif days_ago > 30:
                    return f"Overdue follow-up - {days_ago} days ago"
                else:
                    return "Active relationship - continue nurturing"
            except:
                pass
        
        return "Strengthen relationship foundation"
    
    def _generate_digest_summary(self, priority_contacts: List[Dict]) -> str:
        """Generate summary for weekly digest"""
        if not priority_contacts:
            return "Your network is well-maintained. Consider adding new connections to expand your reach."
        
        high_priority = len([c for c in priority_contacts if c['priority_score'] > 0.8])
        
        if high_priority >= 3:
            return f"Busy week ahead: {high_priority} relationships need immediate attention. Focus on your top 3 priorities."
        elif high_priority >= 1:
            return f"{high_priority} key relationship(s) need attention this week. Opportunity to strengthen important connections."
        else:
            return "Good week for relationship maintenance. Focus on deepening existing connections."
    
    def get_trust_digest_api(self, user_id: str) -> Dict[str, Any]:
        """API endpoint for trust digest - top 3 priority contacts"""
        try:
            contacts = DatabaseHelper.execute_query(
                '''
                SELECT c.*, 
                       COUNT(ci.id) as interaction_count,
                       MAX(ci.interaction_date) as last_interaction
                FROM contacts c
                LEFT JOIN contact_interactions ci ON c.id = ci.contact_id
                WHERE c.user_id = %s
                GROUP BY c.id
                ''',
                (user_id,),
                fetch_all=True
            ) or []
            
            priority_contacts = []
            for contact in contacts:
                priority_score = self._calculate_priority_score(contact)
                if priority_score > 0.5:
                    priority_contacts.append({
                        'id': contact.get('id'),
                        'name': contact.get('name'),
                        'company': contact.get('company'),
                        'priority_score': round(priority_score, 2),
                        'reason': self._get_priority_reason(contact),
                        'warmth_status': contact.get('warmth_status'),
                        'last_interaction': contact.get('last_interaction')
                    })
            
            # Sort and return top 3
            priority_contacts.sort(key=lambda x: x['priority_score'], reverse=True)
            
            return {
                'top_priorities': priority_contacts[:3],
                'total_found': len(priority_contacts),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating trust digest: {e}")
            return {'error': 'Failed to generate trust digest'}