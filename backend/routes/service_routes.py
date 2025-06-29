"""
Service Status Routes - Service health and status checking
"""
from flask import Blueprint, jsonify
from services.contact_intelligence import ContactIntelligence
from services.trust_insights import TrustInsights
from services.social_integrations import SocialIntegrations
from services.contact_sync_engine import ContactSyncEngine

service_bp = Blueprint('service', __name__, url_prefix='/api/services')


@service_bp.route('/status')
def service_status():
    """Get status of all services"""
    try:
        services = {}
        
        # Test Contact Intelligence
        ci = ContactIntelligence()
        services['contact_intelligence'] = ci.get_status()
        
        # Test Trust Insights
        ti = TrustInsights()
        services['trust_insights'] = ti.get_status()
        
        # Test Social Integrations
        si = SocialIntegrations()
        services['social_integrations'] = si.get_status()
        
        # Test Contact Sync Engine
        cse = ContactSyncEngine()
        services['contact_sync_engine'] = cse.get_status()
        
        return jsonify({
            'status': 'healthy',
            'services': services,
            'total_services': len(services)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@service_bp.route('/health')
def quick_health():
    """Quick health check for services"""
    return jsonify({
        'status': 'operational',
        'message': 'All services available for import'
    })