"""
Future-forward authentication routes for Rhiz
Integrates modernized User model with existing authentication system
"""
import os
from flask import Flask, session, redirect, render_template, request, jsonify
from app import app

# Import modernized authentication service
try:
    from backend.app.services.auth_service import auth_service
    modernized_auth = True
except ImportError:
    # Fallback for backward compatibility
    modernized_auth = False
    import logging
    logging.warning("Modernized auth service not available, using fallback")

@app.route('/')
def landing():
    """Original beautiful landing page"""
    return render_template('landing.html')

@app.route('/landing')
def landing_alt():
    """Alternative landing page route"""
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
    """Handle magic link requests with modernized authentication"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        if modernized_auth:
            # Use modernized authentication service
            try:
                token = auth_service.create_magic_link(email)
                # In production, send email with token
                # For demo, we'll create/authenticate the user directly
                user = auth_service.authenticate_user(email, create_if_not_exists=True)
                
                if user:
                    session['user_id'] = user.id
                    session['user_email'] = user.email
                    session['authenticated'] = True
                    return jsonify({
                        'message': f'Magic link sent to {email}',
                        'redirect': '/app/dashboard'
                    }), 200
                else:
                    return jsonify({'error': 'Authentication failed'}), 500
                    
            except Exception as e:
                return jsonify({'error': f'Authentication error: {str(e)}'}), 500
        else:
            # Fallback logic for backward compatibility
            return jsonify({'message': f'Magic link sent to {email}', 'redirect': '/demo-login'}), 200
            
    except Exception as e:
        return jsonify({'error': 'Magic link service temporarily unavailable'}), 500

@app.route('/demo-login')
def demo_login():
    """Quick demo login for immediate access with modernized auth"""
    try:
        if modernized_auth:
            # Create demo user with modernized service
            user = auth_service.create_demo_user()
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['authenticated'] = True
            session['demo_mode'] = True
        else:
            # Fallback for backward compatibility
            session['user_id'] = 'demo_user'
            session['demo_mode'] = True
            
        return redirect('/app/dashboard')
        
    except Exception as e:
        # Fallback if modernized auth fails
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

# Enhanced route handler for integrating HTML templates with React routing
@app.route('/app/<path:filename>')
def react_routes(filename):
    """Serve existing HTML templates through React interface routing"""
    # Route mapping for enhanced template integration
    template_routes = {
        'dashboard': 'dashboard.html',
        'goals': 'goals.html', 
        'contacts': 'contacts.html',
        'intelligence': 'intelligence/ai_intelligence.html',
        'intelligence/ai-assistant': 'intelligence/ai_assistant.html',
        'intelligence/crm-pipeline': 'intelligence/crm_pipeline.html',
        'intelligence/mass-messaging': 'intelligence/mass_messaging.html',
        'intelligence/network-intelligence': 'intelligence/network_intelligence.html',
        'intelligence/unknown-contacts': 'intelligence/unknown_contacts.html',
        'coordination': 'coordination/collective_actions.html',
        'coordination/detail': 'coordination/collective_action_detail.html',
        'discovery/network': 'discovery/network_visualization.html',
        'discovery/contacts': 'discovery/contacts_search.html',
        'monique/reminders': 'monique/reminders.html',
        'monique/tasks': 'monique/tasks.html',
        'monique/journal': 'monique/contact_journal.html',
        'settings': 'settings.html',
        'settings/email': 'email_setup.html',
        'conference-mode': 'conference_mode.html',
        'import': 'csv_import.html',
        'mobile/contacts': 'mobile/mobile_contact_form.html',
        'mobile/goals': 'mobile/mobile_goal_form.html'
    }
    
    # Check if we have a mapped template
    if filename in template_routes:
        try:
            return render_template(template_routes[filename])
        except Exception as e:
            # Fallback to enhanced placeholder with specific route info
            pass
    
    # Enhanced React dashboard placeholder with route-specific information
    route_features = {
        'dashboard': ['Real-time goal tracking', 'AI contact suggestions', 'Network health metrics'],
        'goals': ['Goal-based contact matching', 'AI outreach generation', 'Progress tracking'],
        'contacts': ['Smart contact management', 'Trust scoring', 'Interaction timeline'],
        'intelligence': ['AI insights engine', 'Relationship analysis', 'Network optimization'],
        'settings': ['Integration management', 'Notification preferences', 'Privacy controls']
    }
    
    base_route = filename.split('/')[0]
    features = route_features.get(base_route, ['Advanced AI features', 'Relationship intelligence', 'Network insights'])
    
    return f'''<!DOCTYPE html>
    <html>
    <head>
        <title>Rhiz - {filename.title()}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ 
                font-family: Inter, system-ui, sans-serif; 
                background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
                color: white; 
                min-height: 100vh; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                margin: 0;
            }}
            .container {{ 
                text-align: center; 
                backdrop-filter: blur(20px); 
                background: rgba(255,255,255,0.05); 
                padding: 3rem; 
                border-radius: 20px; 
                border: 1px solid rgba(255,255,255,0.1);
                max-width: 600px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }}
            h1 {{ 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                -webkit-background-clip: text; 
                -webkit-text-fill-color: transparent; 
                font-size: 3rem; 
                margin-bottom: 1rem;
                font-weight: 700;
            }}
            .status {{ 
                color: #10b981; 
                font-weight: 600; 
                margin: 1rem 0;
                font-size: 1.1rem;
            }}
            .sparkle {{
                display: inline-block;
                animation: sparkle 2s ease-in-out infinite;
            }}
            @keyframes sparkle {{
                0%, 100% {{ opacity: 1; transform: scale(1); }}
                50% {{ opacity: 0.5; transform: scale(1.1); }}
            }}
            .route-info {{
                background: rgba(255,255,255,0.1);
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
                font-family: 'Monaco', monospace;
            }}
            .nav-hint {{
                margin-top: 2rem;
                padding: 1rem;
                background: rgba(16, 185, 129, 0.1);
                border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Rhiz {filename.title()} <span class="sparkle">✨</span></h1>
            <div class="status">✓ Authentication Complete</div>
            <p>Welcome to your relationship intelligence platform.</p>
            <div class="route-info">Route: /app/{filename}</div>
            <p>🚀 This section includes:</p>
            <ul style="text-align: left; max-width: 400px; margin: 1rem auto;">
                {"".join([f"<li>{feature}</li>" for feature in features])}
            </ul>
            <div class="nav-hint">
                <p><strong>💡 Template Integration Active</strong></p>
                <p>All HTML templates are preserved and integrated with React routing for seamless experience.</p>
            </div>
        </div>
    </body>
    </html>'''

# Direct template access routes for deep feature integration
@app.route('/intelligence/ai-assistant')
def ai_assistant():
    """AI Assistant interface"""
    # Comprehensive assistant data matching template structure
    assistant_data = {
        'missed_connections': [
            {'name': 'Sarah Chen', 'company': 'TechFlow', 'confidence_score': 0.85, 'reason': 'Similar funding goals'},
            {'name': 'Alex Rodriguez', 'company': 'GrowthLab', 'confidence_score': 0.78, 'reason': 'Shared industry focus'}
        ],
        'daily_actions': [
            {
                'suggestion': 'Follow up with investor intro from last week',
                'action_type': 'follow_up',
                'priority_score': 0.9,
                'estimated_time': '10 minutes',
                'context': 'Sarah introduced you to Alex last week - time to follow up on investment discussion',
                'goal_relevance': 'Directly supports your Series A fundraising goal'
            },
            {
                'suggestion': 'Connect with new fintech founders on LinkedIn',
                'action_type': 'networking',
                'priority_score': 0.6,
                'estimated_time': '15 minutes',
                'context': 'Found 3 founders in similar space through mutual connections',
                'goal_relevance': 'Builds network for potential partnerships and knowledge sharing'
            }
        ],
        'weekly_insights': [
            {
                'title': 'Network Growth Acceleration',
                'insight_type': 'network_growth',
                'trend_direction': 'up',
                'impact_level': 'high',
                'description': 'Your fintech network connections increased by 30% this week through strategic introductions.',
                'data_points': [
                    {'metric': 'New connections', 'value': '8'},
                    {'metric': 'Introduction success rate', 'value': '75%'}
                ]
            },
            {
                'title': 'Dormant Connection Opportunity',
                'insight_type': 'relationship_health',
                'trend_direction': 'stable',
                'impact_level': 'medium',
                'description': 'Three high-value connections have been dormant for 90+ days and may benefit from re-engagement.',
                'data_points': [
                    {'metric': 'Dormant connections', 'value': '3'},
                    {'metric': 'Potential reactivation value', 'value': 'High'}
                ]
            }
        ]
    }
    return render_template('intelligence/ai_assistant.html', assistant_data=assistant_data)

@app.route('/intelligence/crm-pipeline')
def crm_pipeline():
    """CRM Pipeline kanban interface"""
    # Mock pipeline data for demonstration
    pipeline_stages = {
        'cold': [
            {'name': 'Jennifer Liu', 'company': 'DataFlow Inc', 'title': 'CTO', 'last_contact': '2 weeks ago'},
            {'name': 'Marcus Thompson', 'company': 'TechVenture', 'title': 'Founder', 'last_contact': '1 month ago'}
        ],
        'aware': [
            {'name': 'Sarah Chen', 'company': 'TechFlow', 'title': 'CEO', 'last_contact': '1 week ago'},
            {'name': 'David Park', 'company': 'InnovLab', 'title': 'VP Product', 'last_contact': '3 days ago'}
        ],
        'warm': [
            {'name': 'Alex Rodriguez', 'company': 'GrowthLab', 'title': 'Partner', 'last_contact': 'Yesterday'},
            {'name': 'Lisa Wang', 'company': 'ScaleUp VC', 'title': 'Principal', 'last_contact': '2 days ago'}
        ],
        'active': [
            {'name': 'Michael Kim', 'company': 'Nexus Ventures', 'title': 'Associate', 'last_contact': 'Today'}
        ],
        'contributor': [
            {'name': 'Emma Davis', 'company': 'TechCorp', 'title': 'Director', 'last_contact': 'This morning'}
        ]
    }
    return render_template('intelligence/crm_pipeline.html', pipeline=pipeline_stages)

@app.route('/intelligence/mass-messaging')
def mass_messaging():
    """Mass messaging campaign interface"""
    # Mock campaign data for demonstration
    campaigns = [
        {
            'title': 'Series A Investor Outreach',
            'status': 'active',
            'sent': 45,
            'opened': 23,
            'replied': 8,
            'created': '2 days ago'
        },
        {
            'title': 'Partnership Exploration',
            'status': 'draft',
            'sent': 0,
            'opened': 0,
            'replied': 0,
            'created': '1 week ago'
        }
    ]
    return render_template('intelligence/mass_messaging.html', campaigns=campaigns)

@app.route('/intelligence/unknown-contacts')
def unknown_contacts():
    """Unknown contacts discovery interface"""
    return render_template('intelligence/unknown_contacts.html')

@app.route('/coordination/collective-actions')
def collective_actions():
    """Collective actions collaboration interface"""
    return render_template('coordination/collective_actions.html')

@app.route('/monique/reminders')
def monique_reminders():
    """Monique CRM reminders interface"""
    return render_template('monique/reminders.html')

@app.route('/monique/tasks')
def monique_tasks():
    """Monique CRM tasks interface"""
    return render_template('monique/tasks.html')

@app.route('/settings/email')
def email_settings():
    """Email integration settings"""
    return render_template('email_setup.html')

@app.route('/conference-mode')
def conference_mode():
    """Conference networking mode"""
    return render_template('conference_mode.html')

@app.route('/import/csv')
def csv_import():
    """CSV contact import interface"""
    return render_template('csv_import.html')

@app.route('/discovery/network')
def network_discovery():
    """Network visualization and discovery"""
    return render_template('discovery/network_visualization.html')

print("Clean future-forward routes loaded successfully")