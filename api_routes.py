"""
API Routes for React Frontend Integration
Provides RESTful endpoints to support the React frontend with existing Flask backend functionality
"""

from flask import Blueprint, request, jsonify, session
from functools import wraps
import sqlite3
import os
import json
import logging
from datetime import datetime, timedelta
from dataclasses import asdict

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Database connection helper
def get_db():
    db = sqlite3.connect('db.sqlite3')
    db.row_factory = sqlite3.Row
    return db

# Authentication decorator
def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Simple session-based auth for now
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Error handlers
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Auth endpoints
@api_bp.route('/auth/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    
    db = get_db()
    user = db.execute(
        'SELECT id, email, subscription_tier, created_at FROM users WHERE id = ?',
        (user_id,)
    ).fetchone()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user['id'],
        'email': user['email'],
        'subscription_tier': user['subscription_tier'],
        'created_at': user['created_at']
    })

@api_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    # For now, just set session if user exists
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    
    if user:
        session['user_id'] = user['id']
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'subscription_tier': user['subscription_tier']
            }
        })
    
    return jsonify({'error': 'User not found'}), 404

@api_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user with email"""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    # Validate email format
    import re
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    db = get_db()
    
    # Check if user already exists
    existing_user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    if existing_user:
        return jsonify({'error': 'User already exists with this email'}), 409
    
    # Create new user
    import uuid
    user_id = str(uuid.uuid4())
    
    try:
        db.execute('''
            INSERT INTO users (id, email, subscription_tier, created_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, email, 'explorer'))
        db.commit()
        
        # Create session
        session['user_id'] = user_id
        session['authenticated'] = True
        
        # Create starter goal to help with onboarding
        goal_id = str(uuid.uuid4())
        db.execute('''
            INSERT INTO goals (id, user_id, title, description)
            VALUES (?, ?, ?, ?)
        ''', (goal_id, user_id, 
              'Get started with Rhiz', 
              'Add your first contacts and start building your relationship intelligence network'))
        
        db.commit()
        
        return jsonify({
            'success': True,
            'user': {
                'id': user_id,
                'email': email,
                'subscription_tier': 'explorer'
            },
            'onboarding': True
        })
    except Exception as e:
        return jsonify({'error': 'Failed to create user'}), 500

@api_bp.route('/auth/magic-link', methods=['POST'])
def send_magic_link():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    # In production, this would send an actual email
    # For now, we'll just create/login the user
    db = get_db()
    
    # Check if user exists
    user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    
    if not user:
        # Create new user
        cursor = db.execute(
            'INSERT INTO users (email, subscription_tier, created_at) VALUES (?, ?, ?)',
            (email, 'explorer', datetime.now().isoformat())
        )
        user_id = cursor.lastrowid
        db.commit()
    else:
        user_id = user['id']
    
    # Set session
    session['user_id'] = user_id
    
    return jsonify({'success': True, 'message': 'Magic link sent'})

@api_bp.route('/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

# Goals endpoints
@api_bp.route('/goals', methods=['GET'])
@auth_required
def get_goals():
    user_id = session.get('user_id')
    db = get_db()
    
    goals = db.execute(
        'SELECT * FROM goals WHERE user_id = ? ORDER BY created_at DESC',
        (user_id,)
    ).fetchall()
    
    return jsonify([dict(goal) for goal in goals])

@api_bp.route('/goals', methods=['POST'])
@auth_required
def create_goal():
    user_id = session.get('user_id')
    data = request.get_json()
    
    title = data.get('title')
    description = data.get('description')
    
    if not title or not description:
        return jsonify({'error': 'Title and description required'}), 400
    
    db = get_db()
    cursor = db.execute(
        'INSERT INTO goals (user_id, title, description, created_at) VALUES (?, ?, ?, ?)',
        (user_id, title, description, datetime.now().isoformat())
    )
    goal_id = cursor.lastrowid
    db.commit()
    
    # Get the created goal
    goal = db.execute('SELECT * FROM goals WHERE id = ?', (goal_id,)).fetchone()
    
    return jsonify(dict(goal)), 201

@api_bp.route('/goals/<goal_id>/matches', methods=['GET'])
@auth_required
def get_goal_matches(goal_id):
    user_id = session.get('user_id')
    db = get_db()
    
    # Get AI suggestions for this goal
    suggestions = db.execute(
        '''SELECT s.*, c.name as contact_name, g.title as goal_title
           FROM ai_suggestions s
           JOIN contacts c ON s.contact_id = c.id
           JOIN goals g ON s.goal_id = g.id
           WHERE s.goal_id = ? AND g.user_id = ?
           ORDER BY s.confidence DESC''',
        (goal_id, user_id)
    ).fetchall()
    
    return jsonify([dict(suggestion) for suggestion in suggestions])

# Contacts endpoints
@api_bp.route('/contacts', methods=['GET'])
@auth_required
def get_contacts():
    user_id = session.get('user_id')
    db = get_db()
    
    # Get filters from query params
    search = request.args.get('search', '')
    warmth = request.args.get('warmth')
    relationship_type = request.args.get('relationship_type')
    
    query = 'SELECT * FROM contacts WHERE user_id = ?'
    params = [user_id]
    
    if search:
        query += ' AND (name LIKE ? OR company LIKE ? OR title LIKE ?)'
        search_term = f'%{search}%'
        params.extend([search_term, search_term, search_term])
    
    if warmth:
        query += ' AND warmth_status = ?'
        params.append(warmth)
    
    if relationship_type:
        query += ' AND relationship_type = ?'
        params.append(relationship_type)
    
    query += ' ORDER BY name'
    
    contacts = db.execute(query, params).fetchall()
    
    # Add sync status information
    contact_list = []
    for contact in contacts:
        contact_dict = dict(contact)
        
        # Get sync source information (with fallback if table doesn't exist)
        try:
            source_info = db.execute(
                'SELECT source FROM contact_sources WHERE contact_id = ? AND is_primary = 1',
                (contact['id'],)
            ).fetchone()
            contact_dict['sync_status'] = source_info['source'] if source_info else 'manual'
        except sqlite3.OperationalError:
            # Table doesn't exist yet, use manual as default
            contact_dict['sync_status'] = 'manual'
        
        # Parse social handles if present
        if contact_dict.get('social_handles'):
            try:
                contact_dict['social_handles'] = json.loads(contact_dict['social_handles'])
            except:
                contact_dict['social_handles'] = {}
        
        contact_list.append(contact_dict)
    
    return jsonify(contact_list)

@api_bp.route('/contacts', methods=['POST'])
@auth_required
def create_contact():
    user_id = session.get('user_id')
    data = request.get_json()
    
    required_fields = ['name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    db = get_db()
    
    # Prepare contact data
    contact_data = {
        'user_id': user_id,
        'name': data['name'],
        'email': data.get('email'),
        'phone': data.get('phone'),
        'linkedin': data.get('linkedin'),
        'company': data.get('company'),
        'title': data.get('title'),
        'relationship_type': data.get('relationship_type', 'contact'),
        'warmth_status': data.get('warmth_status', 1),
        'warmth_label': data.get('warmth_label', 'Cold'),
        'priority_level': data.get('priority_level', 'medium'),
        'notes': data.get('notes'),
        'tags': data.get('tags'),
        'location': data.get('location'),
        'interests': data.get('interests'),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
    
    columns = ', '.join(contact_data.keys())
    placeholders = ', '.join(['?' for _ in contact_data])
    
    cursor = db.execute(
        f'INSERT INTO contacts ({columns}) VALUES ({placeholders})',
        list(contact_data.values())
    )
    contact_id = cursor.lastrowid
    db.commit()
    
    # Get the created contact
    contact = db.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,)).fetchone()
    
    return jsonify(dict(contact)), 201

@api_bp.route('/contacts/<contact_id>', methods=['GET'])
@auth_required
def get_contact(contact_id):
    user_id = session.get('user_id')
    db = get_db()
    
    contact = db.execute(
        'SELECT * FROM contacts WHERE id = ? AND user_id = ?',
        (contact_id, user_id)
    ).fetchone()
    
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    return jsonify(dict(contact))

@api_bp.route('/contacts/<contact_id>/interactions', methods=['GET'])
@auth_required
def get_contact_interactions(contact_id):
    user_id = session.get('user_id')
    db = get_db()
    
    # Verify contact belongs to user
    contact = db.execute(
        'SELECT id FROM contacts WHERE id = ? AND user_id = ?',
        (contact_id, user_id)
    ).fetchone()
    
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    interactions = db.execute(
        'SELECT * FROM contact_interactions WHERE contact_id = ? ORDER BY timestamp DESC',
        (contact_id,)
    ).fetchall()
    
    return jsonify([dict(interaction) for interaction in interactions])

# Intelligence endpoints
@api_bp.route('/ai-suggestions', methods=['GET'])
@auth_required
def get_ai_suggestions():
    user_id = session.get('user_id')
    db = get_db()
    
    suggestions = db.execute(
        '''SELECT s.*, c.name as contact_name, g.title as goal_title
           FROM ai_suggestions s
           JOIN contacts c ON s.contact_id = c.id
           JOIN goals g ON s.goal_id = g.id
           WHERE g.user_id = ?
           ORDER BY s.confidence DESC
           LIMIT 20''',
        (user_id,)
    ).fetchall()
    
    return jsonify([dict(suggestion) for suggestion in suggestions])

@api_bp.route('/insights', methods=['GET'])
@auth_required
def get_insights():
    user_id = session.get('user_id')
    db = get_db()
    
    # Get basic network insights
    stats = {}
    
    # Count active goals
    stats['active_goals'] = db.execute(
        'SELECT COUNT(*) as count FROM goals WHERE user_id = ?', (user_id,)
    ).fetchone()['count']
    
    # Count contacts by warmth
    stats['warm_contacts'] = db.execute(
        'SELECT COUNT(*) as count FROM contacts WHERE user_id = ? AND warmth_status >= 3', (user_id,)
    ).fetchone()['count']
    
    # Count AI suggestions
    stats['ai_suggestions'] = db.execute(
        '''SELECT COUNT(*) as count FROM ai_suggestions s
           JOIN goals g ON s.goal_id = g.id
           WHERE g.user_id = ?''', (user_id,)
    ).fetchone()['count']
    
    return jsonify(stats)



# Network endpoints
@api_bp.route('/network/graph', methods=['GET'])
@auth_required
def get_network_graph():
    user_id = session.get('user_id')
    db = get_db()
    
    # Get contacts as nodes
    contacts = db.execute(
        'SELECT id, name, company, title, relationship_type FROM contacts WHERE user_id = ?',
        (user_id,)
    ).fetchall()
    
    # Get goals as nodes
    goals = db.execute(
        'SELECT id, title, description FROM goals WHERE user_id = ?',
        (user_id,)
    ).fetchall()
    
    # Build nodes
    nodes = []
    
    # Add user node
    user = db.execute('SELECT id, email FROM users WHERE id = ?', (user_id,)).fetchone()
    if user:
        nodes.append({
            'id': f'user_{user["id"]}',
            'name': user['email'],
            'type': 'user',
            'data': dict(user)
        })
    
    # Add contact nodes
    for contact in contacts:
        nodes.append({
            'id': f'contact_{contact["id"]}',
            'name': contact['name'],
            'type': 'contact',
            'data': dict(contact)
        })
    
    # Add goal nodes
    for goal in goals:
        nodes.append({
            'id': f'goal_{goal["id"]}',
            'name': goal['title'],
            'type': 'goal',
            'data': dict(goal)
        })
    
    # Build edges (simplified)
    edges = []
    
    # Connect user to all goals
    for goal in goals:
        edges.append({
            'id': f'user_goal_{goal["id"]}',
            'source': f'user_{user_id}',
            'target': f'goal_{goal["id"]}',
            'type': 'goal_match',
            'strength': 1
        })
    
    # Connect goals to contacts via AI suggestions
    suggestions = db.execute(
        '''SELECT goal_id, contact_id, confidence 
           FROM ai_suggestions s
           JOIN goals g ON s.goal_id = g.id
           WHERE g.user_id = ?''',
        (user_id,)
    ).fetchall()
    
    for suggestion in suggestions:
        edges.append({
            'id': f'suggestion_{suggestion["goal_id"]}_{suggestion["contact_id"]}',
            'source': f'goal_{suggestion["goal_id"]}',
            'target': f'contact_{suggestion["contact_id"]}',
            'type': 'goal_match',
            'strength': suggestion['confidence']
        })
    
    return jsonify({
        'nodes': nodes,
        'edges': edges
    })

# Health check endpoint
@api_bp.route('/health', methods=['GET'])
def health_check():
    try:
        db = get_db()
        db.execute('SELECT 1').fetchone()
        db.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@api_bp.route('/debug/session', methods=['GET'])
def debug_session():
    """Debug endpoint to check session data"""
    return jsonify({
        'session_data': dict(session),
        'user_id': session.get('user_id'),
        'authenticated': session.get('authenticated'),
        'demo_mode': session.get('demo_mode'),
        'session_keys': list(session.keys())
    })

@api_bp.route('/intelligence/chat', methods=['POST'])
@auth_required
def intelligence_chat():
    """AI-powered chat interface for natural language queries"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        user_id = session.get('user_id')
        
        # Import the ContactNLP class for processing
        try:
            from contact_intelligence import ContactNLP
            nlp_processor = ContactNLP(user_id)
            response = nlp_processor.process_command(user_message)
            
            # Handle string response from ContactNLP
            if isinstance(response, str):
                return jsonify({
                    'response': response,
                    'suggestions': [
                        "Show me my warm contacts",
                        "Who needs a follow-up?",
                        "What's my network summary?",
                        "Find contacts in tech"
                    ]
                })
            else:
                return jsonify({
                    'response': response.get('response', 'I understand your question, but I need more information to provide a helpful answer.'),
                    'suggestions': response.get('suggestions', [
                        "Show me my warm contacts",
                        "Who needs a follow-up?",
                        "What's my network summary?",
                        "Find contacts in tech"
                    ])
                })
            
        except ImportError:
            # Fallback response if NLP module not available
            return jsonify({
                'response': f"I received your message: '{user_message}'. The intelligence system is currently being enhanced. For now, you can use the dashboard to explore your contacts and goals.",
                'suggestions': [
                    "Show me my contacts",
                    "Display my goals",
                    "What's my network status?",
                    "Show recent activities"
                ]
            })
            
    except Exception as e:
        return jsonify({
            'response': "I'm experiencing some technical difficulties. Please try again in a moment.",
            'error': str(e)
        }), 500

