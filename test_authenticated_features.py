#!/usr/bin/env python3
"""
Test relationship intelligence features with mock session
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_authenticated_features():
    """Test features by creating a session and checking responses"""
    
    # Create a session
    session = requests.Session()
    
    # First get the login page to check CSRF tokens if needed
    login_page = session.get(f"{BASE_URL}/login")
    print(f"Login page: {login_page.status_code}")
    
    # Test relationship intelligence API endpoints (these should work even without auth for testing)
    print("\nTesting API endpoints:")
    
    api_endpoints = [
        "/api/relationship-intelligence/analysis",
        "/health"
    ]
    
    for endpoint in api_endpoints:
        try:
            resp = session.get(f"{BASE_URL}{endpoint}")
            print(f"{endpoint}: {resp.status_code}")
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    print(f"  Response type: {type(data)}")
                except:
                    print(f"  Response length: {len(resp.text)}")
        except Exception as e:
            print(f"{endpoint}: Error - {e}")
    
    # Test if templates exist by checking file sizes
    print("\nChecking template files:")
    import os
    templates = [
        "templates/intelligence/relationship_dashboard.html",
        "templates/intelligence/unknown_contacts.html", 
        "templates/intelligence/mass_messaging.html"
    ]
    
    for template in templates:
        if os.path.exists(template):
            size = os.path.getsize(template)
            print(f"✓ {template}: {size} bytes")
        else:
            print(f"✗ {template}: Missing")

if __name__ == "__main__":
    test_authenticated_features()