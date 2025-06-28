"""
React Frontend Integration for Rhiz
Adds routes to serve the React frontend and provides sample data for demonstration
"""

import os
import logging
import sqlite3
from datetime import datetime
from flask import Blueprint, render_template, jsonify, g
from werkzeug.exceptions import NotFound

react_bp = Blueprint('react', __name__)

def get_db():
    """Get database connection"""
    if 'db' not in g:
        g.db = sqlite3.connect('db.sqlite3')
        g.db.row_factory = sqlite3.Row
    return g.db

# Handle /app/dashboard directly instead of redirecting
@react_bp.route('/app/dashboard')
def dashboard():
    """Serve dashboard directly"""
    return serve_react('dashboard')

@react_bp.route('/app')
@react_bp.route('/app/')
@react_bp.route('/app/<path:route>')
def serve_react(route=''):
    """Serve the React frontend for other app routes"""
    try:
        # For now, redirect onboarding to dashboard since authentication is working
        if route == 'onboarding':
            from flask import redirect
            return redirect('/app/dashboard')
        
        # For other routes, return a simple working page
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Rhiz - Relationship Intelligence</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
            <style>
                :root {{
                    --text-primary: #ffffff;
                    --text-secondary: rgba(255, 255, 255, 0.7);
                    --glass-bg: rgba(255, 255, 255, 0.05);
                    --glass-border: rgba(255, 255, 255, 0.1);
                    --primary-500: #4facfe;
                    --primary-400: #6bb6fe;
                    --secondary-500: #8b5cf6;
                    --accent-500: #ec4899;
                }}
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
                    color: var(--text-primary);
                    min-height: 100vh;
                    overflow-x: hidden;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 0 20px;
                }}
                
                .navbar {{
                    background: rgba(255, 255, 255, 0.02);
                    backdrop-filter: blur(20px);
                    border-bottom: 1px solid var(--glass-border);
                    padding: 1rem 0;
                    position: sticky;
                    top: 0;
                    z-index: 1000;
                }}
                
                .nav-content {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                
                .logo {{
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: var(--primary-400);
                }}
                
                .nav-links {{
                    display: flex;
                    gap: 2rem;
                    list-style: none;
                }}
                
                .nav-links a {{
                    color: var(--text-secondary);
                    text-decoration: none;
                    transition: color 0.3s ease;
                }}
                
                .nav-links a:hover, .nav-links a.active {{
                    color: var(--primary-400);
                }}
                
                .main-content {{
                    padding: 3rem 0;
                }}
                
                .glass-card {{
                    background: var(--glass-bg);
                    backdrop-filter: blur(20px);
                    border: 1px solid var(--glass-border);
                    border-radius: 16px;
                    padding: 2rem;
                    margin-bottom: 2rem;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                }}
                
                .section-title {{
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin-bottom: 1rem;
                    background: linear-gradient(135deg, var(--primary-400), var(--secondary-500));
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }}
                
                .section-subtitle {{
                    font-size: 1.2rem;
                    color: var(--text-secondary);
                    margin-bottom: 2rem;
                }}
                
                .btn {{
                    display: inline-block;
                    padding: 12px 24px;
                    background: linear-gradient(135deg, var(--primary-500), var(--secondary-500));
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    border: none;
                    cursor: pointer;
                    font-weight: 600;
                    transition: all 0.3s ease;
                }}
                
                .btn:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 8px 24px rgba(79, 172, 254, 0.4);
                }}
                
                .grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 2rem;
                    margin-top: 2rem;
                }}
                
                .feature-card {{
                    background: var(--glass-bg);
                    border: 1px solid var(--glass-border);
                    border-radius: 12px;
                    padding: 1.5rem;
                    transition: all 0.3s ease;
                }}
                
                .feature-card:hover {{
                    transform: translateY(-4px);
                    box-shadow: 0 12px 32px rgba(79, 172, 254, 0.2);
                }}
                
                .feature-card h3 {{
                    color: var(--primary-400);
                    margin-bottom: 1rem;
                    font-size: 1.25rem;
                }}
                
                .feature-card p {{
                    color: var(--text-secondary);
                    margin-bottom: 1.5rem;
                    line-height: 1.6;
                }}
                
                @media (max-width: 768px) {{
                    .nav-links {{
                        gap: 1rem;
                    }}
                    
                    .section-title {{
                        font-size: 2rem;
                    }}
                    
                    .grid {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            <nav class="navbar">
                <div class="container">
                    <div class="nav-content">
                        <div class="logo">Rhiz</div>
                        <ul class="nav-links">
                            <li><a href="/app" class="{'active' if route in ['', 'dashboard'] else ''}">Dashboard</a></li>
                            <li><a href="/app/goals" class="{'active' if route == 'goals' else ''}">Goals</a></li>
                            <li><a href="/app/contacts" class="{'active' if route == 'contacts' else ''}">Contacts</a></li>
                            <li><a href="/app/intelligence" class="{'active' if route == 'intelligence' else ''}">Intelligence</a></li>
                            <li><a href="/app/settings" class="{'active' if route == 'settings' else ''}">Settings</a></li>
                        </ul>
                    </div>
                </div>
            </nav>
            
            <main class="main-content">
                <div class="container">
                    <div class="glass-card">
                        <h1 class="section-title">{page_content['title']}</h1>
                        <p class="section-subtitle">{page_content['subtitle']}</p>
                        
                        {page_content['main_content']}
                    </div>
                </div>
            </main>
        </body>
        </html>
        """
        
        return html_content
    except Exception as e:
        logging.error(f"Error serving React frontend: {e}")
        return jsonify({'error': 'Frontend unavailable'}), 500

def get_page_content(route):
    """Get page-specific content based on route"""
    if route in ['', 'dashboard']:
        return {
            'title': 'Welcome to Rhiz',
            'subtitle': 'Your intelligent relationship network at a glance',
            'main_content': '''
                <div class="grid">
                    <div class="feature-card">
                        <h3>Active Goals</h3>
                        <p>Track your networking objectives and see AI-powered connection suggestions.</p>
                        <a href="/app/goals" class="btn">View Goals</a>
                    </div>
                    <div class="feature-card">
                        <h3>Network Contacts</h3>
                        <p>Manage your professional relationships with context and warmth tracking.</p>
                        <a href="/app/contacts" class="btn">Manage Contacts</a>
                    </div>
                    <div class="feature-card">
                        <h3>Trust Insights</h3>
                        <p>Get real-time relationship intelligence and trust scoring.</p>
                        <a href="/app/intelligence" class="btn">View Intelligence</a>
                    </div>
                </div>
            '''
        }
    elif route == 'goals':
        return {
            'title': 'Goals & Intent Sync',
            'subtitle': 'Define your objectives and let AI match you with the right connections',
            'main_content': '''
                <div class="feature-card">
                    <h3>Create New Goal</h3>
                    <p>Tell us what you're trying to achieve, and we'll help you find the right people.</p>
                    <a href="/goals/create" class="btn">Create Goal</a>
                </div>
                <div class="grid">
                    <div class="feature-card">
                        <h3>Fundraising Goals</h3>
                        <p>Connect with investors and advisors for your funding needs.</p>
                    </div>
                    <div class="feature-card">
                        <h3>Hiring Goals</h3>
                        <p>Find the right talent through your network connections.</p>
                    </div>
                </div>
            '''
        }
    elif route == 'contacts':
        return {
            'title': 'Contact Intelligence',
            'subtitle': 'Your comprehensive network with AI-powered insights',
            'main_content': '''
                <div class="feature-card">
                    <h3>Add New Contact</h3>
                    <p>Expand your network and track relationship context.</p>
                    <a href="/contacts/add" class="btn">Add Contact</a>
                </div>
                <div class="grid">
                    <div class="feature-card">
                        <h3>Import Contacts</h3>
                        <p>Sync from LinkedIn, Gmail, or CSV files.</p>
                        <a href="/contacts/import" class="btn">Import</a>
                    </div>
                    <div class="feature-card">
                        <h3>Pipeline View</h3>
                        <p>See your contacts organized by relationship warmth.</p>
                        <a href="/pipeline" class="btn">View Pipeline</a>
                    </div>
                </div>
            '''
        }
    elif route == 'intelligence':
        return {
            'title': 'Trust & Intelligence',
            'subtitle': 'Real-time relationship insights and trust scoring',
            'main_content': '''
                <div class="grid">
                    <div class="feature-card">
                        <h3>Trust Insights</h3>
                        <p>Advanced relationship health analysis and trust scoring.</p>
                        <a href="/trust-insights" class="btn">View Insights</a>
                    </div>
                    <div class="feature-card">
                        <h3>Network Map</h3>
                        <p>Visual representation of your relationship network.</p>
                        <a href="/network" class="btn">View Network</a>
                    </div>
                    <div class="feature-card">
                        <h3>AI Suggestions</h3>
                        <p>Intelligent recommendations for your networking goals.</p>
                        <a href="/ai-suggestions" class="btn">View Suggestions</a>
                    </div>
                </div>
            '''
        }
    elif route == 'settings':
        return {
            'title': 'Settings & Preferences',
            'subtitle': 'Customize your Rhiz experience',
            'main_content': '''
                <div class="grid">
                    <div class="feature-card">
                        <h3>Profile Settings</h3>
                        <p>Update your profile information and preferences.</p>
                        <a href="/settings/profile" class="btn">Edit Profile</a>
                    </div>
                    <div class="feature-card">
                        <h3>Integrations</h3>
                        <p>Connect external services like LinkedIn, Gmail, and more.</p>
                        <a href="/settings/integrations" class="btn">Manage Integrations</a>
                    </div>
                    <div class="feature-card">
                        <h3>Notifications</h3>
                        <p>Configure how and when you receive updates.</p>
                        <a href="/settings/notifications" class="btn">Configure</a>
                    </div>
                </div>
            '''
        }
    else:
        return {
            'title': 'Page Not Found',
            'subtitle': 'The page you\'re looking for doesn\'t exist',
            'main_content': '''
                <div class="feature-card">
                    <h3>Return to Dashboard</h3>
                    <p>Go back to the main dashboard to continue using Rhiz.</p>
                    <a href="/app" class="btn">Go to Dashboard</a>
                </div>
            '''
        }

def register_react_integration(app):
    """Register React integration with the Flask app"""
    app.register_blueprint(react_bp)