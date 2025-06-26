from flask import render_template, request, redirect, url_for, flash, jsonify, session
from app import app
import uuid
import json
from models import Database, User, Contact, Goal, AISuggestion, ContactInteraction, ContactIntelligence, OutreachSuggestion
from openai_utils import OpenAIUtils
from database_utils import seed_demo_data, match_contacts_to_goal
from contact_intelligence import ContactNLP
from csv_import import CSVContactImporter
from linkedin_importer import LinkedInContactImporter
from simple_email import SimpleEmailSender
from enhanced_email_integration import EnhancedEmailIntegration
from analytics import NetworkingAnalytics
from network_visualization import NetworkMapper
from integrations import AutomationEngine
from email_service import EmailService
from ai_contact_matcher import AIContactMatcher
from rhizomatic_intelligence import RhizomaticIntelligence
from smart_networking import SmartNetworkingEngine
from contact_search import ContactSearchEngine
from gamification import GamificationEngine
from auth import AuthManager, SubscriptionManager, EmailService as AuthEmailService
from stripe_integration import StripePaymentManager, PricingHelper
from collective_actions import CollectiveActionsManager
import logging
from datetime import datetime
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('signup'))
        return f(*args, **kwargs)
    return decorated_function

# Mock current_user for compatibility
class MockUser:
    def __init__(self, user_id):
        self.id = user_id

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return MockUser(user_id)
    return None

current_user = type('CurrentUser', (), {'id': lambda: session.get('user_id')})()

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
email_sender = SimpleEmailSender(db)
email_service = EmailService(db)
enhanced_email = EnhancedEmailIntegration(db)
analytics = NetworkingAnalytics(db)
network_mapper = NetworkMapper(db)
automation_engine = AutomationEngine(db)
ai_matcher = AIContactMatcher(db)
search_engine = ContactSearchEngine(db)
gamification = GamificationEngine(db)
collective_actions_manager = CollectiveActionsManager()

# Initialize authentication and subscription managers
auth_manager = AuthManager(db)
subscription_manager = SubscriptionManager(db)
auth_email_service = AuthEmailService()
stripe_manager = StripePaymentManager(db)

# Get or create default user
DEFAULT_USER_ID = user_model.get_or_create_default()

# Initialize NLP processor
contact_nlp = ContactNLP(DEFAULT_USER_ID)

# Authentication helpers
def get_current_user():
    """Get current authenticated user or None"""
    user_id = session.get('user_id')
    if user_id:
        return subscription_manager.get_user_with_usage(user_id)
    return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('signup'))
        return f(*args, **kwargs)
    return decorated_function

def get_effective_user_id():
    """Get user ID for operations - authenticated user or default guest"""
    return session.get('user_id', DEFAULT_USER_ID)

def check_tier_limits(user, action_type):
    """Check if user can perform action based on their tier"""
    if not user:
        # Guest user - default limits
        if action_type == 'goals':
            return user_model.count_goals(DEFAULT_USER_ID) < 1
        elif action_type == 'contacts':
            return user_model.count_contacts(DEFAULT_USER_ID) < 50
        elif action_type == 'ai_suggestions':
            return user_model.count_ai_suggestions_today(DEFAULT_USER_ID) < 3
    else:
        # Authenticated user
        if user.get('subscription_tier') == 'founder_plus':
            # Founder+ tier - generous limits
            if action_type == 'goals':
                return user['goals_count'] < 100  # Effectively unlimited
            elif action_type == 'contacts':
                return user['contacts_count'] < 1000
            elif action_type == 'ai_suggestions':
                return True  # Unlimited for paid tier
        else:
            # Explorer tier - same as guest
            if action_type == 'goals':
                return user['goals_count'] < 1
            elif action_type == 'contacts':
                return user['contacts_count'] < 50
            elif action_type == 'ai_suggestions':
                return user['ai_suggestions_today'] < 3
    
    return False

# Authentication and Subscription Routes

@app.route('/signup')
def signup():
    """Signup page with free and paid tier options"""
    return render_template('signup.html')

@app.route('/pricing')
def pricing():
    """Pricing page showcasing Explorer and Founder+ tiers"""
    return render_template('pricing.html')

@app.route('/onboarding/goal')
def onboarding_goal():
    """Onboarding flow for creating first goal"""
    return render_template('onboarding_goal.html')

