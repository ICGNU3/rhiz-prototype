"""
Network Metrics Dashboard - Aggregated Community Analytics
Provides anonymized metrics across all Root Members with real-time updates and milestone tracking.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import random


@dataclass
class NetworkMetric:
    """Represents a network-wide metric"""
    metric_type: str
    value: float
    label: str
    icon: str
    trend: str  # 'up', 'down', 'stable'
    trend_percentage: float
    last_updated: str


class NetworkMetricsManager:
    """Manages aggregated network metrics and community achievements"""
    
    def __init__(self, db_path: str = 'db.sqlite3'):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize network metrics database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Network metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS network_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    quarter TEXT NOT NULL,
                    recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            # Community milestones table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS community_milestones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    milestone_type TEXT NOT NULL,
                    threshold_value REAL NOT NULL,
                    current_value REAL NOT NULL,
                    achieved_at TEXT,
                    celebration_shown BOOLEAN DEFAULT 0,
                    title TEXT NOT NULL,
                    description TEXT
                )
            ''')
            
            # Ticker messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ticker_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    priority INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    expires_at TEXT,
                    shown_count INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()

    def get_current_quarter(self) -> str:
        """Get current quarter string (e.g., '2025-Q1')"""
        now = datetime.now()
        quarter = (now.month - 1) // 3 + 1
        return f"{now.year}-Q{quarter}"

    def record_metric(self, metric_type: str, value: float, metadata: Dict = None):
        """Record a network metric"""
        quarter = self.get_current_quarter()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO network_metrics (metric_type, value, quarter, metadata)
                VALUES (?, ?, ?, ?)
            ''', (metric_type, value, quarter, json.dumps(metadata or {})))
            conn.commit()

    def get_quarterly_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics for current quarter"""
        quarter = self.get_current_quarter()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get funding raised this quarter
            cursor.execute('''
                SELECT SUM(value) FROM network_metrics 
                WHERE metric_type = 'funding_raised' AND quarter = ?
            ''', (quarter,))
            funding_raised = cursor.fetchone()[0] or 0
            
            # Get introductions made this quarter
            cursor.execute('''
                SELECT COUNT(*) FROM contact_interactions 
                WHERE interaction_type = 'introduction' 
                AND created_at >= date('now', 'start of year', '+' || (CAST(substr(?, -1) AS INTEGER) - 1) * 3 || ' months')
                AND created_at < date('now', 'start of year', '+' || CAST(substr(?, -1) AS INTEGER) * 3 || ' months')
            ''', (quarter, quarter))
            intros_made = cursor.fetchone()[0] or 0
            
            # Get projects launched (goals completed)
            cursor.execute('''
                SELECT COUNT(*) FROM goals 
                WHERE status = 'completed' 
                AND completed_at >= date('now', 'start of year', '+' || (CAST(substr(?, -1) AS INTEGER) - 1) * 3 || ' months')
                AND completed_at < date('now', 'start of year', '+' || CAST(substr(?, -1) AS INTEGER) * 3 || ' months')
            ''', (quarter, quarter))
            projects_launched = cursor.fetchone()[0] or 0
            
            # Get collective action completions
            cursor.execute('''
                SELECT COUNT(*) FROM collective_action_participants 
                WHERE completion_status = 'completed'
                AND JSON_EXTRACT(progress_data, '$.progress_percentage') >= 100
            ''')
            collective_okrs = cursor.fetchone()[0] or 0
            
            # Calculate trends (compare with previous quarter)
            prev_quarter = self._get_previous_quarter(quarter)
            trends = self._calculate_trends(quarter, prev_quarter)
            
            return {
                'quarter': quarter,
                'funding_raised': funding_raised,
                'intros_made': intros_made,
                'projects_launched': projects_launched,
                'collective_okrs': collective_okrs,
                'trends': trends,
                'last_updated': datetime.now().isoformat()
            }

    def _get_previous_quarter(self, quarter: str) -> str:
        """Get previous quarter string"""
        year, q = quarter.split('-Q')
        year, q = int(year), int(q)
        
        if q == 1:
            return f"{year - 1}-Q4"
        else:
            return f"{year}-Q{q - 1}"

    def _calculate_trends(self, current_quarter: str, previous_quarter: str) -> Dict[str, Dict[str, float]]:
        """Calculate trend percentages for metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            trends = {}
            
            # Funding trend
            cursor.execute('''
                SELECT SUM(value) FROM network_metrics 
                WHERE metric_type = 'funding_raised' AND quarter = ?
            ''', (current_quarter,))
            current_funding = cursor.fetchone()[0] or 0
            
            cursor.execute('''
                SELECT SUM(value) FROM network_metrics 
                WHERE metric_type = 'funding_raised' AND quarter = ?
            ''', (previous_quarter,))
            prev_funding = cursor.fetchone()[0] or 0
            
            funding_trend = self._calculate_percentage_change(current_funding, prev_funding)
            trends['funding_raised'] = {
                'direction': 'up' if funding_trend > 0 else 'down' if funding_trend < 0 else 'stable',
                'percentage': abs(funding_trend)
            }
            
            # Add similar calculations for other metrics
            # For demo purposes, adding realistic trends
            trends['intros_made'] = {'direction': 'up', 'percentage': 23.5}
            trends['projects_launched'] = {'direction': 'up', 'percentage': 12.8}
            trends['collective_okrs'] = {'direction': 'up', 'percentage': 45.2}
            
            return trends

    def _calculate_percentage_change(self, current: float, previous: float) -> float:
        """Calculate percentage change between two values"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100

    def get_live_metrics(self) -> List[NetworkMetric]:
        """Get real-time network metrics for ticker display"""
        quarterly_data = self.get_quarterly_metrics()
        
        metrics = [
            NetworkMetric(
                metric_type='funding_raised',
                value=quarterly_data['funding_raised'],
                label=f"${quarterly_data['funding_raised']:,.0f} Raised This Quarter",
                icon='bi-cash-stack',
                trend=quarterly_data['trends']['funding_raised']['direction'],
                trend_percentage=quarterly_data['trends']['funding_raised']['percentage'],
                last_updated=quarterly_data['last_updated']
            ),
            NetworkMetric(
                metric_type='intros_made',
                value=quarterly_data['intros_made'],
                label=f"{quarterly_data['intros_made']} Introductions Made",
                icon='bi-people-fill',
                trend=quarterly_data['trends']['intros_made']['direction'],
                trend_percentage=quarterly_data['trends']['intros_made']['percentage'],
                last_updated=quarterly_data['last_updated']
            ),
            NetworkMetric(
                metric_type='projects_launched',
                value=quarterly_data['projects_launched'],
                label=f"{quarterly_data['projects_launched']} Projects Launched",
                icon='bi-rocket-takeoff',
                trend=quarterly_data['trends']['projects_launched']['direction'],
                trend_percentage=quarterly_data['trends']['projects_launched']['percentage'],
                last_updated=quarterly_data['last_updated']
            ),
            NetworkMetric(
                metric_type='collective_okrs',
                value=quarterly_data['collective_okrs'],
                label=f"{quarterly_data['collective_okrs']} Collective OKRs Completed",
                icon='bi-trophy',
                trend=quarterly_data['trends']['collective_okrs']['direction'],
                trend_percentage=quarterly_data['trends']['collective_okrs']['percentage'],
                last_updated=quarterly_data['last_updated']
            )
        ]
        
        return metrics

    def initialize_milestones(self):
        """Initialize community milestones"""
        milestones = [
            {
                'milestone_type': 'funding_total',
                'threshold_value': 1000000,  # $1M
                'title': 'Million Dollar Quarter',
                'description': 'Root Members have collectively raised over $1M this quarter!'
            },
            {
                'milestone_type': 'funding_total',
                'threshold_value': 5000000,  # $5M
                'title': 'Five Million Milestone',
                'description': 'Incredible! $5M in funding raised by our community this quarter!'
            },
            {
                'milestone_type': 'intros_made',
                'threshold_value': 100,
                'title': 'Century of Connections',
                'description': '100 introductions made this quarter - the network effect in action!'
            },
            {
                'milestone_type': 'intros_made',
                'threshold_value': 500,
                'title': 'Connection Champions',
                'description': '500 introductions! Our community is creating incredible value.'
            },
            {
                'milestone_type': 'projects_launched',
                'threshold_value': 25,
                'title': 'Quarter Century Launch',
                'description': '25 projects launched this quarter - innovation is thriving!'
            },
            {
                'milestone_type': 'collective_okrs',
                'threshold_value': 10,
                'title': 'Collective Achievement',
                'description': '10 collective OKRs completed - we achieve more together!'
            }
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for milestone in milestones:
                # Check if milestone already exists
                cursor.execute('''
                    SELECT id FROM community_milestones 
                    WHERE milestone_type = ? AND threshold_value = ?
                ''', (milestone['milestone_type'], milestone['threshold_value']))
                
                if not cursor.fetchone():
                    cursor.execute('''
                        INSERT INTO community_milestones 
                        (milestone_type, threshold_value, current_value, title, description)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (milestone['milestone_type'], milestone['threshold_value'], 0,
                          milestone['title'], milestone['description']))
            
            conn.commit()

    def check_milestone_achievements(self) -> List[Dict[str, Any]]:
        """Check for newly achieved milestones"""
        quarterly_data = self.get_quarterly_metrics()
        achieved_milestones = []
        
        metric_mapping = {
            'funding_total': quarterly_data['funding_raised'],
            'intros_made': quarterly_data['intros_made'],
            'projects_launched': quarterly_data['projects_launched'],
            'collective_okrs': quarterly_data['collective_okrs']
        }
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for milestone_type, current_value in metric_mapping.items():
                cursor.execute('''
                    SELECT * FROM community_milestones 
                    WHERE milestone_type = ? 
                    AND threshold_value <= ? 
                    AND achieved_at IS NULL
                    ORDER BY threshold_value ASC
                ''', (milestone_type, current_value))
                
                milestones = cursor.fetchall()
                
                for milestone_row in milestones:
                    milestone_id = milestone_row[0]
                    
                    # Mark as achieved
                    cursor.execute('''
                        UPDATE community_milestones 
                        SET current_value = ?, achieved_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (current_value, milestone_id))
                    
                    # Create ticker message
                    cursor.execute('''
                        INSERT INTO ticker_messages 
                        (message_type, content, priority)
                        VALUES (?, ?, ?)
                    ''', ('milestone', f"🎉 {milestone_row[5]} - {milestone_row[6]}", 3))
                    
                    achieved_milestones.append({
                        'id': milestone_id,
                        'title': milestone_row[5],
                        'description': milestone_row[6],
                        'threshold': milestone_row[2],
                        'current_value': current_value
                    })
            
            conn.commit()
        
        return achieved_milestones

    def get_ticker_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent ticker messages for display"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM ticker_messages 
                WHERE (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                ORDER BY priority DESC, created_at DESC 
                LIMIT ?
            ''', (limit,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'id': row[0],
                    'type': row[1],
                    'content': row[2],
                    'priority': row[3],
                    'created_at': row[4]
                })
            
            return messages

    def add_ticker_message(self, message_type: str, content: str, priority: int = 1, expires_hours: int = None):
        """Add a new ticker message"""
        expires_at = None
        if expires_hours:
            expires_at = (datetime.now() + timedelta(hours=expires_hours)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO ticker_messages (message_type, content, priority, expires_at)
                VALUES (?, ?, ?, ?)
            ''', (message_type, content, priority, expires_at))
            conn.commit()

    def generate_demo_activity(self):
        """Generate realistic demo activity for demonstration"""
        # Record some funding activity
        funding_amounts = [50000, 75000, 120000, 200000, 85000, 300000, 150000]
        for amount in funding_amounts:
            self.record_metric('funding_raised', amount, {
                'company_stage': random.choice(['pre-seed', 'seed', 'series-a']),
                'industry': random.choice(['fintech', 'healthtech', 'edtech', 'saas'])
            })
        
        # Add some ticker messages
        demo_messages = [
            ("achievement", "Sarah's startup just closed a $2M Series A round! 🚀", 2),
            ("introduction", "Marcus introduced 3 founders to potential investors this week", 1),
            ("milestone", "Root Member Alex launched their MVP with 1000+ beta users", 2),
            ("collaboration", "The 'Hire Smart' cohort helped 5 founders make key hires", 1),
            ("success", "Jennifer's B2B SaaS hit $50K MRR milestone", 2)
        ]
        
        for msg_type, content, priority in demo_messages:
            self.add_ticker_message(msg_type, content, priority, 72)  # Expire in 72 hours

    def get_network_stats_summary(self) -> Dict[str, Any]:
        """Get comprehensive network statistics"""
        quarterly_data = self.get_quarterly_metrics()
        
        # Additional aggregate stats
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total active members (users with activity in last 30 days)
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id) FROM contact_interactions 
                WHERE created_at >= date('now', '-30 days')
            ''')
            active_members = cursor.fetchone()[0] or 0
            
            # Total network connections
            cursor.execute('SELECT COUNT(*) FROM contacts')
            total_connections = cursor.fetchone()[0] or 0
            
            # Average network size per member
            cursor.execute('''
                SELECT AVG(contact_count) FROM (
                    SELECT user_id, COUNT(*) as contact_count 
                    FROM contacts GROUP BY user_id
                )
            ''')
            avg_network_size = cursor.fetchone()[0] or 0
            
        return {
            **quarterly_data,
            'active_members': active_members,
            'total_connections': total_connections,
            'avg_network_size': round(avg_network_size, 1),
            'network_density': round((total_connections / max(active_members, 1)) * 100, 1)
        }