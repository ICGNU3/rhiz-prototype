"""
Fallback Telegram integration when the full telegram library is not available
"""

class MockTelegramBot:
    """Mock Telegram bot for when telegram library is unavailable"""
    
    def __init__(self, db):
        self.db = db
        self.enabled = False
    
    def is_configured(self):
        return False
    
    async def send_notification(self, message, contact_name=None):
        return False
    
    async def send_daily_digest(self, user_id):
        return False