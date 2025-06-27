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

@api_bp.route('/auth/demo-login', methods=['POST'])
def demo_login():
    """Quick demo login for testing"""
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE email = ?', ('demo@rhiz.app',)).fetchone()
    
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
    
    return jsonify({'error': 'Demo user not found'}), 404

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
        
        # Get sync source information
        source_info = db.execute(
            'SELECT source FROM contact_sources WHERE contact_id = ? AND is_primary = 1',
            (contact['id'],)
        ).fetchone()
        
        contact_dict['sync_status'] = source_info['source'] if source_info else 'manual'
        
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
@api_bp.route('/intelligence/suggestions', methods=['GET'])
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
           ORDER BY s.confidence DESC, s.created_at DESC''',
        (user_id,)
    ).fetchall()
    
    return jsonify([dict(suggestion) for suggestion in suggestions])

@api_bp.route('/intelligence/insights', methods=['GET'])
@auth_required
def get_insights():
    user_id = session.get('user_id')
    db = get_db()
    
    # Basic insights
    stats = {}
    
    # Contact count by warmth
    warmth_stats = db.execute(
        'SELECT warmth_label, COUNT(*) as count FROM contacts WHERE user_id = ? GROUP BY warmth_label',
        (user_id,)
    ).fetchall()
    stats['warmth_distribution'] = [dict(row) for row in warmth_stats]
    
    # Goals count
    goals_count = db.execute(
        'SELECT COUNT(*) as count FROM goals WHERE user_id = ?',
        (user_id,)
    ).fetchone()
    stats['total_goals'] = goals_count['count']
    
    # Recent activity
    recent_interactions = db.execute(
        '''SELECT COUNT(*) as count FROM contact_interactions ci
           JOIN contacts c ON ci.contact_id = c.id
           WHERE c.user_id = ? AND ci.timestamp > datetime('now', '-7 days')''',
        (user_id,)
    ).fetchone()
    stats['recent_interactions'] = recent_interactions['count']
    
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

def register_api_routes(app):
    """Register API routes with the Flask app"""
    app.register_blueprint(api_bp)
    logging.info("API routes registered successfully")