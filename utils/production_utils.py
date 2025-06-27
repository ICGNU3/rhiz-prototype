"""
Production utilities for launch readiness
Includes error handling, performance monitoring, and database optimizations
"""
import os
import logging
import time
import functools
from datetime import datetime
from typing import Any, Dict, Optional, Callable
import sqlite3

# Configure production logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log') if os.environ.get('LOG_TO_FILE') else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)

class ProductionErrorHandler:
    """Centralized error handling for production environment"""
    
    @staticmethod
    def handle_database_error(func: Callable) -> Callable:
        """Decorator for database operation error handling"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except sqlite3.Error as e:
                logger.error(f"Database error in {func.__name__}: {e}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error in {func.__name__}: {e}")
                return None
        return wrapper
    
    @staticmethod
    def handle_api_error(func: Callable) -> Callable:
        """Decorator for API operation error handling"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"API error in {func.__name__}: {e}")
                return {"error": str(e), "success": False}
        return wrapper
    
    @staticmethod
    def log_performance(func: Callable) -> Callable:
        """Decorator for performance monitoring"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if execution_time > 1.0:  # Log slow operations
                logger.warning(f"Slow operation {func.__name__}: {execution_time:.2f}s")
            
            return result
        return wrapper

class DatabaseOptimizer:
    """Database optimization utilities for production"""
    
    @staticmethod
    def optimize_database(db_path: str = "db.sqlite3"):
        """Optimize SQLite database for production performance"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Enable WAL mode for better concurrency
            cursor.execute("PRAGMA journal_mode=WAL")
            
            # Optimize cache and temp store
            cursor.execute("PRAGMA cache_size=10000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys=ON")
            
            # Analyze tables for query optimization
            cursor.execute("ANALYZE")
            
            # Create missing indexes for performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_contacts_user_id ON contacts(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_goals_user_id ON goals(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_ai_suggestions_user_id ON ai_suggestions(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_ai_suggestions_goal_id ON ai_suggestions(goal_id)",
                "CREATE INDEX IF NOT EXISTS idx_contact_interactions_contact_id ON contact_interactions(contact_id)",
                "CREATE INDEX IF NOT EXISTS idx_contact_interactions_user_id ON contact_interactions(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_usage_tracking_user_id ON usage_tracking(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_magic_links_token ON magic_links(token)",
                "CREATE INDEX IF NOT EXISTS idx_rhizomatic_insights_user_id ON rhizomatic_insights(user_id)"
            ]
            
            for index_sql in indexes:
                cursor.execute(index_sql)
            
            conn.commit()
            conn.close()
            
            logger.info("Database optimization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Database optimization failed: {e}")
            return False
    
    @staticmethod
    def get_database_stats(db_path: str = "db.sqlite3") -> Dict[str, Any]:
        """Get database statistics for monitoring"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get table counts
            stats = {}
            tables = ['users', 'contacts', 'goals', 'ai_suggestions', 'contact_interactions']
            
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[f"{table}_count"] = cursor.fetchone()[0]
                except sqlite3.Error:
                    stats[f"{table}_count"] = 0
            
            # Get database size
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            stats['database_size_mb'] = (page_count * page_size) / (1024 * 1024)
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}

class HealthChecker:
    """System health monitoring for production"""
    
    @staticmethod
    def check_system_health() -> Dict[str, Any]:
        """Comprehensive system health check"""
        health = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {}
        }
        
        # Database health
        try:
            conn = sqlite3.connect("db.sqlite3")
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            health["checks"]["database"] = "healthy"
        except Exception as e:
            health["checks"]["database"] = f"error: {e}"
            health["status"] = "degraded"
        
        # OpenAI API health
        openai_key = os.environ.get('OPENAI_API_KEY')
        health["checks"]["openai"] = "configured" if openai_key else "not_configured"
        
        # Email service health
        sendgrid_key = os.environ.get('SENDGRID_API_KEY')
        health["checks"]["email"] = "configured" if sendgrid_key else "not_configured"
        
        # Disk space check
        try:
            import shutil
            total, used, free = shutil.disk_usage(".")
            free_gb = free // (1024**3)
            health["checks"]["disk_space_gb"] = free_gb
            if free_gb < 1:
                health["status"] = "warning"
        except Exception:
            health["checks"]["disk_space_gb"] = "unknown"
        
        return health

class SecurityHelper:
    """Security utilities for production"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """Sanitize user input"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        import html
        sanitized = html.escape(text.strip())
        
        # Truncate to max length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def rate_limit_check(user_id: str, action: str, limit: int = 10, window_minutes: int = 60) -> bool:
        """Simple rate limiting for API endpoints"""
        # This would typically use Redis, but using memory for simplicity
        if not hasattr(SecurityHelper, '_rate_limits'):
            SecurityHelper._rate_limits = {}
        
        now = time.time()
        key = f"{user_id}:{action}"
        
        if key not in SecurityHelper._rate_limits:
            SecurityHelper._rate_limits[key] = []
        
        # Clean old entries
        window_seconds = window_minutes * 60
        SecurityHelper._rate_limits[key] = [
            timestamp for timestamp in SecurityHelper._rate_limits[key]
            if now - timestamp < window_seconds
        ]
        
        # Check limit
        if len(SecurityHelper._rate_limits[key]) >= limit:
            return False
        
        # Add current request
        SecurityHelper._rate_limits[key].append(now)
        return True

# Initialize database optimization on import
if os.path.exists("db.sqlite3"):
    DatabaseOptimizer.optimize_database()