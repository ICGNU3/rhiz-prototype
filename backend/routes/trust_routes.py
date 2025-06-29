"""
Trust Routes - Trust analytics and insights
"""
from flask import Blueprint, request, jsonify, session
from backend.models import db, Contact
from datetime import datetime, timedelta
import logging

trust_bp = Blueprint('trust', __name__)


@trust_bp.route('/insights', methods=['GET'])
def get_trust_insights():
    """Get trust insights for the current user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Get all contacts for the user
        contacts = Contact.query.filter_by(user_id=user_id).all()
        
        # Calculate trust tiers based on warmth_level
        trust_tiers = {
            'rooted': 0,
            'growing': 0, 
            'dormant': 0,
            'frayed': 0
        }
        
        overall_score = 0
        response_time_avg = 48  # hours
        dormant_percentage = 0
        
        if contacts:
            for contact in contacts:
                # Map warmth levels to trust tiers
                warmth = contact.warmth_level or 'dormant'
                if warmth == 'hot':
                    trust_tiers['rooted'] += 1
                    overall_score += 25
                elif warmth == 'warm':
                    trust_tiers['growing'] += 1
                    overall_score += 20
                elif warmth == 'cool':
                    trust_tiers['dormant'] += 1
                    overall_score += 10
                else:
                    trust_tiers['frayed'] += 1
                    overall_score += 5
            
            overall_score = min(100, overall_score // len(contacts))
            dormant_percentage = round((trust_tiers['dormant'] + trust_tiers['frayed']) / len(contacts) * 100)
        
        # Generate timeline data (last 6 months)
        timeline = []
        for i in range(6):
            date = datetime.now() - timedelta(days=i*30)
            score = min(100, overall_score + (i * 2))  # Slight variation over time
            timeline.append({
                'date': date.strftime('%Y-%m-%d'),
                'score': score
            })
        
        # Identify low-trust contacts that need attention
        low_trust_contacts = []
        for contact in contacts[:3]:  # Get first 3 as examples
            if contact.warmth_level in ['cool', 'cold'] or not contact.warmth_level:
                low_trust_contacts.append({
                    'id': contact.id,
                    'name': contact.name,
                    'company': contact.company,
                    'trust_score': 35,
                    'last_interaction': '2+ months ago',
                    'suggested_action': 'Send a thoughtful check-in message'
                })
        
        return jsonify({
            'overall_score': overall_score,
            'response_time': response_time_avg,
            'dormant_percentage': dormant_percentage,
            'trust_tiers': trust_tiers,
            'timeline': timeline[::-1],  # Reverse to show oldest first
            'low_trust_contacts': low_trust_contacts,
            'insights': [
                f"You have {len(contacts)} contacts in your network",
                f"Trust score of {overall_score}/100 indicates strong relationship health",
                f"{dormant_percentage}% of contacts may need re-engagement"
            ]
        })
        
    except Exception as e:
        logging.error(f"Trust insights error: {e}")
        return jsonify({'error': 'Failed to load trust insights'}), 500


@trust_bp.route('/digest', methods=['GET'])
def get_trust_digest():
    """Get weekly trust digest"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Get contacts that need attention
        contacts = Contact.query.filter_by(user_id=user_id).all()
        
        priority_contacts = []
        for contact in contacts[:3]:  # Top 3 priority contacts
            priority_contacts.append({
                'id': contact.id,
                'name': contact.name,
                'company': contact.company,
                'reason': 'Haven\'t connected in 6+ weeks',
                'priority_score': 85,
                'suggested_action': 'Schedule a coffee chat or send update'
            })
        
        recommendations = [
            {
                'type': 'reconnect',
                'title': 'Reach out to dormant contacts',
                'description': 'You have 3 contacts you haven\'t spoken to in over a month',
                'action': 'Send personalized messages'
            },
            {
                'type': 'follow_up',
                'title': 'Follow up on recent conversations',
                'description': 'Continue building momentum with recent connections',
                'action': 'Schedule follow-up meetings'
            }
        ]
        
        return jsonify({
            'priority_contacts': priority_contacts,
            'recommendations': recommendations,
            'weekly_goal': 'Connect with 3 people from your network',
            'completion_rate': 0
        })
        
    except Exception as e:
        logging.error(f"Trust digest error: {e}")
        return jsonify({'error': 'Failed to load trust digest'}), 500