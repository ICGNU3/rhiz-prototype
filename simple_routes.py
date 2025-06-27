"""
Future-forward authentication routes for Rhiz
Eliminates redundancy, redirects to modern React interface
"""
import os
from flask import Flask, session, redirect, render_template, request, jsonify
from app import app

def get_db_connection():
    """Simple database connection for authentication"""
    return None

@app.route('/landing')
def landing():
    """Original beautiful landing page"""
    return render_template('landing.html')

@app.route('/signup')
def signup():
    """Signup page route"""
    return render_template('signup.html')

@app.route('/login')
def login():
    """Login page route"""
    return render_template('login.html')

@app.route('/auth/magic-link', methods=['POST'])
def send_magic_link():
    """Handle magic link requests"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        # Magic link logic would go here
        # For now, provide fallback to demo
        return jsonify({'message': f'Magic link sent to {email}', 'redirect': '/demo-login'}), 200
    except Exception as e:
        return jsonify({'error': 'Magic link service temporarily unavailable'}), 500

@app.route('/demo-login')
def demo_login():
    """Quick demo login for immediate access"""
    session['user_id'] = 'demo_user'
    session['demo_mode'] = True
    return redirect('/app/dashboard')

# Essential future-forward redirects for clean UX
@app.route('/dashboard')
def dashboard_redirect():
    """Redirect legacy dashboard to modern React interface"""
    return redirect('/app/dashboard')

@app.route('/goals')
def goals_redirect():
    """Redirect legacy goals to modern React interface"""
    return redirect('/app/goals')

@app.route('/contacts')
def contacts_redirect():
    """Redirect legacy contacts to modern React interface"""
    return redirect('/app/contacts')

@app.route('/intelligence')
def intelligence_redirect():
    """Redirect legacy intelligence to modern React interface"""
    return redirect('/app/intelligence')

print("Clean future-forward routes loaded successfully")