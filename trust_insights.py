"""
Trust Insights Engine for Rhiz
Provides intelligent, real-time indicators of trust, reciprocity, and relational health
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import statistics
from collections import defaultdict
import openai
import os

@dataclass
class TrustSignal:
    """Represents a trust signal data point"""
    contact_id: int
    signal_type: str  # 'response_time', 'interaction_frequency', 'reciprocity', 'sentiment'
    value: float
    timestamp: str
    context: Optional[Dict] = None

@dataclass
class TrustInsight:
    """Represents a trust insight for a contact"""
    contact_id: int
    trust_tier: str  # 'rooted', 'growing', 'dormant', 'frayed'
    trust_score: float  # Private score (0-1)
    reciprocity_index: float  # Measure of mutual interaction
    response_time_avg: float  # Average response time in hours
    interaction_frequency: float  # Interactions per week
    last_interaction: str
    trust_summary: str  # AI-generated summary
    suggested_actions: List[str]
    trust_signals: List[TrustSignal]
    updated_at: str

class TrustInsightsEngine:
    """Main engine for generating trust insights"""
    
    def __init__(self, db_path: str = 'db.sqlite3'):
        self.db_path = db_path
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Trust tier thresholds
        self.trust_thresholds = {
            'rooted': 0.8,      # High trust, frequent reciprocity
            'growing': 0.6,     # Promising, recent positive interactions
            'dormant': 0.4,     # Needs reconnection
            'frayed': 0.0       # Low response, unreciprocated actions
        }
        
    def get_db(self):
        """Get database connection"""
        db = sqlite3.connect(self.db_path)
        db.row_factory = sqlite3.Row
        return db
    
    def init_trust_tables(self):
        """Initialize trust insights tables"""
        db = self.get_db()
        
        # Trust signals table
        db.execute('''
            CREATE TABLE IF NOT EXISTS trust_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER,
                signal_type TEXT NOT NULL,
                value REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                context TEXT,
                FOREIGN KEY (contact_id) REFERENCES contacts (id)
            )
        ''')
        
        # Trust insights table
        db.execute('''
            CREATE TABLE IF NOT EXISTS trust_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER UNIQUE,
                trust_tier TEXT DEFAULT 'dormant',
                trust_score REAL DEFAULT 0.5,
                reciprocity_index REAL DEFAULT 0.5,
                response_time_avg REAL DEFAULT 24.0,
                interaction_frequency REAL DEFAULT 0.0,
                last_interaction DATETIME,
                trust_summary TEXT,
                suggested_actions TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contact_id) REFERENCES contacts (id)
            )
        ''')
        
        # Trust timeline table for historical tracking
        db.execute('''
            CREATE TABLE IF NOT EXISTS trust_timeline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER,
                event_type TEXT NOT NULL,
                event_data TEXT,
                trust_score_change REAL DEFAULT 0.0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (contact_id) REFERENCES contacts (id)
            )
        ''')
        
        # User trust health table
        db.execute('''
            CREATE TABLE IF NOT EXISTS user_trust_health (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                health_score REAL DEFAULT 0.5,
                insights_summary TEXT,
                behavioral_patterns TEXT,
                recommendations TEXT,
                generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Add trust columns to contacts table if they don't exist
        try:
            db.execute('ALTER TABLE contacts ADD COLUMN trust_tier TEXT DEFAULT "dormant"')
            db.execute('ALTER TABLE contacts ADD COLUMN reciprocity_index REAL DEFAULT 0.5')
            db.execute('ALTER TABLE contacts ADD COLUMN last_trust_update DATETIME')
        except sqlite3.OperationalError:
            # Columns already exist
            pass
        
        db.commit()
        db.close()
    
    def record_trust_signal(self, contact_id: int, signal_type: str, value: float, context: Dict = None):
        """Record a trust signal for analysis"""
        db = self.get_db()
        
        db.execute(
            '''INSERT INTO trust_signals (contact_id, signal_type, value, context)
               VALUES (?, ?, ?, ?)''',
            (contact_id, signal_type, value, json.dumps(context) if context else None)
        )
        
        db.commit()
        db.close()
        
        # Trigger trust insight update
        self._update_contact_trust_insight(contact_id)
    
    def calculate_response_time_signal(self, contact_id: int) -> float:
        """Calculate average response time signal"""
        db = self.get_db()
        
        # Get recent interactions with response times
        interactions = db.execute(
            '''SELECT timestamp, interaction_type, notes 
               FROM contact_interactions 
               WHERE contact_id = ? 
               AND timestamp > datetime('now', '-90 days')
               ORDER BY timestamp DESC''',
            (contact_id,)
        ).fetchall()
        
        response_times = []
        for i in range(len(interactions) - 1):
            current = datetime.fromisoformat(interactions[i]['timestamp'])
            previous = datetime.fromisoformat(interactions[i+1]['timestamp'])
            
            # Calculate time difference in hours
            time_diff = (current - previous).total_seconds() / 3600
            if time_diff < 168:  # Less than a week
                response_times.append(time_diff)
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            # Normalize to 0-1 scale (faster response = higher trust)
            normalized_score = max(0, 1 - (avg_response_time / 48))  # 48 hours baseline
            return min(1, normalized_score)
        
        return 0.5  # Default neutral score
    
    def calculate_interaction_frequency_signal(self, contact_id: int) -> float:
        """Calculate interaction frequency signal"""
        db = self.get_db()
        
        # Count interactions in last 30 days
        recent_count = db.execute(
            '''SELECT COUNT(*) as count 
               FROM contact_interactions 
               WHERE contact_id = ? 
               AND timestamp > datetime('now', '-30 days')''',
            (contact_id,)
        ).fetchone()['count']
        
        # Normalize frequency (1+ interactions per week = high)
        frequency_score = min(1.0, recent_count / 4.0)
        return frequency_score
    
    def calculate_reciprocity_signal(self, contact_id: int) -> float:
        """Calculate reciprocity index based on mutual interactions"""
        db = self.get_db()
        
        # Get interaction types and directions
        interactions = db.execute(
            '''SELECT interaction_type, notes
               FROM contact_interactions
               WHERE contact_id = ?
               AND timestamp > datetime('now', '-90 days')''',
            (contact_id,)
        ).fetchall()
        
        if not interactions:
            return 0.5
        
        # Categorize interactions as initiated vs received
        initiated_count = 0
        received_count = 0
        
        for interaction in interactions:
            interaction_type = interaction['interaction_type']
            notes = interaction['notes'] or ''
            
            # Simple heuristic for determining direction
            if interaction_type in ['call_outgoing', 'email_sent', 'message_sent'] or \
               'reached out' in notes.lower() or 'contacted' in notes.lower():
                initiated_count += 1
            elif interaction_type in ['call_incoming', 'email_received', 'message_received'] or \
                 'responded' in notes.lower() or 'replied' in notes.lower():
                received_count += 1
            else:
                # Neutral interactions (meetings, etc.)
                initiated_count += 0.5
                received_count += 0.5
        
        total_directional = initiated_count + received_count
        if total_directional == 0:
            return 0.5
        
        # Calculate reciprocity (balanced is 0.5, more receiving is higher)
        reciprocity = received_count / total_directional
        return reciprocity
    
    def calculate_sentiment_signal(self, contact_id: int) -> float:
        """Calculate sentiment signal from interaction notes"""
        db = self.get_db()
        
        # Get recent interaction notes
        interactions = db.execute(
            '''SELECT notes
               FROM contact_interactions
               WHERE contact_id = ?
               AND notes IS NOT NULL
               AND timestamp > datetime('now', '-60 days')
               ORDER BY timestamp DESC
               LIMIT 10''',
            (contact_id,)
        ).fetchall()
        
        if not interactions:
            return 0.5
        
        # Combine notes for analysis
        all_notes = ' '.join([i['notes'] for i in interactions if i['notes']])
        
        if not all_notes.strip():
            return 0.5
        
        try:
            # Use OpenAI to analyze sentiment
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze the sentiment of these interaction notes and return a trust sentiment score between 0 and 1, where 1 indicates very positive/trusting interactions and 0 indicates negative/concerning interactions. Return only a number."
                    },
                    {
                        "role": "user",
                        "content": all_notes
                    }
                ],
                max_tokens=10
            )
            
            sentiment_score = float(response.choices[0].message.content.strip())
            return max(0, min(1, sentiment_score))
            
        except Exception as e:
            logging.warning(f"Sentiment analysis failed: {e}")
            return 0.5
    
    def _update_contact_trust_insight(self, contact_id: int):
        """Update trust insight for a specific contact"""
        db = self.get_db()
        
        # Calculate all trust signals
        response_time_signal = self.calculate_response_time_signal(contact_id)
        frequency_signal = self.calculate_interaction_frequency_signal(contact_id)
        reciprocity_signal = self.calculate_reciprocity_signal(contact_id)
        sentiment_signal = self.calculate_sentiment_signal(contact_id)
        
        # Record signals
        self.record_trust_signal(contact_id, 'response_time', response_time_signal)
        self.record_trust_signal(contact_id, 'interaction_frequency', frequency_signal)
        self.record_trust_signal(contact_id, 'reciprocity', reciprocity_signal)
        self.record_trust_signal(contact_id, 'sentiment', sentiment_signal)
        
        # Calculate composite trust score
        trust_score = (
            response_time_signal * 0.25 +
            frequency_signal * 0.25 +
            reciprocity_signal * 0.25 +
            sentiment_signal * 0.25
        )
        
        # Determine trust tier
        trust_tier = self._calculate_trust_tier(trust_score, frequency_signal)
        
        # Get last interaction
        last_interaction = db.execute(
            '''SELECT timestamp FROM contact_interactions
               WHERE contact_id = ?
               ORDER BY timestamp DESC
               LIMIT 1''',
            (contact_id,)
        ).fetchone()
        
        last_interaction_date = last_interaction['timestamp'] if last_interaction else None
        
        # Generate AI summary and suggestions
        trust_summary = self._generate_trust_summary(contact_id, trust_score, trust_tier)
        suggested_actions = self._generate_suggested_actions(contact_id, trust_tier, last_interaction_date)
        
        # Update or insert trust insight
        db.execute(
            '''INSERT OR REPLACE INTO trust_insights 
               (contact_id, trust_tier, trust_score, reciprocity_index, 
                response_time_avg, interaction_frequency, last_interaction,
                trust_summary, suggested_actions, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                contact_id, trust_tier, trust_score, reciprocity_signal,
                24.0 / max(0.1, response_time_signal), frequency_signal * 4,  # Convert to weekly
                last_interaction_date, trust_summary,
                json.dumps(suggested_actions), datetime.now().isoformat()
            )
        )
        
        # Update contact table
        db.execute(
            '''UPDATE contacts 
               SET trust_tier = ?, reciprocity_index = ?, last_trust_update = ?
               WHERE id = ?''',
            (trust_tier, reciprocity_signal, datetime.now().isoformat(), contact_id)
        )
        
        db.commit()
        db.close()
    
    def _calculate_trust_tier(self, trust_score: float, frequency_signal: float) -> str:
        """Calculate trust tier based on score and frequency"""
        # Adjust thresholds based on interaction frequency
        if frequency_signal > 0.5:  # High frequency interactions
            if trust_score >= self.trust_thresholds['rooted']:
                return 'rooted'
            elif trust_score >= self.trust_thresholds['growing']:
                return 'growing'
            else:
                return 'dormant'
        else:  # Low frequency
            if trust_score >= 0.7:
                return 'growing'
            elif trust_score >= 0.4:
                return 'dormant'
            else:
                return 'frayed'
    
    def _generate_trust_summary(self, contact_id: int, trust_score: float, trust_tier: str) -> str:
        """Generate AI-powered trust summary"""
        db = self.get_db()
        
        # Get contact and recent interaction data
        contact = db.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,)).fetchone()
        
        recent_interactions = db.execute(
            '''SELECT interaction_type, notes, timestamp
               FROM contact_interactions
               WHERE contact_id = ?
               ORDER BY timestamp DESC
               LIMIT 5''',
            (contact_id,)
        ).fetchall()
        
        if not contact:
            return "Unable to generate summary"
        
        # Build context for AI
        context_data = {
            'contact_name': contact['name'],
            'trust_score': trust_score,
            'trust_tier': trust_tier,
            'recent_interactions': [dict(i) for i in recent_interactions]
        }
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "Generate a brief, insightful trust summary for this contact relationship. Focus on patterns, reciprocity, and relationship health. Keep it under 100 words and personable."
                    },
                    {
                        "role": "user",
                        "content": f"Contact: {contact['name']}\nTrust Tier: {trust_tier}\nTrust Score: {trust_score:.2f}\nRecent interactions: {json.dumps(context_data['recent_interactions'], indent=2)}"
                    }
                ],
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.warning(f"Trust summary generation failed: {e}")
            return f"Trust level: {trust_tier}. Trust score: {trust_score:.1f}/1.0"
    
    def _generate_suggested_actions(self, contact_id: int, trust_tier: str, last_interaction: str) -> List[str]:
        """Generate suggested actions based on trust tier and interaction history"""
        suggestions = []
        
        # Calculate days since last interaction
        days_since_last = 999
        if last_interaction:
            last_date = datetime.fromisoformat(last_interaction.replace('Z', '+00:00'))
            days_since_last = (datetime.now() - last_date).days
        
        if trust_tier == 'rooted':
            if days_since_last > 30:
                suggestions.append("Send a check-in message")
            suggestions.append("Share an opportunity or introduction")
            suggestions.append("Schedule a catch-up call")
            
        elif trust_tier == 'growing':
            suggestions.append("Follow up on recent conversation")
            suggestions.append("Share relevant article or resource")
            suggestions.append("Propose a collaboration")
            
        elif trust_tier == 'dormant':
            suggestions.append("Send a thoughtful reconnection message")
            suggestions.append("Share a memory or past collaboration")
            suggestions.append("Invite to relevant event")
            
        elif trust_tier == 'frayed':
            if days_since_last < 30:
                suggestions.append("Give them space, follow up later")
            suggestions.append("Send a brief, low-pressure message")
            suggestions.append("Reflect on relationship dynamics")
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    def get_trust_insights_for_user(self, user_id: int) -> List[TrustInsight]:
        """Get all trust insights for a user"""
        db = self.get_db()
        
        insights = db.execute(
            '''SELECT ti.*, c.name as contact_name
               FROM trust_insights ti
               JOIN contacts c ON ti.contact_id = c.id
               WHERE c.user_id = ?
               ORDER BY ti.trust_score DESC''',
            (user_id,)
        ).fetchall()
        
        trust_insights = []
        for insight in insights:
            # Get recent trust signals
            signals = db.execute(
                '''SELECT * FROM trust_signals
                   WHERE contact_id = ?
                   ORDER BY timestamp DESC
                   LIMIT 10''',
                (insight['contact_id'],)
            ).fetchall()
            
            trust_insight = TrustInsight(
                contact_id=insight['contact_id'],
                trust_tier=insight['trust_tier'],
                trust_score=insight['trust_score'],
                reciprocity_index=insight['reciprocity_index'],
                response_time_avg=insight['response_time_avg'],
                interaction_frequency=insight['interaction_frequency'],
                last_interaction=insight['last_interaction'],
                trust_summary=insight['trust_summary'],
                suggested_actions=json.loads(insight['suggested_actions']) if insight['suggested_actions'] else [],
                trust_signals=[TrustSignal(
                    contact_id=s['contact_id'],
                    signal_type=s['signal_type'],
                    value=s['value'],
                    timestamp=s['timestamp'],
                    context=json.loads(s['context']) if s['context'] else None
                ) for s in signals],
                updated_at=insight['updated_at']
            )
            trust_insights.append(trust_insight)
        
        db.close()
        return trust_insights
    
    def generate_user_trust_health(self, user_id: int) -> Dict[str, Any]:
        """Generate comprehensive trust health analysis for user"""
        db = self.get_db()
        
        # Get user's trust insights
        insights = self.get_trust_insights_for_user(user_id)
        
        if not insights:
            return {
                'health_score': 0.5,
                'insights_summary': 'No trust data available yet',
                'behavioral_patterns': [],
                'recommendations': ['Start logging interactions to build trust insights']
            }
        
        # Calculate overall health metrics
        avg_trust_score = statistics.mean([i.trust_score for i in insights])
        trust_tier_distribution = defaultdict(int)
        reciprocity_scores = []
        
        for insight in insights:
            trust_tier_distribution[insight.trust_tier] += 1
            reciprocity_scores.append(insight.reciprocity_index)
        
        avg_reciprocity = statistics.mean(reciprocity_scores)
        
        # Analyze patterns
        behavioral_patterns = []
        recommendations = []
        
        # Check for concerning patterns
        frayed_count = trust_tier_distribution.get('frayed', 0)
        dormant_count = trust_tier_distribution.get('dormant', 0)
        
        if frayed_count > len(insights) * 0.2:
            behavioral_patterns.append("High number of strained relationships")
            recommendations.append("Review communication patterns with frayed contacts")
        
        if dormant_count > len(insights) * 0.4:
            behavioral_patterns.append("Many dormant connections")
            recommendations.append("Schedule regular check-ins with dormant contacts")
        
        if avg_reciprocity < 0.3:
            behavioral_patterns.append("Low reciprocity in relationships")
            recommendations.append("Focus on responding more to others' outreach")
        elif avg_reciprocity > 0.7:
            behavioral_patterns.append("Others often reach out first")
            recommendations.append("Take more initiative in reaching out")
        
        # Generate AI insights summary
        health_summary = self._generate_health_summary(
            avg_trust_score, trust_tier_distribution, avg_reciprocity, behavioral_patterns
        )
        
        health_data = {
            'health_score': avg_trust_score,
            'insights_summary': health_summary,
            'behavioral_patterns': behavioral_patterns,
            'recommendations': recommendations,
            'trust_tier_distribution': dict(trust_tier_distribution),
            'avg_reciprocity': avg_reciprocity
        }
        
        # Store health data
        db.execute(
            '''INSERT OR REPLACE INTO user_trust_health
               (user_id, health_score, insights_summary, behavioral_patterns, recommendations)
               VALUES (?, ?, ?, ?, ?)''',
            (
                user_id, avg_trust_score, health_summary,
                json.dumps(behavioral_patterns), json.dumps(recommendations)
            )
        )
        
        db.commit()
        db.close()
        
        return health_data
    
    def _generate_health_summary(self, avg_trust: float, tier_dist: Dict, avg_reciprocity: float, patterns: List[str]) -> str:
        """Generate AI-powered health summary"""
        try:
            context = f"""
            Average Trust Score: {avg_trust:.2f}
            Trust Distribution: {dict(tier_dist)}
            Average Reciprocity: {avg_reciprocity:.2f}
            Behavioral Patterns: {patterns}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "Generate a brief, constructive summary of this person's relationship health patterns. Be encouraging but honest. Keep under 150 words."
                    },
                    {"role": "user", "content": context}
                ],
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.warning(f"Health summary generation failed: {e}")
            return f"Overall trust health: {avg_trust:.1f}/1.0. Focus on strengthening {len(patterns)} identified patterns."
    
    def update_all_trust_insights(self, user_id: int):
        """Update trust insights for all contacts of a user"""
        db = self.get_db()
        
        contacts = db.execute(
            'SELECT id FROM contacts WHERE user_id = ?',
            (user_id,)
        ).fetchall()
        
        for contact in contacts:
            self._update_contact_trust_insight(contact['id'])
        
        db.close()
        logging.info(f"Updated trust insights for {len(contacts)} contacts")