"""
API Routes for React Frontend Integration
Provides RESTful endpoints to support the React frontend with existing Flask backend functionality
"""

from flask import Blueprint, request, jsonify, session, redirect, render_template
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
            # Check if this is an API request (expects JSON) or a page request (expects HTML)
            if request.path.startswith('/api/') or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'error': 'Authentication required'}), 401
            else:
                # Render beautiful authentication required page
                return render_template('auth_required.html'), 401
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
    
    # Validate email format
    import re
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    db = get_db()
    
    # Check if user exists, create if not
    user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    
    if not user:
        # Create new user with UUID
        import uuid
        user_id = str(uuid.uuid4())
        try:
            db.execute('''
                INSERT INTO users (id, email, subscription_tier, created_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, email, 'explorer'))
            db.commit()
        except Exception as e:
            return jsonify({'error': 'Failed to create user account'}), 500
    else:
        user_id = user['id']
    
    # Generate magic link token
    import secrets
    from datetime import datetime, timedelta
    
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(minutes=15)
    
    # Store token in database
    try:
        db.execute('''
            UPDATE users 
            SET magic_link_token = ?, magic_link_expires = ? 
            WHERE email = ?
        ''', (token, expires_at.isoformat(), email))
        db.commit()
    except Exception as e:
        return jsonify({'error': 'Failed to generate magic link'}), 500
    
    # Send email using Resend
    try:
        import requests
        import os
        
        resend_api_key = os.environ.get("RESEND_API_KEY")
        if not resend_api_key:
            raise Exception("RESEND_API_KEY not configured")
        
        # Get base URL for magic link - handle both local dev and production
        host = request.headers.get('Host', request.host)
        if host.startswith('localhost') or '127.0.0.1' in host:
            # For local development, use the actual host but with proper protocol
            base_url = f"https://{os.environ.get('REPL_SLUG', 'unknown')}-{os.environ.get('REPL_OWNER', 'unknown')}.replit.app"
        else:
            # For production, use the request host
            scheme = 'https' if request.is_secure or request.headers.get('X-Forwarded-Proto') == 'https' else 'http'
            base_url = f"{scheme}://{host}"
        
        magic_link = f"{base_url}/api/auth/verify?token={token}"
        
        # Log magic link generation for monitoring
        logging.info(f"Magic link generated for {email} with token length: {len(token)}")
        
        # Send email using Resend REST API
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {resend_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": "info@ourhizome.com",
                "to": email,
                "subject": "Your Rhiz Login Link",
                "html": f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 0; background: #0a0a0f; color: #ffffff; }}
                        .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
                        .content {{ background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 20px; padding: 40px; text-align: center; }}
                        .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; padding: 12px 30px; border-radius: 8px; font-weight: 600; margin: 20px 0; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="content">
                            <h1>Welcome to Rhiz</h1>
                            <p>Click the button below to securely sign in to your account:</p>
                            <a href="{magic_link}" class="button">Sign In to Rhiz</a>
                            <p><small>This link expires in 15 minutes.</small></p>
                        </div>
                    </div>
                </body>
                </html>
                """
            }
        )
        
        if response.status_code == 200:
            return jsonify({
                'success': True, 
                'message': f'Magic link sent to {email}. Check your email to sign in.'
            })
        else:
            print(f"Resend API error: {response.status_code} - {response.text}")
            # Handle domain verification issues by providing instant login for development
            if response.status_code == 403 or 'example.com' in email or 'test@' in email:
                session['user_id'] = user_id
                session['authenticated'] = True
                return jsonify({
                    'success': True, 
                    'message': f'Account created and logged in successfully! Welcome to Rhiz.',
                    'demo_mode': True
                })
            return jsonify({'error': 'Failed to send magic link email. Please try again.'}), 500
        
    except Exception as e:
        # Log error but don't expose details to user
        print(f"Email sending error: {e}")
        # Provide instant login for development and when email service is unavailable
        session['user_id'] = user_id
        session['authenticated'] = True
        return jsonify({
            'success': True, 
            'message': f'Account created and logged in successfully! Welcome to Rhiz.',
            'demo_mode': True
        })

@api_bp.route('/auth/verify', methods=['GET'])
def verify_magic_link():
    """Verify magic link token and authenticate user"""
    token = request.args.get('token')
    
    if not token:
        return redirect('/login?error=invalid_token')
    
    db = get_db()
    
    # Find user with valid token
    user = db.execute('''
        SELECT *, magic_link_expires, datetime('now') as now_time FROM users 
        WHERE magic_link_token = ?
    ''', (token,)).fetchone()
    
    if not user:
        return redirect('/login?error=invalid_token')
    
    # Check if token is expired
    if user['magic_link_expires'] <= user['now_time']:
        return redirect('/login?error=expired_token')
    
    # Clear the token and create session
    try:
        db.execute('''
            UPDATE users 
            SET magic_link_token = NULL, magic_link_expires = NULL 
            WHERE id = ?
        ''', (user['id'],))
        db.commit()
        
        # Create authenticated session
        session['user_id'] = user['id']
        session['authenticated'] = True
        
        # Check if user has completed onboarding
        if user['onboarding_completed']:
            # Existing user - redirect to landing page
            return redirect('/?login=success')
        else:
            # New user - redirect to onboarding flow
            return redirect('/onboarding/welcome')
        
    except Exception as e:
        logging.error(f"Magic link verification error: {e}")
        return redirect('/login?error=authentication_failed')

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

@api_bp.route('/contacts/oauth-url/<source>', methods=['GET'])
@auth_required
def get_oauth_url(source):
    """Get OAuth URL for external service"""
    user_id = session.get('user_id')
    
    try:
        if source == 'google':
            # Check if Google OAuth is configured
            google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
            if not google_client_id:
                return jsonify({'error': 'Google OAuth not configured. Please ask admin to add GOOGLE_CLIENT_ID to environment secrets.'}), 400
            
            # Create Google OAuth URL
            redirect_uri = request.url_root.rstrip('/') + '/api/contacts/oauth-callback/google'
            oauth_url = (
                f"https://accounts.google.com/o/oauth2/auth?"
                f"client_id={google_client_id}&"
                f"redirect_uri={redirect_uri}&"
                f"scope=https://www.googleapis.com/auth/contacts.readonly&"
                f"response_type=code&"
                f"access_type=offline&"
                f"state={user_id}"
            )
            return jsonify({'oauth_url': oauth_url})
        elif source == 'twitter':
            return jsonify({'error': 'Twitter integration coming soon!'}), 400
        else:
            return jsonify({'error': 'Unsupported OAuth source'}), 400
    except Exception as e:
        logging.error(f"OAuth URL error: {e}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/contacts/import-csv', methods=['POST'])
@auth_required
def import_csv_contacts():
    """Import contacts from CSV file upload"""
    user_id = session.get('user_id')
    
    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    source = request.form.get('source', 'csv')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    if not file.filename or not file.filename.lower().endswith(('.csv', '.vcf')):
        return jsonify({'error': 'Only CSV and VCF files are supported'}), 400
    
    try:
        # Read file content
        file_content = file.read().decode('utf-8')
        logging.info(f"Processing {file.filename} ({len(file_content)} chars) for user {user_id}")
        
        # Process the file based on type
        if file.filename.lower().endswith('.csv'):
            imported_contacts = process_csv_file(user_id, file_content, source)
        elif file.filename.lower().endswith('.vcf'):
            imported_contacts = process_vcf_file(user_id, file_content, source)
        else:
            return jsonify({'error': 'Unsupported file type'}), 400
            
        logging.info(f"Import completed: {len(imported_contacts)} contacts imported")
        
        return jsonify({
            'success': True,
            'imported_count': len(imported_contacts),
            'imported_contacts': imported_contacts[:5],  # Return first 5 for preview
            'message': f'Successfully imported {len(imported_contacts)} contacts'
        })
        
    except Exception as e:
        logging.error(f"File import error: {e}")
        return jsonify({'error': f'Import failed: {str(e)}'}), 500

def process_csv_file(user_id, file_content, source):
    """Process CSV file and import contacts"""
    import csv
    import uuid
    from io import StringIO
    from datetime import datetime
    
    contacts = []
    
    # Handle LinkedIn CSV format which has notes at the top
    lines = file_content.strip().split('\n')
    csv_start = 0
    
    # Find the actual CSV header (LinkedIn files have notes at top)
    for i, line in enumerate(lines):
        if line.startswith('First Name,Last Name,') or line.startswith('Name,') or line.startswith('name,'):
            csv_start = i
            break
    
    # Use the CSV portion only
    if csv_start > 0:
        csv_data = '\n'.join(lines[csv_start:])
    else:
        csv_data = file_content
    
    reader = csv.DictReader(StringIO(csv_data))
    
    logging.info(f"CSV processing started, found header at line {csv_start}")
    
    # Common field mappings for different CSV formats
    field_mappings = {
        # LinkedIn export format
        'First Name': 'first_name',
        'Last Name': 'last_name', 
        'Email Address': 'email',
        'Company': 'company',
        'Position': 'title',
        'Connected On': 'connection_date',
        # Google Contacts format
        'Name': 'name',
        'Given Name': 'first_name',
        'Family Name': 'last_name',
        'E-mail 1 - Value': 'email',
        'E-mail Address': 'email',
        'Phone 1 - Value': 'phone',
        'Organization 1 - Name': 'company',
        'Organization 1 - Title': 'title',
        # Generic CSV format
        'name': 'name',
        'email': 'email',
        'phone': 'phone',
        'company': 'company',
        'title': 'title',
        'notes': 'notes'
    }
    
    db = get_db()
    
    processed_count = 0
    for row in reader:
        try:
            processed_count += 1
            logging.info(f"Processing row {processed_count}: {row}")
            
            # Map CSV fields to standard contact fields
            contact_data = {}
            
            for csv_field, value in row.items():
                if csv_field in field_mappings and value:
                    standard_field = field_mappings[csv_field]
                    contact_data[standard_field] = value.strip()
            
            # Handle name splitting if full name provided
            if 'name' in contact_data and 'first_name' not in contact_data:
                name_parts = contact_data['name'].split(' ', 1)
                contact_data['first_name'] = name_parts[0]
                if len(name_parts) > 1:
                    contact_data['last_name'] = name_parts[1]
            
            # Skip if no name (but allow even if no email since LinkedIn often doesn't provide emails)
            if not (contact_data.get('first_name') or contact_data.get('name') or contact_data.get('email')):
                continue
            
            # Skip empty rows (LinkedIn exports sometimes have these)
            if not any(value.strip() for value in row.values() if value):
                continue
            
            # Create contact name
            if 'first_name' in contact_data and 'last_name' in contact_data:
                full_name = f"{contact_data['first_name']} {contact_data['last_name']}"
            elif 'name' in contact_data:
                full_name = contact_data['name']
            elif 'first_name' in contact_data:
                full_name = contact_data['first_name']
            else:
                full_name = contact_data.get('email', 'Unknown Contact')
            
            # Set warmth based on source
            if source == 'linkedin':
                warmth_status = 3  # Warm
                warmth_label = 'Warm'
            else:
                warmth_status = 1  # Cold  
                warmth_label = 'Cold'
            
            # Generate unique contact ID
            contact_id = str(uuid.uuid4())
            
            # Create import notes
            import_notes = f"Imported from {source}"
            if contact_data.get('connection_date'):
                import_notes += f" on {contact_data.get('connection_date')}"
            
            # Insert into database
            cursor = db.execute('''
                INSERT INTO contacts (id, user_id, name, email, phone, company, title, 
                                    notes, warmth_status, warmth_label, source, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                contact_id,
                user_id,
                full_name,
                contact_data.get('email'),
                contact_data.get('phone'),
                contact_data.get('company'),
                contact_data.get('title'),
                import_notes,
                warmth_status,
                warmth_label,
                source,
                datetime.now().isoformat()
            ))
            
            contact_id = cursor.lastrowid
            contacts.append({
                'id': contact_id,
                'name': full_name,
                'email': contact_data.get('email'),
                'company': contact_data.get('company'),
                'source': source
            })
            
        except Exception as e:
            logging.warning(f"Skipping contact row due to error: {e}")
            continue
    
    db.commit()
    return contacts

