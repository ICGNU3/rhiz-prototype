"""
Trust Analytics Routes Module
Handles comprehensive trust metrics, time, and reciprocity analytics
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import request, jsonify, session
from routes import RouteBase, login_required, get_current_user_id
import psycopg2
from psycopg2.extras import RealDictCursor
import os

class TrustAnalyticsRoutes(RouteBase):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def get_db_connection(self):
        """Get database connection"""
        try:
            conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
            return conn
        except Exception as e:
            self.logger.error(f"Database connection error: {e}")
            return None

    def calculate_trust_metrics(self, user_id: str) -> List[Dict[str, Any]]:
        """Calculate comprehensive trust metrics for all user contacts"""
        conn = self.get_db_connection()
        if not conn:
            return []

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get all contacts with interaction data
                query = """
                    SELECT 
                        c.id as contact_id,
                        c.name as contact_name,
                        c.email as contact_email,
                        c.company as contact_company,
                        c.created_at as relationship_start,
                        c.warmth_level,
                        c.notes,
                        COUNT(ci.id) as total_interactions,
                        MAX(ci.created_at) as last_interaction,
                        AVG(CASE WHEN ci.sentiment = 'positive' THEN 1 
                                 WHEN ci.sentiment = 'neutral' THEN 0.5 
                                 ELSE 0 END) as avg_sentiment,
                        COUNT(CASE WHEN ci.interaction_type = 'outbound' THEN 1 END) as outbound_count,
                        COUNT(CASE WHEN ci.interaction_type = 'inbound' THEN 1 END) as inbound_count
                    FROM contacts c
                    LEFT JOIN contact_interactions ci ON c.id = ci.contact_id
                    WHERE c.user_id = %s
                    GROUP BY c.id, c.name, c.email, c.company, c.created_at, c.warmth_level, c.notes
                    ORDER BY last_interaction DESC NULLS LAST
                """
                
                cur.execute(query, (user_id,))
                contacts_data = cur.fetchall()

                metrics = []
                for contact in contacts_data:
                    # Calculate time metrics
                    relationship_start = contact['relationship_start'] or datetime.now()
                    relationship_duration_days = (datetime.now() - relationship_start).days
                    
                    last_interaction = contact['last_interaction']
                    last_interaction_days_ago = 0
                    if last_interaction:
                        last_interaction_days_ago = (datetime.now() - last_interaction).days
                    else:
                        last_interaction_days_ago = relationship_duration_days

                    # Calculate interaction frequency (interactions per month)
                    interaction_frequency_score = 0
                    if relationship_duration_days > 0:
                        interactions_per_day = contact['total_interactions'] / max(relationship_duration_days, 1)
                        interaction_frequency_score = round(interactions_per_day * 30, 1)

                    # Calculate trust score based on multiple factors
                    trust_score = self.calculate_trust_score(
                        contact['warmth_level'] or 'cold',
                        contact['total_interactions'],
                        last_interaction_days_ago,
                        contact['avg_sentiment'] or 0.5,
                        relationship_duration_days
                    )

                    # Calculate reciprocity metrics
                    outbound = contact['outbound_count'] or 0
                    inbound = contact['inbound_count'] or 0
                    total_interactions = outbound + inbound

                    reciprocity_score = 50  # Default balanced
                    outreach_balance = 0
                    response_rate = 100
                    
                    if total_interactions > 0:
                        # Reciprocity: how balanced are the interactions
                        if total_interactions > 1:
                            balance_ratio = min(outbound, inbound) / max(outbound, inbound) if max(outbound, inbound) > 0 else 0
                            reciprocity_score = int(balance_ratio * 100)
                        
                        # Outreach balance: who initiates more (-100 to 100)
                        if total_interactions > 0:
                            outreach_balance = int(((inbound - outbound) / total_interactions) * 100)
                        
                        # Response rate (simplified)
                        if outbound > 0:
                            response_rate = min(int((inbound / outbound) * 100), 100)

                    # Determine trust tier
                    trust_tier = self.determine_trust_tier(
                        trust_score, 
                        last_interaction_days_ago, 
                        interaction_frequency_score
                    )

                    # Determine trust trend (simplified for now)
                    trust_trend = 'stable'
                    if trust_score > 70:
                        trust_trend = 'increasing'
                    elif trust_score < 40:
                        trust_trend = 'decreasing'

                    # Calculate reliability score based on response patterns
                    reliability_score = min(trust_score + 10, 100)

                    # Mutual value score (simplified)
                    mutual_value_score = int((trust_score + reciprocity_score) / 2)

                    # Get recent interactions summary
                    recent_interactions = self.get_recent_interactions(cur, contact['contact_id'], 5)

                    metric = {
                        'contact_id': contact['contact_id'],
                        'contact_name': contact['contact_name'],
                        'contact_email': contact['contact_email'],
                        'contact_company': contact['contact_company'],
                        
                        # Time metrics
                        'relationship_duration_days': relationship_duration_days,
                        'last_interaction_days_ago': last_interaction_days_ago,
                        'interaction_frequency_score': interaction_frequency_score,
                        
                        # Trust metrics
                        'trust_score': trust_score,
                        'trust_trend': trust_trend,
                        'trust_tier': trust_tier,
                        'reliability_score': reliability_score,
                        
                        # Reciprocity metrics
                        'reciprocity_score': reciprocity_score,
                        'outreach_balance': outreach_balance,
                        'response_rate': response_rate,
                        'mutual_value_score': mutual_value_score,
                        
                        # Interaction data
                        'total_interactions': contact['total_interactions'],
                        'recent_interactions': recent_interactions
                    }
                    
                    metrics.append(metric)

                return metrics

        except Exception as e:
            self.logger.error(f"Error calculating trust metrics: {e}")
            return []
        finally:
            conn.close()

    def calculate_trust_score(self, warmth_level: str, total_interactions: int, 
                            days_since_last: int, avg_sentiment: float, 
                            relationship_duration: int) -> int:
        """Calculate trust score based on multiple factors"""
        
        # Base score from warmth level
        warmth_scores = {
            'hot': 80,
            'warm': 60,
            'cool': 40,
            'cold': 20
        }
        base_score = warmth_scores.get(warmth_level, 30)
        
        # Interaction frequency bonus (0-20 points)
        interaction_bonus = min(total_interactions * 2, 20)
        
        # Recency penalty (0-30 points deduction)
        if days_since_last <= 7:
            recency_penalty = 0
        elif days_since_last <= 30:
            recency_penalty = 10
        elif days_since_last <= 90:
            recency_penalty = 20
        else:
            recency_penalty = 30
        
        # Sentiment bonus (0-15 points)
        sentiment_bonus = int((avg_sentiment - 0.5) * 30)
        
        # Duration bonus for long relationships (0-10 points)
        duration_bonus = min(relationship_duration // 365, 5) * 2
        
        trust_score = base_score + interaction_bonus - recency_penalty + sentiment_bonus + duration_bonus
        return max(0, min(100, trust_score))

    def determine_trust_tier(self, trust_score: int, days_since_last: int, 
                           frequency_score: float) -> str:
        """Determine trust tier based on score and activity"""
        
        if trust_score >= 75 and days_since_last <= 30:
            return 'rooted'
        elif trust_score >= 50 and days_since_last <= 60:
            return 'growing'
        elif trust_score >= 30 or days_since_last <= 180:
            return 'dormant'
        else:
            return 'frayed'

    def get_recent_interactions(self, cur, contact_id: str, limit: int = 5) -> List[Dict]:
        """Get recent interactions for a contact"""
        try:
            query = """
                SELECT 
                    created_at,
                    interaction_type,
                    channel,
                    sentiment,
                    notes
                FROM contact_interactions 
                WHERE contact_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """
            cur.execute(query, (contact_id, limit))
            interactions = cur.fetchall()
            
            return [
                {
                    'date': interaction['created_at'].isoformat() if interaction['created_at'] else '',
                    'type': 'outbound' if interaction['interaction_type'] == 'outbound' else 'inbound',
                    'channel': interaction['channel'] or 'other',
                    'sentiment_score': 1 if interaction['sentiment'] == 'positive' else 0.5 if interaction['sentiment'] == 'neutral' else 0
                }
                for interaction in interactions
            ]
        except Exception as e:
            self.logger.error(f"Error getting recent interactions: {e}")
            return []

    def calculate_trust_overview(self, user_id: str) -> Dict[str, Any]:
        """Calculate overall trust analytics overview"""
        conn = self.get_db_connection()
        if not conn:
            return {}

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get total relationships count
                cur.execute("SELECT COUNT(*) as total FROM contacts WHERE user_id = %s", (user_id,))
                total_relationships = cur.fetchone()['total']

                # Calculate metrics for all contacts
                metrics = self.calculate_trust_metrics(user_id)
                
                if not metrics:
                    return {
                        'total_relationships': 0,
                        'avg_trust_score': 0,
                        'avg_reciprocity_score': 0,
                        'relationships_by_tier': {'rooted': 0, 'growing': 0, 'dormant': 0, 'frayed': 0},
                        'trust_trend_summary': {'improving': 0, 'stable': 0, 'declining': 0}
                    }

                # Calculate averages
                avg_trust_score = sum(m['trust_score'] for m in metrics) / len(metrics)
                avg_reciprocity_score = sum(m['reciprocity_score'] for m in metrics) / len(metrics)

                # Group by trust tiers
                relationships_by_tier = {'rooted': 0, 'growing': 0, 'dormant': 0, 'frayed': 0}
                for metric in metrics:
                    tier = metric['trust_tier']
                    if tier in relationships_by_tier:
                        relationships_by_tier[tier] += 1

                # Group by trust trends
                trust_trend_summary = {'improving': 0, 'stable': 0, 'declining': 0}
                for metric in metrics:
                    trend = metric['trust_trend']
                    if trend in trust_trend_summary:
                        trust_trend_summary[trend] += 1

                return {
                    'total_relationships': total_relationships,
                    'avg_trust_score': round(avg_trust_score, 1),
                    'avg_reciprocity_score': round(avg_reciprocity_score, 1),
                    'relationships_by_tier': relationships_by_tier,
                    'trust_trend_summary': trust_trend_summary
                }

        except Exception as e:
            self.logger.error(f"Error calculating trust overview: {e}")
            return {}
        finally:
            conn.close()


# Route definitions
trust_analytics_routes = TrustAnalyticsRoutes()


@login_required
def get_trust_metrics():
    """Get comprehensive trust metrics for all contacts"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401

        metrics = trust_analytics_routes.calculate_trust_metrics(user_id)
        
        return jsonify({
            'success': True,
            'metrics': metrics,
            'count': len(metrics)
        })

    except Exception as e:
        logging.error(f"Error in get_trust_metrics: {e}")
        return jsonify({'error': 'Failed to get trust metrics'}), 500


