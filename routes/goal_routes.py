"""
Goal management routes module
Handles goal CRUD operations and AI-powered goal matching
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from . import RouteBase, login_required, get_current_user_id
from database_utils import match_contacts_to_goal
from ai_contact_matcher import AIContactMatcher
import logging

# Create blueprint
goal_bp = Blueprint('goal_routes', __name__)

class GoalRoutes(RouteBase):
    def __init__(self):
        super().__init__()
        self.ai_matcher = AIContactMatcher(self.db)

goal_routes = GoalRoutes()

@goal_bp.route('/goals')
@login_required
def goals():
    """Redirect to new glassmorphism goals page"""
    return redirect('/app/goals')

@goal_bp.route('/goals/create', methods=['GET', 'POST'])
@login_required
def create_goal():
    """Create a new goal with embedding"""
    if request.method == 'POST':
        user_id = get_current_user_id()
        
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'medium')
        deadline = request.form.get('deadline', None)
        
        if not title or not description:
            goal_routes.flash_error('Both title and description are required')
            return render_template('goal_form.html', 
                                 title=title, 
                                 description=description,
                                 priority=priority,
                                 deadline=deadline)
        
        try:
            # Generate embedding for the goal
            embedding = goal_routes.openai_utils.generate_embedding(description)
            
            # Create goal with embedding
            goal_id = goal_routes.goal_model.create(
                user_id=user_id,
                title=title,
                description=description,
                embedding=embedding,
                priority=priority,
                deadline=deadline
            )
            
            if goal_id:
                # Award XP for creating goal
                goal_routes.award_xp('goal_created', 10, {
                    'goal_id': goal_id,
                    'goal_title': title
                })
                
                goal_routes.flash_success('Goal created successfully!')
                
                # Auto-run goal matching
                return redirect(url_for('goal_routes.match_goal', goal_id=goal_id))
            else:
                goal_routes.flash_error('Failed to create goal')
                
        except Exception as e:
            logging.error(f"Failed to create goal: {e}")
            goal_routes.flash_error(f'Error creating goal: {str(e)}')
        
        return render_template('goal_form.html', 
                             title=title, 
                             description=description,
                             priority=priority,
                             deadline=deadline)
    
    # GET request - show form
    return render_template('goal_form.html')

@goal_bp.route('/goals/<goal_id>')
@login_required
def goal_detail(goal_id):
    """Display goal details with AI suggestions"""
    user_id = get_current_user_id()
    
    try:
        goal = goal_routes.goal_model.get_by_id(goal_id)
        
        if not goal or goal['user_id'] != user_id:
            goal_routes.flash_error('Goal not found')
            return redirect(url_for('goal_routes.goals'))
        
        # Get AI suggestions for this goal
        suggestions = goal_routes.ai_suggestion_model.get_by_goal_id(goal_id)
        
        # Get goal progress/metrics
        goal_metrics = {
            'total_suggestions': len(suggestions),
            'contacted_count': len([s for s in suggestions if s.get('status') == 'contacted']),
            'pending_count': len([s for s in suggestions if s.get('status') == 'pending']),
            'success_rate': 0  # Calculate based on interactions
        }
        
        return render_template('goal_detail.html', 
                             goal=goal,
                             suggestions=suggestions,
                             metrics=goal_metrics)
                             
    except Exception as e:
        logging.error(f"Error loading goal detail: {e}")
        goal_routes.flash_error('Failed to load goal details')
        return redirect(url_for('goal_routes.goals'))

@goal_bp.route('/goals/<goal_id>/match')
@login_required
def match_goal(goal_id):
    """Find contacts that match a specific goal"""
    user_id = get_current_user_id()
    
    try:
        goal = goal_routes.goal_model.get_by_id(goal_id)
        
        if not goal or goal['user_id'] != user_id:
            goal_routes.flash_error('Goal not found')
            return redirect(url_for('goal_routes.goals'))
        
        # Use the enhanced goal matching
        matches = match_contacts_to_goal(user_id, goal_id)
        
        if matches:
            # Store AI suggestions in database
            for match in matches:
                goal_routes.ai_suggestion_model.create(
                    user_id=user_id,
                    goal_id=goal_id,
                    contact_id=match['contact']['id'],
                    confidence_score=match['similarity'],
                    suggestion_type='goal_match',
                    message=match['message'],
                    reasoning=match.get('reasoning', '')
                )
            
            # Award XP for goal matching
            goal_routes.award_xp('goal_matched', 5, {
                'goal_id': goal_id,
                'matches_found': len(matches)
            })
            
            goal_routes.flash_success(f'Found {len(matches)} potential matches!')
        else:
            goal_routes.flash_error('No matches found for this goal')
        
        return render_template('goal_matcher.html',
                             goal=goal,
                             matches=matches,
                             show_results=True)
                             
    except Exception as e:
        logging.error(f"Error matching goal: {e}")
        goal_routes.flash_error('Failed to match goal with contacts')
        return redirect(url_for('goal_routes.goal_detail', goal_id=goal_id))

@goal_bp.route('/goals/<goal_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_goal(goal_id):
    """Edit goal information"""
    user_id = get_current_user_id()
    
    try:
        goal = goal_routes.goal_model.get_by_id(goal_id)
        
        if not goal or goal['user_id'] != user_id:
            goal_routes.flash_error('Goal not found')
            return redirect(url_for('goal_routes.goals'))
        
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            priority = request.form.get('priority', 'medium')
            deadline = request.form.get('deadline', None)
            status = request.form.get('status', 'active')
            
            if not title or not description:
                goal_routes.flash_error('Both title and description are required')
                return render_template('goal_form.html', goal=goal, edit_mode=True)
            
            # Check if description changed (need new embedding)
            regenerate_embedding = description != goal['description']
            embedding = None
            
            if regenerate_embedding:
                try:
                    embedding = goal_routes.openai_utils.generate_embedding(description)
                except Exception as e:
                    logging.error(f"Failed to generate embedding: {e}")
                    goal_routes.flash_error('Failed to update goal embedding')
                    return render_template('goal_form.html', goal=goal, edit_mode=True)
            
            success = goal_routes.goal_model.update(
                goal_id=goal_id,
                title=title,
                description=description,
                priority=priority,
                deadline=deadline,
                status=status,
                embedding=embedding
            )
            
            if success:
                goal_routes.flash_success('Goal updated successfully!')
                
                # If description changed, re-match contacts
                if regenerate_embedding:
                    goal_routes.flash_success('Goal updated! Re-matching contacts...')
                    return redirect(url_for('goal_routes.match_goal', goal_id=goal_id))
                
                return redirect(url_for('goal_routes.goal_detail', goal_id=goal_id))
            else:
                goal_routes.flash_error('Failed to update goal')
        
        return render_template('goal_form.html', goal=goal, edit_mode=True)
        
    except Exception as e:
        logging.error(f"Error editing goal: {e}")
        goal_routes.flash_error('Failed to edit goal')
        return redirect(url_for('goal_routes.goals'))

@goal_bp.route('/goals/<goal_id>/delete', methods=['POST'])
@login_required
def delete_goal(goal_id):
    """Delete a goal"""
    user_id = get_current_user_id()
    
    try:
        goal = goal_routes.goal_model.get_by_id(goal_id)
        
        if not goal or goal['user_id'] != user_id:
            return jsonify({'error': 'Goal not found'}), 404
        
        # Delete associated AI suggestions first
        goal_routes.ai_suggestion_model.delete_by_goal_id(goal_id)
        
        # Delete the goal
        success = goal_routes.goal_model.delete(goal_id)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to delete goal'}), 500
            
    except Exception as e:
        logging.error(f"Error deleting goal: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@goal_bp.route('/api/goals/<goal_id>/suggestions')
@login_required
def get_goal_suggestions(goal_id):
    """API endpoint to get AI suggestions for a goal"""
    user_id = get_current_user_id()
    
    try:
        goal = goal_routes.goal_model.get_by_id(goal_id)
        
        if not goal or goal['user_id'] != user_id:
            return jsonify({'error': 'Goal not found'}), 404
        
        suggestions = goal_routes.ai_suggestion_model.get_by_goal_id(goal_id)
        
        # Format suggestions for API response
        formatted_suggestions = []
        for suggestion in suggestions:
            contact = goal_routes.contact_model.get_by_id(suggestion['contact_id'])
            if contact:
                formatted_suggestions.append({
                    'suggestion_id': suggestion['id'],
                    'contact': {
                        'id': contact['id'],
                        'name': contact['name'],
                        'company': contact['company'],
                        'title': contact['title']
                    },
                    'confidence_score': suggestion['confidence_score'],
                    'message': suggestion['message'],
                    'reasoning': suggestion['reasoning'],
                    'status': suggestion.get('status', 'pending')
                })
        
        return jsonify({'suggestions': formatted_suggestions})
        
    except Exception as e:
        logging.error(f"Error getting goal suggestions: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@goal_bp.route('/goal-matcher', methods=['GET', 'POST'])
def goal_matcher():
    """Single-page goal-based contact matcher (legacy route)"""
    user_id = get_current_user_id()
    
    if request.method == 'POST':
        # This is the original goal matcher functionality
        return redirect(url_for('goal_routes.create_goal'))
    
    # GET request - show interface with recent data
    try:
        goals = goal_routes.goal_model.get_all(user_id)[:5]  # Recent 5
        contacts = goal_routes.contact_model.get_all(user_id)[:6]  # Recent 6
        
        return render_template('goal_matcher.html', 
                             goals=goals, 
                             recent_contacts=contacts,
                             show_results=False)
                             
    except Exception as e:
        logging.error(f"Error loading goal matcher: {e}")
        return render_template('goal_matcher.html', 
                             goals=[], 
                             recent_contacts=[],
                             show_results=False)