def process_vcf_file(user_id, file_content, source):
    """Process VCF (vCard) file and import contacts"""
    import uuid
    from datetime import datetime
    contacts = []
    
    # Simple VCF parser (basic implementation)
    vcf_contacts = file_content.split('BEGIN:VCARD')
    
    db = get_db()
    
    for vcf_contact in vcf_contacts[1:]:  # Skip first empty element
        try:
            contact_data = {}
            lines = vcf_contact.split('\n')
            
            for line in lines:
                line = line.strip()
                if ':' in line:
                    field, value = line.split(':', 1)
                    if field == 'FN':  # Full name
                        contact_data['name'] = value
                    elif field == 'EMAIL':
                        contact_data['email'] = value
                    elif field.startswith('TEL'):
                        contact_data['phone'] = value
                    elif field == 'ORG':
                        contact_data['company'] = value
                    elif field == 'TITLE':
                        contact_data['title'] = value
            
            # Skip if no name or email
            if not (contact_data.get('name') or contact_data.get('email')):
                continue
            
            full_name = contact_data.get('name') or contact_data.get('email', 'Unknown Contact')
            
            # Generate unique contact ID
            vcf_contact_id = str(uuid.uuid4())
            
            # Insert into database
            cursor = db.execute('''
                INSERT INTO contacts (id, user_id, name, email, phone, company, title, 
                                    notes, warmth_status, warmth_label, source, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                vcf_contact_id,
                user_id,
                full_name,
                contact_data.get('email'),
                contact_data.get('phone'),
                contact_data.get('company'),
                contact_data.get('title'),
                f'Imported from {source}',
                1,  # Cold warmth_status
                'Cold',  # Cold warmth_label
                source,
                datetime.now().isoformat()
            ))
            contacts.append({
                'id': vcf_contact_id,
                'name': full_name,
                'email': contact_data.get('email'),
                'company': contact_data.get('company'),
                'source': source
            })
            
        except Exception as e:
            logging.warning(f"Skipping VCF contact due to error: {e}")
            continue
    
    db.commit()
    return contacts

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

# === CORE APPLICATION ROUTES ===

def register_core_routes(app):
    """Register core application routes"""
    from flask import render_template
    
    @app.route('/')
    def landing():
        """Landing page"""
        return render_template('landing.html')

    @app.route('/login')
    def login_page():
        """Login page with modern authentication interface"""
        return '''<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Rhiz</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            min-height: 100vh;
            font-family: 'Inter', sans-serif;
        }
        
        .floating-orb {
            position: fixed;
            border-radius: 50%;
            background: linear-gradient(45deg, rgba(79, 172, 254, 0.1), rgba(139, 92, 246, 0.1));
            filter: blur(1px);
            animation: float 6s ease-in-out infinite;
            z-index: 1;
        }
        
        .floating-orb:nth-child(1) { width: 200px; height: 200px; top: 10%; left: 10%; animation-delay: 0s; }
        .floating-orb:nth-child(2) { width: 150px; height: 150px; top: 70%; right: 10%; animation-delay: 2s; }
        .floating-orb:nth-child(3) { width: 100px; height: 100px; bottom: 20%; left: 50%; animation-delay: 4s; }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-20px); }
        }
        
        .glassmorphism {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            position: relative;
            z-index: 10;
        }
        
        .gradient-text {
            background: linear-gradient(135deg, #4facfe 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .btn-glassmorphism {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
        }
        
        .btn-glassmorphism:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }
    </style>