@login_required
def get_trust_overview():
    """Get trust analytics overview"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401

        overview = trust_analytics_routes.calculate_trust_overview(user_id)
        
        return jsonify({
            'success': True,
            **overview
        })

    except Exception as e:
        logging.error(f"Error in get_trust_overview: {e}")
        return jsonify({'error': 'Failed to get trust overview'}), 500


@login_required
def get_contact_trust_history(contact_id: str):
    """Get trust history for a specific contact"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401

        # Verify contact belongs to user
        conn = trust_analytics_routes.get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id FROM contacts WHERE id = %s AND user_id = %s", 
                    (contact_id, user_id)
                )
                if not cur.fetchone():
                    return jsonify({'error': 'Contact not found'}), 404

                # Get interaction history
                cur.execute("""
                    SELECT 
                        created_at,
                        interaction_type,
                        channel,
                        sentiment,
                        notes
                    FROM contact_interactions 
                    WHERE contact_id = %s 
                    ORDER BY created_at DESC
                """, (contact_id,))
                
                interactions = cur.fetchall()
                
                history = [
                    {
                        'date': interaction['created_at'].isoformat() if interaction['created_at'] else '',
                        'type': interaction['interaction_type'],
                        'channel': interaction['channel'],
                        'sentiment': interaction['sentiment'],
                        'notes': interaction['notes']
                    }
                    for interaction in interactions
                ]

                return jsonify({
                    'success': True,
                    'contact_id': contact_id,
                    'history': history
                })

        finally:
            conn.close()

    except Exception as e:
        logging.error(f"Error in get_contact_trust_history: {e}")
        return jsonify({'error': 'Failed to get contact history'}), 500


