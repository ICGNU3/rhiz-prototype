"""
Rhiz Platform - Clean API Backend
Production-ready Flask application serving API endpoints only
React frontend handles all UI rendering
"""

from backend import create_app
from flask import send_from_directory, send_file, jsonify
import os

# Create Flask app with factory pattern
app = create_app()

# Get absolute paths for reliable file serving
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIST_DIR = os.path.join(BASE_DIR, 'frontend', 'dist')
FRONTEND_ASSETS_DIR = os.path.join(FRONTEND_DIST_DIR, 'assets')
FRONTEND_INDEX_PATH = os.path.join(FRONTEND_DIST_DIR, 'index.html')

# Serve React frontend static assets
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve React static assets"""
    try:
        return send_from_directory(FRONTEND_ASSETS_DIR, filename)
    except FileNotFoundError:
        return '', 404

@app.route('/vite.svg')
def serve_vite_svg():
    """Serve Vite favicon"""
    try:
        return send_from_directory(FRONTEND_DIST_DIR, 'vite.svg')
    except FileNotFoundError:
        return '', 404

# Serve the beautiful original landing page
@app.route('/')
def serve_landing():
    """Serve the original beautiful landing page"""
    from flask import render_template
    return render_template('landing.html')

# Serve beautiful custom login page  
@app.route('/login')
def serve_login_page():
    """Serve beautiful custom login page with glassmorphism design"""
    from flask import render_template_string
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
            margin-bottom: 2rem;
        }
        .form-group { 
            margin-bottom: 1.5rem; 
            text-align: left; 
        }
        .form-label { 
            display: block; 
            font-weight: 600; 
            color: #374151; 
            margin-bottom: 0.5rem; 
        }
        .form-input { 
            width: 100%; 
            padding: 0.75rem 1rem; 
            border: 2px solid #e5e7eb; 
            border-radius: 10px; 
            font-size: 1rem; 
            transition: all 0.3s ease; 
        }
        .form-input:focus { 
            outline: none; 
            border-color: #4f46e5; 
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1); 
        }
        .btn { 
            width: 100%; 
            padding: 0.875rem; 
            border: none; 
            border-radius: 10px; 
            font-size: 1.1rem; 
            font-weight: 600; 
            cursor: pointer; 
            transition: all 0.3s ease; 
        }
        .btn-primary { 
            background: linear-gradient(135deg, #4f46e5, #9333ea); 
            color: white; 
            margin-bottom: 1rem; 
        }
        .btn-primary:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 10px 25px rgba(79, 70, 229, 0.3); 
        }
        .btn-secondary { 
            background: #f3f4f6; 
            color: #6b7280; 
            border: 2px solid #e5e7eb; 
        }
        .btn-secondary:hover { 
            background: #e5e7eb; 
            color: #374151; 
        }
        .divider { 
            margin: 1.5rem 0; 
            text-align: center; 
            color: #9ca3af; 
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
        .message { 
            margin-top: 1rem; 
            padding: 0.75rem; 
            border-radius: 8px; 
            font-size: 0.9rem; 
        }
        .message.success { 
            background: #d1fae5; 
            color: #065f46; 
            border: 1px solid #a7f3d0; 
        }
        .message.error { 
            background: #fee2e2; 
            color: #991b1b; 
            border: 1px solid #fca5a5; 
        }
        .loading { 
            opacity: 0.7; 
            pointer-events: none; 
        }
        .spinner { 
            display: inline-block; 
            width: 1rem; 
            height: 1rem; 
            border: 2px solid transparent; 
            border-top: 2px solid currentColor; 
            border-radius: 50%; 
            animation: spin 1s linear infinite; 
            margin-right: 0.5rem; 
        }
        @keyframes spin { 
            to { transform: rotate(360deg); } 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">Rhiz</div>
        <div class="title">Welcome Back</div>
        <div class="subtitle">Access your relationship intelligence platform</div>

        <form id="loginForm">
            <div class="form-group">
                <label for="email" class="form-label">Email Address</label>
                <input type="email" id="email" name="email" class="form-input" placeholder="Enter your email" required>
            </div>
            
            <button type="submit" class="btn btn-primary" id="loginBtn">
                <span class="btn-text">Send Magic Link</span>
            </button>
        </form>

        <div class="divider">
            <span>or</span>
        </div>

        <button type="button" class="btn btn-secondary" id="demoBtn">
            Try Demo Mode
        </button>

        <div id="message"></div>
    </div>

    <script>
        const form = document.getElementById('loginForm');
        const loginBtn = document.getElementById('loginBtn');
        const demoBtn = document.getElementById('demoBtn');
        const message = document.getElementById('message');

        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            
            loginBtn.classList.add('loading');
            loginBtn.innerHTML = '<span class="spinner"></span>Sending...';
            message.innerHTML = '';

            try {
                const response = await fetch('/api/auth/magic-link', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: email })
                });

                const data = await response.json();
                
                if (response.ok) {
                    message.innerHTML = '<div class="message success">Magic link sent! Check your email.</div>';
                } else {
                    message.innerHTML = '<div class="message error">' + (data.error || 'Something went wrong') + '</div>';
                }
            } catch (error) {
                message.innerHTML = '<div class="message error">Network error. Please try again.</div>';
            }

            loginBtn.classList.remove('loading');
            loginBtn.innerHTML = '<span class="btn-text">Send Magic Link</span>';
        });

        demoBtn.addEventListener('click', async function() {
            demoBtn.classList.add('loading');
            demoBtn.innerHTML = '<span class="spinner"></span>Loading Demo...';

            try {
                const response = await fetch('/api/auth/demo-login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                });

                if (response.ok) {
                    window.location.href = '/app/dashboard';
                } else {
                    message.innerHTML = '<div class="message error">Demo login failed. Please try again.</div>';
                    demoBtn.classList.remove('loading');
                    demoBtn.innerHTML = 'Try Demo Mode';
                }
            } catch (error) {
                message.innerHTML = '<div class="message error">Network error. Please try again.</div>';
                demoBtn.classList.remove('loading');
                demoBtn.innerHTML = 'Try Demo Mode';
            }
        });
    </script>
</body>
</html>
    ''')

# Serve React frontend for app routes
@app.route('/app')
@app.route('/app/<path:path>')
def serve_react_app(path=''):
    """Serve React frontend for app routes"""
    try:
        # Verify the file exists before serving
        if not os.path.exists(FRONTEND_INDEX_PATH):
            return jsonify({
                'error': 'Frontend not built. Run: cd frontend && npm run build',
                'debug_info': f'Looking for: {FRONTEND_INDEX_PATH}'
            }), 500
        
        # Serve React index.html for app routes
        return send_file(FRONTEND_INDEX_PATH)
    except Exception as e:
        return jsonify({
            'error': 'Frontend serving failed',
            'details': str(e),
            'path_checked': FRONTEND_INDEX_PATH
        }), 500

if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=True)