"""
Input validation utilities for secure and type-safe request handling
"""

from typing import Any, Dict, List, Optional, Union
from flask import request
import re
import logging

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class RequestValidator:
    """Validates and sanitizes request data"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email or not isinstance(email, str):
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email.strip()) is not None
    
    @staticmethod
    def validate_user_id(user_id: Any) -> str:
        """Validate and convert user_id to string"""
        if user_id is None:
            raise ValidationError("User ID is required", "user_id")
        
        if isinstance(user_id, (int, str)):
            return str(user_id).strip()
        
        raise ValidationError("Invalid user ID format", "user_id")
    
    @staticmethod
    def validate_contact_id(contact_id: Any) -> str:
        """Validate and convert contact_id to string"""
        if contact_id is None:
            raise ValidationError("Contact ID is required", "contact_id")
        
        if isinstance(contact_id, (int, str)):
            return str(contact_id).strip()
        
        raise ValidationError("Invalid contact ID format", "contact_id")
    
    @staticmethod
    def validate_required_string(value: Any, field_name: str, min_length: int = 1, max_length: int = 500) -> str:
        """Validate required string field"""
        if value is None:
            raise ValidationError(f"{field_name} is required", field_name)
        
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string", field_name)
        
        value = value.strip()
        
        if len(value) < min_length:
            raise ValidationError(f"{field_name} must be at least {min_length} characters", field_name)
        
        if len(value) > max_length:
            raise ValidationError(f"{field_name} must not exceed {max_length} characters", field_name)
        
        return value
    
    @staticmethod
    def validate_optional_string(value: Any, field_name: str, max_length: int = 500) -> Optional[str]:
        """Validate optional string field"""
        if value is None or value == '':
            return None
        
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string", field_name)
        
        value = value.strip()
        
        if len(value) > max_length:
            raise ValidationError(f"{field_name} must not exceed {max_length} characters", field_name)
        
        return value if value else None
    
    @staticmethod
    def validate_integer(value: Any, field_name: str, min_val: int = None, max_val: int = None) -> int:
        """Validate integer field"""
        if value is None:
            raise ValidationError(f"{field_name} is required", field_name)
        
        try:
            if isinstance(value, str):
                int_value = int(value.strip())
            elif isinstance(value, int):
                int_value = value
            else:
                raise ValueError("Invalid type")
        except (ValueError, AttributeError):
            raise ValidationError(f"{field_name} must be a valid integer", field_name)
        
        if min_val is not None and int_value < min_val:
            raise ValidationError(f"{field_name} must be at least {min_val}", field_name)
        
        if max_val is not None and int_value > max_val:
            raise ValidationError(f"{field_name} must not exceed {max_val}", field_name)
        
        return int_value
    
    @staticmethod
    def validate_choice(value: Any, field_name: str, choices: List[str]) -> str:
        """Validate choice from predefined options"""
        if value is None:
            raise ValidationError(f"{field_name} is required", field_name)
        
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string", field_name)
        
        value = value.strip()
        
        if value not in choices:
            raise ValidationError(f"{field_name} must be one of: {', '.join(choices)}", field_name)
        
        return value
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Basic HTML sanitization - remove potentially dangerous tags"""
        if not text:
            return ""
        
        # Remove script tags and their content
        text = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', text, flags=re.IGNORECASE)
        
        # Remove other potentially dangerous tags
        dangerous_tags = ['iframe', 'object', 'embed', 'form', 'input', 'button']
        for tag in dangerous_tags:
            text = re.sub(rf'<{tag}\b[^>]*>', '', text, flags=re.IGNORECASE)
            text = re.sub(rf'</{tag}>', '', text, flags=re.IGNORECASE)
        
        return text.strip()

class FormValidator:
    """Validates form data from Flask requests"""
    
    def __init__(self, form_data: Dict[str, Any] = None):
        self.form_data = form_data or request.form.to_dict()
        self.errors = []
    
    def get_required_string(self, field_name: str, min_length: int = 1, max_length: int = 500) -> str:
        """Get and validate required string field"""
        try:
            value = self.form_data.get(field_name)
            return RequestValidator.validate_required_string(value, field_name, min_length, max_length)
        except ValidationError as e:
            self.errors.append(e.message)
            return ""
    
    def get_optional_string(self, field_name: str, max_length: int = 500) -> Optional[str]:
        """Get and validate optional string field"""
        try:
            value = self.form_data.get(field_name)
            return RequestValidator.validate_optional_string(value, field_name, max_length)
        except ValidationError as e:
            self.errors.append(e.message)
            return None
    
    def get_integer(self, field_name: str, default: int = None, min_val: int = None, max_val: int = None) -> int:
        """Get and validate integer field"""
        try:
            value = self.form_data.get(field_name)
            if value is None and default is not None:
                return default
            return RequestValidator.validate_integer(value, field_name, min_val, max_val)
        except ValidationError as e:
            self.errors.append(e.message)
            return default or 0
    
    def get_choice(self, field_name: str, choices: List[str], default: str = None) -> str:
        """Get and validate choice field"""
        try:
            value = self.form_data.get(field_name)
            if value is None and default is not None:
                return default
            return RequestValidator.validate_choice(value, field_name, choices)
        except ValidationError as e:
            self.errors.append(e.message)
            return default or choices[0] if choices else ""
    
    def get_email(self, field_name: str) -> str:
        """Get and validate email field"""
        try:
            value = self.form_data.get(field_name)
            email = RequestValidator.validate_required_string(value, field_name)
            
            if not RequestValidator.validate_email(email):
                raise ValidationError(f"Invalid email format", field_name)
            
            return email.lower().strip()
        except ValidationError as e:
            self.errors.append(e.message)
            return ""
    
    def has_errors(self) -> bool:
        """Check if validation errors occurred"""
        return len(self.errors) > 0
    
    def get_errors(self) -> List[str]:
        """Get all validation error messages"""
        return self.errors

def validate_session_user_id() -> str:
    """Validate and return user ID from session"""
    from flask import session
    
    user_id = session.get('user_id')
    if not user_id:
        raise ValidationError("Authentication required")
    
    return RequestValidator.validate_user_id(user_id)

def safe_get_user_id(default_user_id: str = None) -> Optional[str]:
    """Safely get user ID from session with fallback"""
    from flask import session
    
    try:
        return validate_session_user_id()
    except ValidationError:
        if default_user_id:
            return default_user_id
        return None

def log_validation_error(error: ValidationError, context: str = ""):
    """Log validation error with context"""
    logging.warning(f"Validation error in {context}: {error.message} (field: {error.field})")

# Decorator for route validation
def validate_form(validation_func):
    """Decorator to validate form data in routes"""
    from functools import wraps
    from flask import flash, redirect, url_for
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                validator = FormValidator()
                validated_data = validation_func(validator)
                
                if validator.has_errors():
                    for error in validator.get_errors():
                        flash(error, 'error')
                    return redirect(url_for('core_routes.dashboard'))
                
                # Pass validated data to the route function
                return f(validated_data, *args, **kwargs)
                
            except Exception as e:
                logging.error(f"Validation decorator error: {e}")
                flash('Invalid request data', 'error')
                return redirect(url_for('core_routes.dashboard'))
        
        return decorated_function
    return decorator