"""
React Frontend Integration for Rhiz
Adds routes to serve the React frontend and provides sample data for demonstration
"""

from flask import Blueprint, send_from_directory, jsonify, request, session
import sqlite3
import os
import logging
from datetime import datetime, timedelta
import json

# Create blueprint for React integration
react_bp = Blueprint('react', __name__)

# Database helper
def get_db():
    db = sqlite3.connect('db.sqlite3')
    db.row_factory = sqlite3.Row
    return db

# Serve React static files
@react_bp.route('/app')
@react_bp.route('/app/')
@react_bp.route('/app/dashboard')
@react_bp.route('/app/goals')
@react_bp.route('/app/contacts')
@react_bp.route('/app/intelligence')
@react_bp.route('/app/settings')
def serve_react():
    """Serve the React frontend for all app routes"""
    try:
        # Get the current route to determine content
        route = request.path
        
        # Route-specific content
        page_content = get_page_content(route)
        
        # In production, this would serve the built React app
        # For development, we'll serve a glassmorphism page with route-specific content
        html_template = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Rhiz - Intelligent Relationship Network</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                :root {
                    --text-primary: #ffffff;
                    --text-secondary: rgba(255, 255, 255, 0.7);
                    --glass-bg: rgba(255, 255, 255, 0.05);
                    --glass-border: rgba(255, 255, 255, 0.1);
                    --primary-500: #4facfe;
                    --primary-400: #6bb6fe;
                    --secondary-500: #8b5cf6;
                    --accent-500: #ec4899;
                }
                
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body { 
                    margin: 0; 
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
                    background: radial-gradient(ellipse at top, #1e3a8a 0%, #0f172a 50%, #0a0b0d 100%);
                    color: var(--text-primary);
                    min-height: 100vh;
                    overflow-x: hidden;
                }
                
                /* Floating background orbs */
                .floating-orbs {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    pointer-events: none;
                    z-index: -1;
                }
                
                .orb {
                    position: absolute;
                    border-radius: 50%;
                    background: linear-gradient(135deg, rgba(79, 172, 254, 0.3), rgba(139, 92, 246, 0.2));
                    animation: float 20s infinite linear;
                    filter: blur(40px);
                }
                
                .orb:nth-child(1) {
                    width: 300px;
                    height: 300px;
                    top: -150px;
                    left: -150px;
                    animation-delay: 0s;
                }
                
                .orb:nth-child(2) {
                    width: 200px;
                    height: 200px;
                    top: 50%;
                    right: -100px;
                    animation-delay: -5s;
                }
                
                .orb:nth-child(3) {
                    width: 400px;
                    height: 400px;
                    bottom: -200px;
                    left: 30%;
                    animation-delay: -10s;
                }
                
                @keyframes float {
                    0%, 100% { transform: translate(0, 0) rotate(0deg); }
                    33% { transform: translate(30px, -30px) rotate(120deg); }
                    66% { transform: translate(-20px, 20px) rotate(240deg); }
                }
                
                /* Navigation */
                .navbar {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    z-index: 50;
                    padding: 1rem 2rem;
                    backdrop-filter: blur(16px);
                    background: var(--glass-bg);
                    border-bottom: 1px solid var(--glass-border);
                }
                
                .nav-container {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    max-width: 1200px;
                    margin: 0 auto;
                }
                
                .logo {
                    font-size: 1.5rem;
                    font-weight: 700;
                    background: linear-gradient(135deg, var(--primary-500), var(--secondary-500));
                    background-clip: text;
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }
                
                .nav-links {
                    display: flex;
                    gap: 2rem;
                    list-style: none;
                }
                
                .nav-link {
                    color: var(--text-secondary);
                    text-decoration: none;
                    font-weight: 500;
                    transition: color 0.3s ease;
                }
                
                .nav-link:hover, .nav-link.active {
                    color: var(--text-primary);
                }
                
                /* Main content */
                .main-content {
                    padding: 8rem 2rem 2rem;
                    max-width: 1200px;
                    margin: 0 auto;
                }
                
                .glass-card {
                    background: var(--glass-bg);
                    backdrop-filter: blur(16px);
                    border: 1px solid var(--glass-border);
                    border-radius: 1rem;
                    padding: 2rem;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                }
                
                .dashboard-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 2rem;
                    margin-bottom: 2rem;
                }
                
                .section-title {
                    font-size: 1.5rem;
                    font-weight: 600;
                    margin-bottom: 1rem;
                    color: var(--text-primary);
                }
                
                .section-subtitle {
                    color: var(--text-secondary);
                    margin-bottom: 2rem;
                }
                
                .stat-item {
                    display: flex;
                    justify-content: space-between;
                    padding: 1rem 0;
                    border-bottom: 1px solid var(--glass-border);
                }
                
                .stat-item:last-child {
                    border-bottom: none;
                }
                
                .stat-label {
                    color: var(--text-secondary);
                }
                
                .stat-value {
                    color: var(--text-primary);
                    font-weight: 600;
                }
                
                .btn {
                    background: linear-gradient(135deg, var(--primary-500), var(--secondary-500));
                    color: white;
                    padding: 0.75rem 1.5rem;
                    border: none;
                    border-radius: 0.5rem;
                    font-weight: 600;
                    text-decoration: none;
                    display: inline-block;
                    transition: all 0.3s ease;
                    cursor: pointer;
                }
                
                .btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px rgba(79, 172, 254, 0.4);
                }
                
                .btn-secondary {
                    background: var(--glass-bg);
                    color: var(--text-primary);
                    border: 1px solid var(--glass-border);
                }
                
                .btn-secondary:hover {
                    background: rgba(255, 255, 255, 0.1);
                    box-shadow: 0 8px 25px rgba(255, 255, 255, 0.1);
                }
                
                .quick-actions {
                    display: flex;
                    gap: 1rem;
                    flex-wrap: wrap;
                    margin-top: 2rem;
                }
                
                .status-indicator {
                    display: inline-flex;
                    align-items: center;
                    gap: 0.5rem;
                    padding: 0.5rem 1rem;
                    background: rgba(34, 197, 94, 0.2);
                    color: #22c55e;
                    border-radius: 0.5rem;
                    border: 1px solid rgba(34, 197, 94, 0.3);
                    font-size: 0.875rem;
                }
                
                .feature-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 1.5rem;
                    margin-top: 2rem;
                }
                
                .feature-card {
                    background: rgba(255, 255, 255, 0.03);
                    border: 1px solid var(--glass-border);
                    border-radius: 0.75rem;
                    padding: 1.5rem;
                    transition: all 0.3s ease;
                }
                
                .feature-card:hover {
                    background: rgba(255, 255, 255, 0.06);
                    transform: translateY(-2px);
                }
                
                .feature-icon {
                    width: 2.5rem;
                    height: 2.5rem;
                    background: linear-gradient(135deg, var(--primary-500), var(--secondary-500));
                    border-radius: 0.5rem;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: 1rem;
                    font-size: 1.25rem;
                }
                
                .feature-title {
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                    color: var(--text-primary);
                }
                
                .feature-description {
                    color: var(--text-secondary);
                    font-size: 0.875rem;
                    line-height: 1.5;
                }
            </style>
        </head>
        <body>
            <div class="floating-orbs">
                <div class="orb"></div>
                <div class="orb"></div>
                <div class="orb"></div>
            </div>
            
            <nav class="navbar">
                <div class="nav-container">
                    <div class="logo">Rhiz</div>
                    <ul class="nav-links">
                        <li><a href="/app" class="nav-link active">Dashboard</a></li>
                        <li><a href="/app/goals" class="nav-link">Goals</a></li>
                        <li><a href="/app/contacts" class="nav-link">Contacts</a></li>
                        <li><a href="/app/intelligence" class="nav-link">Intelligence</a></li>
                        <li><a href="/app/settings" class="nav-link">Settings</a></li>
                    </ul>
                </div>
            </nav>
            
            <main class="main-content">
                <div class="glass-card">
                    <h1 class="section-title">{page_content['title']}</h1>
                    <p class="section-subtitle">{page_content['subtitle']}</p>
                    
                    {page_content['main_content']}
                </div>
            </main>
        </body>
        </html>
        '''
    except Exception as e:
        logging.error(f"Error serving React frontend: {e}")
        return jsonify({'error': 'Frontend unavailable'}), 500

@react_bp.route('/api/demo/seed')
def seed_demo_data():
    """Create sample data for demonstration"""
    try:
        db = get_db()
        
        # Create a demo user if not exists
        user = db.execute('SELECT * FROM users WHERE email = ?', ('demo@rhiz.app',)).fetchone()
        if not user:
            cursor = db.execute(
                'INSERT INTO users (email, subscription_tier, created_at) VALUES (?, ?, ?)',
                ('demo@rhiz.app', 'founder_plus', datetime.now().isoformat())
            )
            user_id = cursor.lastrowid
        else:
            user_id = user['id']
        
        # Create sample goals
        goals = [
            {
                'title': 'Raise $250k Angel Round',
                'description': 'Seeking angel investors for our SaaS platform. Looking for strategic investors with enterprise software experience.'
            },
            {
                'title': 'Hire Senior Developer',
                'description': 'Need to find a senior full-stack developer with React and Python experience for our growing team.'
            },
            {
                'title': 'Find Beta Customers',
                'description': 'Looking for 10-15 early adopters in the SMB space to test our product and provide feedback.'
            }
        ]
        
        goal_ids = []
        for goal in goals:
            existing = db.execute(
                'SELECT id FROM goals WHERE user_id = ? AND title = ?',
                (user_id, goal['title'])
            ).fetchone()
            
            if not existing:
                cursor = db.execute(
                    'INSERT INTO goals (user_id, title, description, created_at) VALUES (?, ?, ?, ?)',
                    (user_id, goal['title'], goal['description'], datetime.now().isoformat())
                )
                goal_ids.append(cursor.lastrowid)
            else:
                goal_ids.append(existing['id'])
        
        # Create sample contacts
        contacts = [
            {
                'name': 'Sarah Chen',
                'email': 'sarah@techventures.com',
                'company': 'TechVentures Capital',
                'title': 'Partner',
                'relationship_type': 'investor',
                'warmth_status': 4,
                'warmth_label': 'Warm',
                'notes': 'Met at TechCrunch. Interested in enterprise SaaS. Focus on Series A.',
                'linkedin': 'https://linkedin.com/in/sarahchen'
            },
            {
                'name': 'Marcus Johnson',
                'email': 'marcus@cloudscale.io',
                'company': 'CloudScale',
                'title': 'CTO',
                'relationship_type': 'founder',
                'warmth_status': 5,
                'warmth_label': 'Hot',
                'notes': 'Fellow founder. Sold previous company to Microsoft. Great mentor.',
                'linkedin': 'https://linkedin.com/in/marcusjohnson'
            },
            {
                'name': 'Emily Rodriguez',
                'email': 'emily@buildwright.com',
                'company': 'BuildWright Solutions',
                'title': 'CEO',
                'relationship_type': 'customer',
                'warmth_status': 3,
                'warmth_label': 'Lukewarm',
                'notes': 'Potential customer. Company has 150 employees. Interested in productivity tools.',
                'linkedin': 'https://linkedin.com/in/emilyrodriguez'
            },
            {
                'name': 'David Kim',
                'email': 'david@freelance.dev',
                'company': 'Independent',
                'title': 'Senior Full-Stack Developer',
                'relationship_type': 'talent',
                'warmth_status': 4,
                'warmth_label': 'Warm',
                'notes': '8 years experience. React, Node.js, Python. Available for hire.',
                'linkedin': 'https://linkedin.com/in/davidkim'
            },
            {
                'name': 'Lisa Park',
                'email': 'lisa@innovatelab.co',
                'company': 'InnovateLab',
                'title': 'Head of Product',
                'relationship_type': 'advisor',
                'warmth_status': 4,
                'warmth_label': 'Warm',
                'notes': 'Product expert. Previously at Google. Open to advising early-stage startups.',
                'linkedin': 'https://linkedin.com/in/lisapark'
            }
        ]
        
        contact_ids = []
        for contact in contacts:
            existing = db.execute(
                'SELECT id FROM contacts WHERE user_id = ? AND email = ?',
                (user_id, contact['email'])
            ).fetchone()
            
            if not existing:
                cursor = db.execute(
                    '''INSERT INTO contacts (
                        user_id, name, email, company, title, relationship_type,
                        warmth_status, warmth_label, notes, linkedin, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (
                        user_id, contact['name'], contact['email'], contact['company'],
                        contact['title'], contact['relationship_type'], contact['warmth_status'],
                        contact['warmth_label'], contact['notes'], contact['linkedin'],
                        datetime.now().isoformat(), datetime.now().isoformat()
                    )
                )
                contact_ids.append(cursor.lastrowid)
            else:
                contact_ids.append(existing['id'])
        
        # Create AI suggestions
        suggestions = [
            {
                'goal_id': goal_ids[0],  # Raise funding
                'contact_id': contact_ids[0],  # Sarah Chen (investor)
                'confidence': 0.92,
                'suggestion': 'Sarah specializes in enterprise SaaS investments and has shown interest in your space. Great fit for your angel round.'
            },
            {
                'goal_id': goal_ids[1],  # Hire developer
                'contact_id': contact_ids[3],  # David Kim (developer)
                'confidence': 0.88,
                'suggestion': 'David has the exact technical skills you need and is actively looking for opportunities.'
            },
            {
                'goal_id': goal_ids[2],  # Beta customers
                'contact_id': contact_ids[2],  # Emily Rodriguez (potential customer)
                'confidence': 0.75,
                'suggestion': 'Emily\'s company fits your target customer profile and she\'s expressed interest in productivity tools.'
            }
        ]
        
        for suggestion in suggestions:
            existing = db.execute(
                'SELECT id FROM ai_suggestions WHERE goal_id = ? AND contact_id = ?',
                (suggestion['goal_id'], suggestion['contact_id'])
            ).fetchone()
            
            if not existing:
                db.execute(
                    '''INSERT INTO ai_suggestions (goal_id, contact_id, confidence, suggestion, created_at)
                       VALUES (?, ?, ?, ?, ?)''',
                    (
                        suggestion['goal_id'], suggestion['contact_id'],
                        suggestion['confidence'], suggestion['suggestion'],
                        datetime.now().isoformat()
                    )
                )
        
        db.commit()
        db.close()
        
        # Set demo user in session
        session['user_id'] = user_id
        
        return jsonify({
            'success': True,
            'message': 'Demo data created successfully',
            'user_id': user_id,
            'goals_created': len(goal_ids),
            'contacts_created': len(contact_ids),
            'suggestions_created': len(suggestions)
        })
        
    except Exception as e:
        logging.error(f"Error seeding demo data: {e}")
        return jsonify({'error': f'Failed to seed demo data: {str(e)}'}), 500

