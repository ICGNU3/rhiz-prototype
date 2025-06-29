from backend import create_app

app = create_app()
from flask import jsonify, send_from_directory, render_template_string, send_file, render_template
import os
import logging
from datetime import datetime
from flask import request, session, redirect

# Routes are now imported through app.py to maintain compatibility

# Login route - must be defined before general routes
@app.route('/login')
def serve_login_page():
    """Serve login page with proper styling"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Rhiz</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: system-ui, -apple-system, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container { 
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 3rem; 
            border-radius: 20px; 
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); 
            max-width: 450px; 
            width: 90%; 
            text-align: center; 
        }
        .logo { 
            font-size: 2.5rem; 
            font-weight: bold; 
            background: linear-gradient(135deg, #4f46e5, #9333ea); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
            margin-bottom: 1rem; 
        }
        .title { 
            font-size: 2rem; 
            font-weight: bold; 
            color: #1f2937; 
            margin-bottom: 0.5rem; 
        }
        .subtitle { 
            font-size: 1.1rem; 
            color: #6b7280; 
            margin-bottom: 2.5rem; 
            line-height: 1.6;
        }
        .form { margin-bottom: 2rem; }
        .input { 
            width: 100%; 
            padding: 1.2rem; 
            border: 2px solid #e5e7eb; 
            border-radius: 12px; 
            font-size: 1rem; 
            margin-bottom: 1.5rem;
            background: rgba(255, 255, 255, 0.8);
            transition: all 0.3s ease;
        }
        .input:focus { 
            outline: none; 
            border-color: #4f46e5; 
            background: rgba(255, 255, 255, 1);
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }
        .btn { 
            width: 100%; 
            padding: 1.2rem; 
            background: linear-gradient(135deg, #4f46e5, #9333ea); 
            color: white; 
            border: none; 
            border-radius: 12px; 
            font-size: 1.1rem; 
            font-weight: 600; 
            cursor: pointer; 
            transition: all 0.3s ease;
            margin-bottom: 1rem;
        }
        .btn:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.4);
        }
        .btn:disabled { 
            opacity: 0.6; 
            cursor: not-allowed; 
            transform: none;
        }
        .demo-btn {
            background: linear-gradient(135deg, #10b981, #059669);
            margin-top: 1rem;
        }
        .demo-btn:hover {
            box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.4);
        }
        .message { 
            padding: 1rem; 
            border-radius: 12px; 
            margin-top: 1rem; 
            font-weight: 500;
        }
        .message.success { 
            background: rgba(209, 250, 229, 0.9); 
            color: #065f46; 
            border: 1px solid #a7f3d0; 
        }
        .message.error { 
            background: rgba(254, 226, 226, 0.9); 
            color: #991b1b; 
            border: 1px solid #fca5a5; 
        }
        .spinner { 
            width: 20px; 
            height: 20px; 
            border: 2px solid transparent; 
            border-top: 2px solid white; 
            border-radius: 50%; 
            animation: spin 1s linear infinite; 
            display: inline-block; 
        }
        @keyframes spin { 
            0% { transform: rotate(0deg); } 
            100% { transform: rotate(360deg); } 
        }
        .divider {
            text-align: center;
            color: #9ca3af;
            margin: 1.5rem 0;
            position: relative;
        }
        .divider::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 1px;
            background: #e5e7eb;
        }
        .divider span {
            background: rgba(255, 255, 255, 0.95);
            padding: 0 1rem;
        }
        .back-link {
            color: #6b7280;
            text-decoration: none;
            font-size: 0.9rem;
            margin-top: 2rem;
            display: inline-block;
            transition: color 0.3s ease;
        }
        .back-link:hover {
            color: #4f46e5;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">Rhiz</div>
        <h1 class="title">Welcome Back</h1>
        <p class="subtitle">Sign in to continue building meaningful relationships with AI-powered insights</p>
        
        <form class="form" id="authForm">
            <input type="email" id="email" class="input" placeholder="Enter your email address" required>
            <button type="submit" class="btn" id="submitBtn">
                Send Magic Link
            </button>
        </form>
        
        <div class="divider">
            <span>or</span>
        </div>
        
        <button type="button" class="btn demo-btn" id="demoBtn">
            Try Demo Access
        </button>
        
        <div id="message" class="message" style="display: none;"></div>
        
        <a href="/" class="back-link">← Back to Home</a>
    </div>

    <script>
        const form = document.getElementById('authForm');
        const emailInput = document.getElementById('email');
        const submitBtn = document.getElementById('submitBtn');
        const demoBtn = document.getElementById('demoBtn');
        const messageDiv = document.getElementById('message');

        // Magic link form submission
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = emailInput.value;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner"></span> Sending Magic Link...';
            
            try {
                const response = await fetch('/api/auth/request-link', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email })
                });
                
                if (response.ok) {
                    showMessage('Magic link sent! Check your email to sign in.', 'success');
                    emailInput.value = '';
                } else {
                    const data = await response.json();
                    showMessage(data.error || 'Something went wrong. Please try again.', 'error');
                }
            } catch (error) {
                showMessage('Network error. Please try again.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Send Magic Link';
            }
        });

        // Demo access button
        demoBtn.addEventListener('click', async () => {
            demoBtn.disabled = true;
            demoBtn.innerHTML = '<span class="spinner"></span> Accessing Demo...';
            
            try {
                const response = await fetch('/api/auth/demo-login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                if (response.ok) {
                    showMessage('Demo access granted! Redirecting...', 'success');
                    setTimeout(() => {
                        window.location.href = '/dashboard';
                    }, 1000);
                } else {
                    showMessage('Demo access temporarily unavailable. Please try magic link.', 'error');
                }
            } catch (error) {
                showMessage('Network error. Please try magic link instead.', 'error');
            } finally {
                demoBtn.disabled = false;
                demoBtn.innerHTML = 'Try Demo Access';
            }
        });

        function showMessage(text, type) {
            messageDiv.textContent = text;
            messageDiv.className = `message ${type}`;
            messageDiv.style.display = 'block';
            setTimeout(() => {
                if (type !== 'success') {
                    messageDiv.style.display = 'none';
                }
            }, 5000);
        }
    </script>
</body>
</html>
    ''')

# Serve React static assets
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve React static assets"""
    return send_from_directory(os.path.join('frontend', 'dist', 'assets'), filename)

