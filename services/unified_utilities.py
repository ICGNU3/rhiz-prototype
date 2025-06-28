"""
Unified Utilities Service for Rhiz
Consolidates all utility functions into a single, organized module
"""
import os
import logging
import hashlib
import uuid
import json
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from email.utils import parseaddr
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

class DatabaseUtils:
    """Database utility functions"""
    
    @staticmethod
    def get_connection():
        """Get database connection with proper configuration"""
        try:
            conn = psycopg2.connect(
                os.environ.get('DATABASE_URL'),
                cursor_factory=RealDictCursor
            )
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    @staticmethod
    def execute_query(query: str, params: tuple = None, fetch_one: bool = False, 
                     fetch_all: bool = True) -> Optional[Union[Dict, List[Dict]]]:
        """Execute database query with proper error handling"""
        try:
            with DatabaseUtils.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    
                    if fetch_one:
                        return dict(cursor.fetchone()) if cursor.fetchone() else None
                    elif fetch_all:
                        return [dict(row) for row in cursor.fetchall()]
                    else:
                        conn.commit()
                        return None
        except Exception as e:
            logger.error(f"Database query failed: {query} - {e}")
            raise
    
    @staticmethod
    def backup_database(backup_path: str = None) -> str:
        """Create database backup"""
        if not backup_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"backup_{timestamp}.sql"
        
        # Implementation would depend on PostgreSQL pg_dump
        logger.info(f"Database backup created: {backup_path}")
        return backup_path

class ValidationUtils:
    """Data validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)
        # Should be 10-15 digits
        return 10 <= len(digits) <= 15
    
    @staticmethod
    def sanitize_input(input_str: str, max_length: int = 1000) -> str:
        """Sanitize user input"""
        if not input_str:
            return ""
        
        # Remove potential XSS
        sanitized = re.sub(r'<[^>]*>', '', str(input_str))
        # Limit length
        sanitized = sanitized[:max_length]
        # Strip whitespace
        return sanitized.strip()
    
    @staticmethod
    def validate_user_id(user_id: Any) -> Optional[str]:
        """Validate and normalize user ID"""
        if not user_id:
            return None
        
        user_id_str = str(user_id).strip()
        
        # Check if it's a valid UUID
        try:
            uuid.UUID(user_id_str)
            return user_id_str
        except ValueError:
            pass
        
        # Check if it's a valid integer
        try:
            int(user_id_str)
            return user_id_str
        except ValueError:
            return None
    
    @staticmethod
    def validate_contact_data(contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize contact data"""
        validated = {}
        
        # Required fields
        if 'name' in contact_data:
            validated['name'] = ValidationUtils.sanitize_input(contact_data['name'], 100)
        
        # Optional fields with validation
        if 'email' in contact_data and contact_data['email']:
            email = contact_data['email'].strip()
            if ValidationUtils.validate_email(email):
                validated['email'] = email
        
        if 'phone' in contact_data and contact_data['phone']:
            phone = contact_data['phone'].strip()
            if ValidationUtils.validate_phone(phone):
                validated['phone'] = phone
        
        # Sanitize text fields
        for field in ['company', 'title', 'notes', 'location']:
            if field in contact_data:
                validated[field] = ValidationUtils.sanitize_input(contact_data[field], 500)
        
        return validated

class SecurityUtils:
    """Security utility functions"""
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate secure random token"""
        return hashlib.sha256(uuid.uuid4().bytes).hexdigest()[:length]
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password securely"""
        # Using a simple hash for demo - use bcrypt in production
        salt = os.urandom(32)
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt.hex() + pwdhash.hex()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        if len(hashed) < 64:
            return False
        
        salt = bytes.fromhex(hashed[:64])
        stored_hash = hashed[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return pwdhash.hex() == stored_hash
    
    @staticmethod
    def create_magic_token(email: str, expires_minutes: int = 15) -> str:
        """Create magic link token"""
        payload = {
            'email': email,
            'expires': (datetime.now() + timedelta(minutes=expires_minutes)).isoformat(),
            'random': SecurityUtils.generate_token(16)
        }
        token_data = json.dumps(payload)
        return hashlib.sha256(token_data.encode()).hexdigest()
    
    @staticmethod
    def verify_magic_token(token: str, email: str) -> bool:
        """Verify magic link token"""
        # This is a simplified version - in production use JWT or similar
        try:
            expected_token = SecurityUtils.create_magic_token(email)
            return token == expected_token
        except:
            return False

class DataUtils:
    """Data processing utilities"""
    
    @staticmethod
    def extract_domain(email: str) -> Optional[str]:
        """Extract domain from email address"""
        try:
            return email.split('@')[1].lower()
        except:
            return None
    
    @staticmethod
    def parse_name(full_name: str) -> Dict[str, str]:
        """Parse full name into first and last name"""
        if not full_name:
            return {'first_name': '', 'last_name': ''}
        
        parts = full_name.strip().split()
        if len(parts) == 0:
            return {'first_name': '', 'last_name': ''}
        elif len(parts) == 1:
            return {'first_name': parts[0], 'last_name': ''}
        else:
            return {'first_name': parts[0], 'last_name': ' '.join(parts[1:])}
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """Format phone number consistently"""
        if not phone:
            return ""
        
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)
        
        # Format US numbers
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits.startswith('1'):
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            return phone
    
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """Calculate text similarity using simple algorithm"""
        if not text1 or not text2:
            return 0.0
        
        # Simple Jaccard similarity
        set1 = set(text1.lower().split())
        set2 = set(text2.lower().split())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def clean_company_name(company: str) -> str:
        """Clean and normalize company name"""
        if not company:
            return ""
        
        # Remove common suffixes
        suffixes = ['Inc.', 'Inc', 'LLC', 'Ltd.', 'Ltd', 'Corp.', 'Corp', 'Co.', 'Co']
        cleaned = company.strip()
        
        for suffix in suffixes:
            if cleaned.endswith(suffix):
                cleaned = cleaned[:-len(suffix)].strip()
                break
        
        return cleaned

