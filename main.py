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

# Serve React frontend static assets
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve React static assets"""
    try:
        return send_from_directory(os.path.join('frontend', 'dist', 'assets'), filename)
    except FileNotFoundError:
        return '', 404

@app.route('/vite.svg')
def serve_vite_svg():
    """Serve Vite favicon"""
    try:
        return send_from_directory(os.path.join('frontend', 'dist'), 'vite.svg')
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
        # Serve React index.html for all frontend routes
        return send_file(os.path.join('frontend', 'dist', 'index.html'))
    except FileNotFoundError:
        return jsonify({'error': 'Frontend not built. Run: cd frontend && npm run build'}), 500

if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=True)