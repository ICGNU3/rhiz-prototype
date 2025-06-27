"""
Intelligence and advanced AI routes module
Handles AI suggestions, network analysis, and sophisticated CRM features
"""

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session
from . import RouteBase, login_required, get_current_user_id
from analytics import NetworkingAnalytics
from network_visualization import NetworkMapper
from ai_contact_matcher import AIContactMatcher
from rhizomatic_intelligence import RhizomaticIntelligence
from smart_networking import SmartNetworkingEngine
from contact_search import ContactSearchEngine
from relationship_intelligence import RelationshipIntelligence
from network_metrics import NetworkMetricsManager
from shared_ai_assistant import SharedAIAssistant
from trust_contribution_engine import TrustContributionEngine
from unknown_contact_discovery import UnknownContactDiscovery
from coordination_infrastructure import CoordinationInfrastructure
import logging

# Create blueprint
intelligence_bp = Blueprint('intelligence_routes', __name__)

class IntelligenceRoutes(RouteBase):
    def __init__(self):
        super().__init__()
        try:
            self.analytics = NetworkingAnalytics(self.db)
        except Exception:
            self.analytics = None
        
        try:
            self.network_mapper = NetworkMapper(self.db)
        except Exception:
            self.network_mapper = None
            
        try:
            self.ai_matcher = AIContactMatcher(self.db)
        except Exception:
            self.ai_matcher = None
            
        try:
            self.rhizomatic_intel = RhizomaticIntelligence(self.db)
        except Exception:
            self.rhizomatic_intel = None
            
        try:
            self.smart_networking = SmartNetworkingEngine(self.db)
        except Exception:
            self.smart_networking = None
            
        try:
            self.search_engine = ContactSearchEngine(self.db)
        except Exception:
            self.search_engine = None
            
        try:
            self.relationship_intel = RelationshipIntelligence(self.db)
        except Exception:
            self.relationship_intel = None
            
        try:
            self.network_metrics = NetworkMetricsManager()
        except Exception:
            self.network_metrics = None
            
        try:
            self.ai_assistant = SharedAIAssistant()
        except Exception:
            self.ai_assistant = None
            
        try:
            self.trust_engine = TrustContributionEngine()
        except Exception:
            self.trust_engine = None
            
        try:
            self.contact_discovery = UnknownContactDiscovery()
        except Exception:
            self.contact_discovery = None
            
        try:
            self.coordination = CoordinationInfrastructure()
        except Exception:
            self.coordination = None

intelligence_routes = IntelligenceRoutes()

# AI Contact Matcher Routes
@intelligence_bp.route('/ai/suggestions')
@login_required
def ai_suggestions():
    """View AI-powered contact suggestions"""
    user_id = get_current_user_id()
    
    try:
        suggestions = intelligence_routes.ai_matcher.suggest_introduction_opportunities(user_id)
        return render_template('intelligence/ai_suggestions.html', suggestions=suggestions)
    except Exception as e:
        logging.error(f"AI suggestions error: {e}")
        intelligence_routes.flash_error('Failed to load AI suggestions')
        return redirect(url_for('core_routes.dashboard'))

@intelligence_bp.route('/ai/network-gaps')
@login_required
def network_gaps():
    """Analyze network gaps and suggest expansions"""
    user_id = get_current_user_id()
    
    try:
        analysis = intelligence_routes.ai_matcher.analyze_network_gaps(user_id)
        return render_template('intelligence/network_gaps.html', analysis=analysis)
    except Exception as e:
        logging.error(f"Network gaps analysis error: {e}")
        intelligence_routes.flash_error('Failed to analyze network gaps')
        return redirect(url_for('core_routes.dashboard'))

