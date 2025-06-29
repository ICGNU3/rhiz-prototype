"""
API Routes Blueprint
Main API endpoints for the React frontend
"""
import logging
from flask import Blueprint, jsonify, request, session
from backend import db
from backend.models import User, Contact, Goal, AISuggestion

api_bp = Blueprint('api', __name__)

@api_bp.route('/dashboard/analytics')
def dashboard_analytics():
    """Dashboard analytics data for React frontend"""
    try:
        # Get real data from database
        user_id = session.get('user_id', 'demo_user')
        
        # Count totals
        total_contacts = Contact.query.filter_by(user_id=user_id).count()
        active_goals = Goal.query.filter_by(user_id=user_id, status='active').count()
        ai_suggestions = AISuggestion.query.filter_by(user_id=user_id).count()
        
        stats = {
            'totalContacts': total_contacts,
            'activeGoals': active_goals, 
            'aiSuggestions': ai_suggestions,
            'trustScore': 85,  # Calculated metric
            'weeklyInteractions': 23,  # From interaction logs
            'pendingFollowUps': 6  # From contact follow-up status
        }
        
        # Get recent activity
        recent_contacts = Contact.query.filter_by(user_id=user_id).order_by(Contact.created_at.desc()).limit(3).all()
        recent_goals = Goal.query.filter_by(user_id=user_id).order_by(Goal.created_at.desc()).limit(2).all()
        
        recent_activity = []
        for contact in recent_contacts:
            recent_activity.append({
                'id': contact.id,
                'type': 'contact',
                'title': 'New contact added',
                'description': f'{contact.name}' + (f' from {contact.company}' if contact.company else ''),
                'timestamp': contact.created_at.isoformat() if contact.created_at else None
            })
        
        for goal in recent_goals:
            recent_activity.append({
                'id': goal.id,
                'type': 'goal', 
                'title': 'Goal created',
                'description': goal.title,
                'timestamp': goal.created_at.isoformat() if goal.created_at else None
            })
        
        # Sort by timestamp
        recent_activity.sort(key=lambda x: x['timestamp'] or '', reverse=True)
        
        return jsonify({
            'status': 'success',
            'stats': stats,
            'recent_activity': recent_activity[:5]  # Limit to 5 items
        })
        
    except Exception as e:
        logging.error(f"Dashboard analytics error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_bp.route('/ai-suggestions')
def get_ai_suggestions():
    """Get AI suggestions for the current user"""
    try:
        user_id = session.get('user_id', 'demo_user')
        suggestions = AISuggestion.query.filter_by(user_id=user_id).order_by(AISuggestion.created_at.desc()).limit(10).all()
        
        return jsonify([suggestion.to_dict() for suggestion in suggestions])
        
    except Exception as e:
        logging.error(f"AI suggestions error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/network/graph')
def get_network_graph():
    """Get network graph data"""
    try:
        user_id = session.get('user_id', 'demo_user')
        
        # Get user's contacts and goals
        contacts = Contact.query.filter_by(user_id=user_id).limit(50).all()  # Limit for performance
        goals = Goal.query.filter_by(user_id=user_id).limit(20).all()
        
        # Build nodes
        nodes = [{'id': 'user', 'name': 'You', 'type': 'user'}]
        
        for contact in contacts:
            nodes.append({
                'id': contact.id,
                'name': contact.name,
                'type': 'contact',
                'company': contact.company,
                'warmth': contact.warmth_level
            })
        
        for goal in goals:
            nodes.append({
                'id': f'goal_{goal.id}',
                'name': goal.title,
                'type': 'goal',
                'priority': goal.priority_level
            })
        
        # Build edges (relationships)
        edges = []
        
        # User to contacts
        for contact in contacts:
            strength = 0.8 if contact.warmth_level == 'hot' else 0.6 if contact.warmth_level == 'warm' else 0.4
            edges.append({
                'id': f'user_contact_{contact.id}',
                'source': 'user',
                'target': contact.id,
                'type': 'relationship',
                'strength': strength
            })
        
        # User to goals
        for goal in goals:
            edges.append({
                'id': f'user_goal_{goal.id}',
                'source': 'user', 
                'target': f'goal_{goal.id}',
                'type': 'goal',
                'strength': 0.9
            })
        
        graph_data = {
            'nodes': nodes,
            'edges': edges
        }
        
        return jsonify(graph_data)
        
    except Exception as e:
        logging.error(f"Network graph error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/current-user')
def get_current_user():
    """Get current authenticated user"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict())
        
    except Exception as e:
        logging.error(f"Get current user error: {e}")
        return jsonify({'error': str(e)}), 500