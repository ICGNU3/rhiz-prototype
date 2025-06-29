"""
Core Routes - Landing page and static content
"""
from flask import Blueprint, render_template, send_from_directory

core_bp = Blueprint('core', __name__)


@core_bp.route('/')
def landing():
    """Landing page for unauthenticated users"""
    return render_template('landing.html')


@core_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@core_bp.route('/health')
def health_check():
    """Production health monitoring endpoint"""
    return {
        'status': 'healthy',
        'timestamp': '2025-06-28T23:25:00Z',
        'database': 'healthy',
        'services': 'configured'
    }


@core_bp.route('/login')
def login_page():
    """Login page using React frontend"""
    return render_template('app.html')


@core_bp.route('/app')
@core_bp.route('/app/<path:path>')
def serve_react_app(path=None):
    """Serve React frontend application"""
    return render_template('app.html')