"""
Simple Email Service - Placeholder Implementation
"""

class SimpleEmailSender:
    """Placeholder for email sending functionality"""
    
    def __init__(self, config=None):
        self.config = config or {}
    
    @staticmethod
    def status():
        return {"service": "simple_email", "ready": False}
    
    def send_email(self, *args, **kwargs):
        """Placeholder method"""
        return {"success": False, "error": "Email service not implemented"}
    
    def send_magic_link(self, *args, **kwargs):
        """Placeholder method"""
        return {"success": False, "error": "Magic link service not implemented"}