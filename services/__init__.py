"""
Services Module - Unified Backend Services
Provides centralized access to all backend services with proper dependency management
"""

# Import core services
from .unified_email_service import UnifiedEmailService, get_email_service
from .unified_utilities import (
    DatabaseUtils, ValidationUtils, SecurityUtils, 
    DataUtils, ImportUtils, ProductionUtils
)

# Import specialized services
try:
    from .stripe_integration import StripeService
except ImportError:
    StripeService = None

try:
    from .telegram_integration import TelegramService
except ImportError:
    TelegramService = None

try:
    from .integrations import IntegrationsService
except ImportError:
    IntegrationsService = None

class ServiceManager:
    """
    Central service manager for all backend services
    Provides singleton access and dependency injection
    """
    
    _instance = None
    _services = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all available services"""
        # Core services (always available)
        self._services['email'] = get_email_service()
        self._services['database'] = DatabaseUtils()
        self._services['validation'] = ValidationUtils()
        self._services['security'] = SecurityUtils()
        self._services['data'] = DataUtils()
        self._services['import'] = ImportUtils()
        self._services['production'] = ProductionUtils()
        
        # Optional services (only if available)
        if StripeService:
            self._services['stripe'] = StripeService()
        
        if TelegramService:
            self._services['telegram'] = TelegramService()
        
        if IntegrationsService:
            self._services['integrations'] = IntegrationsService()
    
    def get_service(self, service_name: str):
        """Get service by name"""
        return self._services.get(service_name)
    
    def get_email_service(self) -> UnifiedEmailService:
        """Get email service"""
        return self._services['email']
    
    def get_database_utils(self) -> DatabaseUtils:
        """Get database utilities"""
        return self._services['database']
    
    def get_validation_utils(self) -> ValidationUtils:
        """Get validation utilities"""
        return self._services['validation']
    
    def get_security_utils(self) -> SecurityUtils:
        """Get security utilities"""
        return self._services['security']
    
    def get_data_utils(self) -> DataUtils:
        """Get data utilities"""
        return self._services['data']
    
    def get_import_utils(self) -> ImportUtils:
        """Get import utilities"""
        return self._services['import']
    
    def get_production_utils(self) -> ProductionUtils:
        """Get production utilities"""
        return self._services['production']
    
    def health_check(self) -> dict:
        """Perform health check on all services"""
        health = {
            'overall_status': 'healthy',
            'services': {},
            'timestamp': ProductionUtils().health_check()['timestamp']
        }
        
        for service_name, service in self._services.items():
            try:
                if hasattr(service, 'health_check'):
                    service_health = service.health_check()
                elif hasattr(service, 'get_service_status'):
                    service_health = service.get_service_status()
                else:
                    service_health = {'status': 'available'}
                
                health['services'][service_name] = service_health
            except Exception as e:
                health['services'][service_name] = {'status': 'error', 'error': str(e)}
                health['overall_status'] = 'degraded'
        
        return health

# Global service manager instance
service_manager = ServiceManager()

# Convenience functions for easy access
def get_email_service():
    """Get email service instance"""
    return service_manager.get_email_service()

def get_database_utils():
    """Get database utilities instance"""
    return service_manager.get_database_utils()

def get_validation_utils():
    """Get validation utilities instance"""
    return service_manager.get_validation_utils()

def get_security_utils():
    """Get security utilities instance"""
    return service_manager.get_security_utils()

def get_data_utils():
    """Get data utilities instance"""
    return service_manager.get_data_utils()

def get_import_utils():
    """Get import utilities instance"""
    return service_manager.get_import_utils()

def get_production_utils():
    """Get production utilities instance"""
    return service_manager.get_production_utils()

def get_service_health():
    """Get health status of all services"""
    return service_manager.health_check()

# Export commonly used classes and functions
__all__ = [
    'ServiceManager',
    'UnifiedEmailService',
    'DatabaseUtils',
    'ValidationUtils', 
    'SecurityUtils',
    'DataUtils',
    'ImportUtils',
    'ProductionUtils',
    'get_email_service',
    'get_database_utils',
    'get_validation_utils',
    'get_security_utils',
    'get_data_utils',
    'get_import_utils',
    'get_production_utils',
    'get_service_health',
    'service_manager'
]