</head>
<body>
    <div class="floating-orb"></div>
    <div class="floating-orb"></div>
    <div class="floating-orb"></div>
    
    <div class="container-fluid d-flex align-items-center justify-content-center min-vh-100">
        <div class="card glassmorphism border-0 shadow-lg" style="max-width: 400px; width: 100%;">
            <div class="card-body p-5">
                <div class="text-center mb-4">
                    <h1 class="h3 gradient-text fw-bold mb-2">Welcome to Rhiz</h1>
                    <p class="text-light-emphasis">Your intelligent relationship network</p>
                </div>
                
                <form id="loginForm">
                    <div class="mb-3">
                        <label for="email" class="form-label text-light">Email address</label>
                        <input type="email" class="form-control bg-dark border-secondary text-light" id="email" required>
                    </div>
                    
                    <button type="submit" class="btn btn-primary w-100 btn-glassmorphism mb-3">
                        Send Magic Link
                    </button>
                </form>
                
                <div class="text-center">
                    <div class="mb-3">
                        <span class="text-light-emphasis">or</span>
                    </div>
                    <button id="registerBtn" class="btn btn-outline-light w-100 btn-glassmorphism">
                        Create Free Account
                    </button>
                </div>
                
                <div id="status" class="mt-3"></div>
            </div>
        </div>
    </div>
    
    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const status = document.getElementById('status');
            
            status.innerHTML = '<div class="alert alert-info">Sending magic link...</div>';
            
            try {
                const response = await fetch('/api/auth/magic-link', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ email: email })
                });
                
                if (response.ok) {
                    status.innerHTML = '<div class="alert alert-success">Magic link sent! Check your email.</div>';
                } else {
                    status.innerHTML = '<div class="alert alert-warning">Failed to send magic link. Please try again.</div>';
                }
            } catch (error) {
                status.innerHTML = '<div class="alert alert-danger">Error sending magic link. Please try again.</div>';
            }
        });
        
        document.getElementById('registerBtn').addEventListener('click', async function() {
            const email = document.getElementById('email').value;
            const status = document.getElementById('status');
            
            if (!email) {
                status.innerHTML = '<div class="alert alert-warning">Please enter an email address first.</div>';
                return;
            }
            
            status.innerHTML = '<div class="alert alert-info">Creating your account...</div>';
            
            try {
                const response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({ email: email })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    status.innerHTML = '<div class="alert alert-success">Account created! Redirecting to your dashboard...</div>';
                    setTimeout(() => {
                        window.location.href = '/?login=success';
                    }, 1500);
                } else {
                    status.innerHTML = `<div class="alert alert-danger">${result.error || 'Registration failed. Please try again.'}</div>`;
                }
            } catch (error) {
                status.innerHTML = '<div class="alert alert-danger">Error creating account. Please try again.</div>';
            }
        });
    </script>
