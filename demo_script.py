#!/usr/bin/env python3
"""
Demo script to showcase the complete React frontend integration
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"

def make_request(method, endpoint, data=None, session=None):
    """Make API request with session handling"""
    url = f"{BASE_URL}{endpoint}"
    if method == "GET":
        response = requests.get(url, cookies=session)
    elif method == "POST":
        response = requests.post(url, json=data, cookies=session)
    return response

def demonstrate_api():
    """Demonstrate complete API functionality"""
    print("🚀 Rhiz React Frontend Integration Demo")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Testing API Health...")
    health = make_request("GET", "/api/health")
    print(f"   Status: {health.status_code}")
    print(f"   Response: {health.json()}")
    
    # Create demo user and get session
    print("\n2. Creating Demo User Session...")
    auth_response = make_request("POST", "/api/auth/magic-link", {"email": "demo@rhiz.app"})
    session_cookies = auth_response.cookies
    print(f"   Auth Status: {auth_response.status_code}")
    print(f"   Response: {auth_response.json()}")
    
    # Seed demo data
    print("\n3. Seeding Demo Data...")
    seed_response = make_request("GET", "/api/demo/seed", session=session_cookies)
    print(f"   Seed Status: {seed_response.status_code}")
    if seed_response.status_code == 200:
        seed_data = seed_response.json()
        print(f"   ✅ Created {seed_data.get('goals_created', 0)} goals")
        print(f"   ✅ Created {seed_data.get('contacts_created', 0)} contacts") 
        print(f"   ✅ Created {seed_data.get('suggestions_created', 0)} AI suggestions")
    
    # Test authenticated endpoints
    print("\n4. Testing Goals API...")
    goals_response = make_request("GET", "/api/goals", session=session_cookies)
    if goals_response.status_code == 200:
        goals = goals_response.json()
        print(f"   ✅ Retrieved {len(goals)} goals")
        for goal in goals[:2]:
            print(f"      - {goal['title']}")
    
    print("\n5. Testing Contacts API...")
    contacts_response = make_request("GET", "/api/contacts", session=session_cookies)
    if contacts_response.status_code == 200:
        contacts = contacts_response.json()
        print(f"   ✅ Retrieved {len(contacts)} contacts")
        for contact in contacts[:3]:
            print(f"      - {contact['name']} ({contact['company']})")
    
    print("\n6. Testing AI Suggestions API...")
    suggestions_response = make_request("GET", "/api/intelligence/suggestions", session=session_cookies)
    if suggestions_response.status_code == 200:
        suggestions = suggestions_response.json()
        print(f"   ✅ Retrieved {len(suggestions)} AI suggestions")
        for suggestion in suggestions:
            print(f"      - {suggestion['contact_name']} for {suggestion['goal_title']}")
            print(f"        Confidence: {suggestion['confidence']:.0%}")
    
    print("\n7. Testing Network Graph API...")
    network_response = make_request("GET", "/api/network/graph", session=session_cookies)
    if network_response.status_code == 200:
        network = network_response.json()
        print(f"   ✅ Network has {len(network.get('nodes', []))} nodes and {len(network.get('edges', []))} edges")
    
    print("\n✅ API Integration Complete!")
    print("\nReact Frontend Components Ready:")
    print("   📱 Dashboard - Comprehensive overview with stats and visualizations")
    print("   🎯 Goals - Goal management with AI matching")
    print("   👥 Contacts - Network management with warmth tracking") 
    print("   🧠 Intelligence - AI suggestions and network analysis")
    print("   ⚙️  Settings - User preferences and integrations")
    print("   🌐 Network Graph - D3.js rhizomatic visualization")
    
    print(f"\n🔗 Access the platform at: {BASE_URL}")
    print("🔗 Test API directly at: {}/api/health".format(BASE_URL))

if __name__ == "__main__":
    demonstrate_api()