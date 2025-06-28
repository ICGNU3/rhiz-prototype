"""
Goal Routes - Goal management and AI matching
"""
from flask import Blueprint, request, jsonify, session
from backend.models import Goal
from backend.extensions import db

goal_bp = Blueprint('goal', __name__)


@goal_bp.route('', methods=['GET'])
def get_goals():
    """Get all goals for the current user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        goals = Goal.query.filter_by(user_id=user_id).all()
        return jsonify([goal.to_dict() for goal in goals])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@goal_bp.route('', methods=['POST'])
def create_goal():
    """Create a new goal"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    if not data or not data.get('title'):
        return jsonify({'error': 'Title is required'}), 400
    
    try:
        goal = Goal(
            user_id=user_id,
            title=data['title'],
            description=data.get('description'),
            category=data.get('category'),
            priority=data.get('priority', 'medium')
        )
        
        db.session.add(goal)
        db.session.commit()
        
        return jsonify(goal.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500