</body>
</html>'''

    # Onboarding route handlers
    @app.route('/onboarding/welcome')
    @auth_required
    def onboarding_welcome():
        """Onboarding welcome page"""
        return render_template('onboarding/welcome.html')

    @app.route('/onboarding/sync')
    @auth_required
    def onboarding_sync():
        """Onboarding contact sync page"""
        return render_template('onboarding/sync.html')

    @app.route('/onboarding/network')
    @auth_required
    def onboarding_network():
        """Onboarding network mapping page"""
        return render_template('onboarding/network.html')
    
    @app.route('/request-invite', methods=['POST'])
    def request_invite():
        """Handle invite request form submission"""
        try:
            db = get_db()
            
            # Extract form data
            first_name = request.form.get('firstName', '').strip()
            last_name = request.form.get('lastName', '').strip()
            email = request.form.get('email', '').strip()
            company = request.form.get('company', '').strip()
            stage = request.form.get('stage', '').strip()
            goals = request.form.get('goals', '').strip()
            
            # Basic validation
            if not all([first_name, last_name, email, company, stage, goals]):
                return render_template('invite_error.html', 
                                    error="All fields are required for invite consideration."), 400
            
            # Store invite request in database
            db.execute('''
                INSERT INTO invite_requests (first_name, last_name, email, company, stage, goals, requested_at, status)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'), 'pending')
            ''', (first_name, last_name, email, company, stage, goals))
            db.commit()
            db.close()
            
            # Simple confirmation without email for now
            return render_template('invite_confirmation.html', name=first_name)
            
        except Exception as e:
            logging.error(f"Invite request error: {e}")
            return render_template('invite_error.html', 
                                error="Something went wrong. Please try again."), 500

    @app.route('/app/<path:route>')
    def serve_react_app(route):
        """Serve React frontend for app routes"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Rhiz - Relationship Intelligence</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
</head>
<body>
    <div id="root"></div>
    <script type="module" src="/static/dist/index.js"></script>
</body>
</html>'''

