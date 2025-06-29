"""
Test configuration for pytest
"""
import pytest
import tempfile
import os
import sys

# Add the root directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def app():
    """Create and configure a test app instance"""
    # Create temporary database for testing
    db_fd, db_path = tempfile.mkstemp()
    
    # Set test environment variables
    os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
    os.environ['TESTING'] = 'True'
    os.environ['SESSION_SECRET'] = 'test-secret-key'
    
    # Import app after setting environment
    from main import app
    app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'DATABASE_URL': f'sqlite:///{db_path}'
    })
    
    yield app
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def authenticated_client(client):
    """Create authenticated test client with demo session"""
    with client.session_transaction() as session:
        session['user_id'] = 'demo_user'
        session['email'] = 'test@rhiz.app'
        session['authenticated'] = True
    return client