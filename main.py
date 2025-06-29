from backend import create_app

app = create_app()
from flask import jsonify, send_from_directory, render_template_string, send_file, render_template, url_for
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

@app.route('/goals')
def serve_goals_page():
    """Serve goals page with authentication check"""
    # Check if user is authenticated
    if 'user_id' not in session:
        return redirect('/login')
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Goals - Rhiz</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: system-ui, -apple-system, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: white;
        }
        
        /* Header */
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1.5rem 2rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            font-size: 1.8rem;
            font-weight: 600;
        }
        .new-goal-btn {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }
        .new-goal-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-1px);
        }
        
        /* Main Layout */
        .main-container {
            display: flex;
            height: calc(100vh - 85px);
        }
        
        /* Left Pane */
        .left-pane {
            width: 350px;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(5px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            overflow-y: auto;
            padding: 1rem;
        }
        .goals-list {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }
        .goal-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(5px);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            cursor: pointer;
            transition: all 0.2s;
        }
        .goal-card:hover, .goal-card.active {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }
        .goal-card.active {
            border-color: rgba(255, 255, 255, 0.3);
        }
        .goal-title {
            font-weight: 600;
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }
        .goal-status {
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-bottom: 0.75rem;
        }
        .progress-bar {
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 3px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4ade80, #22c55e);
            border-radius: 3px;
            transition: width 0.3s ease;
        }
        
        /* Floating Action Button */
        .fab {
            position: fixed;
            bottom: 2rem;
            left: 2rem;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #4f46e5, #9333ea);
            border: none;
            border-radius: 50%;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            transition: all 0.2s;
        }
        .fab:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4);
        }
        
        /* Right Pane */
        .right-pane {
            flex: 1;
            padding: 2rem;
            overflow-y: auto;
        }
        .empty-state {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100%;
            text-align: center;
            color: rgba(255, 255, 255, 0.7);
        }
        .empty-state h3 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }
        
        /* Goal Detail */
        .goal-detail {
            display: none;
        }
        .goal-detail.active {
            display: block;
        }
        .goal-overview {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(5px);
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
        }
        .goal-overview h2 {
            font-size: 1.8rem;
            margin-bottom: 1rem;
        }
        .goal-meta {
            display: flex;
            gap: 2rem;
            margin: 1rem 0;
            flex-wrap: wrap;
        }
        .meta-item {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }
        .meta-label {
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.7);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .meta-value {
            font-weight: 500;
        }
        
        /* Matched Contacts */
        .section {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(5px);
            padding: 1.5rem;
            border-radius: 16px;
            margin-bottom: 2rem;
        }
        .section h3 {
            margin-bottom: 1.5rem;
            font-size: 1.3rem;
        }
        .contacts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1rem;
        }
        .contact-match {
            background: rgba(255, 255, 255, 0.1);
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .contact-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(135deg, #4f46e5, #9333ea);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 0.75rem;
            font-weight: bold;
            font-size: 1.2rem;
        }
        .contact-name {
            font-weight: 500;
            margin-bottom: 0.5rem;
        }
        .connect-btn {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.2s;
        }
        .connect-btn:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        
        /* Action Items */
        .action-items {
            list-style: none;
        }
        .action-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .action-icon {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #4ade80;
        }
        
        /* Modal */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
        }
        .modal.active {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .modal-content {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 2rem;
            border-radius: 20px;
            max-width: 500px;
            width: 90%;
            color: #1f2937;
        }
        .modal h3 {
            margin-bottom: 1.5rem;
            color: #1f2937;
        }
        .form-group {
            margin-bottom: 1rem;
        }
        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #374151;
        }
        .form-input, .form-textarea {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            font-size: 1rem;
        }
        .form-textarea {
            resize: vertical;
            height: 100px;
        }
        .form-actions {
            display: flex;
            gap: 1rem;
            justify-content: flex-end;
            margin-top: 2rem;
        }
        .btn {
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }
        .btn-primary {
            background: linear-gradient(135deg, #4f46e5, #9333ea);
            color: white;
        }
        .btn-secondary {
            background: #e5e7eb;
            color: #374151;
        }
        .btn:hover {
            transform: translateY(-1px);
        }
        
        .loading {
            text-align: center;
            padding: 2rem;
            color: rgba(255, 255, 255, 0.7);
        }
        
        @media (max-width: 768px) {
            .main-container {
                flex-direction: column;
            }
            .left-pane {
                width: 100%;
                height: 300px;
            }
            .goal-meta {
                flex-direction: column;
                gap: 1rem;
            }
            .contacts-grid {
                grid-template-columns: 1fr 1fr;
            }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <h1>Your Goals</h1>
        <button class="new-goal-btn" onclick="openNewGoalModal()">+ New Goal</button>
    </div>
    
    <!-- Main Container -->
    <div class="main-container">
        <!-- Left Pane: Goals List -->
        <div class="left-pane">
            <div class="goals-list" id="goalsList">
                <div class="loading">Loading your goals...</div>
            </div>
        </div>
        
        <!-- Right Pane: Goal Detail -->
        <div class="right-pane">
            <div class="empty-state" id="emptyState">
                <h3>Select a goal to view details</h3>
                <p>Choose a goal from the left to see matched contacts and action items</p>
            </div>
            
            <div class="goal-detail" id="goalDetail">
                <!-- Goal detail content will be inserted here -->
            </div>
        </div>
    </div>
    
    <!-- Floating Action Button -->
    <button class="fab" onclick="openNewGoalModal()">+</button>
    
    <!-- New Goal Modal -->
    <div class="modal" id="newGoalModal">
        <div class="modal-content">
            <h3>Create New Goal</h3>
            <form id="newGoalForm">
                <div class="form-group">
                    <label class="form-label">Goal Title</label>
                    <input type="text" class="form-input" id="goalTitle" required placeholder="e.g., Raise Series A">
                </div>
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <textarea class="form-textarea" id="goalDescription" placeholder="Describe what you want to achieve..."></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">Goal Type</label>
                    <select class="form-input" id="goalType">
                        <option value="fundraising">Fundraising</option>
                        <option value="hiring">Hiring</option>
                        <option value="partnerships">Partnerships</option>
                        <option value="sales">Sales</option>
                        <option value="networking">Networking</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Target Date</label>
                    <input type="date" class="form-input" id="goalDeadline">
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeNewGoalModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">Create Goal</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        let goals = [];
        let selectedGoalId = null;
        
        // Load goals on page load
        async function loadGoals() {
            try {
                const response = await fetch('/api/goals');
                if (!response.ok) {
                    throw new Error('Failed to load goals');
                }
                
                goals = await response.json();
                renderGoalsList();
                
            } catch (error) {
                console.error('Error loading goals:', error);
                document.getElementById('goalsList').innerHTML = `
                    <div style="text-align: center; padding: 2rem; color: rgba(255, 255, 255, 0.7);">
                        <h3>Unable to load goals</h3>
                        <p>Please try refreshing the page</p>
                        <button class="new-goal-btn" onclick="loadGoals()" style="margin-top: 1rem;">Try Again</button>
                    </div>
                `;
            }
        }
        
        function renderGoalsList() {
            const container = document.getElementById('goalsList');
            
            if (goals.length === 0) {
                container.innerHTML = `
                    <div style="text-align: center; padding: 2rem; color: rgba(255, 255, 255, 0.7);">
                        <h3>No goals yet</h3>
                        <p>Create your first goal to start building meaningful relationships</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = goals.map(goal => `
                <div class="goal-card ${selectedGoalId === goal.id ? 'active' : ''}" onclick="selectGoal('${goal.id}')">
                    <div class="goal-title">${goal.title || 'Untitled Goal'}</div>
                    <div class="goal-status">${goal.goal_type || 'general'}</div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${goal.progress_percentage || 0}%"></div>
                    </div>
                </div>
            `).join('');
        }
        
        function selectGoal(goalId) {
            selectedGoalId = goalId;
            const goal = goals.find(g => g.id === goalId);
            
            // Update active state
            renderGoalsList();
            
            // Hide empty state and show goal detail
            document.getElementById('emptyState').style.display = 'none';
            document.getElementById('goalDetail').classList.add('active');
            
            // Render goal detail
            renderGoalDetail(goal);
        }
        
        function renderGoalDetail(goal) {
            const container = document.getElementById('goalDetail');
            
            // Mock matched contacts for demo
            const mockContacts = [
                { name: 'Alice Chen', company: 'TechVC Partners', avatar: 'AC' },
                { name: 'Bob Smith', company: 'Innovation Fund', avatar: 'BS' },
                { name: 'Carol Davis', company: 'Growth Capital', avatar: 'CD' }
            ];
            
            const mockActionItems = [
                'Follow up with Alice about Series A timing',
                'Share updated deck with Bob',
                'Schedule coffee meeting with Carol',
                'Prepare investor update for next week'
            ];
            
            container.innerHTML = `
                <div class="goal-overview">
                    <h2>${goal.title || 'Untitled Goal'}</h2>
                    <p style="margin-bottom: 1.5rem; color: rgba(255, 255, 255, 0.8);">${goal.description || 'No description provided'}</p>
                    
                    <div class="goal-meta">
                        <div class="meta-item">
                            <div class="meta-label">Status</div>
                            <div class="meta-value">${goal.status || 'In Progress'}</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">Type</div>
                            <div class="meta-value">${goal.goal_type || 'General'}</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">Progress</div>
                            <div class="meta-value">${goal.progress_percentage || 0}%</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-label">Created</div>
                            <div class="meta-value">${goal.created_at ? new Date(goal.created_at).toLocaleDateString() : 'Recently'}</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h3>Matched Contacts</h3>
                    <div class="contacts-grid">
                        ${mockContacts.map(contact => `
                            <div class="contact-match">
                                <div class="contact-avatar">${contact.avatar}</div>
                                <div class="contact-name">${contact.name}</div>
                                <div style="font-size: 0.8rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 0.75rem;">${contact.company}</div>
                                <button class="connect-btn" onclick="connectToContact('${contact.name}')">Connect</button>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <div class="section">
                    <h3>AI-Generated Action Items</h3>
                    <ul class="action-items">
                        ${mockActionItems.map(item => `
                            <li class="action-item">
                                <div class="action-icon"></div>
                                <span>${item}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }
        
        function connectToContact(name) {
            alert(`Connecting to ${name}... This will integrate with AI suggestions in the future.`);
        }
        
        // Modal functions
        function openNewGoalModal() {
            document.getElementById('newGoalModal').classList.add('active');
        }
        
        function closeNewGoalModal() {
            document.getElementById('newGoalModal').classList.remove('active');
            document.getElementById('newGoalForm').reset();
        }
        
        // Handle new goal creation
        document.getElementById('newGoalForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                title: document.getElementById('goalTitle').value,
                description: document.getElementById('goalDescription').value,
                goal_type: document.getElementById('goalType').value,
                timeline: document.getElementById('goalDeadline').value,
                status: 'active'
            };
            
            try {
                const response = await fetch('/api/goals', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(formData)
                });
                
                if (response.ok) {
                    closeNewGoalModal();
                    loadGoals(); // Reload goals list
                } else {
                    alert('Failed to create goal. Please try again.');
                }
            } catch (error) {
                console.error('Error creating goal:', error);
                alert('Network error. Please try again.');
            }
        });
        
        // Close modal when clicking outside
        document.getElementById('newGoalModal').addEventListener('click', (e) => {
            if (e.target.id === 'newGoalModal') {
                closeNewGoalModal();
            }
        });
        
        // Initialize page
        loadGoals();
    </script>
</body>
</html>
    ''')

@app.route('/intelligence')
def serve_intelligence_page():
    """Serve AI Intelligence page with chat interface"""
    # Check authentication
    if 'user_id' not in session:
        return redirect(url_for('serve_login_page'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Intelligence - Rhiz</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(-45deg, #1e3a8a, #3730a3, #581c87, #7c2d12);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            min-height: 100vh;
            color: white;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .intelligence-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .hero-bar {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .hero-title {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff, #e0e7ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .hero-subtitle {
            margin-top: 0.5rem;
            color: rgba(255, 255, 255, 0.8);
            font-size: 1rem;
        }
        
        .refresh-btn {
            background: linear-gradient(135deg, #4f46e5, #9333ea);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(79, 70, 229, 0.3);
        }
        
        .main-layout {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 2rem;
            flex: 1;
            min-height: 0;
        }
        
        .chat-panel {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            padding: 1rem 1.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            font-weight: 600;
            color: rgba(255, 255, 255, 0.9);
        }
        
        .chat-history {
            flex: 1;
            padding: 1rem;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            min-height: 400px;
        }
        
        .chat-message {
            display: flex;
            gap: 0.75rem;
            max-width: 80%;
        }
        
        .chat-message.user {
            align-self: flex-end;
            flex-direction: row-reverse;
        }
        
        .message-bubble {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 0.75rem 1rem;
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .chat-message.user .message-bubble {
            background: linear-gradient(135deg, #4f46e5, #9333ea);
        }
        
        .chat-input-area {
            padding: 1rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            gap: 0.75rem;
        }
        
        .chat-input {
            flex: 1;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 0.75rem;
            color: white;
            outline: none;
            resize: none;
            font-family: inherit;
        }
        
        .chat-input::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }
        
        .send-btn {
            background: linear-gradient(135deg, #4f46e5, #9333ea);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .send-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(79, 70, 229, 0.3);
        }
        
        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .insights-panel {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }
        
        .insights-section {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 1.5rem;
        }
        
        .section-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: rgba(255, 255, 255, 0.9);
        }
        
        .recommendation-item {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.75rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            margin-bottom: 0.75rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.2s;
        }
        
        .recommendation-item:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-1px);
        }
        
        .contact-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: linear-gradient(135deg, #4f46e5, #9333ea);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            color: white;
        }
        
        .contact-info {
            flex: 1;
        }
        
        .contact-name {
            font-weight: 600;
            color: rgba(255, 255, 255, 0.9);
        }
        
        .contact-reason {
            font-size: 0.875rem;
            color: rgba(255, 255, 255, 0.7);
            margin-top: 0.25rem;
        }
        
        .go-btn {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            padding: 0.375rem 0.75rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.875rem;
            transition: all 0.2s;
        }
        
        .go-btn:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .alert-item {
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            margin-bottom: 0.75rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-left: 4px solid #10b981;
        }
        
        .alert-text {
            color: rgba(255, 255, 255, 0.9);
            font-weight: 500;
        }
        
        .quick-prompts {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .prompt-btn {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            padding: 0.75rem;
            border-radius: 12px;
            cursor: pointer;
            text-align: left;
            transition: all 0.2s;
            font-size: 0.875rem;
        }
        
        .prompt-btn:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-1px);
        }
        
        .loading {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: rgba(255, 255, 255, 0.7);
            font-style: italic;
        }
        
        .loading-spinner {
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-top: 2px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .main-layout {
                grid-template-columns: 1fr;
                grid-template-rows: 1fr auto;
            }
            
            .insights-panel {
                max-height: 400px;
                overflow-y: auto;
            }
        }
    </style>
</head>
<body>
    <div class="intelligence-container">
        <!-- Hero Bar -->
        <div class="hero-bar">
            <div>
                <h1 class="hero-title">Rhiz AI Assistant</h1>
                <p class="hero-subtitle">Get personalized relationship advice and opportunity insights</p>
            </div>
            <button class="refresh-btn" onclick="refreshInsights()">Refresh Insights</button>
        </div>
        
        <!-- Main Layout -->
        <div class="main-layout">
            <!-- Left Chat Panel -->
            <div class="chat-panel">
                <div class="chat-header">Chat History</div>
                <div class="chat-history" id="chatHistory">
                    <div class="chat-message">
                        <div class="message-bubble">
                            👋 Hello! I'm your Rhiz AI assistant. I can help you with relationship advice, contact prioritization, and opportunity insights. What would you like to know about your network?
                        </div>
                    </div>
                </div>
                <div class="chat-input-area">
                    <textarea class="chat-input" id="chatInput" placeholder="Ask me about your contacts, goals, or relationship strategy..." rows="2"></textarea>
                    <button class="send-btn" id="sendBtn" onclick="sendMessage()">Send</button>
                </div>
            </div>
            
            <!-- Right Insights Panel -->
            <div class="insights-panel">
                <!-- Contact Recommendations -->
                <div class="insights-section">
                    <h3 class="section-title">Contact Recommendations</h3>
                    <div id="recommendations">
                        <div class="loading">
                            <div class="loading-spinner"></div>
                            Loading recommendations...
                        </div>
                    </div>
                </div>
                
                <!-- Opportunity Alerts -->
                <div class="insights-section">
                    <h3 class="section-title">Opportunity Alerts</h3>
                    <div id="alerts">
                        <div class="loading">
                            <div class="loading-spinner"></div>
                            Loading alerts...
                        </div>
                    </div>
                </div>
                
                <!-- Quick Prompts -->
                <div class="insights-section">
                    <h3 class="section-title">Quick Prompts</h3>
                    <div class="quick-prompts">
                        <button class="prompt-btn" onclick="askQuickPrompt('Who should I reach out to for funding opportunities?')">
                            💰 Show me best people to ask for funding
                        </button>
                        <button class="prompt-btn" onclick="askQuickPrompt('Which contacts haven\\'t I spoken to in a while?')">
                            🔄 Find contacts I should reconnect with
                        </button>
                        <button class="prompt-btn" onclick="askQuickPrompt('Who in my network could help with hiring?')">
                            👥 Identify hiring connections
                        </button>
                        <button class="prompt-btn" onclick="askQuickPrompt('What relationship building opportunities do I have this week?')">
                            📅 Weekly relationship opportunities
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let isLoading = false;
        
        // Initialize page
        loadInsights();
        
        // Auto-resize textarea
        document.getElementById('chatInput').addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        // Send message on Enter (but allow Shift+Enter for new lines)
        document.getElementById('chatInput').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        async function sendMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (!message || isLoading) return;
            
            // Add user message to chat
            addMessageToChat(message, 'user');
            input.value = '';
            input.style.height = 'auto';
            
            // Show loading
            setLoading(true);
            
            try {
                const response = await fetch('/api/intelligence/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    addMessageToChat(data.response, 'ai');
                } else {
                    addMessageToChat('Sorry, I encountered an error. Please try again.', 'ai');
                }
            } catch (error) {
                console.error('Chat error:', error);
                addMessageToChat('Sorry, I couldn\\'t process your message right now. Please try again.', 'ai');
            }
            
            setLoading(false);
        }
        
        function addMessageToChat(message, sender) {
            const chatHistory = document.getElementById('chatHistory');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${sender}`;
            
            messageDiv.innerHTML = `
                <div class="message-bubble">
                    ${message}
                </div>
            `;
            
            chatHistory.appendChild(messageDiv);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }
        
        function askQuickPrompt(prompt) {
            const input = document.getElementById('chatInput');
            input.value = prompt;
            sendMessage();
        }
        
        function setLoading(loading) {
            isLoading = loading;
            const sendBtn = document.getElementById('sendBtn');
            sendBtn.disabled = loading;
            sendBtn.textContent = loading ? 'Sending...' : 'Send';
        }
        
        async function loadInsights() {
            try {
                const response = await fetch('/api/insights');
                const data = await response.json();
                
                if (data.success) {
                    updateRecommendations(data.recommendations || []);
                    updateAlerts(data.alerts || []);
                }
            } catch (error) {
                console.error('Failed to load insights:', error);
                showInsightsError();
            }
        }
        
        function updateRecommendations(recommendations) {
            const container = document.getElementById('recommendations');
            
            if (recommendations.length === 0) {
                container.innerHTML = '<p style="color: rgba(255, 255, 255, 0.7); font-style: italic;">No recommendations available.</p>';
                return;
            }
            
            container.innerHTML = recommendations.map(rec => `
                <div class="recommendation-item">
                    <div class="contact-avatar">${rec.name.charAt(0)}</div>
                    <div class="contact-info">
                        <div class="contact-name">${rec.name}</div>
                        <div class="contact-reason">${rec.reason}</div>
                    </div>
                    <button class="go-btn" onclick="openContactDetail('${rec.id}')">Go</button>
                </div>
            `).join('');
        }
        
        function updateAlerts(alerts) {
            const container = document.getElementById('alerts');
            
            if (alerts.length === 0) {
                container.innerHTML = '<p style="color: rgba(255, 255, 255, 0.7); font-style: italic;">No new alerts.</p>';
                return;
            }
            
            container.innerHTML = alerts.map(alert => `
                <div class="alert-item">
                    <div class="alert-text">${alert.text}</div>
                </div>
            `).join('');
        }
        
        function showInsightsError() {
            document.getElementById('recommendations').innerHTML = '<p style="color: rgba(255, 255, 255, 0.7);">Failed to load recommendations.</p>';
            document.getElementById('alerts').innerHTML = '<p style="color: rgba(255, 255, 255, 0.7);">Failed to load alerts.</p>';
        }
        
        async function refreshInsights() {
            const button = event.target;
            const originalText = button.textContent;
            button.textContent = 'Refreshing...';
            button.disabled = true;
            
            await loadInsights();
            
            button.textContent = originalText;
            button.disabled = false;
        }
        
        function openContactDetail(contactId) {
            // TODO: Implement contact detail drawer
            console.log('Opening contact detail for:', contactId);
            alert('Contact detail feature coming soon!');
        }
    </script>
</body>
</html>
    ''')

@app.route('/settings')
def serve_settings_page():
    """Serve Settings page with tabbed interface"""
    # Check authentication
    if 'user_id' not in session:
        return redirect(url_for('serve_login_page'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Settings - Rhiz</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(-45deg, #1e3a8a, #3730a3, #581c87, #7c2d12);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            min-height: 100vh;
            color: white;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .settings-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .settings-header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .settings-title {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff, #e0e7ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .save-btn {
            background: linear-gradient(135deg, #4f46e5, #9333ea);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .save-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(79, 70, 229, 0.3);
        }
        
        .save-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .settings-layout {
            display: grid;
            grid-template-columns: 250px 1fr;
            gap: 2rem;
            flex: 1;
        }
        
        .settings-sidebar {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 1.5rem 0;
            height: fit-content;
        }
        
        .tab-button {
            width: 100%;
            background: none;
            border: none;
            color: rgba(255, 255, 255, 0.8);
            padding: 1rem 1.5rem;
            text-align: left;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 1rem;
            border-left: 3px solid transparent;
        }
        
        .tab-button:hover {
            background: rgba(255, 255, 255, 0.05);
            color: white;
        }
        
        .tab-button.active {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border-left-color: #4f46e5;
        }
        
        .settings-content {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 2rem;
        }
        
        .tab-panel {
            display: none;
        }
        
        .tab-panel.active {
            display: block;
        }
        
        .section-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            color: rgba(255, 255, 255, 0.9);
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: rgba(255, 255, 255, 0.9);
        }
        
        .form-input, .form-select, .form-textarea {
            width: 100%;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 0.75rem;
            color: white;
            outline: none;
            font-family: inherit;
        }
        
        .form-input::placeholder, .form-textarea::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }
        
        .form-input:focus, .form-select:focus, .form-textarea:focus {
            border-color: #4f46e5;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2);
        }
        
        .photo-upload {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .photo-preview {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: linear-gradient(135deg, #4f46e5, #9333ea);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            color: white;
            position: relative;
            overflow: hidden;
        }
        
        .photo-preview img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        
        .upload-btn {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.875rem;
            transition: all 0.2s;
        }
        
        .upload-btn:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .toggle-switch {
            position: relative;
            display: inline-block;
            width: 50px;
            height: 24px;
        }
        
        .toggle-switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.2);
            transition: 0.3s;
            border-radius: 24px;
        }
        
        .slider:before {
            position: absolute;
            content: "";
            height: 18px;
            width: 18px;
            left: 3px;
            bottom: 3px;
            background: white;
            transition: 0.3s;
            border-radius: 50%;
        }
        
        input:checked + .slider {
            background: #4f46e5;
        }
        
        input:checked + .slider:before {
            transform: translateX(26px);
        }
        
        .notification-item {
            display: flex;
            justify-content: between;
            align-items: center;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            margin-bottom: 1rem;
        }
        
        .notification-label {
            flex: 1;
        }
        
        .notification-title {
            font-weight: 500;
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 0.25rem;
        }
        
        .notification-desc {
            font-size: 0.875rem;
            color: rgba(255, 255, 255, 0.7);
        }
        
        .integration-card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1.5rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            margin-bottom: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .integration-info {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .integration-icon {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            background: linear-gradient(135deg, #4f46e5, #9333ea);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            color: white;
        }
        
        .integration-details h3 {
            font-weight: 600;
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 0.25rem;
        }
        
        .integration-details p {
            font-size: 0.875rem;
            color: rgba(255, 255, 255, 0.7);
        }
        
        .integration-actions {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .status-badge {
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        
        .status-connected {
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }
        
        .status-disconnected {
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }
        
        .connect-btn {
            background: linear-gradient(135deg, #4f46e5, #9333ea);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.875rem;
            transition: all 0.2s;
        }
        
        .disconnect-btn {
            background: rgba(239, 68, 68, 0.8);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.875rem;
            transition: all 0.2s;
        }
        
        .connect-btn:hover, .disconnect-btn:hover {
            transform: translateY(-1px);
        }
        
        .danger-zone {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 2rem;
        }
        
        .danger-title {
            color: #ef4444;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        
        .danger-btn {
            background: #ef4444;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .danger-btn:hover {
            background: #dc2626;
        }
        
        .time-input-group {
            display: flex;
            gap: 0.5rem;
            align-items: center;
        }
        
        .time-input {
            width: 80px;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(5px);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        
        .modal.show {
            display: flex;
        }
        
        .modal-content {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-radius: 16px;
            padding: 2rem;
            max-width: 400px;
            width: 90%;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .modal-actions {
            display: flex;
            gap: 1rem;
            justify-content: flex-end;
            margin-top: 1.5rem;
        }
        
        .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        @media (max-width: 768px) {
            .settings-layout {
                grid-template-columns: 1fr;
                gap: 1rem;
            }
            
            .settings-sidebar {
                display: flex;
                overflow-x: auto;
                padding: 0.75rem;
                gap: 0.5rem;
            }
            
            .tab-button {
                white-space: nowrap;
                padding: 0.75rem 1rem;
                border-left: none;
                border-bottom: 3px solid transparent;
            }
            
            .tab-button.active {
                border-left: none;
                border-bottom-color: #4f46e5;
            }
        }
    </style>
</head>
<body>
    <div class="settings-container">
        <!-- Settings Header -->
        <div class="settings-header">
            <h1 class="settings-title">Settings</h1>
            <button class="save-btn" id="saveBtn" onclick="saveSettings()">Save Changes</button>
        </div>
        
        <!-- Settings Layout -->
        <div class="settings-layout">
            <!-- Sidebar -->
            <div class="settings-sidebar">
                <button class="tab-button active" onclick="switchTab('profile')">Profile</button>
                <button class="tab-button" onclick="switchTab('notifications')">Notifications</button>
                <button class="tab-button" onclick="switchTab('integrations')">Integrations</button>
                <button class="tab-button" onclick="switchTab('privacy')">Privacy & Security</button>
            </div>
            
            <!-- Content Area -->
            <div class="settings-content">
                <!-- Profile Tab -->
                <div id="profile-panel" class="tab-panel active">
                    <h2 class="section-title">Profile Settings</h2>
                    
                    <!-- Photo Upload -->
                    <div class="photo-upload">
                        <div class="photo-preview" id="photoPreview">
                            <span id="photoInitial">U</span>
                        </div>
                        <div>
                            <input type="file" id="photoInput" accept="image/*" style="display: none;" onchange="handlePhotoUpload(event)">
                            <button class="upload-btn" onclick="document.getElementById('photoInput').click()">Upload Photo</button>
                            <p style="font-size: 0.875rem; color: rgba(255, 255, 255, 0.7); margin-top: 0.5rem;">JPG, PNG up to 5MB</p>
                        </div>
                    </div>
                    
                    <!-- Profile Form -->
                    <div class="form-group">
                        <label class="form-label" for="fullName">Full Name</label>
                        <input type="text" id="fullName" class="form-input" placeholder="Enter your full name" value="Demo User">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="email">Email Address</label>
                        <input type="email" id="email" class="form-input" placeholder="Enter your email" value="demo@rhiz.app">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="timezone">Timezone</label>
                        <select id="timezone" class="form-select">
                            <option value="UTC">UTC (Coordinated Universal Time)</option>
                            <option value="America/New_York">Eastern Time (ET)</option>
                            <option value="America/Chicago">Central Time (CT)</option>
                            <option value="America/Denver">Mountain Time (MT)</option>
                            <option value="America/Los_Angeles" selected>Pacific Time (PT)</option>
                            <option value="Europe/London">GMT (London)</option>
                            <option value="Europe/Paris">CET (Paris)</option>
                            <option value="Asia/Tokyo">JST (Tokyo)</option>
                        </select>
                    </div>
                </div>
                
                <!-- Notifications Tab -->
                <div id="notifications-panel" class="tab-panel">
                    <h2 class="section-title">Notification Preferences</h2>
                    
                    <div class="notification-item">
                        <div class="notification-label">
                            <div class="notification-title">Email Reminders</div>
                            <div class="notification-desc">Get relationship tips and follow-up reminders via email</div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="emailReminders" checked>
                            <span class="slider"></span>
                        </label>
                    </div>
                    
                    <div class="notification-item">
                        <div class="notification-label">
                            <div class="notification-title">SMS Nudges</div>
                            <div class="notification-desc">Important relationship opportunities sent via text</div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="smsNudges">
                            <span class="slider"></span>
                        </label>
                    </div>
                    
                    <div class="notification-item">
                        <div class="notification-label">
                            <div class="notification-title">Weekly Digest</div>
                            <div class="notification-desc">Weekly summary of network insights and opportunities</div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="weeklyDigest" checked>
                            <span class="slider"></span>
                        </label>
                    </div>
                    
                    <div class="form-group" style="margin-top: 2rem;">
                        <label class="form-label">Quiet Hours</label>
                        <p style="font-size: 0.875rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 1rem;">Don't send notifications during these hours</p>
                        <div class="time-input-group">
                            <input type="time" id="quietStart" class="form-input time-input" value="22:00">
                            <span style="color: rgba(255, 255, 255, 0.7);">to</span>
                            <input type="time" id="quietEnd" class="form-input time-input" value="08:00">
                        </div>
                    </div>
                </div>
                
                <!-- Integrations Tab -->
                <div id="integrations-panel" class="tab-panel">
                    <h2 class="section-title">Connected Accounts</h2>
                    
                    <!-- Google Integration -->
                    <div class="integration-card">
                        <div class="integration-info">
                            <div class="integration-icon">G</div>
                            <div class="integration-details">
                                <h3>Google Contacts</h3>
                                <p>Sync your contacts and calendar events</p>
                            </div>
                        </div>
                        <div class="integration-actions">
                            <span class="status-badge status-disconnected">Disconnected</span>
                            <button class="connect-btn" onclick="connectIntegration('google')">Connect</button>
                        </div>
                    </div>
                    
                    <!-- LinkedIn Integration -->
                    <div class="integration-card">
                        <div class="integration-info">
                            <div class="integration-icon">in</div>
                            <div class="integration-details">
                                <h3>LinkedIn</h3>
                                <p>Import professional connections and updates</p>
                            </div>
                        </div>
                        <div class="integration-actions">
                            <span class="status-badge status-disconnected">Disconnected</span>
                            <button class="connect-btn" onclick="connectIntegration('linkedin')">Connect</button>
                        </div>
                    </div>
                    
                    <!-- Twitter Integration -->
                    <div class="integration-card">
                        <div class="integration-info">
                            <div class="integration-icon">𝕏</div>
                            <div class="integration-details">
                                <h3>Twitter / X</h3>
                                <p>Track social interactions and updates</p>
                            </div>
                        </div>
                        <div class="integration-actions">
                            <span class="status-badge status-disconnected">Disconnected</span>
                            <button class="connect-btn" onclick="connectIntegration('twitter')">Connect</button>
                        </div>
                    </div>
                    
                    <!-- iCloud Integration -->
                    <div class="integration-card">
                        <div class="integration-info">
                            <div class="integration-icon">☁</div>
                            <div class="integration-details">
                                <h3>iCloud Contacts</h3>
                                <p>Sync your Apple contacts and calendar</p>
                            </div>
                        </div>
                        <div class="integration-actions">
                            <span class="status-badge status-disconnected">Disconnected</span>
                            <button class="connect-btn" onclick="connectIntegration('icloud')">Connect</button>
                        </div>
                    </div>
                </div>
                
                <!-- Privacy & Security Tab -->
                <div id="privacy-panel" class="tab-panel">
                    <h2 class="section-title">Privacy & Security</h2>
                    
                    <!-- Change Password -->
                    <div class="form-group">
                        <label class="form-label" for="currentPassword">Current Password</label>
                        <input type="password" id="currentPassword" class="form-input" placeholder="Enter current password">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="newPassword">New Password</label>
                        <input type="password" id="newPassword" class="form-input" placeholder="Enter new password">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label" for="confirmPassword">Confirm New Password</label>
                        <input type="password" id="confirmPassword" class="form-input" placeholder="Confirm new password">
                    </div>
                    
                    <!-- 2FA Toggle -->
                    <div class="notification-item" style="margin: 2rem 0;">
                        <div class="notification-label">
                            <div class="notification-title">Two-Factor Authentication</div>
                            <div class="notification-desc">Add an extra layer of security to your account</div>
                        </div>
                        <label class="toggle-switch">
                            <input type="checkbox" id="twoFactor">
                            <span class="slider"></span>
                        </label>
                    </div>
                    
                    <!-- Data Management -->
                    <div style="margin: 2rem 0;">
                        <h3 style="color: rgba(255, 255, 255, 0.9); margin-bottom: 1rem;">Data Management</h3>
                        <button class="btn-secondary" onclick="downloadData()" style="margin-bottom: 1rem; display: block;">
                            📄 Download My Data
                        </button>
                        <p style="font-size: 0.875rem; color: rgba(255, 255, 255, 0.7);">Export all your data including contacts, goals, and interactions</p>
                    </div>
                    
                    <!-- Danger Zone -->
                    <div class="danger-zone">
                        <h3 class="danger-title">Danger Zone</h3>
                        <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 1rem;">Once you delete your account, there is no going back. Please be certain.</p>
                        <button class="danger-btn" onclick="confirmDeleteAccount()">Delete My Account</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Delete Account Confirmation Modal -->
    <div id="deleteModal" class="modal">
        <div class="modal-content">
            <h3 style="color: #ef4444; margin-bottom: 1rem;">Delete Account</h3>
            <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 1.5rem;">
                Are you sure you want to delete your account? This action cannot be undone and will permanently remove all your data.
            </p>
            <div class="form-group">
                <label class="form-label">Type "DELETE" to confirm:</label>
                <input type="text" id="deleteConfirmInput" class="form-input" placeholder="DELETE">
            </div>
            <div class="modal-actions">
                <button class="btn-secondary" onclick="closeDeleteModal()">Cancel</button>
                <button class="danger-btn" id="confirmDeleteBtn" onclick="deleteAccount()" disabled>Delete Account</button>
            </div>
        </div>
    </div>
    
    <script>
        let hasChanges = false;
        
        // Tab switching
        function switchTab(tabName) {
            // Update buttons
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            // Update panels
            document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
            document.getElementById(tabName + '-panel').classList.add('active');
        }
        
        // Track changes
        document.addEventListener('input', function() {
            hasChanges = true;
            updateSaveButton();
        });
        
        document.addEventListener('change', function() {
            hasChanges = true;
            updateSaveButton();
        });
        
        function updateSaveButton() {
            const saveBtn = document.getElementById('saveBtn');
            if (hasChanges) {
                saveBtn.textContent = 'Save Changes';
                saveBtn.disabled = false;
            } else {
                saveBtn.textContent = 'Saved';
                saveBtn.disabled = true;
            }
        }
        
        // Photo upload
        function handlePhotoUpload(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const photoPreview = document.getElementById('photoPreview');
                    photoPreview.innerHTML = `<img src="${e.target.result}" alt="Profile Photo">`;
                };
                reader.readAsDataURL(file);
            }
        }
        
        // Save settings
        async function saveSettings() {
            const saveBtn = document.getElementById('saveBtn');
            saveBtn.textContent = 'Saving...';
            saveBtn.disabled = true;
            
            try {
                // Collect all settings data
                const settings = {
                    profile: {
                        fullName: document.getElementById('fullName').value,
                        email: document.getElementById('email').value,
                        timezone: document.getElementById('timezone').value
                    },
                    notifications: {
                        emailReminders: document.getElementById('emailReminders').checked,
                        smsNudges: document.getElementById('smsNudges').checked,
                        weeklyDigest: document.getElementById('weeklyDigest').checked,
                        quietHours: {
                            start: document.getElementById('quietStart').value,
                            end: document.getElementById('quietEnd').value
                        }
                    },
                    privacy: {
                        twoFactor: document.getElementById('twoFactor').checked
                    }
                };
                
                const response = await fetch('/api/user/settings', {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(settings)
                });
                
                if (response.ok) {
                    hasChanges = false;
                    saveBtn.textContent = 'Saved';
                    showMessage('Settings saved successfully!', 'success');
                } else {
                    throw new Error('Failed to save settings');
                }
            } catch (error) {
                console.error('Settings save error:', error);
                saveBtn.textContent = 'Save Changes';
                saveBtn.disabled = false;
                showMessage('Failed to save settings. Please try again.', 'error');
            }
        }
        
        // Integration connections
        function connectIntegration(provider) {
            // This would typically open OAuth popup
            showMessage(`${provider} integration will be available soon!`, 'info');
        }
        
        // Data download
        function downloadData() {
            // Trigger data export
            window.open('/api/user/settings?export=true', '_blank');
        }
        
        // Delete account confirmation
        function confirmDeleteAccount() {
            document.getElementById('deleteModal').classList.add('show');
        }
        
        function closeDeleteModal() {
            document.getElementById('deleteModal').classList.remove('show');
            document.getElementById('deleteConfirmInput').value = '';
            document.getElementById('confirmDeleteBtn').disabled = true;
        }
        
        // Enable delete button when "DELETE" is typed
        document.getElementById('deleteConfirmInput').addEventListener('input', function() {
            const confirmBtn = document.getElementById('confirmDeleteBtn');
            confirmBtn.disabled = this.value !== 'DELETE';
        });
        
        async function deleteAccount() {
            try {
                const response = await fetch('/api/user/account', {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    alert('Account deleted successfully. You will be redirected to the homepage.');
                    window.location.href = '/';
                } else {
                    throw new Error('Failed to delete account');
                }
            } catch (error) {
                console.error('Delete account error:', error);
                showMessage('Failed to delete account. Please try again.', 'error');
            }
        }
        
        // Utility function for showing messages
        function showMessage(text, type) {
            // Simple alert for now - could be enhanced with toast notifications
            alert(text);
        }
        
        // Initialize
        updateSaveButton();
    </script>
</body>
</html>
    ''')

@app.route('/network')
def serve_network_page():
    """Serve Network/Relationship Map page with interactive graph"""
    # Check authentication
    if 'user_id' not in session:
        return redirect(url_for('serve_login_page'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network - Rhiz</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(-45deg, #1e3a8a, #3730a3, #581c87, #7c2d12);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            min-height: 100vh;
            color: white;
            overflow: hidden;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .network-container {
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .network-header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            padding: 1rem 2rem;
            display: flex;
            justify-content: between;
            align-items: center;
            z-index: 100;
        }
        
        .network-title {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff, #e0e7ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .filters-toggle {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .filters-toggle:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .network-body {
            flex: 1;
            display: grid;
            grid-template-columns: 300px 1fr 350px;
            position: relative;
        }
        
        .filters-sidebar {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.2);
            padding: 1.5rem;
            overflow-y: auto;
            transition: transform 0.3s ease;
        }
        
        .filters-sidebar.hidden {
            transform: translateX(-100%);
        }
        
        .filter-section {
            margin-bottom: 2rem;
        }
        
        .filter-title {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: rgba(255, 255, 255, 0.9);
        }
        
        .tag-filter {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }
        
        .tag-checkbox {
            display: none;
        }
        
        .tag-label {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 0.375rem 0.75rem;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.875rem;
            transition: all 0.2s;
        }
        
        .tag-checkbox:checked + .tag-label {
            background: linear-gradient(135deg, #4f46e5, #9333ea);
            border-color: #4f46e5;
        }
        
        .tag-label:hover {
            background: rgba(255, 255, 255, 0.15);
        }
        
        .strength-slider {
            margin: 1rem 0;
        }
        
        .slider {
            width: 100%;
            height: 6px;
            border-radius: 3px;
            background: rgba(255, 255, 255, 0.2);
            outline: none;
            -webkit-appearance: none;
        }
        
        .slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: linear-gradient(135deg, #4f46e5, #9333ea);
            cursor: pointer;
        }
        
        .slider::-moz-range-thumb {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: linear-gradient(135deg, #4f46e5, #9333ea);
            cursor: pointer;
            border: none;
        }
        
        .slider-value {
            text-align: center;
            margin-top: 0.5rem;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.875rem;
        }
        
        .date-input {
            width: 100%;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 0.5rem;
            color: white;
            outline: none;
        }
        
        .date-input:focus {
            border-color: #4f46e5;
        }
        
        .graph-canvas {
            position: relative;
            background: rgba(255, 255, 255, 0.02);
            overflow: hidden;
        }
        
        .graph-svg {
            width: 100%;
            height: 100%;
            cursor: grab;
        }
        
        .graph-svg:active {
            cursor: grabbing;
        }
        
        .node {
            fill: #4f46e5;
            stroke: white;
            stroke-width: 2px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .node:hover {
            fill: #9333ea;
            stroke-width: 3px;
        }
        
        .node.selected {
            fill: #10b981;
            stroke: #34d399;
            stroke-width: 4px;
        }
        
        .link {
            stroke: rgba(255, 255, 255, 0.3);
            stroke-width: 1.5px;
        }
        
        .node-label {
            font-size: 12px;
            fill: white;
            text-anchor: middle;
            pointer-events: none;
            font-weight: 500;
        }
        
        .tooltip {
            position: absolute;
            background: rgba(0, 0, 0, 0.9);
            backdrop-filter: blur(10px);
            color: white;
            padding: 0.75rem;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            font-size: 0.875rem;
            pointer-events: none;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.2s;
        }
        
        .tooltip.show {
            opacity: 1;
        }
        
        .detail-panel {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border-left: 1px solid rgba(255, 255, 255, 0.2);
            padding: 1.5rem;
            overflow-y: auto;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        }
        
        .detail-panel.open {
            transform: translateX(0);
        }
        
        .detail-header {
            text-align: center;
            margin-bottom: 1.5rem;
        }
        
        .contact-avatar {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            background: linear-gradient(135deg, #4f46e5, #9333ea);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            color: white;
            margin: 0 auto 1rem;
        }
        
        .contact-name {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: rgba(255, 255, 255, 0.9);
        }
        
        .contact-company {
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 1rem;
        }
        
        .detail-section {
            margin-bottom: 1.5rem;
        }
        
        .detail-section h4 {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            color: rgba(255, 255, 255, 0.9);
        }
        
        .metadata-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
            padding: 0.5rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
        }
        
        .metadata-label {
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.875rem;
        }
        
        .metadata-value {
            color: rgba(255, 255, 255, 0.9);
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .action-buttons {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }
        
        .action-btn {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            padding: 0.75rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            justify-content: center;
        }
        
        .action-btn:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .action-btn.primary {
            background: linear-gradient(135deg, #4f46e5, #9333ea);
        }
        
        .action-btn.danger {
            background: rgba(239, 68, 68, 0.8);
        }
        
        .graph-controls {
            position: absolute;
            top: 1rem;
            right: 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            z-index: 50;
        }
        
        .control-btn {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }
        
        .control-btn:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .close-panel {
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }
        
        .close-panel:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        @media (max-width: 768px) {
            .network-body {
                grid-template-columns: 1fr;
            }
            
            .filters-sidebar {
                position: absolute;
                top: 0;
                left: 0;
                bottom: 0;
                z-index: 200;
                width: 300px;
            }
            
            .detail-panel {
                position: absolute;
                top: 0;
                right: 0;
                bottom: 0;
                z-index: 200;
                width: 350px;
            }
        }
    </style>
</head>
<body>
    <div class="network-container">
        <!-- Header -->
        <div class="network-header">
            <h1 class="network-title">Relationship Map</h1>
            <button class="filters-toggle" onclick="toggleFilters()">
                <span>Filters</span>
                <span id="filtersIcon">▼</span>
            </button>
        </div>
        
        <!-- Body -->
        <div class="network-body">
            <!-- Filters Sidebar -->
            <div class="filters-sidebar" id="filtersSidebar">
                <!-- Tags Filter -->
                <div class="filter-section">
                    <h3 class="filter-title">Tags</h3>
                    <div class="tag-filter">
                        <input type="checkbox" id="tag-mentor" class="tag-checkbox" value="mentor" onchange="applyFilters()">
                        <label for="tag-mentor" class="tag-label">Mentor</label>
                        
                        <input type="checkbox" id="tag-investor" class="tag-checkbox" value="investor" onchange="applyFilters()">
                        <label for="tag-investor" class="tag-label">Investor</label>
                        
                        <input type="checkbox" id="tag-friend" class="tag-checkbox" value="friend" onchange="applyFilters()">
                        <label for="tag-friend" class="tag-label">Friend</label>
                        
                        <input type="checkbox" id="tag-colleague" class="tag-checkbox" value="colleague" onchange="applyFilters()">
                        <label for="tag-colleague" class="tag-label">Colleague</label>
                        
                        <input type="checkbox" id="tag-client" class="tag-checkbox" value="client" onchange="applyFilters()">
                        <label for="tag-client" class="tag-label">Client</label>
                        
                        <input type="checkbox" id="tag-partner" class="tag-checkbox" value="partner" onchange="applyFilters()">
                        <label for="tag-partner" class="tag-label">Partner</label>
                    </div>
                </div>
                
                <!-- Strength Filter -->
                <div class="filter-section">
                    <h3 class="filter-title">Relationship Strength</h3>
                    <div class="strength-slider">
                        <input type="range" id="strengthSlider" class="slider" min="0" max="100" value="0" oninput="updateStrengthValue(); applyFilters()">
                        <div class="slider-value">Min: <span id="strengthValue">0</span></div>
                    </div>
                </div>
                
                <!-- Last Interaction Filter -->
                <div class="filter-section">
                    <h3 class="filter-title">Last Interaction</h3>
                    <input type="date" id="lastInteraction" class="date-input" onchange="applyFilters()" placeholder="Since date">
                </div>
                
                <!-- Reset Filters -->
                <div class="filter-section">
                    <button class="action-btn" onclick="resetFilters()">Reset All Filters</button>
                </div>
            </div>
            
            <!-- Graph Canvas -->
            <div class="graph-canvas">
                <svg class="graph-svg" id="networkGraph"></svg>
                
                <!-- Graph Controls -->
                <div class="graph-controls">
                    <button class="control-btn" onclick="zoomIn()" title="Zoom In">+</button>
                    <button class="control-btn" onclick="zoomOut()" title="Zoom Out">−</button>
                    <button class="control-btn" onclick="resetView()" title="Reset View">⌂</button>
                </div>
                
                <!-- Tooltip -->
                <div class="tooltip" id="tooltip">
                    <div id="tooltipContent"></div>
                </div>
            </div>
            
            <!-- Detail Panel -->
            <div class="detail-panel" id="detailPanel">
                <button class="close-panel" onclick="closeDetailPanel()">×</button>
                
                <div class="detail-header">
                    <div class="contact-avatar" id="detailAvatar">S</div>
                    <div class="contact-name" id="detailName">Select a contact</div>
                    <div class="contact-company" id="detailCompany">Click on a node to view details</div>
                </div>
                
                <div class="detail-section" id="metadataSection">
                    <h4>Relationship Details</h4>
                    <div id="metadataContainer">
                        <!-- Metadata will be populated here -->
                    </div>
                </div>
                
                <div class="detail-section" id="actionsSection">
                    <h4>Actions</h4>
                    <div class="action-buttons">
                        <button class="action-btn primary" onclick="messageContact()">
                            💬 Send Message
                        </button>
                        <button class="action-btn" onclick="addNote()">
                            📝 Add Note
                        </button>
                        <button class="action-btn" onclick="tagContact()">
                            🏷️ Manage Tags
                        </button>
                        <button class="action-btn danger" onclick="removeFromMap()">
                            🗑️ Remove from Map
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let networkData = { nodes: [], links: [] };
        let filteredData = { nodes: [], links: [] };
        let svg, g, simulation;
        let selectedNode = null;
        
        // Initialize the network graph
        async function initializeNetwork() {
            try {
                const response = await fetch('/api/network/graph');
                const data = await response.json();
                
                if (data.success) {
                    networkData = data;
                    filteredData = { ...networkData };
                    createGraph();
                    applyFilters();
                }
            } catch (error) {
                console.error('Failed to load network data:', error);
            }
        }
        
        function createGraph() {
            const width = document.querySelector('.graph-canvas').clientWidth;
            const height = document.querySelector('.graph-canvas').clientHeight;
            
            svg = d3.select('#networkGraph')
                .attr('width', width)
                .attr('height', height);
            
            // Clear existing content
            svg.selectAll('*').remove();
            
            // Create zoom behavior
            const zoom = d3.zoom()
                .scaleExtent([0.1, 10])
                .on('zoom', (event) => {
                    g.attr('transform', event.transform);
                });
            
            svg.call(zoom);
            
            // Create main group
            g = svg.append('g');
            
            // Create simulation
            simulation = d3.forceSimulation()
                .force('link', d3.forceLink().id(d => d.id).distance(100))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(width / 2, height / 2))
                .force('collision', d3.forceCollide().radius(30));
        }
        
        function updateGraph() {
            // Update links
            const link = g.selectAll('.link')
                .data(filteredData.links, d => d.source.id + '-' + d.target.id);
            
            link.exit().remove();
            
            link.enter().append('line')
                .attr('class', 'link')
                .merge(link);
            
            // Update nodes
            const node = g.selectAll('.node')
                .data(filteredData.nodes, d => d.id);
            
            node.exit().remove();
            
            const nodeEnter = node.enter().append('g');
            
            nodeEnter.append('circle')
                .attr('class', 'node')
                .attr('r', d => 10 + (d.strength || 50) * 0.3)
                .on('mouseover', handleNodeHover)
                .on('mouseout', hideTooltip)
                .on('click', handleNodeClick)
                .call(d3.drag()
                    .on('start', dragStarted)
                    .on('drag', dragged)
                    .on('end', dragEnded));
            
            nodeEnter.append('text')
                .attr('class', 'node-label')
                .attr('dy', '.35em')
                .text(d => d.name.split(' ')[0])
                .style('font-size', d => Math.max(8, 12 + (d.strength || 50) * 0.05) + 'px');
            
            // Update simulation
            simulation.nodes(filteredData.nodes);
            simulation.force('link').links(filteredData.links);
            simulation.alpha(1).restart();
            
            simulation.on('tick', () => {
                g.selectAll('.link')
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                
                g.selectAll('.node')
                    .attr('cx', d => d.x)
                    .attr('cy', d => d.y);
                
                g.selectAll('.node-label')
                    .attr('x', d => d.x)
                    .attr('y', d => d.y);
            });
        }
        
        function handleNodeHover(event, d) {
            const tooltip = document.getElementById('tooltip');
            const content = document.getElementById('tooltipContent');
            
            content.innerHTML = `
                <div><strong>${d.name}</strong></div>
                <div>Company: ${d.company || 'Unknown'}</div>
                <div>Strength: ${d.strength || 50}/100</div>
                <div>Last Contact: ${d.lastContact || 'Never'}</div>
            `;
            
            tooltip.style.left = event.pageX + 10 + 'px';
            tooltip.style.top = event.pageY + 10 + 'px';
            tooltip.classList.add('show');
        }
        
        function hideTooltip() {
            document.getElementById('tooltip').classList.remove('show');
        }
        
        function handleNodeClick(event, d) {
            // Update selected node
            g.selectAll('.node').classed('selected', false);
            d3.select(event.target).classed('selected', true);
            selectedNode = d;
            
            // Open detail panel
            openDetailPanel(d);
        }
        
        function openDetailPanel(contact) {
            const panel = document.getElementById('detailPanel');
            const avatar = document.getElementById('detailAvatar');
            const name = document.getElementById('detailName');
            const company = document.getElementById('detailCompany');
            const metadataContainer = document.getElementById('metadataContainer');
            
            // Update contact info
            avatar.textContent = contact.name.charAt(0);
            name.textContent = contact.name;
            company.textContent = contact.company || 'No company';
            
            // Update metadata
            metadataContainer.innerHTML = `
                <div class="metadata-item">
                    <span class="metadata-label">Relationship Strength</span>
                    <span class="metadata-value">${contact.strength || 50}/100</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Last Interaction</span>
                    <span class="metadata-value">${contact.lastContact || 'Never'}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Connection Type</span>
                    <span class="metadata-value">${contact.tags?.[0] || 'Colleague'}</span>
                </div>
                <div class="metadata-item">
                    <span class="metadata-label">Mutual Connections</span>
                    <span class="metadata-value">${contact.mutualConnections || 0}</span>
                </div>
            `;
            
            panel.classList.add('open');
        }
        
        function closeDetailPanel() {
            document.getElementById('detailPanel').classList.remove('open');
            g.selectAll('.node').classed('selected', false);
            selectedNode = null;
        }
        
        // Drag handlers
        function dragStarted(event, d) {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }
        
        function dragged(event, d) {
            d.fx = event.x;
            d.fy = event.y;
        }
        
        function dragEnded(event, d) {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }
        
        // Filter functions
        function applyFilters() {
            const selectedTags = Array.from(document.querySelectorAll('.tag-checkbox:checked')).map(cb => cb.value);
            const minStrength = parseInt(document.getElementById('strengthSlider').value);
            const lastInteractionDate = document.getElementById('lastInteraction').value;
            
            // Filter nodes
            filteredData.nodes = networkData.nodes.filter(node => {
                // Tag filter
                if (selectedTags.length > 0 && !selectedTags.some(tag => node.tags?.includes(tag))) {
                    return false;
                }
                
                // Strength filter
                if ((node.strength || 50) < minStrength) {
                    return false;
                }
                
                // Date filter
                if (lastInteractionDate && node.lastContact) {
                    const interactionDate = new Date(node.lastContact);
                    const filterDate = new Date(lastInteractionDate);
                    if (interactionDate < filterDate) {
                        return false;
                    }
                }
                
                return true;
            });
            
            // Filter links to only include those between filtered nodes
            const nodeIds = new Set(filteredData.nodes.map(n => n.id));
            filteredData.links = networkData.links.filter(link => 
                nodeIds.has(link.source.id || link.source) && 
                nodeIds.has(link.target.id || link.target)
            );
            
            updateGraph();
        }
        
        function resetFilters() {
            // Reset all filter inputs
            document.querySelectorAll('.tag-checkbox').forEach(cb => cb.checked = false);
            document.getElementById('strengthSlider').value = 0;
            document.getElementById('lastInteraction').value = '';
            updateStrengthValue();
            
            // Reset filtered data
            filteredData = { ...networkData };
            updateGraph();
        }
        
        function updateStrengthValue() {
            const value = document.getElementById('strengthSlider').value;
            document.getElementById('strengthValue').textContent = value;
        }
        
        function toggleFilters() {
            const sidebar = document.getElementById('filtersSidebar');
            const icon = document.getElementById('filtersIcon');
            
            sidebar.classList.toggle('hidden');
            icon.textContent = sidebar.classList.contains('hidden') ? '▶' : '▼';
        }
        
        // Zoom controls
        function zoomIn() {
            svg.transition().call(d3.zoom().scaleBy, 1.5);
        }
        
        function zoomOut() {
            svg.transition().call(d3.zoom().scaleBy, 0.75);
        }
        
        function resetView() {
            svg.transition().call(d3.zoom().transform, d3.zoomIdentity);
        }
        
        // Action handlers
        function messageContact() {
            if (selectedNode) {
                alert(`Opening message composer for ${selectedNode.name}`);
            }
        }
        
        function addNote() {
            if (selectedNode) {
                const note = prompt(`Add a note about ${selectedNode.name}:`);
                if (note) {
                    alert(`Note added: "${note}"`);
                }
            }
        }
        
        function tagContact() {
            if (selectedNode) {
                alert(`Tag management for ${selectedNode.name} coming soon!`);
            }
        }
        
        function removeFromMap() {
            if (selectedNode && confirm(`Remove ${selectedNode.name} from the network map?`)) {
                // Remove from data
                networkData.nodes = networkData.nodes.filter(n => n.id !== selectedNode.id);
                networkData.links = networkData.links.filter(l => 
                    l.source.id !== selectedNode.id && l.target.id !== selectedNode.id
                );
                
                closeDetailPanel();
                applyFilters();
            }
        }
        
        // Handle window resize
        window.addEventListener('resize', () => {
            const width = document.querySelector('.graph-canvas').clientWidth;
            const height = document.querySelector('.graph-canvas').clientHeight;
            
            svg.attr('width', width).attr('height', height);
            simulation.force('center', d3.forceCenter(width / 2, height / 2));
            simulation.alpha(1).restart();
        });
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', () => {
            initializeNetwork();
            updateStrengthValue();
        });
    </script>
</body>
</html>
    ''')

@app.route('/trust')
def serve_trust_page():
    """Serve Trust Analytics page with trust score insights"""
    # Check authentication
    if 'user_id' not in session:
        return redirect(url_for('serve_login_page'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trust Analytics - Rhiz</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(-45deg, #1e3a8a, #3730a3, #581c87, #7c2d12);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            min-height: 100vh;
            color: white;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .trust-container {
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .trust-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }
        
        .trust-title {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff, #e0e7ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .refresh-btn {
            background: linear-gradient(135deg, #4f46e5, #9333ea);
            border: none;
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .refresh-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 20px rgba(79, 70, 229, 0.3);
        }
        
        .metrics-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            background: rgba(255, 255, 255, 0.15);
        }
        
        .metric-label {
            font-size: 0.875rem;
            color: rgba(255, 255, 255, 0.7);
            margin-bottom: 0.5rem;
            font-weight: 500;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff, #e0e7ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        .metric-subtitle {
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.6);
        }
        
        .sparkline {
            width: 100%;
            height: 30px;
            margin-top: 0.5rem;
        }
        
        .tier-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .tier-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 1.25rem;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .tier-card:hover {
            transform: translateY(-2px);
            background: rgba(255, 255, 255, 0.15);
        }
        
        .tier-card.rooted {
            border-left: 4px solid #10b981;
        }
        
        .tier-card.growing {
            border-left: 4px solid #3b82f6;
        }
        
        .tier-card.dormant {
            border-left: 4px solid #f59e0b;
        }
        
        .tier-card.frayed {
            border-left: 4px solid #ef4444;
        }
        
        .tier-title {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: rgba(255, 255, 255, 0.9);
        }
        
        .tier-count {
            font-size: 2rem;
            font-weight: 700;
            color: white;
            margin-bottom: 0.5rem;
        }
        
        .tier-action {
            font-size: 0.875rem;
            color: rgba(255, 255, 255, 0.7);
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-block;
            margin-top: 0.5rem;
        }
        
        .tier-action:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .chart-section {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .chart-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: rgba(255, 255, 255, 0.9);
        }
        
        .chart-container {
            position: relative;
            height: 300px;
        }
        
        .alerts-section {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 16px;
            padding: 1.5rem;
        }
        
        .alerts-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: rgba(255, 255, 255, 0.9);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .alert-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            margin-bottom: 0.75rem;
            transition: all 0.2s;
        }
        
        .alert-item:hover {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .alert-info {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }
        
        .alert-name {
            font-weight: 600;
            color: rgba(255, 255, 255, 0.9);
        }
        
        .alert-score {
            font-size: 0.875rem;
            color: rgba(255, 255, 255, 0.7);
        }
        
        .alert-trend {
            font-size: 0.75rem;
            color: #ef4444;
            font-weight: 500;
        }
        
        .reengage-btn {
            background: linear-gradient(135deg, #f59e0b, #d97706);
            border: none;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .reengage-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
        }
        
        .loading {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem;
            color: rgba(255, 255, 255, 0.7);
        }
        
        .loading::after {
            content: '';
            width: 20px;
            height: 20px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-top: 2px solid white;
            border-radius: 50%;
            margin-left: 1rem;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @media (max-width: 768px) {
            .trust-container {
                padding: 1rem;
            }
            
            .trust-header {
                flex-direction: column;
                gap: 1rem;
                text-align: center;
            }
            
            .metrics-row {
                grid-template-columns: 1fr;
            }
            
            .tier-cards {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="trust-container">
        <!-- Header -->
        <div class="trust-header">
            <h1 class="trust-title">Trust Insights</h1>
            <button class="refresh-btn" onclick="refreshInsights()">
                <span>🔄</span>
                <span>Refresh</span>
            </button>
        </div>
        
        <!-- Top Metrics -->
        <div class="metrics-row" id="metricsRow">
            <div class="metric-card">
                <div class="metric-label">Overall Trust Score</div>
                <div class="metric-value" id="overallScore">--</div>
                <div class="metric-subtitle">Across all relationships</div>
                <canvas class="sparkline" id="scoreSparkline"></canvas>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Avg Response Time</div>
                <div class="metric-value" id="avgResponseTime">--</div>
                <div class="metric-subtitle">Days to respond</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Dormant Contacts</div>
                <div class="metric-value" id="dormantPercent">--</div>
                <div class="metric-subtitle">No contact in 90+ days</div>
            </div>
        </div>
        
        <!-- Trust Tier Cards -->
        <div class="tier-cards" id="tierCards">
            <div class="tier-card rooted" onclick="viewTier('rooted')">
                <div class="tier-title">Rooted</div>
                <div class="tier-count" id="rootedCount">--</div>
                <div class="tier-action">View Contacts</div>
            </div>
            
            <div class="tier-card growing" onclick="viewTier('growing')">
                <div class="tier-title">Growing</div>
                <div class="tier-count" id="growingCount">--</div>
                <div class="tier-action">View Contacts</div>
            </div>
            
            <div class="tier-card dormant" onclick="viewTier('dormant')">
                <div class="tier-title">Dormant</div>
                <div class="tier-count" id="dormantCount">--</div>
                <div class="tier-action">View Contacts</div>
            </div>
            
            <div class="tier-card frayed" onclick="viewTier('frayed')">
                <div class="tier-title">Frayed</div>
                <div class="tier-count" id="frayedCount">--</div>
                <div class="tier-action">View Contacts</div>
            </div>
        </div>
        
        <!-- Trust Timeline Chart -->
        <div class="chart-section">
            <h3 class="chart-title">Trust Score Timeline</h3>
            <div class="chart-container">
                <canvas id="trustChart"></canvas>
            </div>
        </div>
        
        <!-- Low-Trust Alerts -->
        <div class="alerts-section">
            <h3 class="alerts-title">
                <span>⚠️</span>
                <span>Low-Trust Alerts</span>
            </h3>
            <div id="alertsContainer">
                <div class="loading">Loading alerts...</div>
            </div>
        </div>
    </div>
    
    <script>
        let trustData = null;
        let trustChart = null;
        
        // Initialize page
        async function initializeTrustPage() {
            await loadTrustInsights();
            createTrustChart();
        }
        
        // Load trust insights data
        async function loadTrustInsights() {
            try {
                const response = await fetch('/api/trust/insights');
                const data = await response.json();
                
                if (data.success) {
                    trustData = data;
                    updateMetrics(data);
                    updateTierCards(data);
                    updateAlerts(data);
                    updateSparkline(data);
                }
            } catch (error) {
                console.error('Failed to load trust insights:', error);
            }
        }
        
        // Update top metrics
        function updateMetrics(data) {
            document.getElementById('overallScore').textContent = data.overall_score || 78;
            document.getElementById('avgResponseTime').textContent = (data.avg_response_time || 1.2) + ' days';
            document.getElementById('dormantPercent').textContent = (data.dormant_percentage || 24) + '%';
        }
        
        // Update tier cards
        function updateTierCards(data) {
            const tiers = data.tier_distribution || {
                rooted: 12,
                growing: 34,
                dormant: 8,
                frayed: 3
            };
            
            document.getElementById('rootedCount').textContent = tiers.rooted;
            document.getElementById('growingCount').textContent = tiers.growing;
            document.getElementById('dormantCount').textContent = tiers.dormant;
            document.getElementById('frayedCount').textContent = tiers.frayed;
        }
        
        // Update low-trust alerts
        function updateAlerts(data) {
            const alerts = data.low_trust_contacts || [
                { name: 'Alice Johnson', score: 45, trend: 'down', company: 'TechCorp' },
                { name: 'Bob Smith', score: 30, trend: 'down', company: 'StartupX' },
                { name: 'Carol Davis', score: 38, trend: 'down', company: 'InnovateLab' }
            ];
            
            const container = document.getElementById('alertsContainer');
            
            if (alerts.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: rgba(255,255,255,0.7); padding: 2rem;">No low-trust alerts. Great job maintaining your relationships!</div>';
                return;
            }
            
            container.innerHTML = alerts.map(alert => `
                <div class="alert-item">
                    <div class="alert-info">
                        <div class="alert-name">${alert.name}</div>
                        <div class="alert-score">Trust Score: ${alert.score}/100</div>
                        <div class="alert-trend">📉 Declining trust</div>
                    </div>
                    <button class="reengage-btn" onclick="reengageContact('${alert.name}')">
                        Re-engage
                    </button>
                </div>
            `).join('');
        }
        
        // Update sparkline chart
        function updateSparkline(data) {
            const canvas = document.getElementById('scoreSparkline');
            const ctx = canvas.getContext('2d');
            
            // Set canvas size
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            
            // Sample sparkline data
            const sparklineData = data.score_history || [72, 75, 73, 76, 78, 80, 78];
            const max = Math.max(...sparklineData);
            const min = Math.min(...sparklineData);
            const range = max - min || 1;
            
            // Clear canvas
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw sparkline
            ctx.strokeStyle = '#10b981';
            ctx.lineWidth = 2;
            ctx.beginPath();
            
            sparklineData.forEach((value, index) => {
                const x = (index / (sparklineData.length - 1)) * canvas.width;
                const y = canvas.height - ((value - min) / range) * canvas.height;
                
                if (index === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            
            ctx.stroke();
        }
        
        // Create trust timeline chart
        function createTrustChart() {
            const ctx = document.getElementById('trustChart').getContext('2d');
            
            // Sample timeline data
            const timelineData = {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Overall Trust Score',
                    data: [72, 75, 73, 76, 78, 80],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            };
            
            trustChart = new Chart(ctx, {
                type: 'line',
                data: timelineData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: false,
                            min: 60,
                            max: 100,
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: 'rgba(255, 255, 255, 0.7)'
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: 'rgba(255, 255, 255, 0.7)'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: 'rgba(255, 255, 255, 0.9)'
                            }
                        }
                    }
                }
            });
        }
        
        // Refresh insights
        async function refreshInsights() {
            const btn = document.querySelector('.refresh-btn');
            btn.style.opacity = '0.6';
            btn.style.pointerEvents = 'none';
            
            await loadTrustInsights();
            
            // Update chart if it exists
            if (trustChart && trustData) {
                // Update chart data here if needed
                trustChart.update();
            }
            
            btn.style.opacity = '1';
            btn.style.pointerEvents = 'auto';
        }
        
        // View tier contacts
        function viewTier(tier) {
            alert(`Viewing ${tier} tier contacts. This would filter the contacts page.`);
        }
        
        // Re-engage contact
        function reengageContact(name) {
            alert(`Opening re-engagement workflow for ${name}`);
        }
        
        // Initialize on page load
        document.addEventListener('DOMContentLoaded', () => {
            initializeTrustPage();
        });
    </script>
</body>
</html>
    ''')

@app.route('/contacts/import')
@app.route('/upload')
def serve_contact_import_page():
    """Serve Contact Upload/Import page with stepper interface"""
    # Check authentication
    if 'user_id' not in session:
        return redirect(url_for('serve_login_page'))
    
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Import Contacts - Rhiz</title>
    <script src="https://unpkg.com/papaparse@5.4.1/papaparse.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(-45deg, #1e3a8a, #3730a3, #581c87, #7c2d12);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            min-height: 100vh;
            color: white;
        }
        
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .import-container {
            padding: 2rem;
            max-width: 1000px;
            margin: 0 auto;
        }
        
        .import-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }
        
        .import-title {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff, #e0e7ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .cancel-btn {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .cancel-btn:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .stepper {
            display: flex;
            margin-bottom: 2rem;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 1rem;
        }
        
        .step {
            flex: 1;
            text-align: center;
            position: relative;
            padding: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .step.active {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
        }
        
        .step.completed {
            color: #10b981;
        }
        
        .step-number {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 0.5rem;
            font-weight: 600;
            font-size: 0.875rem;
        }
        
        .step.active .step-number {
            background: linear-gradient(135deg, #4f46e5, #9333ea);
        }
        
        .step.completed .step-number {
            background: #10b981;
        }
        
        .step-title {
            font-size: 0.875rem;
            font-weight: 500;
            margin-bottom: 0.25rem;
        }
        
        .step-subtitle {
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.7);
        }
        
        .step-content {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        .source-options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .source-card {
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .source-card:hover {
            transform: translateY(-2px);
            background: rgba(255, 255, 255, 0.15);
            border-color: rgba(255, 255, 255, 0.3);
        }
        
        .source-card.selected {
            border-color: #4f46e5;
            background: rgba(79, 70, 229, 0.2);
        }
        
        .source-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        
        .source-title {
            font-size: 1.125rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .source-description {
            font-size: 0.875rem;
            color: rgba(255, 255, 255, 0.7);
        }
        
        .file-upload {
            border: 2px dashed rgba(255, 255, 255, 0.3);
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 1rem;
        }
        
        .file-upload:hover {
            border-color: rgba(255, 255, 255, 0.5);
            background: rgba(255, 255, 255, 0.05);
        }
        
        .file-upload.dragover {
            border-color: #4f46e5;
            background: rgba(79, 70, 229, 0.1);
        }
        
        .file-upload input[type="file"] {
            display: none;
        }
        
        .upload-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            color: rgba(255, 255, 255, 0.6);
        }
        
        .upload-text {
            font-size: 1.125rem;
            margin-bottom: 0.5rem;
        }
        
        .upload-hint {
            font-size: 0.875rem;
            color: rgba(255, 255, 255, 0.7);
        }
        
        .preview-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 1.5rem;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            overflow: hidden;
        }
        
        .preview-table th,
        .preview-table td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .preview-table th {
            background: rgba(255, 255, 255, 0.1);
            font-weight: 600;
            font-size: 0.875rem;
        }
        
        .preview-table td {
            font-size: 0.875rem;
            color: rgba(255, 255, 255, 0.8);
        }
        
        .mapping-section {
            margin-bottom: 2rem;
        }
        
        .mapping-title {
            font-size: 1.125rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        
        .mapping-controls {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }
        
        .mapping-control {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }
        
        .mapping-label {
            font-size: 0.875rem;
            font-weight: 500;
        }
        
        .mapping-select {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 0.75rem;
            color: white;
            font-size: 0.875rem;
        }
        
        .mapping-select option {
            background: #1e293b;
            color: white;
        }
        
        .import-summary {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .summary-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.75rem;
            font-size: 0.875rem;
        }
        
        .summary-label {
            color: rgba(255, 255, 255, 0.7);
        }
        
        .summary-value {
            font-weight: 600;
        }
        
        .progress-section {
            margin-bottom: 2rem;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 1rem;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #4f46e5, #9333ea);
            width: 0%;
            transition: width 0.3s ease;
        }
        
        .progress-text {
            text-align: center;
            font-size: 0.875rem;
            color: rgba(255, 255, 255, 0.8);
        }
        
        .action-buttons {
            display: flex;
            gap: 1rem;
            justify-content: flex-end;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            font-size: 0.875rem;
            font-weight: 500;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .btn-secondary {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
        }
        
        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.2);
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #4f46e5, #9333ea);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 20px rgba(79, 70, 229, 0.3);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .hidden {
            display: none;
        }
        
        .error-message {
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            color: #fca5a5;
            font-size: 0.875rem;
        }
        
        .success-message {
            background: rgba(16, 185, 129, 0.2);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            color: #6ee7b7;
            font-size: 0.875rem;
        }
        
        @media (max-width: 768px) {
            .import-container {
                padding: 1rem;
            }
            
            .import-header {
                flex-direction: column;
                gap: 1rem;
                text-align: center;
            }
            
            .stepper {
                flex-direction: column;
                gap: 0.5rem;
            }
            
            .source-options {
                grid-template-columns: 1fr;
            }
            
            .action-buttons {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="import-container">
        <!-- Header -->
        <div class="import-header">
            <h1 class="import-title">Import Contacts</h1>
            <a href="/contacts" class="cancel-btn">
                <span>✕</span>
                <span>Cancel</span>
            </a>
        </div>
        
        <!-- Stepper -->
        <div class="stepper">
            <div class="step active" id="step1">
                <div class="step-number">1</div>
                <div class="step-title">Choose Source</div>
                <div class="step-subtitle">Select import method</div>
            </div>
            <div class="step" id="step2">
                <div class="step-number">2</div>
                <div class="step-title">Preview & Map</div>
                <div class="step-subtitle">Map fields</div>
            </div>
            <div class="step" id="step3">
                <div class="step-number">3</div>
                <div class="step-title">Confirm & Import</div>
                <div class="step-subtitle">Start import</div>
            </div>
        </div>
        
        <!-- Step 1: Choose Source -->
        <div class="step-content" id="step1-content">
            <div class="source-options">
                <div class="source-card" data-source="csv" onclick="selectSource('csv')">
                    <div class="source-icon">📄</div>
                    <div class="source-title">Upload CSV</div>
                    <div class="source-description">Import from CSV file</div>
                </div>
                
                <div class="source-card" data-source="google" onclick="selectSource('google')">
                    <div class="source-icon">🔗</div>
                    <div class="source-title">Connect Google</div>
                    <div class="source-description">Sync from Google Contacts</div>
                </div>
                
                <div class="source-card" data-source="linkedin" onclick="selectSource('linkedin')">
                    <div class="source-icon">💼</div>
                    <div class="source-title">Connect LinkedIn</div>
                    <div class="source-description">Import LinkedIn connections</div>
                </div>
                
                <div class="source-card" data-source="twitter" onclick="selectSource('twitter')">
                    <div class="source-icon">🐦</div>
                    <div class="source-title">Connect Twitter</div>
                    <div class="source-description">Import Twitter following</div>
                </div>
            </div>
            
            <!-- CSV Upload Area -->
            <div class="file-upload hidden" id="csvUpload">
                <input type="file" id="csvFile" accept=".csv,.txt" onchange="handleFileUpload(event)">
                <div class="upload-icon">📁</div>
                <div class="upload-text">Drop CSV file here or click to browse</div>
                <div class="upload-hint">Supports .csv and .txt files up to 10MB</div>
            </div>
            
            <div class="action-buttons">
                <button class="btn btn-primary" id="nextStep1" onclick="nextStep(1)" disabled>
                    Next
                    <span>→</span>
                </button>
            </div>
        </div>
        
        <!-- Step 2: Preview & Map -->
        <div class="step-content hidden" id="step2-content">
            <div id="previewSection">
                <h3 style="margin-bottom: 1rem;">Preview</h3>
                <table class="preview-table" id="previewTable">
                    <!-- Preview data will be populated here -->
                </table>
            </div>
            
            <div class="mapping-section">
                <h3 class="mapping-title">Field Mapping</h3>
                <div class="mapping-controls" id="mappingControls">
                    <!-- Mapping controls will be populated here -->
                </div>
            </div>
            
            <div class="action-buttons">
                <button class="btn btn-secondary" onclick="previousStep(2)">
                    <span>←</span>
                    Back
                </button>
                <button class="btn btn-primary" id="nextStep2" onclick="nextStep(2)">
                    Next
                    <span>→</span>
                </button>
            </div>
        </div>
        
        <!-- Step 3: Confirm & Import -->
        <div class="step-content hidden" id="step3-content">
            <div class="import-summary" id="importSummary">
                <h3 style="margin-bottom: 1rem;">Import Summary</h3>
                <div class="summary-item">
                    <span class="summary-label">Total rows:</span>
                    <span class="summary-value" id="totalRows">0</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Valid contacts:</span>
                    <span class="summary-value" id="validContacts">0</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Duplicates detected:</span>
                    <span class="summary-value" id="duplicateCount">0</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Will be imported:</span>
                    <span class="summary-value" id="importCount">0</span>
                </div>
            </div>
            
            <div class="progress-section hidden" id="progressSection">
                <h3 style="margin-bottom: 1rem;">Import Progress</h3>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
                <div class="progress-text" id="progressText">Preparing import...</div>
            </div>
            
            <div id="messageArea"></div>
            
            <div class="action-buttons">
                <button class="btn btn-secondary" id="backStep3" onclick="previousStep(3)">
                    <span>←</span>
                    Back
                </button>
                <button class="btn btn-primary" id="startImport" onclick="startImport()">
                    <span>🚀</span>
                    Start Import
                </button>
            </div>
        </div>
    </div>
    
    <script>
        let currentStep = 1;
        let selectedSource = null;
        let csvData = [];
        let csvHeaders = [];
        let fieldMapping = {};
        
        // Source selection
        function selectSource(source) {
            selectedSource = source;
            
            // Update UI
            document.querySelectorAll('.source-card').forEach(card => {
                card.classList.remove('selected');
            });
            document.querySelector(`[data-source="${source}"]`).classList.add('selected');
            
            // Show/hide CSV upload
            const csvUpload = document.getElementById('csvUpload');
            if (source === 'csv') {
                csvUpload.classList.remove('hidden');
            } else {
                csvUpload.classList.add('hidden');
                if (source !== 'csv') {
                    // For external sources, enable next button immediately
                    document.getElementById('nextStep1').disabled = false;
                }
            }
        }
        
        // File upload handling
        function handleFileUpload(event) {
            const file = event.target.files[0];
            if (!file) return;
            
            if (file.size > 10 * 1024 * 1024) {
                showError('File size exceeds 10MB limit');
                return;
            }
            
            Papa.parse(file, {
                header: true,
                skipEmptyLines: true,
                complete: function(results) {
                    if (results.errors.length > 0) {
                        showError('Error parsing CSV: ' + results.errors[0].message);
                        return;
                    }
                    
                    csvData = results.data;
                    csvHeaders = results.meta.fields;
                    
                    if (csvData.length === 0) {
                        showError('CSV file is empty');
                        return;
                    }
                    
                    showSuccess(`CSV loaded successfully: ${csvData.length} rows found`);
                    document.getElementById('nextStep1').disabled = false;
                },
                error: function(error) {
                    showError('Failed to parse CSV: ' + error.message);
                }
            });
        }
        
        // Drag and drop functionality
        const fileUpload = document.getElementById('csvUpload');
        
        fileUpload.addEventListener('dragover', function(e) {
            e.preventDefault();
            fileUpload.classList.add('dragover');
        });
        
        fileUpload.addEventListener('dragleave', function(e) {
            e.preventDefault();
            fileUpload.classList.remove('dragover');
        });
        
        fileUpload.addEventListener('drop', function(e) {
            e.preventDefault();
            fileUpload.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                document.getElementById('csvFile').files = files;
                handleFileUpload({ target: { files: files } });
            }
        });
        
        fileUpload.addEventListener('click', function() {
            document.getElementById('csvFile').click();
        });
        
        // Step navigation
        function nextStep(step) {
            if (step === 1) {
                if (selectedSource === 'csv') {
                    setupStep2();
                } else {
                    // For external sources, show connection process
                    handleExternalConnection();
                }
            } else if (step === 2) {
                setupStep3();
            }
        }
        
        function previousStep(step) {
            if (step === 2) {
                showStep(1);
            } else if (step === 3) {
                showStep(2);
            }
        }
        
        function showStep(step) {
            // Update stepper UI
            document.querySelectorAll('.step').forEach((s, index) => {
                s.classList.remove('active', 'completed');
                if (index + 1 === step) {
                    s.classList.add('active');
                } else if (index + 1 < step) {
                    s.classList.add('completed');
                }
            });
            
            // Show/hide step content
            document.querySelectorAll('.step-content').forEach(content => {
                content.classList.add('hidden');
            });
            document.getElementById(`step${step}-content`).classList.remove('hidden');
            
            currentStep = step;
        }
        
        function setupStep2() {
            if (selectedSource !== 'csv' || csvData.length === 0) {
                showError('No data to preview');
                return;
            }
            
            // Create preview table
            const table = document.getElementById('previewTable');
            table.innerHTML = '';
            
            // Header row
            const headerRow = table.insertRow();
            csvHeaders.forEach(header => {
                const th = document.createElement('th');
                th.textContent = header;
                headerRow.appendChild(th);
            });
            
            // Preview rows (first 5)
            const previewRows = csvData.slice(0, 5);
            previewRows.forEach(row => {
                const tr = table.insertRow();
                csvHeaders.forEach(header => {
                    const td = tr.insertCell();
                    td.textContent = row[header] || '';
                });
            });
            
            // Create mapping controls
            const mappingControls = document.getElementById('mappingControls');
            mappingControls.innerHTML = '';
            
            const fields = ['name', 'email', 'phone', 'company', 'title', 'notes'];
            fields.forEach(field => {
                const control = document.createElement('div');
                control.className = 'mapping-control';
                
                control.innerHTML = `
                    <label class="mapping-label">${field.charAt(0).toUpperCase() + field.slice(1)}</label>
                    <select class="mapping-select" data-field="${field}" onchange="updateMapping('${field}', this.value)">
                        <option value="">-- Skip --</option>
                        ${csvHeaders.map(header => `<option value="${header}">${header}</option>`).join('')}
                    </select>
                `;
                
                mappingControls.appendChild(control);
                
                // Auto-detect mapping
                const possibleMatches = {
                    name: ['name', 'full name', 'contact name', 'first name'],
                    email: ['email', 'email address', 'e-mail'],
                    phone: ['phone', 'phone number', 'mobile', 'telephone'],
                    company: ['company', 'organization', 'employer', 'business'],
                    title: ['title', 'job title', 'position', 'role'],
                    notes: ['notes', 'description', 'comments', 'memo']
                };
                
                const select = control.querySelector('select');
                const matches = possibleMatches[field] || [];
                const matchedHeader = csvHeaders.find(header => 
                    matches.some(match => header.toLowerCase().includes(match.toLowerCase()))
                );
                
                if (matchedHeader) {
                    select.value = matchedHeader;
                    fieldMapping[field] = matchedHeader;
                }
            });
            
            showStep(2);
        }
        
        function updateMapping(field, header) {
            if (header) {
                fieldMapping[field] = header;
            } else {
                delete fieldMapping[field];
            }
        }
        
        function setupStep3() {
            // Validate mapping
            if (!fieldMapping.email && !fieldMapping.name) {
                showError('Please map at least Name or Email field');
                return;
            }
            
            // Calculate summary
            const totalRows = csvData.length;
            const validContacts = csvData.filter(row => {
                const hasEmail = fieldMapping.email && row[fieldMapping.email];
                const hasName = fieldMapping.name && row[fieldMapping.name];
                return hasEmail || hasName;
            }).length;
            
            // Mock duplicate detection (in real app, this would check against existing contacts)
            const duplicateCount = Math.floor(validContacts * 0.1); // Mock 10% duplicates
            const importCount = validContacts - duplicateCount;
            
            // Update summary
            document.getElementById('totalRows').textContent = totalRows;
            document.getElementById('validContacts').textContent = validContacts;
            document.getElementById('duplicateCount').textContent = duplicateCount;
            document.getElementById('importCount').textContent = importCount;
            
            showStep(3);
        }
        
        function handleExternalConnection() {
            const sourceNames = {
                google: 'Google Contacts',
                linkedin: 'LinkedIn',
                twitter: 'Twitter'
            };
            
            showSuccess(`Connecting to ${sourceNames[selectedSource]}...`);
            
            // Simulate connection process
            setTimeout(() => {
                showSuccess(`Successfully connected to ${sourceNames[selectedSource]}! Found 25 contacts.`);
                
                // Mock external data
                csvData = Array.from({ length: 25 }, (_, i) => ({
                    name: `Contact ${i + 1}`,
                    email: `contact${i + 1}@example.com`,
                    company: `Company ${i + 1}`,
                    title: `Position ${i + 1}`
                }));
                csvHeaders = ['name', 'email', 'company', 'title'];
                
                // Auto-map fields for external sources
                fieldMapping = {
                    name: 'name',
                    email: 'email',
                    company: 'company',
                    title: 'title'
                };
                
                setupStep3();
            }, 2000);
        }
        
        async function startImport() {
            if (csvData.length === 0) {
                showError('No data to import');
                return;
            }
            
            // Disable buttons and show progress
            document.getElementById('startImport').disabled = true;
            document.getElementById('backStep3').disabled = true;
            document.getElementById('progressSection').classList.remove('hidden');
            
            try {
                // Prepare import data
                const importData = csvData.map(row => {
                    const contact = {};
                    Object.keys(fieldMapping).forEach(field => {
                        const header = fieldMapping[field];
                        if (header && row[header]) {
                            contact[field] = row[header];
                        }
                    });
                    return contact;
                }).filter(contact => contact.email || contact.name);
                
                // Simulate import progress
                const totalContacts = importData.length;
                let imported = 0;
                
                const updateProgress = () => {
                    imported++;
                    const percentage = (imported / totalContacts) * 100;
                    document.getElementById('progressFill').style.width = percentage + '%';
                    document.getElementById('progressText').textContent = 
                        `Importing contact ${imported} of ${totalContacts}...`;
                    
                    if (imported < totalContacts) {
                        setTimeout(updateProgress, 100);
                    } else {
                        completeImport(totalContacts);
                    }
                };
                
                updateProgress();
                
            } catch (error) {
                showError('Import failed: ' + error.message);
                document.getElementById('startImport').disabled = false;
                document.getElementById('backStep3').disabled = false;
            }
        }
        
        function completeImport(count) {
            document.getElementById('progressText').textContent = `Successfully imported ${count} contacts!`;
            
            showSuccess(`Import completed! ${count} contacts have been added to your network.`);
            
            // Auto-redirect after 3 seconds
            setTimeout(() => {
                window.location.href = '/contacts';
            }, 3000);
        }
        
        function showError(message) {
            const messageArea = document.getElementById('messageArea');
            messageArea.innerHTML = `<div class="error-message">${message}</div>`;
            setTimeout(() => {
                messageArea.innerHTML = '';
            }, 5000);
        }
        
        function showSuccess(message) {
            const messageArea = document.getElementById('messageArea');
            messageArea.innerHTML = `<div class="success-message">${message}</div>`;
            setTimeout(() => {
                messageArea.innerHTML = '';
            }, 5000);
        }
        
        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            showStep(1);
        });
    </script>
</body>
</html>
    ''')

@app.route('/contacts')
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

# Intelligence/AI API endpoints
@app.route('/api/intelligence/chat', methods=['POST'])
def intelligence_chat():
    """Handle AI chat messages"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Import OpenAI here to handle missing API key gracefully
        try:
            import openai
            import os
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            # Get user context from session/database
            user_id = session.get('user_id')
            
            # Create a context-aware prompt
            system_prompt = f"""You are Rhiz, an AI assistant specialized in relationship intelligence and networking advice. 
            You help users build meaningful professional relationships and identify opportunities in their network.
            
            Your responses should be:
            - Helpful and actionable
            - Focused on relationship building and networking strategy
            - Professional but warm in tone
            - Based on relationship intelligence principles
            
            The user ({user_id}) is asking: {user_message}
            
            Provide specific, actionable advice that helps them build better relationships and identify opportunities."""
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            return jsonify({
                'success': True,
                'response': ai_response
            })
            
        except Exception as openai_error:
            logging.error(f"OpenAI API error: {openai_error}")
            
            # Provide helpful fallback response
            fallback_responses = {
                'funding': "For funding opportunities, focus on investors who share your vision. Look for warm introductions through your existing network and research investors who have funded similar companies.",
                'hiring': "When hiring through your network, be specific about the role and skills needed. Ask trusted contacts for referrals and consider offering referral bonuses.",
                'partnerships': "Successful partnerships start with aligned goals. Identify companies that complement your strengths and reach out through mutual connections.",
                'reconnect': "Reconnecting works best with a specific reason to reach out. Share something valuable, congratulate them on recent achievements, or suggest a relevant opportunity."
            }
            
            # Simple keyword matching for fallback
            message_lower = user_message.lower()
            fallback_response = "I'd be happy to help with relationship advice! Try asking about specific topics like funding, hiring, partnerships, or reconnecting with contacts."
            
            for keyword, response in fallback_responses.items():
                if keyword in message_lower:
                    fallback_response = response
                    break
            
            return jsonify({
                'success': True,
                'response': fallback_response
            })
            
    except Exception as e:
        logging.error(f"Chat error: {e}")
        return jsonify({'error': 'Failed to process message'}), 500

@app.route('/api/insights')
def get_insights():
    """Get AI insights including recommendations and alerts"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Mock data for demonstration - in production this would come from AI analysis
        recommendations = [
            {
                'id': 'rec1',
                'name': 'Sarah Chen',
                'reason': 'Recently promoted to VP Engineering - great time to reconnect about technical partnerships'
            },
            {
                'id': 'rec2',
                'name': 'Marcus Rodriguez',
                'reason': 'Active in startup funding - could be valuable for your Series A discussions'
            },
            {
                'id': 'rec3',
                'name': 'Jennifer Kim',
                'reason': 'Posted about hiring challenges - opportunity to offer your recruiting solution'
            },
            {
                'id': 'rec4',
                'name': 'Alex Thompson',
                'reason': 'Haven\'t spoken in 6 months - good time for a coffee catch-up'
            }
        ]
        
        alerts = [
            {
                'text': 'Sarah Chen just changed jobs to VP Engineering at TechCorp - perfect timing for outreach'
            },
            {
                'text': 'Marcus Rodriguez mentioned looking for AI startups on LinkedIn yesterday'
            },
            {
                'text': 'Jennifer Kim is attending the same conference as you next week - schedule a meetup'
            }
        ]
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'alerts': alerts
        })
        
    except Exception as e:
        logging.error(f"Insights error: {e}")
        return jsonify({'error': 'Failed to load insights'}), 500

# User Settings API endpoints
@app.route('/api/user/settings', methods=['PATCH'])
def update_user_settings():
    """Update user settings"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        # In a real implementation, this would save to database
        # For demo purposes, we'll just return success
        
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully'
        })
        
    except Exception as e:
        logging.error(f"Settings update error: {e}")
        return jsonify({'error': 'Failed to update settings'}), 500

@app.route('/api/user/settings')
def get_user_settings():
    """Get user settings or export data"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        export_data = request.args.get('export') == 'true'
        user_id = session.get('user_id')
        
        if export_data:
            # Generate data export
            export_content = {
                'user_id': user_id,
                'export_date': datetime.utcnow().isoformat(),
                'contacts': [
                    {
                        'name': 'Sarah Chen',
                        'email': 'sarah@techcorp.com',
                        'company': 'TechCorp',
                        'notes': 'VP Engineering, interested in AI partnerships'
                    },
                    {
                        'name': 'Marcus Rodriguez',
                        'email': 'marcus@vcfirm.com',
                        'company': 'VC Firm',
                        'notes': 'Partner focusing on early-stage AI startups'
                    }
                ],
                'goals': [
                    {
                        'title': 'Raise Series A',
                        'description': 'Secure $5M Series A funding',
                        'status': 'active'
                    }
                ],
                'interactions': [
                    {
                        'date': '2024-01-15',
                        'contact': 'Sarah Chen',
                        'type': 'email',
                        'notes': 'Discussed potential partnership opportunities'
                    }
                ]
            }
            
            # Return as downloadable JSON file
            from flask import make_response
            import json
            
            response = make_response(json.dumps(export_content, indent=2))
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = f'attachment; filename=rhiz_data_export_{user_id}.json'
            return response
        
        else:
            # Return current settings
            settings = {
                'profile': {
                    'fullName': 'Demo User',
                    'email': 'demo@rhiz.app',
                    'timezone': 'America/Los_Angeles'
                },
                'notifications': {
                    'emailReminders': True,
                    'smsNudges': False,
                    'weeklyDigest': True,
                    'quietHours': {
                        'start': '22:00',
                        'end': '08:00'
                    }
                },
                'integrations': {
                    'google': {'connected': False},
                    'linkedin': {'connected': False},
                    'twitter': {'connected': False},
                    'icloud': {'connected': False}
                },
                'privacy': {
                    'twoFactor': False
                }
            }
            
            return jsonify({
                'success': True,
                'settings': settings
            })
        
    except Exception as e:
        logging.error(f"Settings error: {e}")
        return jsonify({'error': 'Failed to load settings'}), 500

@app.route('/api/user/account', methods=['DELETE'])
def delete_user_account():
    """Delete user account"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        user_id = session.get('user_id')
        
        # In a real implementation, this would:
        # 1. Delete all user data from database
        # 2. Cancel any subscriptions
        # 3. Send confirmation email
        # 4. Log the deletion for compliance
        
        # Clear the session
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Account deleted successfully'
        })
        
    except Exception as e:
        logging.error(f"Account deletion error: {e}")
        return jsonify({'error': 'Failed to delete account'}), 500

# Network Graph API endpoint
@app.route('/api/network/graph')
def get_network_graph():
    """Get network graph data for D3.js visualization"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Mock network data - in production this would come from database analysis
        nodes = [
            {
                'id': 'user',
                'name': 'You',
                'company': 'Your Company',
                'strength': 100,
                'lastContact': '2024-01-30',
                'tags': ['self'],
                'mutualConnections': 0
            },
            {
                'id': 'sarah_chen',
                'name': 'Sarah Chen',
                'company': 'TechCorp',
                'strength': 85,
                'lastContact': '2024-01-28',
                'tags': ['colleague', 'mentor'],
                'mutualConnections': 3
            },
            {
                'id': 'marcus_rodriguez',
                'name': 'Marcus Rodriguez',
                'company': 'VC Partners',
                'strength': 75,
                'lastContact': '2024-01-25',
                'tags': ['investor'],
                'mutualConnections': 2
            },
            {
                'id': 'jennifer_kim',
                'name': 'Jennifer Kim',
                'company': 'Design Studio',
                'strength': 70,
                'lastContact': '2024-01-20',
                'tags': ['friend', 'partner'],
                'mutualConnections': 4
            },
            {
                'id': 'alex_thompson',
                'name': 'Alex Thompson',
                'company': 'StartupX',
                'strength': 60,
                'lastContact': '2024-01-15',
                'tags': ['colleague'],
                'mutualConnections': 1
            },
            {
                'id': 'maria_garcia',
                'name': 'Maria Garcia',
                'company': 'InnovateLab',
                'strength': 65,
                'lastContact': '2024-01-22',
                'tags': ['mentor', 'advisor'],
                'mutualConnections': 2
            },
            {
                'id': 'david_lee',
                'name': 'David Lee',
                'company': 'TechFlow',
                'strength': 55,
                'lastContact': '2024-01-10',
                'tags': ['client'],
                'mutualConnections': 1
            },
            {
                'id': 'emily_zhang',
                'name': 'Emily Zhang',
                'company': 'CloudVentures',
                'strength': 80,
                'lastContact': '2024-01-29',
                'tags': ['investor', 'friend'],
                'mutualConnections': 3
            },
            {
                'id': 'robert_johnson',
                'name': 'Robert Johnson',
                'company': 'BuildCorp',
                'strength': 45,
                'lastContact': '2024-01-05',
                'tags': ['colleague'],
                'mutualConnections': 0
            },
            {
                'id': 'lisa_wang',
                'name': 'Lisa Wang',
                'company': 'CreativeSpace',
                'strength': 72,
                'lastContact': '2024-01-26',
                'tags': ['partner', 'friend'],
                'mutualConnections': 2
            }
        ]
        
        # Network connections (edges)
        links = [
            {'source': 'user', 'target': 'sarah_chen', 'strength': 85},
            {'source': 'user', 'target': 'marcus_rodriguez', 'strength': 75},
            {'source': 'user', 'target': 'jennifer_kim', 'strength': 70},
            {'source': 'user', 'target': 'alex_thompson', 'strength': 60},
            {'source': 'user', 'target': 'maria_garcia', 'strength': 65},
            {'source': 'user', 'target': 'david_lee', 'strength': 55},
            {'source': 'user', 'target': 'emily_zhang', 'strength': 80},
            {'source': 'user', 'target': 'robert_johnson', 'strength': 45},
            {'source': 'user', 'target': 'lisa_wang', 'strength': 72},
            
            # Mutual connections
            {'source': 'sarah_chen', 'target': 'marcus_rodriguez', 'strength': 60},
            {'source': 'sarah_chen', 'target': 'jennifer_kim', 'strength': 65},
            {'source': 'marcus_rodriguez', 'target': 'emily_zhang', 'strength': 70},
            {'source': 'jennifer_kim', 'target': 'lisa_wang', 'strength': 75},
            {'source': 'maria_garcia', 'target': 'emily_zhang', 'strength': 55},
            {'source': 'alex_thompson', 'target': 'david_lee', 'strength': 50},
            {'source': 'emily_zhang', 'target': 'lisa_wang', 'strength': 68},
            {'source': 'sarah_chen', 'target': 'maria_garcia', 'strength': 72}
        ]
        
        return jsonify({
            'success': True,
            'nodes': nodes,
            'links': links
        })
        
    except Exception as e:
        logging.error(f"Network graph error: {e}")
        return jsonify({'error': 'Failed to load network data'}), 500

@app.route('/api/contacts/<contact_id>')
def get_contact_detail(contact_id):
    """Get detailed information about a specific contact"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Mock contact details - in production this would query the database
        contact_details = {
            'sarah_chen': {
                'id': 'sarah_chen',
                'name': 'Sarah Chen',
                'email': 'sarah@techcorp.com',
                'phone': '+1 (555) 123-4567',
                'company': 'TechCorp',
                'title': 'VP Engineering',
                'location': 'San Francisco, CA',
                'strength': 85,
                'lastContact': '2024-01-28',
                'tags': ['colleague', 'mentor'],
                'mutualConnections': 3,
                'notes': 'Brilliant engineer and mentor. Always available for technical discussions.',
                'interactions': [
                    {'date': '2024-01-28', 'type': 'email', 'note': 'Discussed AI architecture patterns'},
                    {'date': '2024-01-20', 'type': 'coffee', 'note': 'Coffee chat about career growth'},
                    {'date': '2024-01-15', 'type': 'linkedin', 'note': 'Connected on technical blog post'}
                ]
            },
            'marcus_rodriguez': {
                'id': 'marcus_rodriguez',
                'name': 'Marcus Rodriguez',
                'email': 'marcus@vcpartners.com',
                'phone': '+1 (555) 234-5678',
                'company': 'VC Partners',
                'title': 'Partner',
                'location': 'Palo Alto, CA',
                'strength': 75,
                'lastContact': '2024-01-25',
                'tags': ['investor'],
                'mutualConnections': 2,
                'notes': 'Active investor in AI startups. Great network in enterprise software.',
                'interactions': [
                    {'date': '2024-01-25', 'type': 'meeting', 'note': 'Funding discussion'},
                    {'date': '2024-01-10', 'type': 'email', 'note': 'Shared market insights'},
                    {'date': '2024-01-05', 'type': 'event', 'note': 'Met at TechCrunch event'}
                ]
            }
        }
        
        contact = contact_details.get(contact_id)
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        return jsonify({
            'success': True,
            'contact': contact
        })
        
    except Exception as e:
        logging.error(f"Contact detail error: {e}")
        return jsonify({'error': 'Failed to load contact details'}), 500

# Trust Analytics API endpoint
@app.route('/api/trust/insights')
def get_trust_insights():
    """Get trust insights and analytics data"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # Get timeline parameter
        timeline = request.args.get('timeline', 'false').lower() == 'true'
        
        # Mock trust insights data - in production this would analyze actual contact relationships
        insights_data = {
            'success': True,
            'overall_score': 78,
            'avg_response_time': 1.2,
            'dormant_percentage': 24,
            'tier_distribution': {
                'rooted': 12,
                'growing': 34,
                'dormant': 8,
                'frayed': 3
            },
            'score_history': [72, 75, 73, 76, 78, 80, 78],
            'low_trust_contacts': [
                {
                    'name': 'Alice Johnson',
                    'score': 45,
                    'trend': 'down',
                    'company': 'TechCorp',
                    'last_contact': '2024-01-05',
                    'decline_reason': 'No response to last 3 messages'
                },
                {
                    'name': 'Bob Smith',
                    'score': 30,
                    'trend': 'down',
                    'company': 'StartupX',
                    'last_contact': '2023-12-20',
                    'decline_reason': 'Missed scheduled calls'
                },
                {
                    'name': 'Carol Davis',
                    'score': 38,
                    'trend': 'down',
                    'company': 'InnovateLab',
                    'last_contact': '2024-01-10',
                    'decline_reason': 'Delayed email responses'
                }
            ]
        }
        
        # Add timeline data if requested
        if timeline:
            insights_data['timeline'] = {
                'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'overall_scores': [72, 75, 73, 76, 78, 80],
                'tier_counts': {
                    'rooted': [10, 11, 11, 12, 12, 12],
                    'growing': [30, 32, 34, 34, 34, 34],
                    'dormant': [12, 10, 8, 7, 8, 8],
                    'frayed': [5, 4, 3, 3, 3, 3]
                }
            }
        
        return jsonify(insights_data)
        
    except Exception as e:
        logging.error(f"Trust insights error: {e}")
        return jsonify({'error': 'Failed to load trust insights'}), 500

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