@app.route('/vite.svg')
def serve_vite_svg():
    """Serve Vite favicon"""
    try:
        return send_from_directory(os.path.join('frontend', 'dist'), 'vite.svg')
    except FileNotFoundError:
        return '', 404

# Serve React frontend routes
@app.route('/')
def serve_landing():
    """Serve landing page"""
    try:
        return send_file(os.path.join('frontend', 'dist', 'index.html'))
    except FileNotFoundError:
        return render_template('landing.html')

@app.route('/dashboard')
def serve_dashboard():
    """Serve dashboard for authenticated users"""
    # Check if user is authenticated
    if 'user_id' not in session:
        return redirect('/login')
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Rhiz</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: system-ui, -apple-system, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .logo { 
            font-size: 1.5rem; 
            font-weight: bold; 
            background: linear-gradient(135deg, #fff, #f0f0f0); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
        }
        .nav { display: flex; gap: 2rem; }
        .nav a { color: white; text-decoration: none; opacity: 0.8; transition: opacity 0.3s; }
        .nav a:hover { opacity: 1; }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 2rem; 
        }
        .welcome { 
            text-align: center; 
            margin-bottom: 3rem; 
        }
        .welcome h1 { 
            font-size: 3rem; 
            margin-bottom: 1rem; 
            background: linear-gradient(135deg, #fff, #f0f0f0); 
            -webkit-background-clip: text; 
            -webkit-text-fill-color: transparent; 
        }
        .welcome p { 
            font-size: 1.2rem; 
            opacity: 0.9; 
        }
        .grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 2rem; 
            margin-bottom: 3rem; 
        }
        .card { 
            background: rgba(255, 255, 255, 0.1); 
            backdrop-filter: blur(10px); 
            padding: 2rem; 
            border-radius: 16px; 
            transition: transform 0.3s; 
        }
        .card:hover { 
            transform: translateY(-5px); 
        }
        .card h3 { 
            margin-bottom: 1rem; 
            font-size: 1.5rem; 
        }
        .card p { 
            opacity: 0.8; 
            line-height: 1.6; 
        }
        .btn { 
            background: rgba(255, 255, 255, 0.2); 
            color: white; 
            border: none; 
            padding: 0.75rem 1.5rem; 
            border-radius: 8px; 
            cursor: pointer; 
            transition: all 0.3s; 
            text-decoration: none; 
            display: inline-block; 
            margin-top: 1rem; 
        }
        .btn:hover { 
            background: rgba(255, 255, 255, 0.3); 
            transform: translateY(-2px); 
        }
        .stats { 
            display: flex; 
            justify-content: space-around; 
            margin-bottom: 3rem; 
        }
        .stat { 
            text-align: center; 
        }
        .stat-number { 
            font-size: 2.5rem; 
            font-weight: bold; 
            display: block; 
        }
        .stat-label { 
            opacity: 0.8; 
            font-size: 0.9rem; 
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">Rhiz</div>
        <div class="nav">
            <a href="/dashboard">Dashboard</a>
            <a href="/contacts">Contacts</a>
            <a href="/goals">Goals</a>
            <a href="#" onclick="logout()">Logout</a>
        </div>
    </div>
    
    <div class="container">
        <div class="welcome">
            <h1>Welcome back!</h1>
            <p>Your relationship intelligence dashboard</p>
        </div>
        
        <div class="stats">
            <div class="stat">
                <span class="stat-number">12</span>
                <span class="stat-label">Active Contacts</span>
            </div>
            <div class="stat">
                <span class="stat-number">5</span>
                <span class="stat-label">Goals in Progress</span>
            </div>
            <div class="stat">
                <span class="stat-number">8</span>
                <span class="stat-label">AI Suggestions</span>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>📋 Recent Goals</h3>
                <p>Track your relationship building objectives and see AI-powered suggestions for connecting with the right people.</p>
                <a href="/goals" class="btn">View Goals</a>
            </div>
            
            <div class="card">
                <h3>👥 Contact Network</h3>
                <p>Manage your professional relationships with intelligent insights about connection strength and interaction patterns.</p>
                <a href="/contacts" class="btn">View Contacts</a>
            </div>
            
            <div class="card">
                <h3>🤖 AI Insights</h3>
                <p>Get personalized recommendations for strengthening relationships and achieving your networking goals.</p>
                <a href="/intelligence" class="btn">View Insights</a>
            </div>
            
            <div class="card">
                <h3>📈 Trust Analytics</h3>
                <p>Monitor relationship health, trust levels, and communication patterns across your professional network.</p>
                <a href="/trust" class="btn">View Analytics</a>
            </div>
        </div>
    </div>
    
    <script>
        function logout() {
            fetch('/api/auth/logout', { method: 'POST' })
                .then(() => window.location.href = '/login');
        }
    </script>
</body>
</html>
    ''')

@app.route('/contacts') 
@app.route('/goals')
@app.route('/404')
def serve_react():
    """Serve React frontend application"""
    try:
        return send_file(os.path.join('frontend', 'dist', 'index.html'))
    except FileNotFoundError:
        # Fallback HTML if React build not available - development mode
        return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rhiz - Relationship Intelligence Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: system-ui, -apple-system, sans-serif; }
        .container { min-height: 100vh; background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%); display: flex; align-items: center; justify-content: center; }
        .card { background: white; padding: 3rem; border-radius: 16px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); max-width: 500px; width: 90%; text-align: center; }
        .logo { font-size: 2rem; font-weight: bold; background: linear-gradient(135deg, #4f46e5, #9333ea); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1rem; }
        .title { font-size: 2.5rem; font-weight: bold; color: #1f2937; margin-bottom: 1rem; }
        .subtitle { font-size: 1.2rem; color: #6b7280; margin-bottom: 2rem; }
        .form { margin-bottom: 2rem; }
        .input { width: 100%; padding: 1rem; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 1rem; margin-bottom: 1rem; }
        .input:focus { outline: none; border-color: #4f46e5; }
        .btn { width: 100%; padding: 1rem; background: linear-gradient(135deg, #4f46e5, #9333ea); color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: transform 0.2s; }
        .btn:hover { transform: translateY(-2px); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .message { padding: 1rem; border-radius: 8px; margin-top: 1rem; }
        .message.success { background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }
        .message.error { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
        .spinner { width: 20px; height: 20px; border: 2px solid transparent; border-top: 2px solid white; border-radius: 50%; animation: spin 1s linear infinite; display: inline-block; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="logo">Rhiz</div>
            <h1 class="title">Relationship Intelligence</h1>
            <p class="subtitle">Transform how you build professional relationships with AI-powered insights</p>
            
            <form class="form" id="authForm">
                <input type="email" id="email" class="input" placeholder="Enter your email address" required>
                <button type="submit" class="btn" id="submitBtn">
                    Get Magic Link
                </button>
            </form>
            
            <div id="message" class="message" style="display: none;"></div>
        </div>
    </div>

    <script>
        const form = document.getElementById('authForm');
        const emailInput = document.getElementById('email');
        const submitBtn = document.getElementById('submitBtn');
        const messageDiv = document.getElementById('message');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const email = emailInput.value;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner"></span> Sending...';
            
            try {
                const response = await fetch('/api/auth/request-link', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email })
                });
                
                if (response.ok) {
                    showMessage('Magic link sent! Check your email to sign in.', 'success');
                    emailInput.value = '';
                } else {
                    const data = await response.json();
                    showMessage(data.error || 'Something went wrong. Please try again.', 'error');
                }
            } catch (error) {
                showMessage('Network error. Please try again.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Get Magic Link';
            }
        });

        function showMessage(text, type) {
            messageDiv.textContent = text;
            messageDiv.className = `message ${type}`;
            messageDiv.style.display = 'block';
            setTimeout(() => {
                messageDiv.style.display = 'none';
            }, 5000);
        }
    </script>
</body>
</html>
    ''')


