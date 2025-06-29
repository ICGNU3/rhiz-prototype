"""Test the main Flask application functionality."""
import pytest
from flask import Flask


def test_app_creation():
    """Test that the Flask app can be created successfully."""
    from backend import create_app
    app = create_app({'TESTING': True})
    assert app is not None
    assert isinstance(app, Flask)
    assert app.config['TESTING'] is True


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    
    # Parse JSON response
    data = response.get_json()
    assert data is not None
    assert 'status' in data
    assert 'timestamp' in data


def test_landing_page(client):
    """Test the landing page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Rhiz' in response.data


def test_login_page(client):
    """Test the login page loads correctly."""
    response = client.get('/login')
    assert response.status_code == 200
    # Should contain login form elements
    assert b'email' in response.data or b'Email' in response.data


def test_protected_route_requires_auth(client):
    """Test that protected routes require authentication."""
    response = client.get('/app/dashboard')
    # Should redirect to login or return 302/401
    assert response.status_code in [302, 401]


def test_api_prefix_exists(client):
    """Test that API routes are properly configured."""
    # This should return 401 for auth required, not 404
    response = client.get('/api/auth/me')
    assert response.status_code != 404


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_404_page(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
    
    def test_invalid_api_endpoint(self, client):
        """Test invalid API endpoint handling."""
        response = client.get('/api/invalid-endpoint')
        assert response.status_code == 404


class TestAuthentication:
    """Test authentication-related functionality."""
    
    def test_magic_link_request_endpoint_exists(self, client):
        """Test magic link request endpoint exists."""
        # POST without data should not crash
        response = client.post('/api/auth/request-link')
        # Should return error for missing data, not 404
        assert response.status_code != 404
    
    def test_auth_verify_endpoint_exists(self, client):
        """Test auth verification endpoint exists."""
        response = client.get('/api/auth/verify')
        # Should return error for missing token, not 404
        assert response.status_code != 404


class TestDatabase:
    """Test database connectivity and basic operations."""
    
    def test_database_connection(self, app):
        """Test that database connection works."""
        with app.app_context():
            from backend.extensions import db
            # Should not raise an exception
            with db.engine.connect() as connection:
                result = connection.execute(db.text('SELECT 1'))
                assert result is not None
    
    def test_user_model_creation(self, app, sample_user_data):
        """Test user model can be created."""
        with app.app_context():
            from backend.models import User
            from backend.extensions import db
            
            user = User(**sample_user_data)
            db.session.add(user)
            db.session.commit()
            
            # Verify user was created
            assert user.id is not None
            assert user.email == sample_user_data['email']


class TestAPIEndpoints:
    """Test API endpoint existence and basic functionality."""
    
    def test_contacts_api_exists(self, client):
        """Test contacts API endpoint exists."""
        response = client.get('/api/contacts')
        # Should require auth, not be missing
        assert response.status_code != 404
    
    def test_goals_api_exists(self, client):
        """Test goals API endpoint exists."""
        response = client.get('/api/goals')
        # Should require auth, not be missing
        assert response.status_code != 404
    
    def test_dashboard_api_exists(self, client):
        """Test dashboard analytics API exists."""
        response = client.get('/api/dashboard/analytics')
        # Should require auth, not be missing
        assert response.status_code != 404