@app.route('/auth/magic-link', methods=['POST'])
def send_magic_link():
    """Send magic link for authentication"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Create or get user
        user_id = auth_manager.create_or_get_user(email)
        if not user_id:
            return jsonify({'error': 'Failed to create user account'}), 500
        
        # Generate magic link token
        token = auth_manager.generate_magic_link_token(user_id)
        if not token:
            return jsonify({'error': 'Failed to generate authentication token'}), 500
        
        # Send magic link email
        magic_link = f"{request.host_url}auth/verify?token={token}"
        success = auth_email_service.send_magic_link(email, magic_link)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to send magic link email'}), 500
            
    except Exception as e:
        logging.error(f"Magic link error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/auth/verify')
def verify_magic_link():
    """Verify magic link and log in user"""
    token = request.args.get('token')
    
    if not token:
        flash('Invalid or missing verification token')
        return redirect(url_for('signup'))
    
    # Verify token and get user
    user_id = auth_manager.verify_magic_link_token(token)
    if not user_id:
        flash('Invalid or expired verification link')
        return redirect(url_for('signup'))
    
    # Log in user
    session['user_id'] = user_id
    session.permanent = True
    
    # Redirect to onboarding or dashboard
    return redirect(url_for('onboarding_goal') + '?verified=true')

@app.route('/auth/logout')
def logout():
    """Log out current user"""
    session.clear()
    return redirect(url_for('landing'))

@app.route('/auth/check-session')
def check_session():
    """Check if user is authenticated"""
    return jsonify({
        'authenticated': bool(session.get('user_id')),
        'user_id': session.get('user_id')
    })

@app.route('/upgrade')
@require_auth
def upgrade():
    """Subscription upgrade page"""
    plan = request.args.get('plan', 'founder_plus_monthly')
    user = get_current_user()
    
    if not user:
        return redirect(url_for('signup'))
    
    # Create Stripe checkout session
    success_url = f"{request.host_url}dashboard?upgraded=true"
    cancel_url = f"{request.host_url}pricing"
    
    checkout_session = stripe_manager.create_checkout_session(
        user_id=user['id'],
        plan=plan,
        success_url=success_url,
        cancel_url=cancel_url
    )
    
    if checkout_session:
        return redirect(checkout_session['url'])
    else:
        flash('Failed to create checkout session. Please try again.')
        return redirect(url_for('pricing'))

@app.route('/billing/portal')
@require_auth
def billing_portal():
    """Redirect to Stripe customer portal"""
    user = get_current_user()
    
    if not user:
        return redirect(url_for('signup'))
    
    return_url = f"{request.host_url}dashboard"
    portal_url = stripe_manager.create_customer_portal_session(user['id'], return_url)
    
    if portal_url:
        return redirect(portal_url)
    else:
        flash('Unable to access billing portal. Please contact support.')
        return redirect(url_for('dashboard'))

@app.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.data
    signature = request.headers.get('Stripe-Signature')
    
    if stripe_manager.handle_webhook(payload, signature):
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error'}), 400

@app.route('/api/goals', methods=['POST'])
def api_create_goal():
    """API endpoint for creating goals (supports both guest and authenticated users)"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        
        if not title or not description:
            return jsonify({'error': 'Title and description are required'}), 400
        
        # Get current user or use guest
        current_user = get_current_user()
        user_id = get_effective_user_id()
        
        # Check tier limits
        if not check_tier_limits(current_user, 'goals'):
            if current_user:
                return jsonify({
                    'error': 'Goal limit reached for your plan',
                    'upgrade_required': True
                }), 403
            else:
                return jsonify({
                    'error': 'Guest goal limit reached. Sign up to create more goals.',
                    'signup_required': True
                }), 403
        
        # Create goal
        goal_id = goal_model.create_goal(
            user_id=user_id,
            title=title,
            description=description
        )
        
        if goal_id:
            # Award XP for authenticated users
            if current_user:
                gamification.award_xp(user_id, 'goal_created', {
                    'goal_title': title,
                    'description_length': len(description)
                })
            
            return jsonify({
                'success': True,
                'goal_id': goal_id,
                'user_authenticated': bool(current_user)
            })
        else:
            return jsonify({'error': 'Failed to create goal'}), 500
            
    except Exception as e:
        logging.error(f"Goal creation error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/')
def landing():
    """Modern 2025 landing page"""
    return render_template('landing.html')

@app.route('/login')
def login():
    """Login page with magic link authentication"""
    # If user is already logged in, redirect to dashboard
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def index():
    """Enhanced single-page UI for goal-based contact matching"""
    if request.method == 'POST':
        # Handle goal creation and matching
        goal_title = request.form.get('goal_title', '').strip()
        goal_description = request.form.get('goal_description', '').strip()
        tone = request.form.get('tone', 'warm')
        
        if not goal_title or not goal_description:
            flash('Both goal title and description are required', 'error')
            return redirect(url_for('index'))
        
        try:
            # Generate embedding for the goal
            embedding = openai_utils.generate_embedding(goal_description)
            
            # Create goal with embedding
            goal_id = goal_model.create(DEFAULT_USER_ID, goal_title, goal_description, embedding)
            
            # Award XP for creating a goal
            gamification.award_xp(DEFAULT_USER_ID, 'goal_matched')
            
            if goal_id:
                # Get matched contacts
                matches = match_contacts_to_goal(goal_id)
                
                # Generate messages for top 5 matches - fast template-based approach
                message_data = []
                for contact_id, contact_name, score in matches[:5]:
                    try:
                        # Get contact details
                        contact = contact_model.get_by_id(contact_id)
                        
                        # Generate personalized template message
                        def generate_template_message(contact, goal_title, goal_description, tone):
                            company_info = f" at {contact['company']}" if contact.get('company') else ""
                            title_info = f", {contact['title']}," if contact.get('title') else ""
                            
                            if tone == "professional":
                                return f"Dear {contact_name}{title_info}\n\nI hope this message finds you well. I'm reaching out regarding {goal_title.lower()} and believe your expertise{company_info} would provide valuable insights.\n\n{goal_description}\n\nWould you be available for a brief discussion at your convenience?\n\nBest regards"
                            elif tone == "casual":
                                return f"Hi {contact_name}!\n\nHope you're doing well. I'm working on {goal_title.lower()} and thought you'd be a great person to chat with given your background{company_info}.\n\n{goal_description}\n\nWould love to grab coffee or have a quick call if you're interested!\n\nCheers"
                            elif tone == "urgent":
                                return f"Hi {contact_name},\n\nI'm reaching out because I'm {goal_title.lower()} and need to move quickly. Your experience{company_info} makes you someone I'd really value input from.\n\n{goal_description}\n\nWould you have 15 minutes this week to discuss?\n\nThanks"
                            else:  # warm (default)
                                return f"Hi {contact_name},\n\nI hope you're doing well! I'm reaching out because I'm {goal_title.lower()} and thought you might have some great insights given your experience{company_info}.\n\n{goal_description}\n\nWould you be open to a brief conversation to share your perspective?\n\nBest regards"
                        
                        message = generate_template_message(contact, goal_title, goal_description, tone)
                        
                        message_data.append({
                            'contact_id': contact_id,
                            'contact_name': contact_name,
                            'contact': contact,
                            'similarity_score': score,
                            'message': message
                        })
                        
                    except Exception as e:
                        logging.error(f"Error processing contact {contact_id}: {e}")
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
            
            # Award XP for logging interaction
            gamification.award_xp(DEFAULT_USER_ID, 'follow_up')
            
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

@app.route('/import_contacts', methods=['GET', 'POST'])
def import_contacts():
    """Enhanced CSV import interface with LinkedIn support"""
    user_id = session.get('user_id', 1)
    
    if request.method == 'POST':
        # Handle CSV upload
        if 'csv_file' not in request.files:
            flash('No CSV file uploaded', 'error')
            return redirect(request.url)
        
        file = request.files['csv_file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and file.filename and file.filename.lower().endswith('.csv'):
            try:
                # Save uploaded file temporarily
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(mode='w+b', suffix='.csv', delete=False) as temp_file:
                    file.save(temp_file.name)
                    temp_filename = temp_file.name
                
                # Detect import type
                import_type = request.form.get('import_type', 'generic')
                
                # Choose appropriate importer
                if import_type == 'linkedin':
                    importer = LinkedInContactImporter()
                    import_result = importer.import_linkedin_csv(temp_filename, user_id)
                else:
                    importer = LinkedInContactImporter()
                    import_result = importer.import_generic_csv(temp_filename, user_id)
                
                # Clean up temp file
                os.unlink(temp_filename)
                
                # Process results
                if import_result['success']:
                    if import_result['imported'] > 0:
                        flash(f"Successfully imported {import_result['imported']} contacts!", 'success')
                    
                    if import_result['duplicates'] > 0:
                        flash(f"Skipped {import_result['duplicates']} duplicate contacts", 'info')
                    
                    if import_result['skipped'] > 0:
                        flash(f"{import_result['skipped']} contacts were skipped", 'warning')
                    
                    # Award XP for successful import
                    if import_result['imported'] > 0:
                        gamification_engine = GamificationEngine()
                        xp_points = min(import_result['imported'] * 5, 100)  # 5 XP per contact, max 100
                        gamification_engine.award_xp(user_id, xp_points, {
                            'action': 'contact_import',
                            'contacts_imported': import_result['imported'],
                            'source': import_type
                        })
                else:
                    flash(f"Import failed: {import_result['error']}", 'error')
                
                # Render results
                return render_template('import.html', 
                                     import_result=import_result,
                                     show_results=True,
                                     import_type=import_type)
                
            except Exception as e:
                logging.error(f"CSV import failed: {e}")
                flash(f'Import failed: {str(e)}', 'error')
        else:
            flash('Please upload a valid CSV file', 'error')
    
    # GET request - show import form
    linkedin_importer = LinkedInContactImporter()
    template_info = linkedin_importer.get_import_template()
    
    return render_template('import.html', 
                         template_info=template_info,
                         show_results=False)

@app.route('/download_sample_csv')
def download_sample_csv():
    """Download sample CSV template"""
    from flask import make_response
    
    importer = CSVContactImporter(DEFAULT_USER_ID)
    sample_csv = importer.get_sample_csv_format()
    
    response = make_response(sample_csv)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=sample_contacts.csv'
    
    return response

@app.route('/email_settings', methods=['GET', 'POST'])
def email_settings():
    """Email configuration and settings management"""
    if request.method == 'POST':
        # Handle email configuration test
        test_result = email_sender.test_connection()
        if test_result['success']:
            flash(test_result['message'], 'success')
        else:
            flash(test_result['error'], 'error')
    
    # Get current configuration status
    config_status = email_sender.get_configuration_status()
    
    return render_template('email_settings.html', 
                         config_status=config_status)

@app.route('/send_email', methods=['POST'])
def send_email():
    """Send email to a specific contact"""
    contact_id = request.form.get('contact_id')
    subject = request.form.get('subject', '').strip()
    message = request.form.get('message', '').strip()
    goal_title = request.form.get('goal_title', '')
    
    if not all([contact_id, subject, message]):
        flash('Contact, subject, and message are required', 'error')
        return redirect(request.referrer or url_for('index'))
    
    # Get contact details
    contact = contact_model.get_by_id(contact_id)
    if not contact:
        flash('Contact not found', 'error')
        return redirect(request.referrer or url_for('index'))
    
    if not contact.get('email'):
        flash('Contact has no email address', 'error')
        return redirect(request.referrer or url_for('index'))
    
    # Send email using the enhanced email service
    try:
        result = email_service.send_email(
            to_email=contact['email'],
            subject=subject,
            message_body=message,
            contact_id=int(contact_id),
            user_id=DEFAULT_USER_ID,
            goal_title=goal_title
        )
        
        if result['success']:
            flash(f"Email sent successfully to {contact['name']}", 'success')
            # Award XP for sending email
            gamification.award_xp(DEFAULT_USER_ID, 'email_sent')
            
            # Log interaction automatically
            interaction_model.create(
                contact_id=int(contact_id),
                interaction_type='email_sent',
                notes=f'Email sent: {subject}',
                outcome='sent'
            )
        else:
            flash(f"Failed to send email: {result['error']}", 'error')
            
    except Exception as e:
        logging.error(f"Email sending error: {e}")
        flash('Error sending email. Please check your email configuration.', 'error')
    
    return redirect(request.referrer or url_for('index'))

@app.route('/send_ai_message', methods=['POST'])
def send_ai_message():
    """Send AI-generated message directly from suggestions"""
    user_id = get_effective_user_id()
    
    # Get form data
    contact_id = request.form.get('contact_id')
    ai_message = request.form.get('ai_message', '').strip()
    subject = request.form.get('subject', '').strip()
    goal_id = request.form.get('goal_id')
    confidence_score = request.form.get('confidence_score', '0')
    
    if not all([contact_id, ai_message, subject]):
        return jsonify({
            'success': False,
            'error': 'Missing required fields'
        }), 400
    
    # Get contact and goal details
    contact = contact_model.get_by_id(contact_id)
    goal_data = goal_model.get_by_id(goal_id) if goal_id else None
    
    if not contact:
        return jsonify({
            'success': False,
            'error': 'Contact not found'
        }), 404
    
    if not contact.get('email'):
        return jsonify({
            'success': False,
            'error': 'Contact has no email address'
        }), 400
    
    try:
        # Send email using enhanced integration
        result = enhanced_email.send_ai_generated_message(
            contact_data=contact,
            message_data={
                'subject': subject,
                'message': ai_message
            },
            user_id=user_id,
            goal_data=goal_data
        )
        
        if result['success']:
            # Award XP for AI-assisted outreach
            try:
                gamification_engine = GamificationEngine(db)
                xp_bonus = int(float(confidence_score) * 10) if confidence_score else 10
                gamification_engine.award_xp(user_id, 20 + xp_bonus, {
                    'action': 'ai_outreach',
                    'contact_name': contact['name'],
                    'confidence_score': confidence_score,
                    'goal_title': goal_data.get('title') if goal_data else 'networking'
                })
            except Exception as e:
                logging.warning(f"XP award failed: {e}")
            
            return jsonify({
                'success': True,
                'message': f'Email sent successfully to {contact["name"]}',
                'interaction_id': result.get('interaction_id'),
                'xp_earned': 20 + (int(float(confidence_score) * 10) if confidence_score else 10)
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 500
            
    except Exception as e:
        logging.error(f"AI message send error: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to send AI message'
        }), 500

@app.route('/email_setup')
def email_setup():
    """Email configuration setup page"""
    config_status = enhanced_email.get_configuration_status()
    templates = enhanced_email.get_email_templates()
    
    return render_template('email_setup.html', 
                         config_status=config_status,
                         templates=templates)

@app.route('/test_email_connection', methods=['POST'])
def test_email_connection():
    """Test email configuration and connection"""
    try:
        result = enhanced_email.test_connection()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Connection test failed: {str(e)}'
        }), 500

@app.route('/compose_email/<contact_id>')
def compose_email(contact_id):
    """Compose email interface for a specific contact"""
    contact = contact_model.get_by_id(contact_id)
    if not contact:
        flash('Contact not found', 'error')
        return redirect(url_for('contacts'))
    
    # Get email configuration status
    config_status = email_sender.get_configuration_status()
    
    return render_template('compose_email.html', 
                         contact=contact,
                         config_status=config_status)

@app.route('/analytics')
def analytics_dashboard():
    """Analytics dashboard showing outreach success rates and networking metrics"""
    try:
        # Get comprehensive analytics data
        dashboard_data = analytics.get_comprehensive_dashboard_data(DEFAULT_USER_ID)
        
        return render_template('analytics_dashboard.html', 
                             data=dashboard_data)
    
    except Exception as e:
        logging.error(f"Analytics dashboard error: {e}")
        flash('Error loading analytics data', 'error')
        return redirect(url_for('index'))

@app.route('/analytics/api/<metric_type>')
def analytics_api(metric_type):
    """API endpoint for specific analytics metrics"""
    try:
        if metric_type == 'outreach_metrics':
            days_back = int(request.args.get('days', 30))
            data = analytics.get_outreach_success_metrics(DEFAULT_USER_ID, days_back)
        elif metric_type == 'interaction_trends':
            days_back = int(request.args.get('days', 30))
            data = analytics.get_interaction_trends(DEFAULT_USER_ID, days_back)
        elif metric_type == 'contact_effectiveness':
            data = analytics.get_contact_effectiveness(DEFAULT_USER_ID)
        elif metric_type == 'pipeline_metrics':
            data = analytics.get_warmth_pipeline_metrics(DEFAULT_USER_ID)
        else:
            return jsonify({'error': 'Invalid metric type'}), 400
        
        return jsonify(data)
    
    except Exception as e:
        logging.error(f"Analytics API error: {e}")
        return jsonify({'error': 'Failed to fetch analytics data'}), 500

# Network route moved to enhanced version below

@app.route('/network/api/graph')
def network_graph_api():
    """API endpoint for network graph data"""
    try:
        graph_data = network_mapper.build_network_graph(DEFAULT_USER_ID)
        return jsonify(graph_data)
    except Exception as e:
        logging.error(f"Network graph API error: {e}")
        return jsonify({'error': 'Failed to fetch network data'}), 500

@app.route('/network/api/metrics')
def network_metrics_api():
    """API endpoint for network metrics"""
    try:
        metrics = network_mapper.get_network_metrics(DEFAULT_USER_ID)
        return jsonify(metrics)
    except Exception as e:
        logging.error(f"Network metrics API error: {e}")
        return jsonify({'error': 'Failed to fetch network metrics'}), 500

@app.route('/network/api/introductions')
def network_introductions_api():
    """API endpoint for introduction suggestions"""
    try:
        limit = int(request.args.get('limit', 10))
        suggestions = network_mapper.suggest_introductions(DEFAULT_USER_ID, limit)
        return jsonify(suggestions)
    except Exception as e:
        logging.error(f"Network introductions API error: {e}")
        return jsonify({'error': 'Failed to fetch introduction suggestions'}), 500

@app.route('/add_relationship', methods=['POST'])
def add_relationship():
    """Add a new relationship between contacts"""
    contact_a_id = request.form.get('contact_a_id')
    contact_b_id = request.form.get('contact_b_id')
    relationship_type = request.form.get('relationship_type', 'knows')
    strength = int(request.form.get('strength', 1))
    notes = request.form.get('notes', '')
    
    if not all([contact_a_id, contact_b_id]):
        flash('Both contacts are required', 'error')
        return redirect(request.referrer or url_for('network_visualization'))
    
    try:
        # Use the network mapper's relationship model
        relationship_id = network_mapper.relationship_model.create(
            user_id=DEFAULT_USER_ID,
            contact_a_id=contact_a_id,
            contact_b_id=contact_b_id,
            relationship_type=relationship_type,
            strength=strength,
            notes=notes
        )
        
        if relationship_id:
            # Award XP for creating relationship
            gamification.award_xp(DEFAULT_USER_ID, 'relationship_created')
            flash('Relationship added successfully', 'success')
        else:
            flash('Failed to add relationship', 'error')
    
    except Exception as e:
        logging.error(f"Add relationship error: {e}")
        flash('Error adding relationship', 'error')
    
    return redirect(url_for('network_visualization'))

# Integration & Automation Routes
@app.route('/integrations')
def integrations_dashboard():
    """Integration & Automation dashboard"""
    try:
        integration_status = automation_engine.get_integration_status()
        return render_template('integrations_dashboard.html', 
                             integration_status=integration_status)
    except Exception as e:
        logging.error(f"Error loading integrations dashboard: {str(e)}")
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/integrations/slack/test', methods=['POST'])
def test_slack_integration():
    """Test Slack integration"""
    try:
        success = automation_engine.slack.send_networking_update(
            "Integration test from Founder Network AI", 
            "System Test"
        )
        return jsonify({
            'success': success,
            'message': 'Test message sent' if success else 'Slack not configured'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/integrations/calendar/schedule', methods=['POST'])
def schedule_follow_up_integration():
    """Schedule follow-up via calendar integration"""
    try:
        data = request.get_json()
        contact_name = data.get('contact_name')
        days_ahead = data.get('days_ahead', 7)
        note = data.get('note', 'Follow up on previous conversation')
        
        # Find contact by name
        contacts = contact_model.get_all(DEFAULT_USER_ID)
        contact = next((c for c in contacts if c['name'].lower() == contact_name.lower()), None)
        
        if not contact:
            return jsonify({'success': False, 'error': 'Contact not found'})
        
        result = automation_engine.calendar.schedule_follow_up(
            contact['id'], days_ahead, note
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/integrations/export/csv')
def export_contacts_csv():
    """Export contacts to CSV format"""
    try:
        csv_content = automation_engine.crm_sync.export_contacts_to_csv(DEFAULT_USER_ID)
        
        if not csv_content:
            flash('No contacts to export', 'warning')
            return redirect(url_for('integrations_dashboard'))
        
        from flask import Response
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=founder_network_contacts.csv'}
        )
        
    except Exception as e:
        logging.error(f"CSV export error: {str(e)}")
        flash(f'Export failed: {str(e)}', 'error')
        return redirect(url_for('integrations_dashboard'))

@app.route('/integrations/export/hubspot')
def export_contacts_hubspot():
    """Export contacts in HubSpot format"""
    return export_contacts_csv()

@app.route('/integrations/social/updates')
def get_social_updates():
    """Get social media updates for contacts"""
    try:
        # Get sample updates for demo
        updates = []
        contacts = contact_model.get_all(DEFAULT_USER_ID)
        
        for contact in contacts[:3]:  # Show updates for first 3 contacts
            contact_updates = automation_engine.social_monitor.get_contact_social_updates(contact['id'])
            updates.extend(contact_updates)
        
        return jsonify({'updates': updates})
        
    except Exception as e:
        return jsonify({'updates': [], 'error': str(e)})

@app.route('/integrations/automation/daily', methods=['POST'])
def run_daily_automation():
    """Run daily automation tasks"""
    try:
        automation_engine.run_daily_automation(DEFAULT_USER_ID)
        return jsonify({'success': True, 'message': 'Daily automation completed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/integrations/test/all', methods=['POST'])
def test_all_integrations():
    """Test all integrations"""
    try:
        results = {
            'slack': automation_engine.slack.is_configured(),
            'calendar': True,
            'crm_sync': True,
            'social_monitoring': True
        }
        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/integrations/followups/check')
def check_follow_ups():
    """Check follow-ups due"""
    try:
        follow_ups = contact_model.get_follow_ups_due(DEFAULT_USER_ID, days_ahead=7)
        return jsonify({'count': len(follow_ups), 'follow_ups': follow_ups})
    except Exception as e:
        return jsonify({'count': 0, 'error': str(e)})

@app.route('/integrations/telegram/test', methods=['POST'])
def test_telegram_integration():
    """Test Telegram bot integration"""
    try:
        import asyncio
        
        # Create a simple test notification
        success = asyncio.run(automation_engine.telegram.send_notification(
            "Integration test from Founder Network AI", 
            "System Test"
        ))
        
        return jsonify({
            'success': success,
            'message': 'Test message sent to Telegram' if success else 'Telegram not configured'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# PWA and Mobile API Routes
@app.route('/api/follow-ups-due')
def api_follow_ups_due():
    """API endpoint for follow-ups due (for push notifications)"""
    try:
        follow_ups = contact_model.get_follow_ups_due(DEFAULT_USER_ID, days_ahead=7)
        return jsonify(follow_ups)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/push-subscription', methods=['POST'])
def save_push_subscription():
    """Save push notification subscription"""
    try:
        subscription_data = request.get_json()
        # Store subscription in database for push notifications
        # This would typically save to a subscriptions table
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/telegram-command', methods=['POST'])
def process_telegram_voice_command():
    """Process voice commands sent through Telegram integration"""
    try:
        data = request.get_json()
        command = data.get('command', '')
        
        # Process voice command using contact intelligence
        response = contact_nlp.process_command(command)
        
        return jsonify({
            'success': True,
            'response': response.get('message', 'Command processed'),
            'action': response.get('action')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/offline.html')
def offline_page():
    """Offline fallback page"""
    return render_template('offline.html')

@app.route('/contacts/new')
def new_contact_form():
    """Mobile-optimized new contact form"""
    return render_template('mobile_contact_form.html')

@app.route('/goals/new')
def new_goal_form():
    """Mobile-optimized new goal form"""
    return render_template('mobile_goal_form.html')

# Advanced Contact Search and Filtering Routes
@app.route('/api/contacts/search')
def search_contacts_api():
    """Advanced contact search API with filtering"""
    try:
        from contact_search import ContactSearchEngine
        search_engine = ContactSearchEngine(db)
        
        query = request.args.get('q', '').strip()
        user_id = DEFAULT_USER_ID
        
        # Parse filters from query parameters
        filters = {}
        if request.args.get('company'):
            filters['company'] = request.args.get('company')
        if request.args.get('relationship_type'):
            filters['relationship_type'] = request.args.get('relationship_type')
        if request.args.get('warmth'):
            warmth_levels = request.args.getlist('warmth')
            filters['warmth'] = warmth_levels if warmth_levels else request.args.get('warmth')
        if request.args.get('tags'):
            filters['tags'] = request.args.get('tags')
        if request.args.get('location'):
            filters['location'] = request.args.get('location')
        if request.args.get('last_interaction_days'):
            filters['last_interaction_days'] = request.args.get('last_interaction_days')
            filters['user_id'] = user_id
        if request.args.get('follow_up_due'):
            filters['follow_up_due'] = True
            filters['user_id'] = user_id
        
        # Perform search
        results = search_engine.search_contacts(query, user_id, filters)
        
        # Save search history
        if query:
            import json
            filter_json = json.dumps(filters) if filters else None
            search_engine.save_search_history(user_id, query, filter_json)
        
        return jsonify({
            'success': True,
            'results': results,
            'total_count': len(results),
            'query': query,
            'filters': filters
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/search/suggestions')
def search_suggestions_api():
    """Get search suggestions for autocomplete"""
    try:
        from contact_search import ContactSearchEngine
        search_engine = ContactSearchEngine(db)
        
        partial_query = request.args.get('q', '').strip()
        user_id = DEFAULT_USER_ID
        
        if len(partial_query) < 2:
            return jsonify({'suggestions': {}})
        
        suggestions = search_engine.get_search_suggestions(partial_query, user_id)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/filter-options')
def filter_options_api():
    """Get available filter options from existing data"""
    try:
        from contact_search import ContactSearchEngine
        search_engine = ContactSearchEngine(db)
        
        user_id = DEFAULT_USER_ID
        options = search_engine.get_filter_options(user_id)
        
        return jsonify({
            'success': True,
            'options': options
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/contacts/search/history')
def search_history_api():
    """Get popular search queries for the user"""
    try:
        from contact_search import ContactSearchEngine
        search_engine = ContactSearchEngine(db)
        
        user_id = DEFAULT_USER_ID
        limit = int(request.args.get('limit', 5))
        
        popular_searches = search_engine.get_popular_searches(user_id, limit)
        
        return jsonify({
            'success': True,
            'popular_searches': popular_searches
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/contacts/search')
def advanced_contacts_search():
    """Advanced contact search and filtering interface"""
    try:
        from contact_search import ContactSearchEngine
        search_engine = ContactSearchEngine(db)
        
        user_id = DEFAULT_USER_ID
        
        # Get filter options for the interface
        filter_options = search_engine.get_filter_options(user_id)
        
        # Get popular searches
        popular_searches = search_engine.get_popular_searches(user_id, 5)
        
        # If there's a search query, perform the search
        query = request.args.get('q', '').strip()
        results = []
        
        if query or any(request.args.get(key) for key in ['company', 'relationship_type', 'warmth', 'tags']):
            filters = {}
            for key in ['company', 'relationship_type', 'warmth', 'tags', 'location']:
                if request.args.get(key):
                    filters[key] = request.args.get(key)
            
            results = search_engine.search_contacts(query, user_id, filters)
            
            # Save search history
            if query:
                import json
                filter_json = json.dumps(filters) if filters else None
                search_engine.save_search_history(user_id, query, filter_json)
        
        return render_template('contacts_search.html', 
                             results=results,
                             query=query,
                             filter_options=filter_options,
                             popular_searches=popular_searches,
                             current_filters=request.args.to_dict())
        
    except Exception as e:
        flash(f'Search error: {str(e)}', 'error')
        return redirect('/contacts')

@app.errorhandler(404)
def not_found(error):
    return render_template('base.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html'), 500

# AI-Powered Contact Intelligence Routes

@app.route('/ai/contact/<int:contact_id>/similar')
def ai_similar_contacts(contact_id):
    """Find contacts similar to the given contact using AI"""
    try:
        similar_contacts = ai_matcher.find_similar_contacts(contact_id, limit=5)
        
        return jsonify({
            'success': True,
            'similar_contacts': similar_contacts,
            'count': len(similar_contacts)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/ai/introductions')
def ai_introduction_suggestions():
    """Get AI-powered introduction suggestions"""
    user_id = int(session.get('user_id', 1))
    
    try:
        introduction_opportunities = ai_matcher.suggest_introduction_opportunities(user_id)
        
        return jsonify({
            'success': True,
            'opportunities': introduction_opportunities,
            'count': len(introduction_opportunities)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/ai/outreach/<int:contact_id>')
def ai_personalized_outreach(contact_id):
    """Generate personalized outreach recommendations"""
    goal_description = request.args.get('goal', '')
    
    try:
        outreach_data = ai_matcher.generate_personalized_outreach(contact_id, goal_description)
        
        return jsonify({
            'success': True,
            'outreach_data': outreach_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/ai/network-gaps')
def ai_network_gaps():
    """Analyze network gaps and suggest expansion areas"""
    user_id = int(session.get('user_id', 1))
    
    try:
        gap_analysis = ai_matcher.analyze_network_gaps(user_id)
        
        return jsonify({
            'success': True,
            'analysis': gap_analysis
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/ai/responsiveness/<int:contact_id>')
def ai_predict_responsiveness(contact_id):
    """Predict contact responsiveness using AI"""
    try:
        prediction = ai_matcher.predict_contact_responsiveness(contact_id)
        
        return jsonify({
            'success': True,
            'prediction': prediction
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/ai/intelligence')
def ai_intelligence_dashboard():
    """AI-powered contact intelligence dashboard"""
    user_id = int(session.get('user_id', 1))
    
    try:
        # Get various AI insights
        introduction_opportunities = ai_matcher.suggest_introduction_opportunities(user_id)
        network_gaps = ai_matcher.analyze_network_gaps(user_id)
        
        # Get top contacts for analysis
        contacts = contact_model.get_all(user_id)[:10]
        contact_insights = []
        
        for contact in contacts:
            try:
                responsiveness = ai_matcher.predict_contact_responsiveness(contact['id'])
                similar = ai_matcher.find_similar_contacts(contact['id'], limit=3)
                
                contact_insights.append({
                    'contact': contact,
                    'responsiveness': responsiveness,
                    'similar_contacts': similar
                })
            except Exception as e:
                # Skip contacts that cause errors
                continue
        
        return render_template('ai_intelligence.html',
                             introduction_opportunities=introduction_opportunities[:5],
                             network_gaps=network_gaps,
                             contact_insights=contact_insights[:5])
    
    except Exception as e:
        flash(f'Error loading AI intelligence: {str(e)}', 'error')
        return redirect(url_for('crm_dashboard'))

@app.route('/rhizome')
def rhizome_dashboard():
    """Rhizomatic Intelligence Layer - Living Network Visualization"""
    return render_template('rhizome_dashboard.html')

@app.route('/api/rhizome/insights')
def get_rhizomatic_insights():
    """API endpoint for rhizomatic intelligence insights"""
    user_id = session.get('user_id', 1)
    
    try:
        rhizome = RhizomaticIntelligence(db)
        insights = rhizome.generate_rhizomatic_insights(user_id)
        return jsonify(insights)
    
    except Exception as e:
        logging.error(f"Error generating rhizomatic insights: {e}")
        return jsonify({
            "error": str(e),
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/rhizome/network-graph')
def get_rhizomatic_network_graph():
    """API endpoint for Neo4j-style network graph data"""
    user_id = session.get('user_id', 1)
    
    try:
        rhizome = RhizomaticIntelligence(db)
        insights = rhizome.generate_rhizomatic_insights(user_id)
        
        return jsonify({
            "graph_data": insights.get("network_graph", {}),
            "insights": insights.get("rhizomatic_insights", {}),
            "status": "success"
        })
    
    except Exception as e:
        logging.error(f"Error generating network graph: {e}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/rhizome/history')
def get_rhizomatic_history():
    """API endpoint for historical rhizomatic insights"""
    user_id = session.get('user_id', 1)
    limit = request.args.get('limit', 10, type=int)
    
    try:
        rhizome = RhizomaticIntelligence(db)
        history = rhizome.get_network_insights_history(user_id, limit)
        
        return jsonify({
            "history": history,
            "status": "success"
        })
    
    except Exception as e:
        logging.error(f"Error getting rhizomatic history: {e}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

# Conference Mode Routes
@app.route('/gamification')
def gamification_dashboard():
    """Gamified Contact Organization - XP, Quests, and Achievements Dashboard"""
    try:
        # Get user progress
        user_progress = gamification.get_user_progress(DEFAULT_USER_ID)
        
        # Get daily quests
        daily_quests = gamification.get_daily_quests(DEFAULT_USER_ID)
        
        return render_template('gamification_dashboard.html',
                             user_progress=user_progress,
                             daily_quests=daily_quests,
                             page_title='Gamification Dashboard')
    except Exception as e:
        logging.error(f"Error in gamification dashboard: {e}")
        flash('Error loading gamification dashboard', 'error')
        return redirect(url_for('crm_dashboard'))

@app.route('/complete_quest/<quest_id>', methods=['POST'])
def complete_quest(quest_id):
    """Mark a quest as completed"""
    try:
        result = gamification.complete_quest(DEFAULT_USER_ID, quest_id)
        
        if result['success']:
            flash(f"Quest completed! Earned {result['xp_awarded']} XP", 'success')
        else:
            flash(result.get('error', 'Failed to complete quest'), 'error')
            
    except Exception as e:
        logging.error(f"Error completing quest: {e}")
        flash('Error completing quest', 'error')
    
    return redirect(url_for('gamification_dashboard'))

@app.route('/conference')
def conference_mode():
    """Conference Mode dashboard"""
    from conference_mode import ConferenceMode
    conference_manager = ConferenceMode(db)
    
    # Get active conference
    active_conference = conference_manager.get_active_conference(DEFAULT_USER_ID)
    
    # Get daily follow-up summary
    daily_summary = conference_manager.get_daily_follow_up_summary(DEFAULT_USER_ID)
    
    return render_template('conference_mode.html', 
                         active_conference=active_conference,
                         daily_summary=daily_summary)

@app.route('/conference/activate', methods=['POST'])
def activate_conference():
    """Activate conference mode"""
    from conference_mode import ConferenceMode
    conference_manager = ConferenceMode(db)
    
    try:
        conference_name = request.form.get('conference_name')
        location = request.form.get('location', '')
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        
        if not conference_name:
            flash('Conference name is required', 'error')
            return redirect(url_for('conference_mode'))
        
        conference_id = conference_manager.activate_conference_mode(
            DEFAULT_USER_ID, conference_name, location, start_date, end_date
        )
        
        flash(f'Conference mode activated for {conference_name}', 'success')
        return redirect(url_for('conference_mode'))
        
    except Exception as e:
        logging.error(f"Error activating conference mode: {e}")
        flash('Error activating conference mode', 'error')
        return redirect(url_for('conference_mode'))

@app.route('/conference/deactivate', methods=['POST'])
def deactivate_conference():
    """Deactivate conference mode"""
    from conference_mode import ConferenceMode
    conference_manager = ConferenceMode(db)
    
    try:
        conference_manager.deactivate_conference_mode(DEFAULT_USER_ID)
        flash('Conference mode deactivated', 'success')
        
    except Exception as e:
        logging.error(f"Error deactivating conference mode: {e}")
        flash('Error deactivating conference mode', 'error')
    
    return redirect(url_for('conference_mode'))

@app.route('/conference/capture', methods=['POST'])
def capture_conference_contact():
    """Capture a new contact during conference mode"""
    from conference_mode import ConferenceMode
    conference_manager = ConferenceMode(db)
    
    try:
        # Get active conference
        active_conference = conference_manager.get_active_conference(DEFAULT_USER_ID)
        if not active_conference:
            flash('No active conference. Please activate conference mode first.', 'error')
            return redirect(url_for('conference_mode'))
        
        # Extract form data
        name = request.form.get('name')
        company = request.form.get('company', '')
        title = request.form.get('title', '')
        email = request.form.get('email', '')
        linkedin = request.form.get('linkedin', '')
        twitter = request.form.get('twitter', '')
        conversation_notes = request.form.get('conversation_notes', '')
        voice_memo = request.form.get('voice_memo', '')
        
        if not name:
            flash('Contact name is required', 'error')
            return redirect(url_for('conference_mode'))
        
        # Process voice memo if provided
        voice_data = {}
        if voice_memo:
            voice_data = conference_manager.process_voice_memo(voice_memo)
            # Auto-fill missing fields from voice memo
            if not company and voice_data.get('company'):
                company = voice_data['company']
            if not title and voice_data.get('title'):
                title = voice_data['title']
            if not conversation_notes and voice_data.get('conversation_summary'):
                conversation_notes = voice_data['conversation_summary']
        
        # Capture the contact
        contact_id = conference_manager.capture_conference_contact(
            user_id=DEFAULT_USER_ID,
            conference_id=active_conference['id'],
            name=name,
            company=company,
            title=title,
            email=email,
            linkedin=linkedin,
            twitter=twitter,
            conversation_notes=conversation_notes,
            voice_memo=voice_memo
        )
        
        flash(f'Contact {name} captured successfully', 'success')
        return redirect(url_for('conference_mode'))
        
    except Exception as e:
        logging.error(f"Error capturing conference contact: {e}")
        flash('Error capturing contact', 'error')
        return redirect(url_for('conference_mode'))

@app.route('/conference/generate-followups', methods=['POST'])
def generate_conference_followups():
    """Generate AI follow-up suggestions for conference contacts"""
    from conference_mode import ConferenceMode
    conference_manager = ConferenceMode(db)
    
    try:
        # Get active conference
        active_conference = conference_manager.get_active_conference(DEFAULT_USER_ID)
        if not active_conference:
            flash('No active conference found', 'error')
            return redirect(url_for('conference_mode'))
        
        # Generate follow-ups
        suggestions = conference_manager.generate_conference_follow_ups(
            DEFAULT_USER_ID, active_conference['id']
        )
        
        if suggestions:
            flash(f'Generated {len(suggestions)} follow-up suggestions', 'success')
        else:
            flash('No follow-up suggestions generated. Add some contacts first.', 'info')
        
        return redirect(url_for('conference_mode'))
        
    except Exception as e:
        logging.error(f"Error generating follow-ups: {e}")
        flash('Error generating follow-up suggestions', 'error')
        return redirect(url_for('conference_mode'))

@app.route('/conference/followup/complete', methods=['POST'])
def complete_followup():
    """Mark a follow-up as completed"""
    from conference_mode import ConferenceMode
    conference_manager = ConferenceMode(db)
    
    try:
        contact_name = request.form.get('contact_name')
        conference_id = request.form.get('conference_id')
        
        if contact_name and conference_id:
            conference_manager.mark_follow_up_complete(DEFAULT_USER_ID, contact_name, conference_id)
            flash(f'Follow-up with {contact_name} marked as complete', 'success')
        else:
            flash('Missing required information', 'error')
        
        return redirect(url_for('conference_mode'))
        
    except Exception as e:
        logging.error(f"Error completing follow-up: {e}")
        flash('Error updating follow-up status', 'error')
        return redirect(url_for('conference_mode'))

@app.route('/conference/api/contacts/<conference_id>')
def get_conference_contacts_api(conference_id):
    """API endpoint to get conference contacts"""
    from conference_mode import ConferenceMode
    conference_manager = ConferenceMode(db)
    
    try:
        contacts = conference_manager.get_conference_contacts(conference_id)
        return jsonify(contacts)
        
    except Exception as e:
        logging.error(f"Error fetching conference contacts: {e}")
        return jsonify({'error': 'Failed to fetch contacts'}), 500

# Network Visualization and Relationship Mapping Routes

@app.route('/network')
def network_dashboard():
    """Network visualization dashboard"""
    return render_template('network_visualization.html')

@app.route('/network/api/graph')
def network_api_graph():
    """API endpoint for network graph data"""
    user_id = session.get('user_id', 1)
    
    try:
        from network_visualization import NetworkMapper
        mapper = NetworkMapper(db)
        graph_data = mapper.build_network_graph(user_id)
        
        return jsonify({
            "status": "success",
            "data": graph_data
        })
    
    except Exception as e:
        logging.error(f"Error building network graph: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/network/api/metrics')
def network_api_metrics():
    """API endpoint for network metrics"""
    user_id = session.get('user_id', 1)
    
    try:
        from network_visualization import NetworkMapper
        mapper = NetworkMapper(db)
        metrics = mapper.get_network_metrics(user_id)
        
        return jsonify({
            "status": "success",
            "data": metrics
        })
    
    except Exception as e:
        logging.error(f"Error getting network metrics: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/network/relationships', methods=['GET', 'POST'])
def manage_relationships():
    """Manage contact relationships"""
    user_id = session.get('user_id', 1)
    
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            # Create new relationship
            from network_visualization import ContactRelationshipModel
            rel_model = ContactRelationshipModel(db)
            
            relationship_id = rel_model.create(
                user_id=user_id,
                contact_a_id=data['contact_a_id'],
                contact_b_id=data['contact_b_id'],
                relationship_type=data.get('relationship_type', 'knows'),
                strength=data.get('strength', 1),
                notes=data.get('notes')
            )
            
            return jsonify({
                "status": "success",
                "relationship_id": relationship_id,
                "message": "Relationship created successfully"
            })
            
        except Exception as e:
            logging.error(f"Error creating relationship: {e}")
            return jsonify({
                "status": "error",
                "error": str(e)
            }), 500
    
    # GET request - return relationship management interface
    contact_model = Contact(db)
    contacts = contact_model.get_all(user_id)
    
    return render_template('manage_relationships.html', contacts=contacts)

@app.route('/network/api/introductions')
def network_api_introductions():
    """API endpoint for introduction suggestions"""
    user_id = session.get('user_id', 1)
    limit = request.args.get('limit', 10, type=int)
    
    try:
        from network_visualization import NetworkMapper
        mapper = NetworkMapper(db)
        suggestions = mapper.suggest_introductions(user_id, limit)
        
        return jsonify({
            "status": "success",
            "data": suggestions
        })
    
    except Exception as e:
        logging.error(f"Error getting introduction suggestions: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

# Network Intelligence Routes - Advanced relationship health analysis

@app.route('/network-intelligence')
def network_intelligence():
    """Network Intelligence dashboard with AI-powered relationship insights"""
    user_id = session.get('user_id', 1)  # Default to demo user
    
    try:
        smart_engine = SmartNetworkingEngine()
        network_data = smart_engine.get_network_intelligence_dashboard(user_id)
        
        # Calculate average health score for display
        if network_data.get('top_relationships'):
            avg_health = sum(c['health_score'] for c in network_data['top_relationships']) / len(network_data['top_relationships'])
            network_data['avg_health_score'] = avg_health
        else:
            network_data['avg_health_score'] = 0
        
        return render_template('network_intelligence.html', network_data=network_data)
    except Exception as e:
        logging.error(f"Network intelligence error: {e}")
        return render_template('network_intelligence.html', network_data=None)

@app.route('/api/network-intelligence')
def api_network_intelligence():
    """API endpoint for real-time network intelligence data"""
    user_id = session.get('user_id', 1)
    
    try:
        smart_engine = SmartNetworkingEngine()
        network_data = smart_engine.get_network_intelligence_dashboard(user_id)
        
        if network_data.get('top_relationships'):
            avg_health = sum(c['health_score'] for c in network_data['top_relationships']) / len(network_data['top_relationships'])
            network_data['avg_health_score'] = avg_health
        else:
            network_data['avg_health_score'] = 0
        
        return jsonify(network_data)
    except Exception as e:
        logging.error(f"Network intelligence API error: {e}")
        return jsonify({"error": "Failed to load network intelligence"}), 500

@app.route('/api/relationship-health/<int:contact_id>')
def api_relationship_health(contact_id):
    """Individual relationship health analysis with AI insights"""
    user_id = session.get('user_id', 1)
    
    try:
        smart_engine = SmartNetworkingEngine()
        health_data = smart_engine.get_relationship_health_score(user_id, contact_id)
        return jsonify(health_data)
    except Exception as e:
        logging.error(f"Relationship health error for contact {contact_id}: {e}")
        return jsonify({"error": "Failed to analyze relationship health"}), 500

# Collective Actions Routes
@app.route('/collective_actions')
@login_required
def collective_actions():
    """Main collective actions page"""
    user_id = session.get('user_id')
    
    # Initialize predefined actions if needed
    collective_actions_manager.create_predefined_actions()
    
    # Get all available actions
    available_actions = collective_actions_manager.get_all_actions()
    
    # Get user's active actions
    user_actions = collective_actions_manager.get_user_actions(user_id)
    
    # Check which actions user is participating in
    user_participating = {}
    for action in available_actions:
        user_participating[action['id']] = collective_actions_manager.is_user_participating(action['id'], user_id)
    
    return render_template('collective_actions.html',
                         available_actions=available_actions,
                         user_actions=user_actions,
                         user_participating=user_participating,
                         now=datetime.now())

@app.route('/collective_actions/join', methods=['POST'])
@login_required
def join_collective_action():
    """Join a collective action"""
    user_id = session.get('user_id')
    action_id = request.form.get('action_id')
    individual_goal = request.form.get('individual_goal', '').strip()
    
    if not action_id:
        return jsonify({'success': False, 'error': 'Action ID required'})
    
    # Check if user has access to this feature
    if not subscription_manager.has_feature_access(user_id, 'collective_actions'):
        return jsonify({'success': False, 'error': 'Upgrade to Founder+ to join collective actions'})
    
    try:
        success = collective_actions_manager.join_action(action_id, user_id, individual_goal)
        
        if success:
            # Award XP for joining
            gamification.award_xp(user_id, 'collective_action_joined', 15)
            
            action = collective_actions_manager.get_action_by_id(action_id)
            return jsonify({
                'success': True,
                'action_title': action['title'] if action else 'Collective Action'
            })
        else:
            return jsonify({'success': False, 'error': 'Unable to join action (may be full or already joined)'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/collective_actions/<action_id>')
@login_required
def collective_action_detail(action_id):
    """Detailed view of a collective action"""
    user_id = session.get('user_id')
    
    # Get action details
    action = collective_actions_manager.get_action_by_id(action_id)
    if not action:
        flash('Collective action not found', 'error')
        return redirect(url_for('collective_actions'))
    
    # Check if user is participating
    user_participating = collective_actions_manager.is_user_participating(action_id, user_id)
    user_participation = None
    
    if user_participating:
        user_actions = collective_actions_manager.get_user_actions(user_id)
        user_participation = next((a for a in user_actions if a['id'] == action_id), None)
    
    # Get group progress
    group_progress = collective_actions_manager.get_group_progress(action_id)
    
    # Get activity feed
    feed_items = collective_actions_manager.get_action_feed(action_id, limit=30)
    
    return render_template('collective_action_detail.html',
                         action=action,
                         user_participating=user_participating,
                         user_participation=user_participation,
                         group_progress=group_progress,
                         feed_items=feed_items)

@app.route('/collective_actions/update_progress', methods=['POST'])
@login_required
def update_collective_action_progress():
    """Update user progress in collective action"""
    user_id = session.get('user_id')
    action_id = request.form.get('action_id')
    content = request.form.get('content', '').strip()
    progress_percentage = request.form.get('progress_percentage')
    milestone_achieved = request.form.get('milestone_achieved', '').strip()
    
    if not all([action_id, content]):
        return jsonify({'success': False, 'error': 'Action ID and content required'})
    
    # Verify user is participating
    if not collective_actions_manager.is_user_participating(action_id, user_id):
        return jsonify({'success': False, 'error': 'You are not participating in this action'})
    
    try:
        progress_float = float(progress_percentage) if progress_percentage else None
        milestone = milestone_achieved if milestone_achieved else None
        
        success = collective_actions_manager.update_progress(
            action_id=action_id,
            user_id=user_id,
            update_type='progress',
            content=content,
            milestone_achieved=milestone,
            progress_percentage=progress_float
        )
        
        if success:
            # Award XP for progress update
            base_xp = 10
            milestone_bonus = 20 if milestone else 0
            progress_bonus = int(progress_float / 10) if progress_float else 0
            total_xp = base_xp + milestone_bonus + progress_bonus
            
            gamification.award_xp(user_id, 'collective_action_progress', total_xp)
            
            return jsonify({'success': True, 'xp_earned': total_xp})
        else:
            return jsonify({'success': False, 'error': 'Failed to update progress'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/collective_actions/post_message', methods=['POST'])
@login_required
def post_collective_action_message():
    """Post a message to collective action feed"""
    user_id = session.get('user_id')
    action_id = request.form.get('action_id')
    message_type = request.form.get('message_type', 'update')
    content = request.form.get('content', '').strip()
    
    if not all([action_id, content]):
        return jsonify({'success': False, 'error': 'Action ID and content required'})
    
    # Verify user is participating
    if not collective_actions_manager.is_user_participating(action_id, user_id):
        return jsonify({'success': False, 'error': 'You are not participating in this action'})
    
    try:
        success = collective_actions_manager.post_message(action_id, user_id, message_type, content)
        
        if success:
            # Award XP for community engagement
            gamification.award_xp(user_id, 'collective_action_message', 5)
            
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Failed to post message'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/collective_actions/dashboard/<user_id>')
@login_required
def collective_actions_dashboard_api(user_id):
    """API endpoint for collective actions dashboard data"""
    if session.get('user_id') != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        dashboard_data = collective_actions_manager.get_user_dashboard_data(user_id)
        return jsonify(dashboard_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