# API endpoints for React frontend
@app.route('/api/auth/me')
def get_current_user():
    """Get current authenticated user"""
    # Mock user for now - replace with real authentication
    return jsonify({
        'id': 'demo_user',
        'email': 'demo@rhiz.app',
        'subscription_tier': 'free',
        'goals_count': 3,
        'contacts_count': 8,
        'ai_suggestions_used': 5
    })



@app.route('/api/goals')
def get_goals():
    """Get all goals for the current user"""
    return jsonify([
        {
            'id': '1',
            'title': 'Raise Series A Funding',
            'description': 'Secure $2M Series A funding from aligned investors',
            'goal_type': 'fundraising',
            'timeline': '6 months',
            'status': 'active',
            'priority_level': 'high',
            'progress_percentage': 35,
            'created_at': '2024-01-15'
        },
        {
            'id': '2',
            'title': 'Hire Senior Backend Engineer',
            'description': 'Find and hire a senior backend engineer with ML experience',
            'goal_type': 'hiring',
            'timeline': '3 months',
            'status': 'active',
            'priority_level': 'high',
            'progress_percentage': 60,
            'created_at': '2024-02-01'
        },
        {
            'id': '3',
            'title': 'Partnership with Integration Platform',
            'description': 'Establish strategic partnership for platform integrations',
            'goal_type': 'partnerships',
            'timeline': '4 months',
            'status': 'active',
            'priority_level': 'medium',
            'progress_percentage': 20,
            'created_at': '2024-02-15'
        }
    ])

