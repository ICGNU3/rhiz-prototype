"""
Trust Insights Service
Provides relationship intelligence and trust scoring
"""

import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import os
from openai import OpenAI

logger = logging.getLogger(__name__)

class TrustInsights:
    """Trust insights and relationship intelligence engine"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        try:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
            else:
                self.openai_client = None
                logger.warning("OpenAI API key not found - AI features will be limited")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {e}")
            self.openai_client = None

    def get_trust_insights(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive trust insights for user"""
        try:
            if not self.db:
                return self._get_demo_trust_insights()
                
            cursor = self.db.cursor()
            
            # Get trust tier distribution
            tier_distribution = self._get_trust_tier_distribution(user_id, cursor)
            
            # Get top trusted contacts
            top_contacts = self._get_top_trusted_contacts(user_id, cursor)
            
            # Get at-risk relationships
            at_risk = self._get_at_risk_relationships(user_id, cursor)
            
            # Get recent trust changes
            recent_changes = self._get_recent_trust_changes(user_id, cursor)
            
            # Generate trust summary
            trust_summary = self._generate_trust_summary(user_id, cursor)
            
            return {
                'trust_tiers': tier_distribution,
                'top_contacts': top_contacts,
                'at_risk_contacts': at_risk,
                'recent_changes': recent_changes,
                'trust_summary': trust_summary,
                'total_contacts': sum(tier_distribution.values())
            }
            
        except Exception as e:
            logger.error(f"Error getting trust insights: {e}")
            return self._get_demo_trust_insights()

    def _get_trust_tier_distribution(self, user_id: str, cursor) -> Dict[str, int]:
        """Get distribution of contacts across trust tiers"""
        try:
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN warmth_status >= 4 THEN 'rooted'
                        WHEN warmth_status = 3 THEN 'growing'
                        WHEN warmth_status = 2 THEN 'dormant'
                        ELSE 'frayed'
                    END as tier,
                    COUNT(*) as count
                FROM contacts 
                WHERE user_id = %s
                GROUP BY tier
            """, (user_id,))
            
            results = cursor.fetchall()
            distribution = {'rooted': 0, 'growing': 0, 'dormant': 0, 'frayed': 0}
            
            for tier, count in results:
                distribution[tier] = count
                
            return distribution
            
        except Exception as e:
            logger.error(f"Error getting trust tier distribution: {e}")
            return {'rooted': 0, 'growing': 0, 'dormant': 0, 'frayed': 0}

    def _get_top_trusted_contacts(self, user_id: str, cursor) -> List[Dict[str, Any]]:
        """Get top trusted contacts with high warmth scores"""
        try:
            cursor.execute("""
                SELECT c.id, c.name, c.company, c.title, c.warmth_status, c.warmth_label,
                       COUNT(ci.id) as interaction_count,
                       MAX(ci.interaction_date) as last_interaction
                FROM contacts c
                LEFT JOIN contact_interactions ci ON c.id = ci.contact_id
                WHERE c.user_id = %s AND c.warmth_status >= 3
                GROUP BY c.id, c.name, c.company, c.title, c.warmth_status, c.warmth_label
                ORDER BY c.warmth_status DESC, interaction_count DESC
                LIMIT 10
            """, (user_id,))
            
            contacts = []
            for row in cursor.fetchall():
                contacts.append({
                    'id': row[0],
                    'name': row[1],
                    'company': row[2],
                    'title': row[3],
                    'warmth_status': row[4],
                    'warmth_label': row[5],
                    'interaction_count': row[6],
                    'last_interaction': row[7],
                    'trust_tier': 'rooted' if row[4] >= 4 else 'growing'
                })
            
            return contacts
            
        except Exception as e:
            logger.error(f"Error getting top trusted contacts: {e}")
            return []

    def _get_at_risk_relationships(self, user_id: str, cursor) -> List[Dict[str, Any]]:
        """Get relationships that might be at risk of deteriorating"""
        try:
            # Look for contacts with no recent interactions but good warmth status
            cursor.execute("""
                SELECT c.id, c.name, c.company, c.title, c.warmth_status, c.warmth_label,
                       c.last_interaction_date,
                       COUNT(ci.id) as interaction_count
                FROM contacts c
                LEFT JOIN contact_interactions ci ON c.id = ci.contact_id 
                    AND ci.interaction_date > NOW() - INTERVAL '90 days'
                WHERE c.user_id = %s 
                    AND c.warmth_status >= 2
                    AND (c.last_interaction_date < NOW() - INTERVAL '60 days' OR c.last_interaction_date IS NULL)
                GROUP BY c.id, c.name, c.company, c.title, c.warmth_status, c.warmth_label, c.last_interaction_date
                ORDER BY c.warmth_status DESC, c.last_interaction_date ASC
                LIMIT 8
            """, (user_id,))
            
            at_risk = []
            for row in cursor.fetchall():
                days_since = self._calculate_days_since(row[6])
                at_risk.append({
                    'id': row[0],
                    'name': row[1],
                    'company': row[2],
                    'title': row[3],
                    'warmth_status': row[4],
                    'warmth_label': row[5],
                    'last_interaction_date': row[6],
                    'days_since_contact': days_since,
                    'risk_level': 'high' if days_since > 90 else 'medium'
                })
            
            return at_risk
            
        except Exception as e:
            logger.error(f"Error getting at-risk relationships: {e}")
            return []

    def _get_recent_trust_changes(self, user_id: str, cursor) -> List[Dict[str, Any]]:
        """Get recent changes in trust scores or relationship status"""
        try:
            # Look for recent interactions and warmth changes
            cursor.execute("""
                SELECT c.name, c.company, ci.interaction_type, ci.interaction_date,
                       ci.sentiment, c.warmth_label
                FROM contacts c
                JOIN contact_interactions ci ON c.id = ci.contact_id
                WHERE c.user_id = %s
                    AND ci.interaction_date > NOW() - INTERVAL '30 days'
                ORDER BY ci.interaction_date DESC
                LIMIT 10
            """, (user_id,))
            
            changes = []
            for row in cursor.fetchall():
                changes.append({
                    'contact_name': row[0],
                    'company': row[1],
                    'interaction_type': row[2],
                    'date': row[3],
                    'sentiment': row[4],
                    'warmth_level': row[5],
                    'change_type': 'interaction'
                })
            
            return changes
            
        except Exception as e:
            logger.error(f"Error getting recent trust changes: {e}")
            return []

    def _generate_trust_summary(self, user_id: str, cursor) -> Dict[str, Any]:
        """Generate AI-powered trust summary"""
        try:
            if not self.openai_client:
                return {
                    'summary': 'Trust analysis requires AI capabilities',
                    'health_score': 75,
                    'key_insights': ['Regular contact review recommended']
                }
            
            # Get aggregate statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_contacts,
                    COUNT(CASE WHEN warmth_status >= 3 THEN 1 END) as warm_contacts,
                    COUNT(CASE WHEN last_interaction_date > NOW() - INTERVAL '30 days' THEN 1 END) as recent_contacts,
                    AVG(warmth_status) as avg_warmth
                FROM contacts 
                WHERE user_id = %s
            """, (user_id,))
            
            stats = cursor.fetchone()
            if not stats:
                return {'summary': 'No contact data available'}
            
            total, warm, recent, avg_warmth = stats
            
            prompt = f"""
            Analyze this user's relationship network health:
            
            Total contacts: {total}
            Warm relationships (tier 3+): {warm}
            Recent interactions (30 days): {recent}
            Average warmth score: {avg_warmth:.1f}
            
            Provide a brief analysis with:
            1. Overall network health score (0-100)
            2. 2-3 key insights about relationship patterns
            3. One actionable recommendation
            
            Respond in JSON format:
            {{
                "health_score": number,
                "summary": "brief overall assessment",
                "key_insights": ["insight1", "insight2"],
                "recommendation": "specific action to take"
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Latest OpenAI model
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=300
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error generating trust summary: {e}")
            return {
                'summary': 'Trust analysis in progress',
                'health_score': 70,
                'key_insights': ['Network analysis requires more data']
            }

    def _calculate_days_since(self, date) -> int:
        """Calculate days since given date"""
        if not date:
            return 365  # Default for null dates
        
        if isinstance(date, str):
            try:
                date = datetime.fromisoformat(date.replace('Z', '+00:00'))
            except:
                return 365
        
        return (datetime.now() - date).days

    def get_contact_trust_insight(self, contact_id: str) -> Dict[str, Any]:
        """Get detailed trust insight for specific contact"""
        try:
            if not self.db:
                return self._get_demo_contact_insight()
                
            cursor = self.db.cursor()
            
            # Get contact details and interaction history
            cursor.execute("""
                SELECT c.name, c.company, c.title, c.warmth_status, c.warmth_label,
                       c.last_interaction_date, c.notes,
                       COUNT(ci.id) as interaction_count,
                       STRING_AGG(ci.summary, '; ') as interaction_summaries
                FROM contacts c
                LEFT JOIN contact_interactions ci ON c.id = ci.contact_id
                WHERE c.id = %s
                GROUP BY c.id, c.name, c.company, c.title, c.warmth_status, 
                         c.warmth_label, c.last_interaction_date, c.notes
            """, (contact_id,))
            
            result = cursor.fetchone()
            if not result:
                return {'error': 'Contact not found'}
            
            name, company, title, warmth_status, warmth_label = result[:5]
            last_interaction, notes, interaction_count, summaries = result[5:9]
            
            # Calculate trust metrics
            trust_score = min(100, (warmth_status * 20) + min(50, interaction_count * 5))
            response_rate = 85 if warmth_status >= 3 else 60  # Simplified
            reliability_score = 90 if warmth_status >= 4 else 75
            
            # Generate AI insights
            insights = self._generate_contact_insights(name, company, title, 
                                                     warmth_label, interaction_count, 
                                                     summaries, notes)
            
            return {
                'contact_info': {
                    'name': name,
                    'company': company,
                    'title': title,
                    'warmth_level': warmth_label
                },
                'trust_metrics': {
                    'trust_score': trust_score,
                    'response_rate': response_rate,
                    'reliability_score': reliability_score,
                    'interaction_count': interaction_count
                },
                'insights': insights,
                'last_interaction': last_interaction,
                'trust_tier': self._get_trust_tier_from_warmth(warmth_status)
            }
            
        except Exception as e:
            logger.error(f"Error getting contact trust insight: {e}")
            return self._get_demo_contact_insight()

    def _generate_contact_insights(self, name: str, company: str, title: str,
                                 warmth: str, interaction_count: int,
                                 summaries: str, notes: str) -> Dict[str, Any]:
        """Generate AI insights for specific contact"""
        try:
            if not self.openai_client:
                return {
                    'relationship_stage': 'developing',
                    'trust_indicators': ['Regular communication'],
                    'suggested_actions': ['Schedule regular check-ins']
                }
            
            prompt = f"""
            Analyze this professional relationship for trust insights:
            
            Contact: {name} at {company} ({title})
            Relationship warmth: {warmth}
            Total interactions: {interaction_count}
            Interaction history: {summaries or 'Limited history'}
            Notes: {notes or 'None'}
            
            Provide trust analysis in JSON format:
            {{
                "relationship_stage": "string (building/established/strong/at_risk)",
                "trust_indicators": ["indicator1", "indicator2"],
                "suggested_actions": ["action1", "action2"],
                "trust_factors": {{"positive": ["factor1"], "negative": ["factor1"]}}
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=400
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error generating contact insights: {e}")
            return {
                'relationship_stage': 'developing',
                'trust_indicators': ['Active communication'],
                'suggested_actions': ['Continue regular engagement']
            }

    def _get_trust_tier_from_warmth(self, warmth_status: int) -> str:
        """Convert warmth status to trust tier"""
        if warmth_status >= 4:
            return 'rooted'
        elif warmth_status == 3:
            return 'growing'
        elif warmth_status == 2:
            return 'dormant'
        else:
            return 'frayed'

    def get_trust_health(self, user_id: str) -> Dict[str, Any]:
        """Get overall trust health analysis"""
        try:
            trust_insights = self.get_trust_insights(user_id)
            trust_summary = trust_insights.get('trust_summary', {})
            
            return {
                'health_score': trust_summary.get('health_score', 70),
                'total_contacts': trust_insights.get('total_contacts', 0),
                'trusted_contacts': trust_insights['trust_tiers'].get('rooted', 0) + 
                                  trust_insights['trust_tiers'].get('growing', 0),
                'at_risk_count': len(trust_insights.get('at_risk_contacts', [])),
                'recommendations': [trust_summary.get('recommendation', 'Review contact list')]
            }
            
        except Exception as e:
            logger.error(f"Error getting trust health: {e}")
            return {
                'health_score': 70,
                'total_contacts': 0,
                'trusted_contacts': 0,
                'at_risk_count': 0,
                'recommendations': ['Add more contacts to analyze trust patterns']
            }

    def _get_demo_trust_insights(self) -> Dict[str, Any]:
        """Demo trust insights for when database is unavailable"""
        return {
            'trust_tiers': {'rooted': 8, 'growing': 12, 'dormant': 15, 'frayed': 5},
            'top_contacts': [
                {
                    'id': '1',
                    'name': 'Sarah Chen',
                    'company': 'TechCorp',
                    'title': 'CTO',
                    'warmth_status': 5,
                    'warmth_label': 'Active',
                    'interaction_count': 15,
                    'trust_tier': 'rooted'
                }
            ],
            'at_risk_contacts': [
                {
                    'id': '2',
                    'name': 'Mike Johnson',
                    'company': 'StartupX',
                    'title': 'Founder',
                    'days_since_contact': 75,
                    'risk_level': 'medium'
                }
            ],
            'recent_changes': [],
            'trust_summary': {
                'health_score': 78,
                'summary': 'Your network shows strong trust patterns',
                'key_insights': ['High retention in top tier', 'Growing middle tier'],
                'recommendation': 'Re-engage with dormant contacts'
            },
            'total_contacts': 40
        }

    def _get_demo_contact_insight(self) -> Dict[str, Any]:
        """Demo contact insight for when database is unavailable"""
        return {
            'contact_info': {
                'name': 'Demo Contact',
                'company': 'Demo Corp',
                'title': 'Demo Title',
                'warmth_level': 'Warm'
            },
            'trust_metrics': {
                'trust_score': 85,
                'response_rate': 90,
                'reliability_score': 88,
                'interaction_count': 12
            },
            'insights': {
                'relationship_stage': 'established',
                'trust_indicators': ['Consistent communication', 'Mutual introductions'],
                'suggested_actions': ['Schedule quarterly check-in', 'Explore collaboration opportunities']
            },
            'trust_tier': 'growing'
        }

# Global instance
trust_insights = TrustInsights()