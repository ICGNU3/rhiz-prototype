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

# Serve React frontend for all non-API routes
@app.route('/')
@app.route('/<path:path>')
def serve_react_app(path=''):
    """Serve React frontend for all routes"""
    # Skip API routes - let them be handled by backend blueprints
    if path.startswith('api/'):
        return '', 404
    
    try:
        # Verify the file exists before serving
        if not os.path.exists(FRONTEND_INDEX_PATH):
            return jsonify({
                'error': 'Frontend not built. Run: cd frontend && npm run build',
                'debug_info': f'Looking for: {FRONTEND_INDEX_PATH}'
            }), 500
        
        # Serve React index.html for all frontend routes
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