# Network Visualization Routes
@intelligence_bp.route('/network')
@login_required
def network_map():
    """Interactive network visualization"""
    user_id = get_current_user_id()
    
    try:
        network_data = intelligence_routes.network_mapper.get_network_data(user_id)
        metrics = intelligence_routes.network_metrics.get_network_overview(user_id)
        
        return render_template('intelligence/network_map.html', 
                             network=network_data, 
                             metrics=metrics)
    except Exception as e:
        logging.error(f"Network map error: {e}")
        intelligence_routes.flash_error('Failed to load network map')
        return redirect(url_for('core_routes.dashboard'))

@intelligence_bp.route('/api/network/graph')
@login_required
def api_network_graph():
    """API endpoint for network graph data"""
    user_id = get_current_user_id()
    
    try:
        graph_data = intelligence_routes.network_mapper.get_graph_data(user_id)
        return jsonify(graph_data)
    except Exception as e:
        logging.error(f"Network graph API error: {e}")
        return jsonify({'error': 'Failed to load network data'}), 500

# Smart Networking Routes
@intelligence_bp.route('/smart-networking')
@login_required
def smart_networking():
    """Smart networking dashboard with health scores"""
    user_id = get_current_user_id()
    
    try:
        dashboard_data = intelligence_routes.smart_networking.get_dashboard_data(user_id)
        return render_template('intelligence/smart_networking.html', **dashboard_data)
    except Exception as e:
        logging.error(f"Smart networking error: {e}")
        intelligence_routes.flash_error('Failed to load smart networking data')
        return redirect(url_for('core_routes.dashboard'))

# Relationship Intelligence Routes
@intelligence_bp.route('/relationship-intelligence')
@login_required
def relationship_intelligence():
    """Advanced relationship intelligence dashboard"""
    user_id = get_current_user_id()
    
    try:
        intel_data = intelligence_routes.relationship_intel.get_intelligence_dashboard(user_id)
        return render_template('intelligence/relationship_intel.html', **intel_data)
    except Exception as e:
        logging.error(f"Relationship intelligence error: {e}")
        intelligence_routes.flash_error('Failed to load relationship intelligence')
        return redirect(url_for('core_routes.dashboard'))

# Trust & Contribution Engine Routes
@intelligence_bp.route('/trust-insights')
@login_required
def trust_insights():
    """Trust and contribution insights dashboard"""
    user_id = get_current_user_id()
    
    try:
        trust_data = intelligence_routes.trust_engine.get_trust_dashboard(user_id)
        return render_template('intelligence/trust_insights.html', **trust_data)
    except Exception as e:
        logging.error(f"Trust insights error: {e}")
        intelligence_routes.flash_error('Failed to load trust insights')
        return redirect(url_for('core_routes.dashboard'))

# Unknown Contact Discovery Routes
@intelligence_bp.route('/contact-discovery')
@login_required
def contact_discovery():
    """Unknown contact discovery dashboard"""
    user_id = get_current_user_id()
    
    try:
        discovery_data = intelligence_routes.contact_discovery.get_discovery_dashboard(user_id)
        return render_template('intelligence/contact_discovery.html', **discovery_data)
    except Exception as e:
        logging.error(f"Contact discovery error: {e}")
        intelligence_routes.flash_error('Failed to load contact discovery')
        return redirect(url_for('core_routes.dashboard'))

@intelligence_bp.route('/api/discover-contacts', methods=['POST'])
@login_required
def api_discover_contacts():
    """API endpoint to discover new contacts"""
    user_id = get_current_user_id()
    
    try:
        discovery_params = request.json or {}
        results = intelligence_routes.contact_discovery.discover_unknown_contacts(
            user_id, 
            **discovery_params
        )
        
        return jsonify(results)
    except Exception as e:
        logging.error(f"Contact discovery API error: {e}")
        return jsonify({'error': 'Discovery failed'}), 500

# Coordination Infrastructure Routes
@intelligence_bp.route('/coordination')
@login_required
def coordination_hub():
    """Coordination infrastructure dashboard"""
    user_id = get_current_user_id()
    
    try:
        coordination_data = intelligence_routes.coordination.get_coordination_dashboard(user_id)
        return render_template('intelligence/coordination_hub.html', **coordination_data)
    except Exception as e:
        logging.error(f"Coordination hub error: {e}")
        intelligence_routes.flash_error('Failed to load coordination hub')
        return redirect(url_for('core_routes.dashboard'))

