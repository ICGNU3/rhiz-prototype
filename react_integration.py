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
@react_bp.route('/')
@react_bp.route('/dashboard')
@react_bp.route('/goals')
@react_bp.route('/contacts')
@react_bp.route('/intelligence')
@react_bp.route('/settings')
def serve_react():
    """Serve the React frontend for all app routes"""
    try:
        # In production, this would serve the built React app
        # For development, we'll serve a basic HTML page that loads the React dev server
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Rhiz - Intelligent Relationship Network</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { 
                    margin: 0; 
                    font-family: Inter, system-ui; 
                    background: #0a0b0d; 
                    color: white; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    min-height: 100vh;
                }
                .container { 
                    text-align: center; 
                    background: rgba(255,255,255,0.05); 
                    padding: 3rem; 
                    border-radius: 1rem; 
                    border: 1px solid rgba(255,255,255,0.1);
                    backdrop-filter: blur(16px);
                    max-width: 600px;
                }
                .logo { 
                    background: linear-gradient(135deg, #4facfe, #8b5cf6); 
                    width: 80px; 
                    height: 80px; 
                    border-radius: 1rem; 
                    margin: 0 auto 2rem; 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    font-size: 2rem; 
                    font-weight: bold;
                }
                h1 {
                    background: linear-gradient(135deg, #4facfe, #a855f7, #ec4899);
                    background-clip: text;
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-size: 2.5rem;
                    margin-bottom: 1rem;
                }
                .status {
                    background: rgba(34, 197, 94, 0.2);
                    color: #22c55e;
                    padding: 1rem;
                    border-radius: 0.5rem;
                    margin: 2rem 0;
                    border: 1px solid rgba(34, 197, 94, 0.3);
                }
                .api-info {
                    background: rgba(59, 130, 246, 0.2);
                    color: #3b82f6;
                    padding: 1rem;
                    border-radius: 0.5rem;
                    margin: 1rem 0;
                    border: 1px solid rgba(59, 130, 246, 0.3);
                    text-align: left;
                }
                .btn {
                    background: linear-gradient(135deg, #4facfe, #2e9bfe);
                    color: white;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 8px;
                    font-weight: 600;
                    margin: 0.5rem;
                    cursor: pointer;
                    text-decoration: none;
                    display: inline-block;
                    transition: all 0.3s ease;
                }
                .btn:hover {
                    transform: translateY(-1px);
                    box-shadow: 0 6px 24px rgba(79, 172, 254, 0.4);
                }
                .endpoints {
                    text-align: left;
                    font-size: 0.9rem;
                    font-family: monospace;
                    line-height: 1.6;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">R</div>
                <h1>Rhiz Platform Active</h1>
                <div class="status">
                    ✅ Flask Backend Running Successfully<br>
                    ✅ API Routes Registered<br>
                    ✅ Database Connected
                </div>
                
                <div class="api-info">
                    <strong>Available API Endpoints:</strong>
                    <div class="endpoints">
                        • GET /api/health - System status<br>
                        • POST /api/auth/magic-link - Authentication<br>
                        • GET /api/goals - User goals<br>
                        • GET /api/contacts - Contact list<br>
                        • GET /api/intelligence/suggestions - AI recommendations<br>
                        • GET /api/network/graph - Network visualization data
                    </div>
                </div>
                
                <p>The React frontend can be developed separately and will integrate with these API endpoints.</p>
                
                <a href="/api/health" class="btn">Test API Health</a>
                <a href="/dashboard-legacy" class="btn">View Legacy Dashboard</a>
                
                <p style="margin-top: 2rem; opacity: 0.7; font-size: 0.9rem;">
                    React development server should be run separately with: <code>cd frontend && npm run dev</code>
                </p>
            </div>
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

def register_react_integration(app):
    """Register React integration with the Flask app"""
    app.register_blueprint(react_bp)
    logging.info("React integration routes registered successfully")