def get_page_content(route):
    """Get page-specific content based on route"""
    if route.endswith('/goals') or route.endswith('/app/goals'):
        return {
            'title': 'Goals & Matching',
            'subtitle': 'AI-powered goal matching with semantic analysis',
            'main_content': '''
                <div class="dashboard-grid">
                    <div class="glass-card">
                        <h3 class="section-title">Create New Goal</h3>
                        <form class="goal-form">
                            <div class="form-group">
                                <label class="form-label">Goal Title</label>
                                <input type="text" class="form-input" placeholder="e.g., Raise $250k Angel Round">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Description</label>
                                <textarea class="form-input" rows="3" placeholder="Describe your goal in detail..."></textarea>
                            </div>
                            <button type="submit" class="btn">Create Goal & Find Matches</button>
                        </form>
                    </div>
                    
                    <div class="glass-card">
                        <h3 class="section-title">Recent Goals</h3>
                        <div class="goal-list">
                            <div class="goal-item">
                                <h4 class="goal-title">Raise $250k Angel Round</h4>
                                <p class="goal-description">Seeking angel investors for our SaaS platform...</p>
                                <div class="goal-stats">
                                    <span class="stat-badge">3 matches found</span>
                                    <span class="stat-badge">92% confidence</span>
                                </div>
                            </div>
                            <div class="goal-item">
                                <h4 class="goal-title">Hire Senior Developer</h4>
                                <p class="goal-description">Need to find a senior full-stack developer...</p>
                                <div class="goal-stats">
                                    <span class="stat-badge">2 matches found</span>
                                    <span class="stat-badge">88% confidence</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            '''
        }
    elif route.endswith('/contacts') or route.endswith('/app/contacts'):
        return {
            'title': 'Contact Intelligence',
            'subtitle': 'Multi-source contact sync with intelligent deduplication',
            'main_content': '''
                <div class="dashboard-grid">
                    <div class="glass-card">
                        <h3 class="section-title">Contact Management</h3>
                        <div class="contact-stats">
                            <div class="stat-item">
                                <span class="stat-label">Total Contacts</span>
                                <span class="stat-value">5</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Warm Connections</span>
                                <span class="stat-value">3</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Last Sync</span>
                                <span class="stat-value">2 hours ago</span>
                            </div>
                        </div>
                        <div class="quick-actions">
                            <button class="btn">Add Contact</button>
                            <button class="btn btn-secondary">Import CSV</button>
                            <button class="btn btn-secondary">Sync LinkedIn</button>
                        </div>
                    </div>
                    
                    <div class="glass-card">
                        <h3 class="section-title">Recent Contacts</h3>
                        <div class="contact-list">
                            <div class="contact-item">
                                <div class="contact-info">
                                    <h4 class="contact-name">Sarah Chen</h4>
                                    <p class="contact-company">TechVentures Capital - Partner</p>
                                </div>
                                <span class="warmth-badge warm">Warm</span>
                            </div>
                            <div class="contact-item">
                                <div class="contact-info">
                                    <h4 class="contact-name">Marcus Johnson</h4>
                                    <p class="contact-company">CloudScale - CTO</p>
                                </div>
                                <span class="warmth-badge hot">Hot</span>
                            </div>
                        </div>
                    </div>
                </div>
            '''
        }
    elif route.endswith('/intelligence') or route.endswith('/app/intelligence'):
        return {
            'title': 'Trust Insights',
            'subtitle': 'Real-time relationship intelligence with trust scoring',
            'main_content': '''
                <div class="dashboard-grid">
                    <div class="glass-card">
                        <h3 class="section-title">Trust Analytics</h3>
                        <div class="trust-metrics">
                            <div class="metric-card">
                                <h4 class="metric-title">Network Health</h4>
                                <div class="metric-value">87%</div>
                                <p class="metric-description">Overall relationship strength</p>
                            </div>
                            <div class="metric-card">
                                <h4 class="metric-title">Response Rate</h4>
                                <div class="metric-value">72%</div>
                                <p class="metric-description">Average contact responsiveness</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="glass-card">
                        <h3 class="section-title">AI Recommendations</h3>
                        <div class="recommendation-list">
                            <div class="recommendation-item">
                                <h4 class="recommendation-title">Introduction Opportunity</h4>
                                <p class="recommendation-description">Connect Sarah Chen with Marcus Johnson - both interested in SaaS investments</p>
                                <button class="btn btn-small">Make Introduction</button>
                            </div>
                            <div class="recommendation-item">
                                <h4 class="recommendation-title">Follow-up Reminder</h4>
                                <p class="recommendation-description">Emily Rodriguez hasn't responded in 2 weeks - consider gentle follow-up</p>
                                <button class="btn btn-small">Send Follow-up</button>
                            </div>
                        </div>
                    </div>
                </div>
            '''
        }
    elif route.endswith('/settings') or route.endswith('/app/settings'):
        return {
            'title': 'Settings',
            'subtitle': 'Configure your Rhiz experience',
            'main_content': '''
                <div class="dashboard-grid">
                    <div class="glass-card">
                        <h3 class="section-title">API Integrations</h3>
                        <div class="integration-list">
                            <div class="integration-item">
                                <div class="integration-info">
                                    <h4 class="integration-name">OpenAI</h4>
                                    <p class="integration-status">Connected</p>
                                </div>
                                <span class="status-indicator">✅ Active</span>
                            </div>
                            <div class="integration-item">
                                <div class="integration-info">
                                    <h4 class="integration-name">LinkedIn</h4>
                                    <p class="integration-status">Not Connected</p>
                                </div>
                                <button class="btn btn-small">Connect</button>
                            </div>
                        </div>
                    </div>
                    
                    <div class="glass-card">
                        <h3 class="section-title">Preferences</h3>
                        <div class="preferences-list">
                            <div class="preference-item">
                                <label class="preference-label">AI Suggestion Frequency</label>
                                <select class="form-input">
                                    <option>Real-time</option>
                                    <option>Daily</option>
                                    <option>Weekly</option>
                                </select>
                            </div>
                            <div class="preference-item">
                                <label class="preference-label">Trust Insights</label>
                                <input type="checkbox" checked> Enable automatic trust scoring
                            </div>
                        </div>
                    </div>
                </div>
            '''
        }
    else:
        # Default dashboard content
        return {
            'title': 'Welcome to Rhiz',
            'subtitle': 'Your intelligent relationship network is ready',
            'main_content': '''
                <div class="dashboard-grid">
                    <div class="glass-card">
                        <h3 class="section-title">System Status</h3>
                        <div class="stat-item">
                            <span class="stat-label">Backend</span>
                            <span class="status-indicator">✅ Running</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Database</span>
                            <span class="status-indicator">✅ Connected</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">API Routes</span>
                            <span class="status-indicator">✅ Active</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">AI Engine</span>
                            <span class="status-indicator">✅ Ready</span>
                        </div>
                    </div>
                    
                    <div class="glass-card">
                        <h3 class="section-title">Quick Stats</h3>
                        <div class="stat-item">
                            <span class="stat-label">Total Contacts</span>
                            <span class="stat-value">5</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Active Goals</span>
                            <span class="stat-value">3</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">AI Suggestions</span>
                            <span class="stat-value">12</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Trust Insights</span>
                            <span class="stat-value">Ready</span>
                        </div>
                    </div>
                </div>
                
                <div class="feature-grid">
                    <div class="feature-card">
                        <div class="feature-icon">🎯</div>
                        <h4 class="feature-title">Goals & Matching</h4>
                        <p class="feature-description">AI-powered goal matching with your network contacts using semantic analysis</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">👥</div>
                        <h4 class="feature-title">Contact Intelligence</h4>
                        <p class="feature-description">Multi-source contact sync with intelligent deduplication and enrichment</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🧠</div>
                        <h4 class="feature-title">Trust Insights</h4>
                        <p class="feature-description">Real-time relationship intelligence with trust scoring and behavioral analysis</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🌐</div>
                        <h4 class="feature-title">Network Visualization</h4>
                        <p class="feature-description">Interactive relationship mapping with rhizomatic intelligence layers</p>
                    </div>
                </div>
                
                <div class="quick-actions">
                    <a href="/api/health" class="btn">Test API Health</a>
                    <a href="/dashboard-legacy" class="btn btn-secondary">View Legacy Dashboard</a>
                    <a href="/api/demo/seed" class="btn btn-secondary">Load Demo Data</a>
                </div>
            '''
        }

def register_react_integration(app):
    """Register React integration with the Flask app"""
    app.register_blueprint(react_bp)
    logging.info("React integration routes registered successfully")