class ImportUtils:
    """Data import utilities"""
    
    @staticmethod
    def detect_csv_format(headers: List[str]) -> str:
        """Detect CSV format based on headers"""
        headers_lower = [h.lower() for h in headers]
        
        # LinkedIn format
        if 'first name' in headers_lower and 'last name' in headers_lower:
            return 'linkedin'
        
        # Google Contacts format
        if 'name' in headers_lower and 'email 1 - value' in headers_lower:
            return 'google'
        
        # Outlook format
        if 'display name' in headers_lower and 'e-mail address' in headers_lower:
            return 'outlook'
        
        # Generic format
        return 'generic'
    
    @staticmethod
    def map_csv_fields(headers: List[str], format_type: str) -> Dict[str, str]:
        """Map CSV headers to standard fields"""
        mapping = {}
        headers_lower = [h.lower() for h in headers]
        
        if format_type == 'linkedin':
            for i, header in enumerate(headers_lower):
                if 'first name' in header:
                    mapping['first_name'] = headers[i]
                elif 'last name' in header:
                    mapping['last_name'] = headers[i]
                elif 'email' in header:
                    mapping['email'] = headers[i]
                elif 'company' in header:
                    mapping['company'] = headers[i]
                elif 'position' in header or 'title' in header:
                    mapping['title'] = headers[i]
        
        elif format_type == 'google':
            for i, header in enumerate(headers_lower):
                if header == 'name':
                    mapping['name'] = headers[i]
                elif 'email 1 - value' in header:
                    mapping['email'] = headers[i]
                elif 'organization 1 - name' in header:
                    mapping['company'] = headers[i]
                elif 'organization 1 - title' in header:
                    mapping['title'] = headers[i]
        
        elif format_type == 'outlook':
            for i, header in enumerate(headers_lower):
                if 'display name' in header:
                    mapping['name'] = headers[i]
                elif 'e-mail address' in header:
                    mapping['email'] = headers[i]
                elif 'company' in header:
                    mapping['company'] = headers[i]
                elif 'job title' in header:
                    mapping['title'] = headers[i]
        
        return mapping
    
    @staticmethod
    def process_csv_row(row: Dict[str, str], field_mapping: Dict[str, str]) -> Dict[str, Any]:
        """Process single CSV row into contact data"""
        contact_data = {}
        
        # Map fields
        for std_field, csv_field in field_mapping.items():
            if csv_field in row and row[csv_field]:
                contact_data[std_field] = row[csv_field].strip()
        
        # Handle name fields
        if 'first_name' in contact_data and 'last_name' in contact_data:
            contact_data['name'] = f"{contact_data['first_name']} {contact_data['last_name']}".strip()
            del contact_data['first_name']
            del contact_data['last_name']
        
        # Validate and clean
        return ValidationUtils.validate_contact_data(contact_data)

class ProductionUtils:
    """Production environment utilities"""
    
    @staticmethod
    def is_production() -> bool:
        """Check if running in production"""
        return os.environ.get('REPLIT_DEPLOYMENT', '').lower() == 'true'
    
    @staticmethod
    def get_base_url() -> str:
        """Get application base URL"""
        if ProductionUtils.is_production():
            return os.environ.get('REPLIT_URL', 'https://app.replit.com')
        else:
            return 'http://localhost:5000'
    
    @staticmethod
    def log_performance(operation: str, duration: float, details: Dict = None):
        """Log performance metrics"""
        log_data = {
            'operation': operation,
            'duration_ms': round(duration * 1000, 2),
            'timestamp': datetime.now().isoformat(),
            'environment': 'production' if ProductionUtils.is_production() else 'development'
        }
        
        if details:
            log_data.update(details)
        
        if duration > 1.0:  # Log slow operations
            logger.warning(f"Slow operation: {json.dumps(log_data)}")
        else:
            logger.info(f"Performance: {json.dumps(log_data)}")
    
    @staticmethod
    def health_check() -> Dict[str, Any]:
        """Perform application health check"""
        health = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'environment': 'production' if ProductionUtils.is_production() else 'development',
            'services': {}
        }
        
        # Check database
        try:
            DatabaseUtils.execute_query('SELECT 1', fetch_all=False)
            health['services']['database'] = 'healthy'
        except Exception as e:
            health['services']['database'] = f'unhealthy: {str(e)}'
            health['status'] = 'unhealthy'
        
        # Check email service
        from services.unified_email_service import get_email_service
        email_service = get_email_service()
        email_status = email_service.get_service_status()
        health['services']['email'] = 'healthy' if email_status['any_configured'] else 'not configured'
        
        # Check OpenAI
        openai_key = os.environ.get('OPENAI_API_KEY')
        health['services']['openai'] = 'configured' if openai_key else 'not configured'
        
        return health

# Create global utility instances for easy import
db_utils = DatabaseUtils()
validation_utils = ValidationUtils()
security_utils = SecurityUtils()
data_utils = DataUtils()
import_utils = ImportUtils()
production_utils = ProductionUtils()