@app.route('/api/contacts')
def get_contacts():
    """Get all contacts for the current user"""
    return jsonify([
        {
            'id': '1',
            'name': 'Sarah Chen',
            'email': 'sarah@example.com',
            'company': 'Vertex Ventures',
            'title': 'Partner',
            'relationship_type': 'investor',
            'warmth_level': 'warm',
            'last_interaction_date': '2024-02-20',
            'notes': 'Met at TechCrunch. Interested in B2B SaaS. Prefers companies with proven traction.'
        },
        {
            'id': '2',
            'name': 'Marcus Rivera',
            'email': 'marcus@techcorp.com',
            'company': 'TechCorp',
            'title': 'CTO',
            'relationship_type': 'partner',
            'warmth_level': 'cool',
            'last_interaction_date': '2024-01-15',
            'notes': 'Potential integration partner. Looking for relationship intelligence tools.'
        },
        {
            'id': '3',
            'name': 'Jessica Thompson',
            'email': 'jessica@dev.com',
            'company': 'DevCorp',
            'title': 'Senior Backend Engineer',
            'relationship_type': 'employee',
            'warmth_level': 'warm',
            'last_interaction_date': '2024-02-25',
            'notes': 'Excellent Python and ML background. Available for new opportunities.'
        },
        {
            'id': '4',
            'name': 'David Kim',
            'email': 'david@startup.io',
            'company': 'StartupIO',
            'title': 'Founder',
            'relationship_type': 'mentor',
            'warmth_level': 'warm',
            'last_interaction_date': '2024-02-18',
            'notes': 'Successful B2B founder. Great strategic advice on product-market fit.'
        },
        {
            'id': '5',
            'name': 'Emily Zhang',
            'email': 'emily@growth.com',
            'company': 'Growth Labs',
            'title': 'VP Marketing',
            'relationship_type': 'customer',
            'warmth_level': 'cold',
            'last_interaction_date': '2024-01-10',
            'notes': 'Interested in relationship intelligence for their sales team. Follow up needed.'
        }
    ])