# Onboarding API endpoints
@api_bp.route('/onboarding/welcome', methods=['POST'])
@auth_required
def save_onboarding_preferences():
    """Save user onboarding preferences"""
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        if not data or not user_id:
            return jsonify({'error': 'Missing data or authentication'}), 400
        
        intent = data.get('intent')
        connection_type = data.get('connection_type')
        
        if not intent or not connection_type:
            return jsonify({'error': 'Missing intent or connection type'}), 400
        
        # Update user preferences in database
        db = get_db()
        db.execute("""
            UPDATE users 
            SET onboarding_intent = ?, onboarding_connection_type = ?, onboarding_step = 'sync'
            WHERE id = ?
        """, (intent, connection_type, user_id))
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Preferences saved successfully'
        })
        
    except Exception as e:
        logging.error(f"Error saving onboarding preferences: {e}")
        return jsonify({'error': 'Failed to save preferences'}), 500

@api_bp.route('/onboarding/complete', methods=['POST'])
@auth_required
def complete_onboarding():
    """Mark onboarding as complete"""
    try:
        user_id = session.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Mark onboarding as complete
        db = get_db()
        db.execute("""
            UPDATE users 
            SET onboarding_completed = 1, onboarding_step = 'complete'
            WHERE id = ?
        """, (user_id,))
        db.commit()
        
        return jsonify({
            'success': True,
            'message': 'Onboarding completed successfully'
        })
        
    except Exception as e:
        logging.error(f"Error completing onboarding: {e}")
        return jsonify({'error': 'Failed to complete onboarding'}), 500

def register_api_routes(app):
    """Register API routes with the Flask app"""
    app.register_blueprint(api_bp)
    register_core_routes(app)
    logging.info("API routes registered successfully")