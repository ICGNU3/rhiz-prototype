from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app
from models import Database, User, Contact, Goal, AISuggestion, ContactInteraction, ContactIntelligence, OutreachSuggestion
from openai_utils import OpenAIUtils
from database_utils import seed_demo_data, match_contacts_to_goal
from contact_intelligence import ContactNLP
import logging

# Initialize database and models
db = Database()
user_model = User(db)
contact_model = Contact(db)
goal_model = Goal(db)
ai_suggestion_model = AISuggestion(db)
interaction_model = ContactInteraction(db)
outreach_suggestion_model = OutreachSuggestion(db)
contact_intelligence = ContactIntelligence(db)
openai_utils = OpenAIUtils()

# Get or create default user
DEFAULT_USER_ID = user_model.get_or_create_default()

# Initialize NLP processor
contact_nlp = ContactNLP(DEFAULT_USER_ID)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Enhanced single-page UI for goal-based contact matching"""
    if request.method == 'POST':
        # Handle goal creation and matching
        goal_title = request.form.get('goal_title', '').strip()
        goal_description = request.form.get('goal_description', '').strip()
        
        if not goal_title or not goal_description:
            flash('Both goal title and description are required', 'error')
            return redirect(url_for('index'))
        
        try:
            # Generate embedding for the goal
            embedding = openai_utils.generate_embedding(goal_description)
            
            # Create goal with embedding
            goal_id = goal_model.create(DEFAULT_USER_ID, goal_title, goal_description, embedding)
            
            if goal_id:
                # Get matched contacts
                matches = match_contacts_to_goal(goal_id)
                
                # Generate AI messages for top matches
                message_data = []
                for contact_id, contact_name, score in matches[:10]:
                    try:
                        # Get contact details
                        contact = contact_model.get_by_id(contact_id)
                        
                        # Generate personalized message
                        from database_utils import load_contact_bio
                        contact_bio = load_contact_bio(contact_id)
                        
                        message = openai_utils.generate_message(
                            contact_name=contact_name,
                            goal_title=goal_title,
                            goal_description=goal_description,
                            contact_bio=contact_bio,
                            tone="warm"
                        )
                        
                        message_data.append({
                            'contact_id': contact_id,
                            'contact_name': contact_name,
                            'contact': contact,
                            'similarity_score': score,
                            'message': message
                        })
                        
                    except Exception as e:
                        logging.error(f"Error generating message for contact {contact_id}: {e}")
                        continue
                
                # Render results page
                return render_template('goal_matcher.html', 
                                     goal_title=goal_title,
                                     goal_description=goal_description,
                                     matches=message_data,
                                     show_results=True)
            else:
                flash('Failed to create goal', 'error')
                
        except Exception as e:
            logging.error(f"Failed to process goal: {e}")
            flash(f'Error processing goal: {str(e)}', 'error')
    
    # GET request - show the main interface
    goals = goal_model.get_all(DEFAULT_USER_ID)
    recent_contacts = contact_model.get_all(DEFAULT_USER_ID)[:6]  # Show recent 6
    
    return render_template('goal_matcher.html', 
                         goals=goals, 
                         recent_contacts=recent_contacts,
                         show_results=False)
    
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

# ============ CRM INTELLIGENCE ROUTES ============

@app.route('/crm')
def crm_dashboard():
    """Enhanced CRM dashboard with intelligence features"""
    # Generate daily suggestions
    contact_intelligence.generate_daily_suggestions(DEFAULT_USER_ID)
    
    # Get data for dashboard
    suggestions = outreach_suggestion_model.get_daily_suggestions(DEFAULT_USER_ID, limit=5)
    follow_ups = contact_model.get_follow_ups_due(DEFAULT_USER_ID, days_ahead=7)
    timeline = interaction_model.get_timeline(DEFAULT_USER_ID, days_back=7)
    pipeline = contact_model.get_pipeline_view(DEFAULT_USER_ID)
    
    # Get contact stats
    all_contacts = contact_model.get_all(DEFAULT_USER_ID)
    high_priority = contact_model.get_by_filters(DEFAULT_USER_ID, priority_level="High")
    
    stats = {
        'total_contacts': len(all_contacts),
        'high_priority': len(high_priority),
        'follow_ups_due': len(follow_ups),
        'suggestions': len(suggestions)
    }
    
    return render_template('crm_dashboard.html', 
                         suggestions=suggestions, 
                         follow_ups=follow_ups, 
                         timeline=timeline,
                         pipeline=pipeline,
                         stats=stats)

@app.route('/crm/pipeline')
def crm_pipeline():
    """Kanban-style pipeline view"""
    pipeline = contact_model.get_pipeline_view(DEFAULT_USER_ID)
    return render_template('crm_pipeline.html', pipeline=pipeline)

@app.route('/crm/timeline')
def crm_timeline():
    """Interaction timeline view"""
    days_back = request.args.get('days', 30, type=int)
    timeline = interaction_model.get_timeline(DEFAULT_USER_ID, days_back)
    return render_template('crm_timeline.html', timeline=timeline, days_back=days_back)

@app.route('/crm/suggestions')
def crm_suggestions():
    """Daily outreach suggestions"""
    contact_intelligence.generate_daily_suggestions(DEFAULT_USER_ID)
    suggestions = outreach_suggestion_model.get_daily_suggestions(DEFAULT_USER_ID)
    return render_template('crm_suggestions.html', suggestions=suggestions)

@app.route('/crm/contact/<contact_id>')
def contact_detail(contact_id):
    """Detailed contact view with intelligence"""
    contact = contact_model.get_by_id(contact_id)
    if not contact:
        flash('Contact not found', 'error')
        return redirect(url_for('contacts'))
    
    interactions = interaction_model.get_by_contact(contact_id)
    summary = contact_intelligence.summarize_contact_history(contact_id)
    
    return render_template('contact_detail.html', 
                         contact=contact, 
                         interactions=interactions,
                         summary=summary)

@app.route('/crm/nlp', methods=['GET', 'POST'])
def crm_nlp():
    """Natural language processing interface"""
    response = None
    
    if request.method == 'POST':
        command = request.form.get('command', '').strip()
        if command:
            try:
                response = contact_nlp.process_command(command)
            except Exception as e:
                logging.error(f"NLP processing error: {e}")
                response = "Sorry, I couldn't process that request. Please try again."
    
    return render_template('crm_nlp.html', response=response)

@app.route('/crm/update_warmth', methods=['POST'])
def update_warmth():
    """Update contact warmth status"""
    contact_id = request.form.get('contact_id')
    warmth_status = request.form.get('warmth_status', type=int)
    warmth_label = request.form.get('warmth_label')
    
    if contact_id and warmth_status and warmth_label:
        contact_model.update_warmth_status(contact_id, warmth_status, warmth_label)
        flash('Contact warmth updated successfully', 'success')
    else:
        flash('Invalid warmth update data', 'error')
    
    return redirect(request.referrer or url_for('crm_dashboard'))

@app.route('/crm/log_interaction', methods=['POST'])
def crm_log_interaction():
    """Enhanced interaction logging"""
    contact_id = request.form.get('contact_id')
    interaction_type = request.form.get('interaction_type', 'Email')
    status = request.form.get('status', 'completed')
    direction = request.form.get('direction', 'outbound')
    subject = request.form.get('subject')
    summary = request.form.get('summary')
    sentiment = request.form.get('sentiment', 'neutral')
    notes = request.form.get('notes')
    follow_up_needed = request.form.get('follow_up_needed') == 'on'
    follow_up_action = request.form.get('follow_up_action')
    follow_up_date = request.form.get('follow_up_date')
    duration_minutes = request.form.get('duration_minutes', type=int)
    
    if contact_id:
        interaction_id = interaction_model.create(
            contact_id=contact_id,
            user_id=DEFAULT_USER_ID,
            interaction_type=interaction_type,
            status=status,
            direction=direction,
            subject=subject,
            summary=summary,
            sentiment=sentiment,
            notes=notes,
            follow_up_needed=follow_up_needed,
            follow_up_action=follow_up_action,
            follow_up_date=follow_up_date,
            duration_minutes=duration_minutes
        )
        
        if interaction_id:
            # Update contact last interaction
            contact_model.update_last_interaction(contact_id, interaction_type)
            flash('Interaction logged successfully', 'success')
        else:
            flash('Failed to log interaction', 'error')
    else:
        flash('Contact ID required', 'error')
    
    return redirect(request.referrer or url_for('crm_dashboard'))

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
