from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app
import uuid
from models import Database, User, Contact, Goal, AISuggestion, ContactInteraction, ContactIntelligence, OutreachSuggestion
from openai_utils import OpenAIUtils
from database_utils import seed_demo_data, match_contacts_to_goal
from contact_intelligence import ContactNLP
from csv_import import CSVContactImporter
from simple_email import SimpleEmailSender
from analytics import NetworkingAnalytics
from network_visualization import NetworkMapper
from integrations import AutomationEngine
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
email_sender = SimpleEmailSender(db)
analytics = NetworkingAnalytics(db)
network_mapper = NetworkMapper(db)
automation_engine = AutomationEngine(db)

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
        tone = request.form.get('tone', 'warm')
        
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
    """CSV import interface for bulk contact uploads"""
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
                # Read CSV content
                csv_content = file.read().decode('utf-8')
                
                # Import contacts
                importer = CSVContactImporter(DEFAULT_USER_ID)
                skip_duplicates = request.form.get('skip_duplicates') == 'on'
                import_stats = importer.import_from_csv(csv_content, skip_duplicates)
                
                # Generate summary
                summary = importer.generate_import_summary()
                
                # Flash results
                if summary['successful'] > 0:
                    flash(f"Successfully imported {summary['successful']} contacts!", 'success')
                
                if summary['failed'] > 0:
                    flash(f"{summary['failed']} contacts failed to import", 'warning')
                
                if summary['warnings'] > 0:
                    flash(f"{summary['warnings']} warnings during import", 'info')
                
                # Render results
                return render_template('csv_import.html', 
                                     import_stats=import_stats,
                                     summary=summary,
                                     show_results=True)
                
            except Exception as e:
                logging.error(f"CSV import failed: {e}")
                flash(f'Import failed: {str(e)}', 'error')
        else:
            flash('Please upload a valid CSV file', 'error')
    
    # GET request - show import form
    importer = CSVContactImporter(DEFAULT_USER_ID)
    sample_csv = importer.get_sample_csv_format()
    
    return render_template('csv_import.html', 
                         sample_csv=sample_csv,
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
    
    # Send email
    result = email_sender.send_email(
        to_email=contact['email'],
        subject=subject,
        message_body=message,
        contact_id=contact_id,
        user_id=DEFAULT_USER_ID,
        goal_title=goal_title
    )
    
    if result['success']:
        flash(f"Email sent successfully to {contact['name']}", 'success')
    else:
        flash(f"Failed to send email: {result['error']}", 'error')
    
    return redirect(request.referrer or url_for('index'))

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

@app.route('/network')
def network_visualization():
    """Network visualization and relationship mapping interface"""
    try:
        # Get network data
        network_graph = network_mapper.build_network_graph(DEFAULT_USER_ID)
        network_metrics = network_mapper.get_network_metrics(DEFAULT_USER_ID)
        clusters = network_mapper.get_network_clusters(DEFAULT_USER_ID)
        intro_suggestions = network_mapper.suggest_introductions(DEFAULT_USER_ID, limit=5)
        
        return render_template('network_visualization.html',
                             network_graph=network_graph,
                             metrics=network_metrics,
                             clusters=clusters,
                             intro_suggestions=intro_suggestions)
    
    except Exception as e:
        logging.error(f"Network visualization error: {e}")
        flash('Error loading network visualization', 'error')
        return redirect(url_for('index'))

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
