from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app
from models import Database, User, Contact, Goal, AISuggestion, ContactInteraction
from openai_utils import OpenAIUtils
from database_utils import seed_demo_data, match_contacts_to_goal
import logging

# Initialize database and models
db = Database()
user_model = User(db)
contact_model = Contact(db)
goal_model = Goal(db)
ai_suggestion_model = AISuggestion(db)
interaction_model = ContactInteraction(db)
openai_utils = OpenAIUtils()

# Get or create default user
DEFAULT_USER_ID = user_model.get_or_create_default()

@app.route('/')
def index():
    """Main dashboard showing goals and recent contacts"""
    goals = goal_model.get_all(DEFAULT_USER_ID)
    contacts = contact_model.get_all(DEFAULT_USER_ID)
    
    # If no data exists, seed demo data
    if not goals and not contacts:
        seed_demo_data(DEFAULT_USER_ID)
        goals = goal_model.get_all(DEFAULT_USER_ID)
        contacts = contact_model.get_all(DEFAULT_USER_ID)
    
    return render_template('index.html', goals=goals[:5], contacts=contacts[:5])

@app.route('/goals')
def goals():
    """Display all goals"""
    all_goals = goal_model.get_all(DEFAULT_USER_ID)
    return render_template('goals.html', goals=all_goals)

@app.route('/contacts')
def contacts():
    """Display all contacts"""
    all_contacts = contact_model.get_all(DEFAULT_USER_ID)
    return render_template('contacts.html', contacts=all_contacts)

@app.route('/create_goal', methods=['GET', 'POST'])
def create_goal():
    """Create a new goal with embedding"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        
        if not title or not description:
            flash('Both title and description are required', 'error')
            return redirect(url_for('goals'))
        
        try:
            # Generate embedding for the goal
            embedding = openai_utils.generate_embedding(description)
            
            # Create goal with embedding
            goal_id = goal_model.create(DEFAULT_USER_ID, title, description, embedding)
            
            if goal_id:
                flash('Goal created successfully!', 'success')
                return redirect(url_for('match_goal', goal_id=goal_id))
            else:
                flash('Failed to create goal', 'error')
        except Exception as e:
            logging.error(f"Failed to create goal: {e}")
            flash(f'Error creating goal: {str(e)}', 'error')
    
    return redirect(url_for('goals'))

@app.route('/create_contact', methods=['POST'])
def create_contact():
    """Create a new contact"""
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    twitter = request.form.get('twitter', '').strip()
    linkedin = request.form.get('linkedin', '').strip()
    notes = request.form.get('notes', '').strip()
    tags = request.form.get('tags', '').strip()
    
    if not name:
        flash('Contact name is required', 'error')
        return redirect(url_for('contacts'))
    
    contact_id = contact_model.create(
        DEFAULT_USER_ID, name, email, phone, twitter, linkedin, notes, tags
    )
    
    if contact_id:
        flash('Contact created successfully!', 'success')
    else:
        flash('Failed to create contact', 'error')
    
    return redirect(url_for('contacts'))

@app.route('/match_goal/<goal_id>')
def match_goal(goal_id):
    """Match contacts to a specific goal and generate suggestions"""
    goal = goal_model.get_by_id(goal_id)
    if not goal:
        flash('Goal not found', 'error')
        return redirect(url_for('goals'))
    
    try:
        # Get contact matches
        matches = match_contacts_to_goal(goal_id)
        
        # Generate AI suggestions for top matches
        suggestions = []
        for contact_id, contact_name, score in matches[:10]:
            contact = contact_model.get_by_id(contact_id)
            if contact:
                try:
                    message = openai_utils.generate_outreach_message(
                        contact_name=contact['name'],
                        goal_title=goal['title'],
                        goal_description=goal['description'],
                        contact_notes=contact.get('notes', ''),
                        tone="warm"
                    )
                    
                    # Save AI suggestion
                    ai_suggestion_model.create(contact_id, goal_id, message, score)
                    
                    suggestions.append({
                        'contact': contact,
                        'score': score,
                        'message': message
                    })
                except Exception as e:
                    logging.error(f"Failed to generate message for contact {contact_id}: {e}")
                    suggestions.append({
                        'contact': contact,
                        'score': score,
                        'message': f"Error generating message: {str(e)}"
                    })
        
        return render_template('results.html', goal=goal, suggestions=suggestions)
    
    except Exception as e:
        logging.error(f"Failed to match goal {goal_id}: {e}")
        flash(f'Error matching contacts: {str(e)}', 'error')
        return redirect(url_for('goals'))

@app.route('/log_interaction', methods=['POST'])
def log_interaction():
    """Log interaction outcome for a contact"""
    contact_id = request.form.get('contact_id')
    status = request.form.get('status')
    notes = request.form.get('notes', '').strip()
    
    if not contact_id or not status:
        flash('Contact ID and status are required', 'error')
        return redirect(request.referrer or url_for('index'))
    
    interaction_id = interaction_model.create(contact_id, DEFAULT_USER_ID, status, notes)
    
    if interaction_id:
        # Update last interaction timestamp
        contact_model.update_last_interaction(contact_id)
        flash('Interaction logged successfully!', 'success')
    else:
        flash('Failed to log interaction', 'error')
    
    return redirect(request.referrer or url_for('index'))

@app.route('/api/copy_message', methods=['POST'])
def copy_message():
    """API endpoint to handle message copying (returns success response)"""
    return jsonify({'status': 'success', 'message': 'Message copied to clipboard'})

@app.errorhandler(404)
def not_found(error):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html'), 500