# Analytics endpoints
@api_bp.route('/analytics/dashboard', methods=['GET'])
@auth_required
def get_dashboard_analytics():
    user_id = session.get('user_id')
    db = get_db()
    
    # Basic dashboard stats
    stats = {}
    
    # Total counts
    stats['total_contacts'] = db.execute(
        'SELECT COUNT(*) as count FROM contacts WHERE user_id = ?', (user_id,)
    ).fetchone()['count']
    
    stats['total_goals'] = db.execute(
        'SELECT COUNT(*) as count FROM goals WHERE user_id = ?', (user_id,)
    ).fetchone()['count']
    
    stats['total_suggestions'] = db.execute(
        '''SELECT COUNT(*) as count FROM ai_suggestions s
           JOIN goals g ON s.goal_id = g.id
           WHERE g.user_id = ?''', (user_id,)
    ).fetchone()['count']
    
    # Recent activity (last 7 days)
    stats['recent_interactions'] = db.execute(
        '''SELECT COUNT(*) as count FROM contact_interactions ci
           JOIN contacts c ON ci.contact_id = c.id
           WHERE c.user_id = ? AND ci.timestamp > datetime('now', '-7 days')''',
        (user_id,)
    ).fetchone()['count']
    
    return jsonify(stats)

# Multi-Source Contact Sync endpoints
@api_bp.route('/contacts/sync', methods=['POST'])
@auth_required
def sync_contacts():
    """Initiate contact sync from external source"""
    user_id = session.get('user_id')
    data = request.get_json()
    source = data.get('source')
    
    if not source:
        return jsonify({'error': 'Source required'}), 400
    
    try:
        from contact_sync_engine import ContactSyncEngine
        sync_engine = ContactSyncEngine()
        sync_engine.init_sync_tables()
        
        # Create sync job
        job_id = sync_engine.create_sync_job(user_id, source)
        
        # For demo purposes, simulate sync completion
        sync_engine.update_sync_job(job_id, 'completed', total_contacts=10, processed_contacts=10)
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': f'{source.title()} sync initiated'
        })
    except Exception as e:
        logging.error(f"Sync error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/contacts/sync-jobs', methods=['GET'])
@auth_required
def get_sync_jobs():
    """Get sync job status"""
    user_id = session.get('user_id')
    db = get_db()
    
    jobs = db.execute(
        '''SELECT * FROM sync_jobs 
           WHERE user_id = ? 
           ORDER BY started_at DESC 
           LIMIT 10''',
        (user_id,)
    ).fetchall()
    
    return jsonify([dict(job) for job in jobs])

@api_bp.route('/contacts/merge-candidates', methods=['GET'])
@auth_required
def get_merge_candidates():
    """Get potential duplicate contacts for review"""
    user_id = session.get('user_id')
    
    try:
        from contact_sync_engine import ContactSyncEngine
        sync_engine = ContactSyncEngine()
        candidates = sync_engine.get_merge_candidates(user_id)
        return jsonify(candidates)
    except Exception as e:
        logging.error(f"Merge candidates error: {e}")
        return jsonify([])

@api_bp.route('/contacts/enrich/<int:contact_id>', methods=['POST'])
@auth_required
def enrich_contact(contact_id):
    """Enrich contact with additional data"""
    user_id = session.get('user_id')
    db = get_db()
    
    # Verify contact belongs to user
    contact = db.execute(
        'SELECT * FROM contacts WHERE id = ? AND user_id = ?',
        (contact_id, user_id)
    ).fetchone()
    
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404
    
    try:
        from contact_sync_engine import ContactSyncEngine
        sync_engine = ContactSyncEngine()
        results = sync_engine.enrich_contact(contact_id)
        return jsonify(results)
    except Exception as e:
        logging.error(f"Enrichment error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/contacts/sources', methods=['GET'])
@auth_required
def get_contact_sources():
    """Get available integration sources"""
    try:
        from social_integrations import SocialIntegrationManager
        manager = SocialIntegrationManager()
        sources = manager.get_available_integrations()
        
        # Add manual and CSV as always available
        all_sources = ['manual', 'csv'] + sources
        
        return jsonify({
            'sources': all_sources,
            'oauth_available': sources
        })
    except Exception as e:
        logging.error(f"Sources error: {e}")
        return jsonify({'sources': ['manual', 'csv'], 'oauth_available': []})

@api_bp.route('/contacts/oauth/<source>', methods=['GET'])
@auth_required
def get_oauth_url(source):
    """Get OAuth URL for external service"""
    user_id = session.get('user_id')
    
    try:
        from social_integrations import SocialIntegrationManager
        manager = SocialIntegrationManager()
        
        # Generate state with user_id for security
        state = f"{user_id}_{source}_{datetime.now().timestamp()}"
        oauth_url = manager.get_auth_url(source, state)
        
        if oauth_url:
            return jsonify({'oauth_url': oauth_url, 'state': state})
        else:
            return jsonify({'error': f'{source} integration not configured'}), 400
    except Exception as e:
        logging.error(f"OAuth URL error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/contacts/import/csv', methods=['POST'])
@auth_required
def import_csv_contacts():
    """Import contacts from CSV data"""
    user_id = session.get('user_id')
    data = request.get_json()
    csv_data = data.get('csv_data', [])
    
    if not csv_data:
        return jsonify({'error': 'CSV data required'}), 400
    
    try:
        from contact_sync_engine import ContactSyncEngine
        sync_engine = ContactSyncEngine()
        sync_engine.init_sync_tables()
        
        results = sync_engine.process_csv_contacts(user_id, csv_data)
        return jsonify(results)
    except Exception as e:
        logging.error(f"CSV import error: {e}")
        return jsonify({'error': str(e)}), 500

# Trust Insights endpoints
@api_bp.route('/trust/insights', methods=['GET'])
@auth_required
def get_trust_insights():
    """Get trust insights for current user"""
    user_id = session.get('user_id')
    
    try:
        from trust_insights import TrustInsightsEngine
        trust_engine = TrustInsightsEngine()
        trust_engine.init_trust_tables()
        
        insights = trust_engine.get_trust_insights_for_user(user_id)
        
        # Convert to dict for JSON serialization
        insights_data = []
        for insight in insights:
            insight_dict = asdict(insight)
            insight_dict['trust_signals'] = [asdict(signal) for signal in insight.trust_signals]
            insights_data.append(insight_dict)
        
        return jsonify({
            'success': True,
            'insights': insights_data
        })
        
    except Exception as e:
        logging.error(f"Trust insights error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/trust/health', methods=['GET'])
@auth_required
def get_trust_health():
    """Get user's overall trust health analysis"""
    user_id = session.get('user_id')
    
    try:
        from trust_insights import TrustInsightsEngine
        trust_engine = TrustInsightsEngine()
        health_data = trust_engine.generate_user_trust_health(user_id)
        
        return jsonify({
            'success': True,
            'health': health_data
        })
        
    except Exception as e:
        logging.error(f"Trust health error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/trust/update', methods=['POST'])
@auth_required
def update_trust_insights():
    """Update trust insights for all user contacts"""
    user_id = session.get('user_id')
    
    try:
        from trust_insights import TrustInsightsEngine
        trust_engine = TrustInsightsEngine()
        trust_engine.init_trust_tables()
        trust_engine.update_all_trust_insights(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Trust insights updated successfully'
        })
        
    except Exception as e:
        logging.error(f"Trust update error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/trust/signal', methods=['POST'])
@auth_required
def record_trust_signal():
    """Record a trust signal for a contact"""
    user_id = session.get('user_id')
    data = request.get_json()
    
    contact_id = data.get('contact_id')
    signal_type = data.get('signal_type')
    value = data.get('value')
    context = data.get('context', {})
    
    if not all([contact_id, signal_type, value is not None]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Verify contact belongs to user
        db = get_db()
        contact = db.execute(
            'SELECT id FROM contacts WHERE id = ? AND user_id = ?',
            (contact_id, user_id)
        ).fetchone()
        db.close()
        
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        from trust_insights import TrustInsightsEngine
        trust_engine = TrustInsightsEngine()
        trust_engine.record_trust_signal(contact_id, signal_type, value, context)
        
        return jsonify({
            'success': True,
            'message': 'Trust signal recorded'
        })
        
    except Exception as e:
        logging.error(f"Trust signal error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/trust/contact/<int:contact_id>', methods=['GET'])
@auth_required
def get_contact_trust_insight(contact_id):
    """Get detailed trust insight for specific contact"""
    user_id = session.get('user_id')
    
    try:
        # Verify contact belongs to user
        db = get_db()
        contact = db.execute(
            'SELECT * FROM contacts WHERE id = ? AND user_id = ?',
            (contact_id, user_id)
        ).fetchone()
        
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        # Get trust insight
        insight = db.execute(
            'SELECT * FROM trust_insights WHERE contact_id = ?',
            (contact_id,)
        ).fetchone()
        
        # Get trust signals
        signals = db.execute(
            '''SELECT * FROM trust_signals 
               WHERE contact_id = ? 
               ORDER BY timestamp DESC 
               LIMIT 20''',
            (contact_id,)
        ).fetchall()
        
        # Get trust timeline
        timeline = db.execute(
            '''SELECT * FROM trust_timeline 
               WHERE contact_id = ? 
               ORDER BY timestamp DESC 
               LIMIT 50''',
            (contact_id,)
        ).fetchall()
        
        db.close()
        
        return jsonify({
            'success': True,
            'contact': dict(contact),
            'insight': dict(insight) if insight else None,
            'signals': [dict(s) for s in signals],
            'timeline': [dict(t) for t in timeline]
        })
        
    except Exception as e:
        logging.error(f"Contact trust insight error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/trust/tiers', methods=['GET'])
@auth_required
def get_trust_tiers():
    """Get trust tier distribution for user"""
    user_id = session.get('user_id')
    
    try:
        db = get_db()
        
        # Get trust tier distribution
        tier_distribution = db.execute(
            '''SELECT trust_tier, COUNT(*) as count
               FROM contacts 
               WHERE user_id = ? AND trust_tier IS NOT NULL
               GROUP BY trust_tier''',
            (user_id,)
        ).fetchall()
        
        # Get contacts by tier
        tiers_data = {}
        for tier_row in tier_distribution:
            tier = tier_row['trust_tier']
            contacts = db.execute(
                '''SELECT c.*, ti.trust_score, ti.last_interaction
                   FROM contacts c
                   LEFT JOIN trust_insights ti ON c.id = ti.contact_id
                   WHERE c.user_id = ? AND c.trust_tier = ?
                   ORDER BY ti.trust_score DESC''',
                (user_id, tier)
            ).fetchall()
            
            tiers_data[tier] = {
                'count': tier_row['count'],
                'contacts': [dict(c) for c in contacts]
            }
        
        db.close()
        
        return jsonify({
            'success': True,
            'tiers': tiers_data
        })
        
    except Exception as e:
        logging.error(f"Trust tiers error: {e}")
        return jsonify({'error': str(e)}), 500

def register_api_routes(app):
    """Register API routes with the Flask app"""
    app.register_blueprint(api_bp)
    logging.info("API routes registered successfully")