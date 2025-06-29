"""Test configuration and fixtures for pytest."""
import os
import tempfile
from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from backend import create_app
from backend.extensions import db


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    """Create and configure a new app instance for each test."""
    # Create a temporary file to use as the test database
    db_fd, db_path = tempfile.mkstemp()
    
    # Configure the app for testing
    test_config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    }
    
    app = create_app(test_config)
    
    # Create the database and tables
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    # Clean up the temporary database file
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app: Flask):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers() -> dict:
    """Create authentication headers for API testing."""
    return {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer test-token'
    }


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user data for testing."""
    return {
        'email': 'test@example.com',
        'name': 'Test User',
        'subscription_tier': 'explorer'
    }


@pytest.fixture
def sample_contact_data() -> dict:
    """Sample contact data for testing."""
    return {
        'name': 'John Doe',
        'email': 'john@example.com',
        'company': 'Tech Corp',
        'title': 'Software Engineer',
        'notes': 'Met at conference',
        'warmth_level': 'warm'
    }


@pytest.fixture
def sample_goal_data() -> dict:
    """Sample goal data for testing."""
    return {
        'title': 'Find CTO for startup',
        'description': 'Looking for an experienced CTO to join our team',
        'goal_type': 'hiring',
        'priority_level': 'high',
        'target_date': '2024-12-31'
    }


@pytest.fixture
def authenticated_user(app: Flask, sample_user_data: dict):
    """Create an authenticated user for testing."""
    with app.app_context():
        from backend.models import User
        user = User(**sample_user_data)
        db.session.add(user)
        db.session.commit()
        return user