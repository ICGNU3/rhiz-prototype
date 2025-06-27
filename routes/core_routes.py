"""
Core application routes module
Handles dashboard, landing page, and main navigation routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from . import RouteBase, login_required, get_current_user_id, get_current_user
from analytics import NetworkingAnalytics
from database_utils import seed_demo_data
import logging

# Create blueprint
core_bp = Blueprint('core_routes', __name__)

class CoreRoutes(RouteBase):
    def __init__(self):
        super().__init__()
        self.analytics = NetworkingAnalytics(self.db)

core_routes = CoreRoutes()

@core_bp.route('/')
def landing():
    """Landing page for unauthenticated users"""
    if 'user_id' in session:
        return redirect(url_for('core_routes.dashboard'))
    
    try:
        return render_template('landing.html')
    except Exception as e:
        logging.error(f"Landing page template error: {e}")
        # Temporary fallback during refactoring
        return '''
        <!DOCTYPE html>
        <html lang="en" data-bs-theme="dark">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Rhiz - Relationship Intelligence Platform</title>
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            <style>
                body { background: #1a1a1a; color: white; font-family: 'Inter', sans-serif; }
                .container { max-width: 800px; margin: 100px auto; padding: 40px; text-align: center; }
                .glass-card { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); 
                             border-radius: 20px; padding: 40px; backdrop-filter: blur(10px); }
                .btn-primary { background: linear-gradient(135deg, #3b82f6, #8b5cf6); border: none; 
                              padding: 12px 24px; border-radius: 10px; text-decoration: none; 
                              color: white; display: inline-block; margin: 10px; }
                .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(59,130,246,0.3); }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="glass-card">
                    <h1 style="font-size: 3rem; margin-bottom: 20px;">🚀 Rhiz</h1>
                    <h2 style="color: #8b5cf6; margin-bottom: 30px;">Relationship Intelligence Platform</h2>
                    <p style="font-size: 1.2rem; margin-bottom: 40px; opacity: 0.9;">
                        High-context relationship intelligence for builders who activate meaningful connections.
                        Coordination infrastructure for the people building what's next.
                    </p>
                    <div>
                        <a href="/signup" class="btn-primary">Join the Intelligence Network</a>
                        <a href="/health" class="btn-primary">System Status</a>
                    </div>
                    <p style="margin-top: 40px; opacity: 0.6; font-size: 0.9rem;">
                        <em>Full landing page temporarily simplified during Phase 1 refactoring.</em>
                    </p>
                </div>
            </div>
        </body>
        </html>
        '''

@core_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard for authenticated users"""
    user_id = get_current_user_id()
    
    try:
        # Import models correctly from routes package
        from . import goal_model, contact_model, ai_suggestion_model, interaction_model, gamification
        
        # Get dashboard data safely
        dashboard_data = {
            'goals': goal_model.get_all(user_id)[:5] if goal_model.get_all(user_id) else [],
            'contacts': contact_model.get_all(user_id)[:6] if contact_model.get_all(user_id) else [],
            'ai_suggestions': ai_suggestion_model.get_recent(user_id, limit=5) if hasattr(ai_suggestion_model, 'get_recent') else [],
            'recent_interactions': interaction_model.get_recent(user_id, limit=5) if hasattr(interaction_model, 'get_recent') else []
        }
        
        # Get user stats safely
        all_goals = goal_model.get_all(user_id) if goal_model.get_all(user_id) else []
        all_contacts = contact_model.get_all(user_id) if contact_model.get_all(user_id) else []
        
        stats = {
            'total_goals': len(all_goals),
            'total_contacts': len(all_contacts),
            'pending_follow_ups': getattr(interaction_model, 'count_pending_follow_ups', lambda x: 0)(user_id),
            'this_month_interactions': getattr(interaction_model, 'count_this_month', lambda x: 0)(user_id)
        }
        
        # Get user level/XP info safely
        user_profile = gamification.get_user_profile(user_id) if hasattr(gamification, 'get_user_profile') else {}
        
        return render_template('dashboard.html', 
                             **dashboard_data,
                             stats=stats,
                             user_profile=user_profile)
                             
    except Exception as e:
        logging.error(f"Dashboard error: {e}")
        logging.exception("Full dashboard error traceback:")
        
        # Try with minimal data
        try:
            return render_template('dashboard.html', 
                                 goals=[], 
                                 contacts=[], 
                                 ai_suggestions=[],
                                 recent_interactions=[],
                                 stats={'total_goals': 0, 'total_contacts': 0, 'pending_follow_ups': 0, 'this_month_interactions': 0},
                                 user_profile={'xp': 0, 'title': 'Contact Seeker', 'streak_count': 0})
        except Exception as template_error:
            logging.error(f"Template error: {template_error}")
            # Return simple HTML if template fails
            return '''
            <!DOCTYPE html>
            <html><head><title>Dashboard</title></head>
            <body>
                <h1>Dashboard</h1>
                <p>Welcome to your dashboard!</p>
                <p>User ID: ''' + str(user_id) + '''</p>
            </body></html>
            '''