@intelligence_bp.route('/coordination/projects/create', methods=['POST'])
@login_required
def create_coordination_project():
    """Create new coordination project"""
    user_id = get_current_user_id()
    
    try:
        project_data = {
            'title': request.form.get('title', '').strip(),
            'description': request.form.get('description', '').strip(),
            'template_type': request.form.get('template_type', 'custom'),
            'participants': request.form.getlist('participants[]')
        }
        
        if not project_data['title']:
            intelligence_routes.flash_error('Project title is required')
            return redirect(url_for('intelligence_routes.coordination_hub'))
        
        project_id = intelligence_routes.coordination.create_project(user_id, **project_data)
        
        if project_id:
            intelligence_routes.flash_success('Project created successfully!')
            intelligence_routes.award_xp('project_created', 15, {
                'project_id': project_id,
                'template_type': project_data['template_type']
            })
        else:
            intelligence_routes.flash_error('Failed to create project')
            
        return redirect(url_for('intelligence_routes.coordination_hub'))
        
    except Exception as e:
        logging.error(f"Project creation error: {e}")
        intelligence_routes.flash_error('Failed to create project')
        return redirect(url_for('intelligence_routes.coordination_hub'))

# Shared AI Assistant Routes
@intelligence_bp.route('/ai-assistant')
@login_required
def ai_assistant():
    """Ambient AI assistant dashboard"""
    user_id = get_current_user_id()
    
    try:
        assistant_data = intelligence_routes.ai_assistant.get_assistant_dashboard(user_id)
        return render_template('intelligence/ai_assistant.html', **assistant_data)
    except Exception as e:
        logging.error(f"AI assistant error: {e}")
        intelligence_routes.flash_error('Failed to load AI assistant')
        return redirect(url_for('core_routes.dashboard'))

@intelligence_bp.route('/api/ai-assistant/connections')
@login_required
def api_missed_connections():
    """API endpoint for missed connections"""
    user_id = get_current_user_id()
    
    try:
        connections = intelligence_routes.ai_assistant.get_missed_connections(user_id)
        return jsonify({'connections': connections})
    except Exception as e:
        logging.error(f"Missed connections API error: {e}")
        return jsonify({'error': 'Failed to load connections'}), 500

@intelligence_bp.route('/api/ai-assistant/micro-actions')
@login_required
def api_micro_actions():
    """API endpoint for daily micro-actions"""
    user_id = get_current_user_id()
    
    try:
        actions = intelligence_routes.ai_assistant.generate_daily_micro_actions(user_id)
        return jsonify({'actions': actions})
    except Exception as e:
        logging.error(f"Micro-actions API error: {e}")
        return jsonify({'error': 'Failed to load micro-actions'}), 500

# Advanced Search Routes
@intelligence_bp.route('/search/advanced')
@login_required
def advanced_search():
    """Advanced contact search interface"""
    user_id = get_current_user_id()
    
    try:
        search_options = intelligence_routes.search_engine.get_search_options(user_id)
        return render_template('intelligence/advanced_search.html', **search_options)
    except Exception as e:
        logging.error(f"Advanced search error: {e}")
        intelligence_routes.flash_error('Failed to load search interface')
        return redirect(url_for('core_routes.dashboard'))

@intelligence_bp.route('/api/search', methods=['POST'])
@login_required
def api_search():
    """API endpoint for advanced search"""
    user_id = get_current_user_id()
    
    try:
        search_params = request.json or {}
        results = intelligence_routes.search_engine.advanced_search(user_id, **search_params)
        return jsonify(results)
    except Exception as e:
        logging.error(f"Search API error: {e}")
        return jsonify({'error': 'Search failed'}), 500