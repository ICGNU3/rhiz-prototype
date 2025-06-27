"""
Trust & Contribution Tracking Engine
Advanced relationship trust scoring and contribution history analysis
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass

@dataclass
class TrustMetric:
    contact_id: int
    trust_score: float  # 0.0 to 1.0
    reliability_score: float
    responsiveness_score: float
    value_delivered_score: float
    consistency_score: float
    last_updated: datetime

@dataclass
class ContributionEvent:
    id: int
    contact_id: int
    contribution_type: str  # introduction, advice, resource, opportunity, support
    value_level: str  # low, medium, high, critical
    description: str
    outcome: str  # successful, pending, failed
    date_created: datetime
    impact_score: float

class TrustContributionEngine:
    """Engine for tracking trust and contribution patterns in professional relationships"""
    
    def __init__(self, db_path: str = 'db.sqlite3'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_trust_tables()
        
    def _init_trust_tables(self):
        """Initialize trust and contribution tracking tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS trust_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER NOT NULL,
                    trust_score REAL DEFAULT 0.5,
                    reliability_score REAL DEFAULT 0.5,
                    responsiveness_score REAL DEFAULT 0.5,
                    value_delivered_score REAL DEFAULT 0.5,
                    consistency_score REAL DEFAULT 0.5,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contact_id) REFERENCES contacts (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS contribution_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER NOT NULL,
                    contribution_type TEXT NOT NULL,
                    value_level TEXT NOT NULL,
                    description TEXT,
                    outcome TEXT DEFAULT 'pending',
                    impact_score REAL DEFAULT 0.0,
                    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contact_id) REFERENCES contacts (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS trust_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    contact_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    score_change REAL NOT NULL,
                    reason TEXT,
                    date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (contact_id) REFERENCES contacts (id)
                )
            ''')
            
            conn.commit()
    
    def record_contribution(self, contact_id: int, contribution_type: str, 
                          value_level: str, description: str = "", 
                          outcome: str = "pending") -> int:
        """Record a contribution from a contact"""
        
        # Calculate impact score based on type and value level
        impact_scores = {
            'introduction': {'low': 0.2, 'medium': 0.4, 'high': 0.7, 'critical': 1.0},
            'advice': {'low': 0.1, 'medium': 0.3, 'high': 0.5, 'critical': 0.8},
            'resource': {'low': 0.3, 'medium': 0.5, 'high': 0.8, 'critical': 1.0},
            'opportunity': {'low': 0.4, 'medium': 0.6, 'high': 0.9, 'critical': 1.0},
            'support': {'low': 0.2, 'medium': 0.4, 'high': 0.6, 'critical': 0.9}
        }
        
        impact_score = impact_scores.get(contribution_type, {}).get(value_level, 0.0)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                INSERT INTO contribution_events 
                (contact_id, contribution_type, value_level, description, outcome, impact_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (contact_id, contribution_type, value_level, description, outcome, impact_score))
            
            contribution_id = cursor.lastrowid
            
            # Update trust scores based on contribution
            self._update_trust_from_contribution(contact_id, contribution_type, value_level, outcome)
            
            conn.commit()
            
        self.logger.info(f"Recorded contribution {contribution_type} from contact {contact_id}")
        return contribution_id
    
    def update_contribution_outcome(self, contribution_id: int, outcome: str) -> bool:
        """Update the outcome of a contribution and adjust trust scores"""
        
        with sqlite3.connect(self.db_path) as conn:
            # Get contribution details
            contribution = conn.execute('''
                SELECT contact_id, contribution_type, value_level, impact_score 
                FROM contribution_events WHERE id = ?
            ''', (contribution_id,)).fetchone()
            
            if not contribution:
                return False
                
            contact_id, contrib_type, value_level, base_impact = contribution
            
            # Update outcome
            conn.execute('''
                UPDATE contribution_events SET outcome = ? WHERE id = ?
            ''', (outcome, contribution_id))
            
            # Adjust trust based on outcome
            outcome_multipliers = {
                'successful': 1.2,
                'pending': 1.0,
                'failed': 0.3,
                'exceeded_expectations': 1.5
            }
            
            multiplier = outcome_multipliers.get(outcome, 1.0)
            self._adjust_trust_score(contact_id, base_impact * multiplier, f"Contribution outcome: {outcome}")
            
            conn.commit()
            
        return True
    
    def _update_trust_from_contribution(self, contact_id: int, contribution_type: str, 
                                      value_level: str, outcome: str):
        """Update trust metrics based on a new contribution"""
        
        # Get or create trust metrics
        trust_metrics = self.get_trust_metrics(contact_id)
        if not trust_metrics:
            self._create_initial_trust_metrics(contact_id)
            trust_metrics = self.get_trust_metrics(contact_id)
        
        # Calculate trust adjustments
        adjustments = {
            'introduction': {'value_delivered_score': 0.1, 'trust_score': 0.05},
            'advice': {'value_delivered_score': 0.05, 'reliability_score': 0.03},
            'resource': {'value_delivered_score': 0.08, 'trust_score': 0.04},
            'opportunity': {'value_delivered_score': 0.12, 'trust_score': 0.08},
            'support': {'consistency_score': 0.06, 'trust_score': 0.03}
        }
        
        value_multipliers = {'low': 0.5, 'medium': 1.0, 'high': 1.5, 'critical': 2.0}
        outcome_multipliers = {'successful': 1.0, 'pending': 0.5, 'failed': -0.2}
        
        base_adjustments = adjustments.get(contribution_type, {})
        multiplier = value_multipliers.get(value_level, 1.0) * outcome_multipliers.get(outcome, 1.0)
        
        # Apply adjustments
        with sqlite3.connect(self.db_path) as conn:
            for metric, adjustment in base_adjustments.items():
                final_adjustment = adjustment * multiplier
                
                conn.execute(f'''
                    UPDATE trust_metrics 
                    SET {metric} = MIN(1.0, MAX(0.0, {metric} + ?)),
                        last_updated = CURRENT_TIMESTAMP
                    WHERE contact_id = ?
                ''', (final_adjustment, contact_id))
                
                # Record in trust history
                conn.execute('''
                    INSERT INTO trust_history (contact_id, event_type, score_change, reason)
                    VALUES (?, ?, ?, ?)
                ''', (contact_id, f"{metric}_adjustment", final_adjustment, 
                     f"Contribution: {contribution_type} ({value_level})"))
            
            # Update overall trust score as weighted average
            conn.execute('''
                UPDATE trust_metrics 
                SET trust_score = (reliability_score * 0.3 + responsiveness_score * 0.2 + 
                                 value_delivered_score * 0.4 + consistency_score * 0.1),
                    last_updated = CURRENT_TIMESTAMP
                WHERE contact_id = ?
            ''', (contact_id,))
            
            conn.commit()
    
    def _create_initial_trust_metrics(self, contact_id: int):
        """Create initial trust metrics for a new contact"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO trust_metrics (contact_id) VALUES (?)
            ''', (contact_id,))
            conn.commit()
    
    def get_trust_metrics(self, contact_id: int) -> Optional[TrustMetric]:
        """Get trust metrics for a contact"""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute('''
                SELECT contact_id, trust_score, reliability_score, responsiveness_score,
                       value_delivered_score, consistency_score, last_updated
                FROM trust_metrics WHERE contact_id = ?
            ''', (contact_id,)).fetchone()
            
            if row:
                return TrustMetric(
                    contact_id=row[0],
                    trust_score=row[1],
                    reliability_score=row[2],
                    responsiveness_score=row[3],
                    value_delivered_score=row[4],
                    consistency_score=row[5],
                    last_updated=datetime.fromisoformat(row[6])
                )
        
        return None
    
    def get_contribution_history(self, contact_id: int, limit: int = 50) -> List[ContributionEvent]:
        """Get contribution history for a contact"""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute('''
                SELECT id, contact_id, contribution_type, value_level, description,
                       outcome, impact_score, date_created
                FROM contribution_events 
                WHERE contact_id = ?
                ORDER BY date_created DESC
                LIMIT ?
            ''', (contact_id, limit)).fetchall()
            
            return [ContributionEvent(
                id=row[0],
                contact_id=row[1],
                contribution_type=row[2],
                value_level=row[3],
                description=row[4],
                outcome=row[5],
                impact_score=row[6],
                date_created=datetime.fromisoformat(row[7])
            ) for row in rows]
    
    def get_top_contributors(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top contributors based on total impact score"""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute('''
                SELECT c.id, c.name, c.title, c.company,
                       COALESCE(tm.trust_score, 0.5) as trust_score,
                       COALESCE(SUM(ce.impact_score), 0) as total_contribution,
                       COUNT(ce.id) as contribution_count
                FROM contacts c
                LEFT JOIN trust_metrics tm ON c.id = tm.contact_id
                LEFT JOIN contribution_events ce ON c.id = ce.contact_id
                WHERE c.user_id = ?
                GROUP BY c.id
                ORDER BY total_contribution DESC, trust_score DESC
                LIMIT ?
            ''', (user_id, limit)).fetchall()
            
            return [{
                'contact_id': row[0],
                'name': row[1],
                'title': row[2],
                'company': row[3],
                'trust_score': row[4],
                'total_contribution': row[5],
                'contribution_count': row[6]
            } for row in rows]
    
    def get_trust_insights(self, user_id: int) -> Dict[str, Any]:
        """Get trust and contribution insights for user's network"""
        with sqlite3.connect(self.db_path) as conn:
            # Network trust overview
            trust_overview = conn.execute('''
                SELECT 
                    COUNT(*) as total_contacts,
                    AVG(tm.trust_score) as avg_trust,
                    COUNT(CASE WHEN tm.trust_score >= 0.8 THEN 1 END) as high_trust_count,
                    COUNT(CASE WHEN tm.trust_score >= 0.6 THEN 1 END) as medium_trust_count
                FROM contacts c
                LEFT JOIN trust_metrics tm ON c.id = tm.contact_id
                WHERE c.user_id = ?
            ''', (user_id,)).fetchone()
            
            # Recent contributions
            recent_contributions = conn.execute('''
                SELECT contribution_type, COUNT(*) as count
                FROM contribution_events ce
                JOIN contacts c ON ce.contact_id = c.id
                WHERE c.user_id = ? AND ce.date_created >= datetime('now', '-30 days')
                GROUP BY contribution_type
                ORDER BY count DESC
            ''', (user_id,)).fetchall()
            
            # Trust trends
            trust_trends = conn.execute('''
                SELECT 
                    DATE(th.date_recorded) as date,
                    AVG(th.score_change) as avg_change
                FROM trust_history th
                JOIN contacts c ON th.contact_id = c.id
                WHERE c.user_id = ? AND th.date_recorded >= datetime('now', '-90 days')
                GROUP BY DATE(th.date_recorded)
                ORDER BY date
            ''', (user_id,)).fetchall()
            
            return {
                'trust_overview': {
                    'total_contacts': trust_overview[0] if trust_overview else 0,
                    'avg_trust_score': trust_overview[1] if trust_overview else 0.5,
                    'high_trust_contacts': trust_overview[2] if trust_overview else 0,
                    'medium_trust_contacts': trust_overview[3] if trust_overview else 0
                },
                'recent_contributions': [
                    {'type': row[0], 'count': row[1]} for row in recent_contributions
                ],
                'trust_trends': [
                    {'date': row[0], 'change': row[1]} for row in trust_trends
                ]
            }
    
    def _adjust_trust_score(self, contact_id: int, adjustment: float, reason: str):
        """Directly adjust trust score with reason logging"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE trust_metrics 
                SET trust_score = MIN(1.0, MAX(0.0, trust_score + ?)),
                    last_updated = CURRENT_TIMESTAMP
                WHERE contact_id = ?
            ''', (adjustment, contact_id))
            
            conn.execute('''
                INSERT INTO trust_history (contact_id, event_type, score_change, reason)
                VALUES (?, ?, ?, ?)
            ''', (contact_id, 'manual_adjustment', adjustment, reason))
            
            conn.commit()
    
    def record_interaction_trust_impact(self, contact_id: int, interaction_type: str, 
                                      response_time_hours: Optional[float] = None):
        """Record trust impact from regular interactions"""
        
        # Responsiveness scoring
        if response_time_hours is not None:
            if response_time_hours <= 2:
                responsiveness_boost = 0.02
            elif response_time_hours <= 24:
                responsiveness_boost = 0.01
            elif response_time_hours <= 72:
                responsiveness_boost = 0.0
            else:
                responsiveness_boost = -0.01
                
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE trust_metrics 
                    SET responsiveness_score = MIN(1.0, MAX(0.0, responsiveness_score + ?)),
                        last_updated = CURRENT_TIMESTAMP
                    WHERE contact_id = ?
                ''', (responsiveness_boost, contact_id))
                
                conn.execute('''
                    INSERT INTO trust_history (contact_id, event_type, score_change, reason)
                    VALUES (?, ?, ?, ?)
                ''', (contact_id, 'responsiveness_update', responsiveness_boost, 
                     f"Response time: {response_time_hours:.1f}h"))
                
                conn.commit()
        
        # Consistency scoring (regular interaction)
        consistency_boost = 0.005 if interaction_type in ['email', 'meeting', 'call'] else 0.002
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE trust_metrics 
                SET consistency_score = MIN(1.0, consistency_score + ?),
                    last_updated = CURRENT_TIMESTAMP
                WHERE contact_id = ?
            ''', (consistency_boost, contact_id))
            
            conn.commit()