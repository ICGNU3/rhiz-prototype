import os
import logging
import sqlite3
from flask import Flask, render_template
from werkzeug.middleware.proxy_fix import ProxyFix

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
    logging.info("Environment variables loaded from .env file")
except ImportError:
    # python-dotenv not installed, use os.environ directly
    logging.info("Loading environment variables from system")

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize database with migration support
def init_db():
    """Initialize the database with schema and handle migrations"""
    import os
    
    # If database doesn't exist, create it fresh
    if not os.path.exists('db.sqlite3'):
        conn = sqlite3.connect('db.sqlite3')
        try:
            with open('schema.sql', 'r') as f:
                conn.executescript(f.read())
            conn.commit()
            logging.info("Database created successfully from schema.sql")
        except FileNotFoundError:
            logging.error("schema.sql not found! Creating basic schema...")
            # Create basic schema if schema.sql is missing
            basic_schema = """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS contacts (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                name TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            CREATE TABLE IF NOT EXISTS goals (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                title TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            """
            conn.executescript(basic_schema)
            conn.commit()
            logging.info("Basic database schema created")
        finally:
            conn.close()
        return
    
    # Check if we need to migrate existing database
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    try:
        # Check if new columns exist
        cursor.execute("PRAGMA table_info(contacts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'warmth_status' not in columns:
            logging.info("Migrating database to new CRM schema...")
            # Drop and recreate with new schema for simplicity in this case
            conn.close()
            os.remove('db.sqlite3')
            # Recreate fresh
            conn = sqlite3.connect('db.sqlite3')
            with open('schema.sql', 'r') as f:
                conn.executescript(f.read())
            conn.commit()
            logging.info("Database migrated successfully")
        else:
            logging.info("Database schema is up to date")
            
    except Exception as e:
        logging.error(f"Migration error: {e}")
        # If anything goes wrong, recreate fresh
        conn.close()
        if os.path.exists('db.sqlite3'):
            os.remove('db.sqlite3')
        conn = sqlite3.connect('db.sqlite3')
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        conn.commit()
        logging.info("Database recreated due to migration error")
    
    finally:
        conn.close()

# Initialize database on startup
try:
    init_db()
    
    # Initialize sync tables for multi-source contact management
    try:
        from services.contact_sync_engine import ContactSyncEngine
        sync_engine = ContactSyncEngine()
        sync_engine.init_sync_tables()
        logging.info("Multi-source contact sync tables initialized")
    except Exception as sync_error:
        logging.warning(f"Sync tables initialization warning: {sync_error}")
        # Continue without sync tables - they'll be created on first use
        
except Exception as e:
    logging.error(f"Failed to initialize database: {e}")

# Create essential API endpoints directly for React frontend integration
from flask import jsonify

# Basic dashboard analytics endpoint
@app.route('/api/dashboard/analytics')
def dashboard_analytics():
    """Dashboard analytics data for React frontend"""
    try:
        # Mock data for now - will be replaced with real database queries
        stats = {
            'totalContacts': 12,
            'activeGoals': 4,
            'aiSuggestions': 8,
            'trustScore': 85,
            'weeklyInteractions': 23,
            'pendingFollowUps': 6
        }
        
        recent_activity = [
            {
                'id': '1',
                'type': 'contact',
                'title': 'New contact added',
                'description': 'Sarah Chen from TechCorp',
                'timestamp': '2025-06-28T20:30:00Z'
            },
            {
                'id': '2', 
                'type': 'goal',
                'title': 'Goal created',
                'description': 'Find technical co-founder',
                'timestamp': '2025-06-28T19:15:00Z'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'stats': stats,
            'recent_activity': recent_activity
        })
    except Exception as e:
        logging.error(f"Dashboard analytics error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Goals API endpoints
@app.route('/api/goals')
def get_goals():
    """Get all goals for the current user"""
    try:
        # Mock data - replace with database queries
        goals = [
            {
                'id': '1',
                'user_id': 'demo_user',
                'title': 'Find technical co-founder',
                'description': 'Looking for a CTO/technical co-founder with React and Python experience',
                'created_at': '2025-06-28T10:00:00Z'
            },
            {
                'id': '2',
                'user_id': 'demo_user', 
                'title': 'Raise seed funding',
                'description': 'Target $500k seed round from angel investors',
                'created_at': '2025-06-28T11:00:00Z'
            }
        ]
        return jsonify(goals)
    except Exception as e:
        logging.error(f"Goals API error: {e}")
        return jsonify({'error': str(e)}), 500

# Contacts API endpoints
@app.route('/api/contacts')
def get_contacts():
    """Get all contacts for the current user"""
    try:
        # Mock data - replace with database queries
        contacts = [
            {
                'id': '1',
                'user_id': 'demo_user',
                'name': 'Sarah Chen',
                'email': 'sarah@techcorp.com',
                'company': 'TechCorp',
                'title': 'Senior Developer',
                'warmth_status': 3,
                'warmth_label': 'Warm',
                'relationship_type': 'professional',
                'priority_level': 'high',
                'created_at': '2025-06-28T10:00:00Z'
            }
        ]
        return jsonify(contacts)
    except Exception as e:
        logging.error(f"Contacts API error: {e}")
        return jsonify({'error': str(e)}), 500

# Intelligence API endpoints
@app.route('/api/ai-suggestions')
def get_ai_suggestions():
    """Get AI suggestions for the current user"""
    try:
        suggestions = [
            {
                'id': '1',
                'contact_id': '1',
                'goal_id': '1',
                'suggestion': 'Sarah Chen might be interested in your technical co-founder role',
                'confidence': 0.85,
                'created_at': '2025-06-28T12:00:00Z'
            }
        ]
        return jsonify(suggestions)
    except Exception as e:
        logging.error(f"AI suggestions error: {e}")
        return jsonify({'error': str(e)}), 500

# Network API endpoint
@app.route('/api/network/graph')
def get_network_graph():
    """Get network graph data"""
    try:
        graph_data = {
            'nodes': [
                {'id': 'user', 'name': 'You', 'type': 'user'},
                {'id': '1', 'name': 'Sarah Chen', 'type': 'contact'},
                {'id': 'goal_1', 'name': 'Find CTO', 'type': 'goal'}
            ],
            'edges': [
                {'id': 'e1', 'source': 'user', 'target': '1', 'type': 'relationship', 'strength': 0.8},
                {'id': 'e2', 'source': 'user', 'target': 'goal_1', 'type': 'goal_match', 'strength': 0.9}
            ]
        }
        return jsonify(graph_data)
    except Exception as e:
        logging.error(f"Network graph error: {e}")
        return jsonify({'error': str(e)}), 500

# Add basic landing page route
@app.route('/')
def landing():
    """Landing page for unauthenticated users"""
    try:
        return render_template('landing.html')
    except Exception as e:
        logging.error(f"Landing page template error: {e}")
        return '''
        <!DOCTYPE html>
        <html lang="en" data-bs-theme="dark">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Rhiz - Relationship Intelligence Platform</title>
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            <style>
                body { background: #1a1a1a; color: white; font-family: 'Inter', sans-serif; }
                .container { max-width: 800px; margin: 100px auto; padding: 40px; text-align: center; }
                .glass-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); 
                             border-radius: 20px; padding: 40px; backdrop-filter: blur(10px); }
                .btn-primary { background: linear-gradient(135deg, #3b82f6, #8b5cf6); border: none; 
                              padding: 12px 24px; border-radius: 10px; text-decoration: none; 
                              color: white; display: inline-block; margin: 10px; }
                .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(59,130,246,0.3); }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="glass-card">
                    <h1 style="font-size: 3rem; margin-bottom: 1rem; background: linear-gradient(135deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Rhiz</h1>
                    <p style="font-size: 1.2rem; margin-bottom: 2rem; opacity: 0.8;">Relationship Intelligence Platform</p>
                    <p style="margin-bottom: 2rem;">High-context relationship intelligence for builders who activate meaningful connections.</p>
                    <a href="/about" class="btn-primary">Learn More</a>
                    <a href="/founders-log" class="btn-primary">Founder's Log</a>
                </div>
            </div>
        </body>
        </html>
        '''

@app.route('/about')
def about():
    """About page"""
    try:
        return render_template('about.html')
    except:
        return "About page - Rhiz platform"

@app.route('/founders-log')
def founders_log():
    """Founder's log page"""
    try:
        return render_template('founders-log.html')
    except:
        return "Founder's log - Build updates and transparency"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