@app.route('/api/auth/request-link', methods=['POST'])
def request_magic_link():
    """Handle magic link request"""
    try:
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
        else:
            email = request.form.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # For demo purposes, we'll create a session immediately
        # Skip email sending and go straight to authentication
        session['user_id'] = 'demo_user'
        session['email'] = email
        session['authenticated'] = True
        
        return jsonify({
            'message': 'Authentication successful',
            'success': True,
            'demo_mode': True,
            'redirect': '/app/dashboard'
        })
        
    except Exception as e:
        logging.error(f"Authentication failed: {e}")
        return jsonify({'error': 'Authentication failed. Please try again.'}), 500

@app.route('/api/auth/verify')
def verify_magic_link():
    """Verify magic link token"""
    token = request.args.get('token')
    
    if not token:
        return jsonify({'error': 'Token is required'}), 400
    
    # For demo purposes, accept any token
    session['user_id'] = 'demo_user'
    session['email'] = 'demo@rhiz.app'
    session['authenticated'] = True
    
    return redirect('/app/dashboard')

@app.route('/api/auth/demo-login', methods=['POST'])
def demo_login():
    """Demo login for development"""
    try:
        # Create demo session
        session['user_id'] = 'demo_user'
        session['email'] = 'demo@rhiz.app'
        session['authenticated'] = True
        
        logging.info("Demo login successful")
        return jsonify({'success': True, 'user_id': 'demo_user'})
    except Exception as e:
        logging.error(f"Demo login failed: {e}")
        return jsonify({'error': 'Demo login failed. Please try again.'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout current user"""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/dashboard/analytics')
def dashboard_analytics_api():
    """Dashboard analytics data for React frontend"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    return jsonify({
        'contacts': 12,
        'goals': 6,
        'interactions': 24,
        'ai_suggestions': 8,
        'trust_score': 85,
        'network_growth': 15,
        'recent_activity': {
            'contacts_added': 3,
            'goals_completed': 1,
            'messages_sent': 5
        },
        'status': 'success'
    })

@app.route('/api/service-status')
def service_status():
    """Check status of all placeholder services"""
    try:
        from service_status import get_all_service_status
        return jsonify(get_all_service_status())
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "message": "Service status check failed"
        }), 500

# React routes are handled by serve_react() above



@app.route('/health')
def health_check():
    """Production health monitoring endpoint"""
    try:
        health = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "environment": "production" if os.environ.get('REPLIT_DEPLOYMENT') else "development"
        }
        
        # Check critical services
        checks = {}
        
        # Database check
        try:
            import psycopg2
            conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            conn.close()
            checks["database"] = "healthy"
        except Exception as e:
            checks["database"] = f"error: {str(e)[:100]}"
            health["status"] = "degraded"
        
        # API keys check
        checks["openai"] = "configured" if os.environ.get('OPENAI_API_KEY') else "missing"
        checks["resend"] = "configured" if os.environ.get('RESEND_API_KEY') else "missing"
        checks["stripe"] = "configured" if os.environ.get('STRIPE_SECRET_KEY') else "missing"
        
        health["checks"] = checks
        
        # Return appropriate status code
        status_code = 200 if health["status"] == "healthy" else 503
        return jsonify(health), status_code
        
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return jsonify({
            "status": "error",
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Health check unavailable"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