@login_required
def update_trust_score():
    """Update trust score for a contact"""
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({'error': 'User not authenticated'}), 401

        data = request.get_json()
        contact_id = data.get('contact_id')
        score = data.get('score')

        if not contact_id or score is None:
            return jsonify({'error': 'Missing contact_id or score'}), 400

        if not (0 <= score <= 100):
            return jsonify({'error': 'Score must be between 0 and 100'}), 400

        # For now, we'll update the warmth_level based on score
        warmth_mapping = {
            (80, 100): 'hot',
            (60, 79): 'warm',
            (40, 59): 'cool',
            (0, 39): 'cold'
        }

        warmth_level = 'cold'
        for (min_score, max_score), level in warmth_mapping.items():
            if min_score <= score <= max_score:
                warmth_level = level
                break

        conn = trust_analytics_routes.get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        try:
            with conn.cursor() as cur:
                # Verify contact belongs to user and update
                cur.execute("""
                    UPDATE contacts 
                    SET warmth_level = %s 
                    WHERE id = %s AND user_id = %s
                """, (warmth_level, contact_id, user_id))
                
                if cur.rowcount == 0:
                    return jsonify({'error': 'Contact not found'}), 404

                conn.commit()

                return jsonify({
                    'success': True,
                    'message': 'Trust score updated',
                    'new_warmth_level': warmth_level
                })

        finally:
            conn.close()

    except Exception as e:
        logging.error(f"Error in update_trust_score: {e}")
        return jsonify({'error': 'Failed to update trust score'}), 500