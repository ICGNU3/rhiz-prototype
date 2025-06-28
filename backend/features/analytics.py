"""
Analytics module for outreach success rates and networking insights.
Provides comprehensive metrics and data visualization for founder networking.
"""

from models import Database, ContactInteraction, Contact, Goal, OutreachSuggestion
from datetime import datetime, timedelta
import logging

class NetworkingAnalytics:
    def __init__(self, db):
        self.db = db
        self.interaction_model = ContactInteraction(db)
        self.contact_model = Contact(db)
        self.goal_model = Goal(db)
        self.outreach_model = OutreachSuggestion(db)
    
    def get_outreach_success_metrics(self, user_id, days_back=30):
        """Calculate outreach success rates and metrics"""
        # Get interactions from the last N days
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Email outreach metrics
        cursor.execute("""
            SELECT 
                status,
                COUNT(*) as count
            FROM contact_interactions 
            WHERE user_id = ? 
            AND interaction_type = 'Email' 
            AND direction = 'outbound'
            AND timestamp >= ?
            GROUP BY status
        """, (user_id, cutoff_date.isoformat()))
        
        email_stats = dict(cursor.fetchall())
        
        # Response rates (assuming responses are logged as inbound interactions)
        cursor.execute("""
            SELECT COUNT(*) as responses
            FROM contact_interactions 
            WHERE user_id = ? 
            AND interaction_type = 'Email' 
            AND direction = 'inbound'
            AND timestamp >= ?
        """, (user_id, cutoff_date.isoformat()))
        
        responses = cursor.fetchone()[0]
        
        # Total outbound emails
        total_sent = email_stats.get('sent', 0)
        total_failed = email_stats.get('failed', 0)
        total_outbound = total_sent + total_failed
        
        # Calculate rates
        success_rate = (total_sent / total_outbound * 100) if total_outbound > 0 else 0
        response_rate = (responses / total_sent * 100) if total_sent > 0 else 0
        
        return {
            'total_outbound': total_outbound,
            'total_sent': total_sent,
            'total_failed': total_failed,
            'total_responses': responses,
            'success_rate': round(success_rate, 1),
            'response_rate': round(response_rate, 1),
            'period_days': days_back
        }
    
    def get_interaction_trends(self, user_id, days_back=30):
        """Get daily interaction trends"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                interaction_type,
                direction,
                COUNT(*) as count
            FROM contact_interactions 
            WHERE user_id = ? 
            AND created_at >= ?
            GROUP BY DATE(created_at), interaction_type, direction
            ORDER BY date DESC
        """, (user_id, cutoff_date.isoformat()))
        
        trends = cursor.fetchall()
        
        # Process trends by date
        daily_stats = {}
        for date, interaction_type, direction, count in trends:
            if date not in daily_stats:
                daily_stats[date] = {'outbound': 0, 'inbound': 0, 'total': 0}
            
            daily_stats[date][direction] += count
            daily_stats[date]['total'] += count
        
        return daily_stats
    
    def get_contact_effectiveness(self, user_id):
        """Analyze which types of contacts are most effective"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                c.relationship_type,
                c.warmth_label,
                COUNT(ci.id) as interactions,
                COUNT(CASE WHEN ci.direction = 'inbound' THEN 1 END) as responses
            FROM contacts c
            LEFT JOIN contact_interactions ci ON c.id = ci.contact_id
            WHERE c.user_id = ?
            GROUP BY c.relationship_type, c.warmth_label
            HAVING interactions > 0
            ORDER BY interactions DESC
        """, (user_id,))
        
        effectiveness = []
        for relationship_type, warmth_label, interactions, responses in cursor.fetchall():
            response_rate = (responses / interactions * 100) if interactions > 0 else 0
            effectiveness.append({
                'relationship_type': relationship_type,
                'warmth_label': warmth_label,
                'interactions': interactions,
                'responses': responses,
                'response_rate': round(response_rate, 1)
            })
        
        return effectiveness
    
    def get_goal_performance(self, user_id):
        """Analyze performance by goals"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                g.title,
                g.description,
                COUNT(ci.id) as interactions,
                COUNT(CASE WHEN ci.status = 'sent' THEN 1 END) as successful_outreach
            FROM goals g
            LEFT JOIN contact_interactions ci ON ci.subject LIKE '%' || g.title || '%'
            WHERE g.user_id = ?
            GROUP BY g.id, g.title, g.description
            ORDER BY interactions DESC
        """, (user_id,))
        
        goal_performance = []
        for title, description, interactions, successful_outreach in cursor.fetchall():
            success_rate = (successful_outreach / interactions * 100) if interactions > 0 else 0
            goal_performance.append({
                'title': title,
                'description': description[:100] + '...' if len(description or '') > 100 else description,
                'interactions': interactions,
                'successful_outreach': successful_outreach,
                'success_rate': round(success_rate, 1)
            })
        
        return goal_performance
    
    def get_network_growth(self, user_id, days_back=90):
        """Track network growth over time"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Contacts added over time
        cursor.execute("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as new_contacts
            FROM contacts 
            WHERE user_id = ? 
            AND created_at >= ?
            GROUP BY DATE(created_at)
            ORDER BY date
        """, (user_id, cutoff_date.isoformat()))
        
        growth_data = cursor.fetchall()
        
        # Calculate cumulative growth
        total_contacts = 0
        growth_trends = []
        for date, new_contacts in growth_data:
            total_contacts += new_contacts
            growth_trends.append({
                'date': date,
                'new_contacts': new_contacts,
                'total_contacts': total_contacts
            })
        
        return growth_trends
    
    def get_warmth_pipeline_metrics(self, user_id):
        """Analyze contacts by warmth pipeline stages"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                warmth_label,
                COUNT(*) as count,
                AVG(warmth_status) as avg_warmth_score
            FROM contacts 
            WHERE user_id = ?
            GROUP BY warmth_label
            ORDER BY avg_warmth_score
        """, (user_id,))
        
        pipeline_data = []
        total_contacts = 0
        
        for warmth_label, count, avg_score in cursor.fetchall():
            total_contacts += count
            pipeline_data.append({
                'warmth_label': warmth_label,
                'count': count,
                'avg_score': round(avg_score, 1)
            })
        
        # Add percentages
        for item in pipeline_data:
            item['percentage'] = round((item['count'] / total_contacts * 100), 1) if total_contacts > 0 else 0
        
        return pipeline_data
    
    def get_top_performing_contacts(self, user_id, limit=10):
        """Get contacts with highest interaction rates"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                c.name,
                c.company,
                c.relationship_type,
                COUNT(ci.id) as total_interactions,
                COUNT(CASE WHEN ci.direction = 'inbound' THEN 1 END) as responses,
                MAX(ci.created_at) as last_interaction
            FROM contacts c
            LEFT JOIN contact_interactions ci ON c.id = ci.contact_id
            WHERE c.user_id = ?
            GROUP BY c.id, c.name, c.company, c.relationship_type
            HAVING total_interactions > 0
            ORDER BY total_interactions DESC, responses DESC
            LIMIT ?
        """, (user_id, limit))
        
        top_contacts = []
        for name, company, rel_type, interactions, responses, last_interaction in cursor.fetchall():
            response_rate = (responses / interactions * 100) if interactions > 0 else 0
            top_contacts.append({
                'name': name,
                'company': company or 'Unknown',
                'relationship_type': rel_type,
                'total_interactions': interactions,
                'responses': responses,
                'response_rate': round(response_rate, 1),
                'last_interaction': last_interaction
            })
        
        return top_contacts
    
    def get_comprehensive_dashboard_data(self, user_id):
        """Get all analytics data for the dashboard"""
        return {
            'outreach_metrics': self.get_outreach_success_metrics(user_id),
            'interaction_trends': self.get_interaction_trends(user_id),
            'contact_effectiveness': self.get_contact_effectiveness(user_id),
            'goal_performance': self.get_goal_performance(user_id),
            'network_growth': self.get_network_growth(user_id),
            'pipeline_metrics': self.get_warmth_pipeline_metrics(user_id),
            'top_contacts': self.get_top_performing_contacts(user_id),
            'generated_at': datetime.now().isoformat()
        }