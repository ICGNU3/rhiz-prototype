#!/usr/bin/env python3
"""
Test script for relationship intelligence features
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_feature_access():
    """Test if the relationship intelligence features are accessible"""
    
    # Test health endpoint first
    health_resp = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {health_resp.status_code}")
    if health_resp.status_code == 200:
        print(f"Health status: {health_resp.json()}")
    
    # Test the main landing page
    home_resp = requests.get(BASE_URL)
    print(f"\nHome page: {home_resp.status_code}")
    
    # Test relationship intelligence routes (should redirect to login if not authenticated)
    intelligence_routes = [
        "/intelligence/relationships",
        "/intelligence/unknown-contacts", 
        "/intelligence/mass-messaging"
    ]
    
    print("\nTesting relationship intelligence routes:")
    for route in intelligence_routes:
        try:
            resp = requests.get(f"{BASE_URL}{route}", allow_redirects=False)
            print(f"{route}: {resp.status_code} - {'Redirect' if resp.status_code in [301, 302] else 'Direct'}")
        except Exception as e:
            print(f"{route}: Error - {e}")
    
    # Test navigation presence by checking if the route endpoints exist
    print("\nTesting route registration:")
    try:
        # Test a route that should exist
        resp = requests.get(f"{BASE_URL}/login")
        print(f"Login route: {resp.status_code}")
        
        # Check if navigation includes Intelligence dropdown
        if "Intelligence" in resp.text:
            print("✓ Intelligence dropdown found in navigation")
        else:
            print("✗ Intelligence dropdown not found")
            
        if "Relationship Intelligence" in resp.text:
            print("✓ Relationship Intelligence section found")
        else:
            print("✗ Relationship Intelligence section not found")
            
    except Exception as e:
        print(f"Navigation test error: {e}")

if __name__ == "__main__":
    test_feature_access()