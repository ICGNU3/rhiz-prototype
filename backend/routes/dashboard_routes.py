"""
Dashboard Routes - Dashboard analytics and overview data
"""
from flask import Blueprint, request, jsonify, session
from backend.models import Contact, Goal, AISuggestion, ContactInteraction
from backend.extensions import db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/analytics', methods=['GET'])
def get_dashboard_analytics():
    """Get dashboard analytics data for React frontend"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Get counts
        contact_count = Contact.query.filter_by(user_id=user_id).count()
        goal_count = Goal.query.filter_by(user_id=user_id).count()
        suggestion_count = AISuggestion.query.filter_by(user_id=user_id, status='pending').count()
        
        # Get recent interactions count
        interaction_count = db.session.query(ContactInteraction).join(
            Contact, ContactInteraction.contact_id == Contact.id
        ).filter(Contact.user_id == user_id).count()
        
        return jsonify({
            'contacts': contact_count,
            'goals': goal_count,
            'ai_suggestions': suggestion_count,
            'interactions': interaction_count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/network', methods=['GET'])
def get_network_graph():
    """Get network graph data"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        contacts = Contact.query.filter_by(user_id=user_id).limit(50).all()
        
        # Create simple network structure
        nodes = []
        edges = []
        
        for contact in contacts:
            nodes.append({
                'id': str(contact.id),
                'label': contact.name,
                'company': contact.company,
                'warmth': contact.warmth_level
            })
        
        return jsonify({
            'nodes': nodes,
            'edges': edges
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500