import os
import logging
import sqlite3
from flask import Flask, render_template, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
import psycopg2
from psycopg2.extras import RealDictCursor

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

# Contact Import API endpoints
@app.route('/api/contacts/upload', methods=['POST'])
def upload_contacts():
    """Upload and parse CSV contacts file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'Only CSV files are supported'}), 400
        
        # Read and parse CSV file
        import csv
        import io
        
        # Read file content
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        
        contacts_imported = 0
        failed_imports = 0
        user_id = 'demo_user'  # For now, use demo user
        
        # Connect to database
        conn = psycopg2.connect(
            host=os.environ.get('PGHOST'),
            database=os.environ.get('PGDATABASE'),
            user=os.environ.get('PGUSER'),
            password=os.environ.get('PGPASSWORD'),
            port=os.environ.get('PGPORT')
        )
        cursor = conn.cursor()
        
        # Create contacts table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                phone VARCHAR(50),
                company VARCHAR(255),
                title VARCHAR(255),
                notes TEXT,
                source VARCHAR(50) DEFAULT 'csv_upload',
                warmth_status INTEGER DEFAULT 1,
                warmth_label VARCHAR(50) DEFAULT 'Cold',
                relationship_type VARCHAR(50) DEFAULT 'professional',
                priority_level VARCHAR(50) DEFAULT 'medium',
                tags TEXT,
                linkedin_url VARCHAR(500),
                twitter_url VARCHAR(500),
                website_url VARCHAR(500),
                address TEXT,
                birthday DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        for row in csv_input:
            try:
                # Map CSV columns to contact fields (flexible mapping)
                name = (row.get('Name') or row.get('name') or 
                       row.get('Full Name') or row.get('full_name') or
                       f"{row.get('First Name', '')} {row.get('Last Name', '')}".strip() or
                       f"{row.get('first_name', '')} {row.get('last_name', '')}".strip())
                
                email = (row.get('Email') or row.get('email') or 
                        row.get('Email Address') or row.get('email_address'))
                
                phone = (row.get('Phone') or row.get('phone') or
                        row.get('Phone Number') or row.get('phone_number'))
                
                company = (row.get('Company') or row.get('company') or
                          row.get('Organization') or row.get('organization'))
                
                title = (row.get('Title') or row.get('title') or
                        row.get('Job Title') or row.get('job_title') or
                        row.get('Position') or row.get('position'))
                
                notes = (row.get('Notes') or row.get('notes') or
                        row.get('Description') or row.get('description'))
                
                linkedin_url = (row.get('LinkedIn') or row.get('linkedin') or
                               row.get('LinkedIn URL') or row.get('linkedin_url'))
                
                # Skip if no name
                if not name or name.strip() == '':
                    failed_imports += 1
                    continue
                
                # Insert contact into database
                cursor.execute('''
                    INSERT INTO contacts (user_id, name, email, phone, company, title, notes, source, linkedin_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (user_id, name.strip(), email, phone, company, title, notes, 'csv_upload', linkedin_url))
                
                contacts_imported += 1
                
            except Exception as row_error:
                logging.error(f"Failed to import row: {row_error}")
                failed_imports += 1
                continue
        
        # Record the import in contact_sources table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_sources (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                source_type VARCHAR(50) NOT NULL,
                source_name VARCHAR(255) NOT NULL,
                import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_contacts INTEGER DEFAULT 0,
                successful_imports INTEGER DEFAULT 0,
                failed_imports INTEGER DEFAULT 0,
                status VARCHAR(50) DEFAULT 'completed'
            )
        ''')
        
        cursor.execute('''
            INSERT INTO contact_sources (user_id, source_type, source_name, total_contacts, successful_imports, failed_imports)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (user_id, 'csv_upload', file.filename, contacts_imported + failed_imports, contacts_imported, failed_imports))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': f'Successfully imported {contacts_imported} contacts',
            'contacts_imported': contacts_imported,
            'failed_imports': failed_imports,
            'total_processed': contacts_imported + failed_imports
        })
        
    except Exception as e:
        logging.error(f"Contact upload error: {e}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/contacts/sync/status')
def get_sync_status():
    """Get status of contact sync operations"""
    try:
        user_id = 'demo_user'
        
        conn = psycopg2.connect(
            host=os.environ.get('PGHOST'),
            database=os.environ.get('PGDATABASE'),
            user=os.environ.get('PGUSER'),
            password=os.environ.get('PGPASSWORD'),
            port=os.environ.get('PGPORT')
        )
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Create contact_sources table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contact_sources (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(255) NOT NULL,
                source_type VARCHAR(50) NOT NULL,
                source_name VARCHAR(255) NOT NULL,
                import_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_contacts INTEGER DEFAULT 0,
                successful_imports INTEGER DEFAULT 0,
                failed_imports INTEGER DEFAULT 0,
                status VARCHAR(50) DEFAULT 'completed'
            )
        ''')
        
        # Get recent import history
        cursor.execute('''
            SELECT source_type, source_name, import_date, successful_imports, failed_imports, status
            FROM contact_sources 
            WHERE user_id = %s 
            ORDER BY import_date DESC 
            LIMIT 10
        ''', (user_id,))
        
        imports = cursor.fetchall()
        
        # Get total contact count
        cursor.execute('SELECT COUNT(*) as total FROM contacts WHERE user_id = %s', (user_id,))
        total_contacts = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'total_contacts': total_contacts,
            'recent_imports': [dict(imp) for imp in imports],
            'available_sources': [
                {'name': 'CSV Upload', 'type': 'csv_upload', 'status': 'available'},
                {'name': 'Gmail Contacts', 'type': 'gmail', 'status': 'coming_soon'},
                {'name': 'LinkedIn Connections', 'type': 'linkedin', 'status': 'coming_soon'},
                {'name': 'Phone Contacts', 'type': 'phone', 'status': 'coming_soon'},
                {'name': 'iCloud Contacts', 'type': 'icloud', 'status': 'coming_soon'}
            ]
        })
        
    except Exception as e:
        logging.error(f"Sync status error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/sync/<source_type>', methods=['POST'])
def sync_contacts(source_type):
    """Trigger contact sync from external sources (placeholder for now)"""
    try:
        user_id = 'demo_user'
        
        # For now, return placeholder responses for external integrations
        if source_type == 'gmail':
            return jsonify({
                'status': 'coming_soon',
                'message': 'Gmail integration coming soon. Please use CSV upload for now.',
                'oauth_url': '/auth/gmail'  # Placeholder
            })
        elif source_type == 'linkedin':
            return jsonify({
                'status': 'coming_soon', 
                'message': 'LinkedIn integration coming soon. You can export your LinkedIn connections as CSV.',
                'oauth_url': '/auth/linkedin'  # Placeholder
            })
        elif source_type == 'phone':
            return jsonify({
                'status': 'coming_soon',
                'message': 'Phone contacts sync coming soon.',
                'instructions': 'For now, you can export your phone contacts as vCard and convert to CSV.'
            })
        else:
            return jsonify({'error': 'Unknown sync source'}), 400
            
    except Exception as e:
        logging.error(f"Contact sync error: {e}")
        return jsonify({'error': str(e)}), 500

# Contact Import frontend page
@app.route('/app/contacts/import')
def contact_import_page():
    """Serve contact import interface"""
    try:
        return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Import Contacts - Rhiz</title>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
            <style>
                .glass-card {
                    background: rgba(255,255,255,0.05);
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 16px;
                    backdrop-filter: blur(10px);
                }
                .gradient-text {
                    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                .upload-area {
                    border: 2px dashed rgba(255,255,255,0.3);
                    transition: all 0.3s ease;
                }
                .upload-area:hover {
                    border-color: rgba(59, 130, 246, 0.5);
                    background: rgba(59, 130, 246, 0.05);
                }
                .upload-area.dragover {
                    border-color: #3b82f6;
                    background: rgba(59, 130, 246, 0.1);
                }
            </style>
        </head>
        <body class="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900">
            <!-- Navigation -->
            <nav class="glass-card m-4 p-4">
                <div class="flex justify-between items-center">
                    <h1 class="text-2xl font-bold gradient-text">Rhiz</h1>
                    <div class="space-x-4">
                        <a href="/app/dashboard" class="text-white hover:text-blue-300">Dashboard</a>
                        <a href="/app/contacts" class="text-white hover:text-blue-300">Contacts</a>
                        <a href="/app/goals" class="text-white hover:text-blue-300">Goals</a>
                        <a href="/app/intelligence" class="text-white hover:text-blue-300">Intelligence</a>
                    </div>
                </div>
            </nav>

            <div class="container mx-auto px-4 py-8">
                <div class="max-w-4xl mx-auto">
                    <h2 class="text-3xl font-bold text-white mb-2">Import Contacts</h2>
                    <p class="text-gray-300 mb-8">Add contacts from various sources to build your network</p>
                    
                    <!-- Import Options -->
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                        <!-- CSV Upload -->
                        <div class="glass-card p-6">
                            <h3 class="text-xl font-semibold text-white mb-4">📄 CSV Upload</h3>
                            <p class="text-gray-300 mb-4">Upload a CSV file with your contacts</p>
                            
                            <div id="upload-area" class="upload-area p-8 text-center rounded-lg mb-4">
                                <div class="text-4xl mb-4">📁</div>
                                <p class="text-white mb-2">Drop your CSV file here or</p>
                                <button onclick="document.getElementById('file-input').click()" 
                                        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
                                    Choose File
                                </button>
                                <input type="file" id="file-input" accept=".csv" style="display: none;">
                                <p class="text-gray-400 text-sm mt-2">Supports: Name, Email, Phone, Company, Title</p>
                            </div>
                            
                            <div id="upload-progress" class="hidden">
                                <div class="bg-gray-700 rounded-full h-2 mb-2">
                                    <div id="progress-bar" class="bg-blue-600 h-2 rounded-full" style="width: 0%"></div>
                                </div>
                                <p id="progress-text" class="text-gray-300 text-sm"></p>
                            </div>
                            
                            <div id="upload-result" class="hidden mt-4"></div>
                        </div>

                        <!-- Sync Status -->
                        <div class="glass-card p-6">
                            <h3 class="text-xl font-semibold text-white mb-4">📊 Import Status</h3>
                            <div id="sync-status">
                                <p class="text-gray-300">Loading status...</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- External Sync Options -->
                    <div class="glass-card p-6 mb-8">
                        <h3 class="text-xl font-semibold text-white mb-6">🔗 Sync from External Sources</h3>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            <button onclick="syncFromSource('gmail')" 
                                    class="p-4 bg-red-600 bg-opacity-20 border border-red-500 border-opacity-30 rounded-lg hover:bg-opacity-30 transition-all">
                                <div class="text-2xl mb-2">📧</div>
                                <div class="text-white font-medium">Gmail</div>
                                <div class="text-gray-400 text-sm">Coming Soon</div>
                            </button>
                            
                            <button onclick="syncFromSource('linkedin')" 
                                    class="p-4 bg-blue-600 bg-opacity-20 border border-blue-500 border-opacity-30 rounded-lg hover:bg-opacity-30 transition-all">
                                <div class="text-2xl mb-2">💼</div>
                                <div class="text-white font-medium">LinkedIn</div>
                                <div class="text-gray-400 text-sm">Coming Soon</div>
                            </button>
                            
                            <button onclick="syncFromSource('phone')" 
                                    class="p-4 bg-green-600 bg-opacity-20 border border-green-500 border-opacity-30 rounded-lg hover:bg-opacity-30 transition-all">
                                <div class="text-2xl mb-2">📱</div>
                                <div class="text-white font-medium">Phone</div>
                                <div class="text-gray-400 text-sm">Coming Soon</div>
                            </button>
                            
                            <button onclick="syncFromSource('icloud')" 
                                    class="p-4 bg-purple-600 bg-opacity-20 border border-purple-500 border-opacity-30 rounded-lg hover:bg-opacity-30 transition-all">
                                <div class="text-2xl mb-2">☁️</div>
                                <div class="text-white font-medium">iCloud</div>
                                <div class="text-gray-400 text-sm">Coming Soon</div>
                            </button>
                        </div>
                    </div>
                    
                    <!-- Recent Imports -->
                    <div class="glass-card p-6">
                        <h3 class="text-xl font-semibold text-white mb-4">📈 Recent Imports</h3>
                        <div id="recent-imports">
                            <p class="text-gray-300">Loading recent imports...</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                // File upload handling
                const uploadArea = document.getElementById('upload-area');
                const fileInput = document.getElementById('file-input');
                const uploadProgress = document.getElementById('upload-progress');
                const progressBar = document.getElementById('progress-bar');
                const progressText = document.getElementById('progress-text');
                const uploadResult = document.getElementById('upload-result');
                
                // Drag and drop
                uploadArea.addEventListener('dragover', (e) => {
                    e.preventDefault();
                    uploadArea.classList.add('dragover');
                });
                
                uploadArea.addEventListener('dragleave', () => {
                    uploadArea.classList.remove('dragover');
                });
                
                uploadArea.addEventListener('drop', (e) => {
                    e.preventDefault();
                    uploadArea.classList.remove('dragover');
                    const files = e.dataTransfer.files;
                    if (files.length > 0) {
                        handleFileUpload(files[0]);
                    }
                });
                
                fileInput.addEventListener('change', (e) => {
                    if (e.target.files.length > 0) {
                        handleFileUpload(e.target.files[0]);
                    }
                });
                
                function handleFileUpload(file) {
                    if (!file.name.toLowerCase().endsWith('.csv')) {
                        showUploadResult('error', 'Please select a CSV file');
                        return;
                    }
                    
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    // Show progress
                    uploadProgress.classList.remove('hidden');
                    progressText.textContent = 'Uploading file...';
                    progressBar.style.width = '10%';
                    
                    fetch('/api/contacts/upload', {
                        method: 'POST',
                        body: formData,
                        credentials: 'include'
                    })
                    .then(response => {
                        progressBar.style.width = '50%';
                        progressText.textContent = 'Processing contacts...';
                        return response.json();
                    })
                    .then(data => {
                        progressBar.style.width = '100%';
                        progressText.textContent = 'Complete!';
                        
                        setTimeout(() => {
                            uploadProgress.classList.add('hidden');
                            if (data.status === 'success') {
                                showUploadResult('success', 
                                    `Successfully imported ${data.contacts_imported} contacts. ${data.failed_imports} failed.`);
                                loadSyncStatus(); // Refresh status
                            } else {
                                showUploadResult('error', data.error || 'Upload failed');
                            }
                        }, 1000);
                    })
                    .catch(error => {
                        uploadProgress.classList.add('hidden');
                        showUploadResult('error', 'Upload failed: ' + error.message);
                    });
                }
                
                function showUploadResult(type, message) {
                    uploadResult.classList.remove('hidden');
                    uploadResult.className = `mt-4 p-4 rounded-lg ${type === 'success' ? 'bg-green-600 bg-opacity-20 border border-green-500 text-green-300' : 'bg-red-600 bg-opacity-20 border border-red-500 text-red-300'}`;
                    uploadResult.textContent = message;
                    
                    setTimeout(() => {
                        uploadResult.classList.add('hidden');
                    }, 5000);
                }
                
                function syncFromSource(sourceType) {
                    fetch(`/api/contacts/sync/${sourceType}`, {
                        method: 'POST',
                        credentials: 'include',
                        headers: {'Content-Type': 'application/json'}
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'coming_soon') {
                            alert(data.message);
                        } else if (data.oauth_url) {
                            window.location.href = data.oauth_url;
                        }
                    })
                    .catch(error => {
                        alert('Sync failed: ' + error.message);
                    });
                }
                
                function loadSyncStatus() {
                    fetch('/api/contacts/sync/status', {
                        credentials: 'include'
                    })
                    .then(response => response.json())
                    .then(data => {
                        // Update sync status
                        document.getElementById('sync-status').innerHTML = `
                            <div class="text-2xl font-bold text-blue-300 mb-2">${data.total_contacts}</div>
                            <p class="text-gray-300">Total Contacts</p>
                        `;
                        
                        // Update recent imports
                        const recentImports = document.getElementById('recent-imports');
                        if (data.recent_imports && data.recent_imports.length > 0) {
                            recentImports.innerHTML = data.recent_imports.map(imp => `
                                <div class="border-b border-gray-600 pb-2 mb-2">
                                    <div class="flex justify-between items-center">
                                        <span class="text-white font-medium">${imp.source_name}</span>
                                        <span class="text-green-300">${imp.successful_imports} imported</span>
                                    </div>
                                    <p class="text-gray-400 text-sm">${new Date(imp.import_date).toLocaleString()}</p>
                                </div>
                            `).join('');
                        } else {
                            recentImports.innerHTML = '<p class="text-gray-400">No imports yet</p>';
                        }
                    })
                    .catch(error => {
                        console.error('Failed to load sync status:', error);
                    });
                }
                
                // Load initial status
                loadSyncStatus();
            </script>
        </body>
        </html>
        '''
    except Exception as e:
        logging.error(f"Contact import page error: {e}")
        return f"Error loading contact import page: {e}", 500

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

# React frontend routes - serve the React app for authenticated users
@app.route('/app')
@app.route('/app/')
@app.route('/app/<path:path>')
def serve_react_app(path=None):
    """Serve React frontend application"""
    try:
        # For now, serve a functional HTML page that includes working dashboard
        return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Rhiz - Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
            <style>
                .glass-card {
                    background: rgba(255,255,255,0.05);
                    border: 1px solid rgba(255,255,255,0.1);
                    border-radius: 16px;
                    backdrop-filter: blur(10px);
                }
                .gradient-text {
                    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
            </style>
        </head>
        <body class="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-blue-900">
            <!-- Navigation -->
            <nav class="glass-card m-4 p-4">
                <div class="flex justify-between items-center">
                    <h1 class="text-2xl font-bold gradient-text">Rhiz</h1>
                    <div class="space-x-4">
                        <a href="/app/dashboard" class="text-white hover:text-blue-300">Dashboard</a>
                        <a href="/app/contacts" class="text-white hover:text-blue-300">Contacts</a>
                        <a href="/app/goals" class="text-white hover:text-blue-300">Goals</a>
                        <a href="/app/intelligence" class="text-white hover:text-blue-300">Intelligence</a>
                    </div>
                </div>
            </nav>

            <div class="container mx-auto px-4 py-8">
                <!-- Dashboard Stats -->
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div class="glass-card p-6">
                        <h3 class="text-lg font-semibold text-white mb-2">Total Contacts</h3>
                        <p class="text-3xl font-bold text-blue-300" id="totalContacts">Loading...</p>
                    </div>
                    <div class="glass-card p-6">
                        <h3 class="text-lg font-semibold text-white mb-2">Active Goals</h3>
                        <p class="text-3xl font-bold text-green-300" id="activeGoals">Loading...</p>
                    </div>
                    <div class="glass-card p-6">
                        <h3 class="text-lg font-semibold text-white mb-2">Trust Score</h3>
                        <p class="text-3xl font-bold text-purple-300" id="trustScore">Loading...</p>
                    </div>
                </div>
                
                <!-- Quick Actions -->
                <div class="glass-card p-6 mb-8">
                    <h3 class="text-xl font-semibold text-white mb-4">Quick Actions</h3>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <button onclick="navigateTo('/app/contacts')" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-lg text-center">
                            Add Contact
                        </button>
                        <button onclick="navigateTo('/app/goals')" class="bg-green-600 hover:bg-green-700 text-white px-4 py-3 rounded-lg text-center">
                            Create Goal
                        </button>
                        <button onclick="navigateTo('/app/intelligence')" class="bg-purple-600 hover:bg-purple-700 text-white px-4 py-3 rounded-lg text-center">
                            AI Insights
                        </button>
                        <button onclick="navigateTo('/app/intelligence')" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-3 rounded-lg text-center">
                            Send Message
                        </button>
                    </div>
                </div>
                
                <!-- Recent Activity -->
                <div class="glass-card p-6">
                    <h3 class="text-xl font-semibold text-white mb-4">Recent Activity</h3>
                    <div id="recentActivity">Loading...</div>
                </div>
            </div>
            
            <script>
                // Load dashboard data from working API endpoint
                fetch('/api/dashboard/analytics', {
                    credentials: 'include',
                    headers: {'Content-Type': 'application/json'}
                })
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'success') {
                        document.getElementById('totalContacts').textContent = data.stats.totalContacts;
                        document.getElementById('activeGoals').textContent = data.stats.activeGoals;
                        document.getElementById('trustScore').textContent = data.stats.trustScore + '%';
                        
                        const activityHtml = data.recent_activity.map(activity => 
                            `<div class="border-b border-gray-600 pb-3 mb-3">
                                <div class="flex items-center space-x-2">
                                    <span class="inline-block w-2 h-2 bg-blue-400 rounded-full"></span>
                                    <p class="text-white font-medium">${activity.title}</p>
                                </div>
                                <p class="text-gray-300 ml-4">${activity.description}</p>
                                <p class="text-gray-400 text-sm ml-4">${new Date(activity.timestamp).toLocaleString()}</p>
                            </div>`
                        ).join('');
                        document.getElementById('recentActivity').innerHTML = activityHtml;
                    }
                })
                .catch(err => {
                    console.error('Failed to load dashboard:', err);
                    document.getElementById('totalContacts').textContent = 'Error';
                    document.getElementById('activeGoals').textContent = 'Error';
                    document.getElementById('trustScore').textContent = 'Error';
                    document.getElementById('recentActivity').innerHTML = '<p class="text-red-300">Failed to load activity</p>';
                });
                
                function navigateTo(path) {
                    window.location.href = path;
                }
            </script>
        </body>
        </html>
        '''
    except Exception as e:
        logging.error(f"React app serving error: {e}")
        return f"Error serving React app: {e}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
