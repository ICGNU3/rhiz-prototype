"""
Custom exceptions and error handlers for the Rhiz application
"""
from flask import jsonify
import logging

class RhizError(Exception):
    """Base exception class for Rhiz application"""
    status_code = 500
    
    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

class ValidationError(RhizError):
    """Validation error exception"""
    status_code = 400

class AuthenticationError(RhizError):
    """Authentication error exception"""
    status_code = 401

class AuthorizationError(RhizError):
    """Authorization error exception"""
    status_code = 403

class NotFoundError(RhizError):
    """Resource not found exception"""
    status_code = 404

class ContactSyncError(RhizError):
    """Contact synchronization error"""
    status_code = 422

class AIServiceError(RhizError):
    """AI service error exception"""
    status_code = 503

def register_error_handlers(app):
    """Register error handlers with Flask app"""
    
    @app.errorhandler(RhizError)
    def handle_rhiz_error(error):
        """Handle custom Rhiz errors"""
        response = {
            'error': error.message,
            'status_code': error.status_code
        }
        if error.payload:
            response.update(error.payload)
        
        logging.error(f"RhizError: {error.message} (Status: {error.status_code})")
        return jsonify(response), error.status_code
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle bad request errors"""
        logging.error(f"Bad Request: {error}")
        return jsonify({
            'error': 'Bad request',
            'status_code': 400
        }), 400
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle not found errors"""
        logging.error(f"Not Found: {error}")
        return jsonify({
            'error': 'Resource not found',
            'status_code': 404
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle internal server errors"""
        logging.error(f"Internal Server Error: {error}")
        return jsonify({
            'error': 'Internal server error',
            'status_code': 500
        }), 500