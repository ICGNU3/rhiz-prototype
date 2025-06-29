#!/usr/bin/env python3
"""
Comprehensive Testing and Issue Detection Script
Tests all platform components and identifies issues for fixing
"""

import requests
import json
import sys
import time
from datetime import datetime

class PlatformTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.issues = []
        self.tests_passed = 0
        self.tests_total = 0
        
    def test_endpoint(self, name, method, endpoint, expected_status=200, data=None, headers=None):
        """Test a single endpoint and log results"""
        self.tests_total += 1
        try:
            if method.upper() == "GET":
                response = self.session.get(f"{self.base_url}{endpoint}", headers=headers)
            elif method.upper() == "POST":
                response = self.session.post(f"{self.base_url}{endpoint}", json=data, headers=headers)
            else:
                response = self.session.request(method, f"{self.base_url}{endpoint}", json=data, headers=headers)
                
            if response.status_code == expected_status:
                print(f"✅ {name}: {response.status_code}")
                self.tests_passed += 1
                return response
            else:
                print(f"❌ {name}: Expected {expected_status}, got {response.status_code}")
                self.issues.append(f"{name}: Status {response.status_code} (expected {expected_status})")
                return None
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)}")
            self.issues.append(f"{name}: Exception - {str(e)}")
            return None
    
    def run_comprehensive_tests(self):
        """Run all platform tests"""
        print("🔍 COMPREHENSIVE PLATFORM TESTING")
        print("=" * 50)
        
        # Backend Health Check
        self.test_endpoint("Health Check", "GET", "/health")
        
        # Authentication Tests
        auth_response = self.test_endpoint("Demo Login", "POST", "/api/auth/demo-login", 200, {})
        if auth_response:
            print("   Authenticated successfully")
            
        # Core API Tests
        self.test_endpoint("User Profile", "GET", "/api/auth/profile")
        self.test_endpoint("Current User", "GET", "/api/auth/me")
        self.test_endpoint("Contacts List", "GET", "/api/contacts")
        self.test_endpoint("Goals List", "GET", "/api/goals")
        self.test_endpoint("Dashboard Analytics", "GET", "/api/dashboard/analytics")
        
        # AI Intelligence Tests
        self.test_endpoint("AI Chat", "POST", "/api/intelligence/chat", 200, {"message": "Help with networking"})
        self.test_endpoint("AI Insights", "GET", "/api/intelligence/insights")
        
        # Trust Analytics Tests
        self.test_endpoint("Trust Insights", "GET", "/api/trust/insights")
        self.test_endpoint("Trust Digest", "GET", "/api/trust/digest")
        
        # Network Visualization
        self.test_endpoint("Network Graph", "GET", "/api/network/graph")
        
        # Frontend Routes
        self.test_endpoint("Landing Page", "GET", "/")
        self.test_endpoint("App Route", "GET", "/app/dashboard", 302)  # Should redirect if not authenticated properly
        
        print("\n" + "=" * 50)
        print(f"📊 RESULTS: {self.tests_passed}/{self.tests_total} tests passed")
        
        if self.issues:
            print(f"\n⚠️  ISSUES FOUND ({len(self.issues)}):")
            for issue in self.issues:
                print(f"   - {issue}")
        else:
            print("\n🎉 ALL TESTS PASSED!")
            
        return len(self.issues) == 0

def check_frontend_build():
    """Check if React frontend builds successfully"""
    print("\n🔨 CHECKING FRONTEND BUILD")
    print("-" * 30)
    
    import subprocess
    try:
        # Change to frontend directory and build
        result = subprocess.run(
            ["npm", "run", "build"], 
            cwd="./frontend",
            capture_output=True, 
            text=True, 
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ Frontend builds successfully")
            return True
        else:
            print("❌ Frontend build failed:")
            print(result.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Frontend build timed out")
        return False
    except Exception as e:
        print(f"❌ Frontend build error: {str(e)}")
        return False

def check_database_health():
    """Check database connectivity and data"""
    print("\n💾 CHECKING DATABASE HEALTH")
    print("-" * 30)
    
    try:
        import psycopg2
        import os
        
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        cursor = conn.cursor()
        
        # Check table existence
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['users', 'contacts', 'goals', 'auth_tokens']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            print(f"❌ Missing tables: {missing_tables}")
            return False
        else:
            print("✅ All required tables present")
            
        # Check data counts
        for table in required_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} records")
            
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return False

def main():
    """Main testing function"""
    print("🚀 RHIZ PLATFORM - COMPREHENSIVE TEST & FIX")
    print("=" * 60)
    
    # Run all tests
    tester = PlatformTester()
    api_healthy = tester.run_comprehensive_tests()
    
    frontend_healthy = check_frontend_build()
    database_healthy = check_database_health()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 FINAL HEALTH REPORT")
    print("-" * 30)
    print(f"Backend API: {'✅ HEALTHY' if api_healthy else '❌ ISSUES'}")
    print(f"Frontend Build: {'✅ HEALTHY' if frontend_healthy else '❌ ISSUES'}")
    print(f"Database: {'✅ HEALTHY' if database_healthy else '❌ ISSUES'}")
    
    overall_healthy = api_healthy and frontend_healthy and database_healthy
    print(f"\nOVERALL STATUS: {'🎉 READY FOR DEPLOYMENT' if overall_healthy else '⚠️  NEEDS FIXES'}")
    
    return overall_healthy

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)