@core_bp.route('/index')
def index():
    """Legacy index route - redirect to dashboard"""
    return redirect(url_for('core_routes.dashboard'))

@core_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    from datetime import datetime
    import os
    
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
            conn = core_routes.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
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
            "error": str(e)
        }), 500

@core_bp.route('/settings')
@login_required
def settings():
    """User settings page"""
    user_id = get_current_user_id()
    
    try:
        user = core_routes.auth_manager.get_user_by_id(user_id)
        user_profile = core_routes.gamification.get_user_profile(user_id)
        usage_summary = core_routes.subscription_manager.get_usage_summary(user_id)
        
        return render_template('settings.html',
                             user=user,
                             user_profile=user_profile,
                             usage=usage_summary)
                             
    except Exception as e:
        logging.error(f"Settings error: {e}")
        core_routes.flash_error('Error loading settings')
        return redirect(url_for('core_routes.dashboard'))

@core_bp.route('/analytics')
@login_required
def analytics_dashboard():
    """Analytics dashboard"""
    user_id = get_current_user_id()
    
    try:
        analytics_data = core_routes.analytics.get_comprehensive_dashboard_data(user_id)
        
        return render_template('analytics_dashboard.html', analytics=analytics_data)
        
    except Exception as e:
        logging.error(f"Analytics error: {e}")
        core_routes.flash_error('Error loading analytics')
        return redirect(url_for('core_routes.dashboard'))

@core_bp.route('/demo-data')
@login_required
def seed_demo_data_route():
    """Seed demo data for user (development/demo purposes)"""
    user_id = get_current_user_id()
    
    try:
        # Check if user already has data
        existing_goals = len(core_routes.goal_model.get_all(user_id))
        existing_contacts = len(core_routes.contact_model.get_all(user_id))
        
        if existing_goals > 0 or existing_contacts > 0:
            core_routes.flash_error('Demo data already exists. Clear your data first.')
            return redirect(url_for('core_routes.dashboard'))
        
        # Seed demo data
        seed_demo_data(user_id)
        
        core_routes.flash_success('Demo data created successfully!')
        return redirect(url_for('core_routes.dashboard'))
        
    except Exception as e:
        logging.error(f"Demo data seeding error: {e}")
        core_routes.flash_error('Failed to create demo data')
        return redirect(url_for('core_routes.dashboard'))

@core_bp.route('/search')
@login_required
def global_search():
    """Global search across contacts, goals, and interactions"""
    user_id = get_current_user_id()
    query = request.args.get('q', '').strip()
    
    if not query:
        return render_template('search_results.html', 
                             query='', 
                             results={'contacts': [], 'goals': [], 'interactions': []})
    
    try:
        search_results = {
            'contacts': core_routes.contact_model.search(user_id, query),
            'goals': core_routes.goal_model.search(user_id, query),
            'interactions': core_routes.interaction_model.search(user_id, query)
        }
        
        return render_template('search_results.html', 
                             query=query,
                             results=search_results)
                             
    except Exception as e:
        logging.error(f"Search error: {e}")
        core_routes.flash_error('Search failed')
        return render_template('search_results.html', 
                             query=query, 
                             results={'contacts': [], 'goals': [], 'interactions': []})

# API Routes for AJAX functionality

@core_bp.route('/api/dashboard/stats')
@login_required
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    user_id = get_current_user_id()
    
    try:
        stats = {
            'total_goals': len(core_routes.goal_model.get_all(user_id)),
            'total_contacts': len(core_routes.contact_model.get_all(user_id)),
            'pending_follow_ups': core_routes.interaction_model.count_pending_follow_ups(user_id),
            'this_month_interactions': core_routes.interaction_model.count_this_month(user_id),
            'ai_suggestions_count': len(core_routes.ai_suggestion_model.get_recent(user_id, limit=10))
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logging.error(f"API stats error: {e}")
        return jsonify({'error': 'Failed to load stats'}), 500

@core_bp.route('/api/user/profile')
@login_required
def api_user_profile():
    """API endpoint for user profile information"""
    user_id = get_current_user_id()
    
    try:
        user = core_routes.auth_manager.get_user_by_id(user_id)
        user_profile = core_routes.gamification.get_user_profile(user_id)
        
        profile_data = {
            'user': {
                'id': user['id'],
                'email': user['email'],
                'subscription_tier': user.get('subscription_tier', 'explorer'),
                'created_at': user.get('created_at', '')
            },
            'gamification': user_profile
        }
        
        return jsonify(profile_data)
        
    except Exception as e:
        logging.error(f"API profile error: {e}")
        return jsonify({'error': 'Failed to load profile'}), 500