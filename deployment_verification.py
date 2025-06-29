#!/usr/bin/env python3
"""
Deployment Verification Script
Checks all deployment requirements and configurations
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    exists = Path(filepath).exists()
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {filepath}")
    return exists

def check_package_availability():
    """Check if required packages are available"""
    packages = ["flask", "gunicorn", "flask_sqlalchemy", "flask_migrate", "flask_cors", "psycopg2"]
    print("\n📦 Package Availability:")
    
    all_available = True
    for package in packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package}")
            all_available = False
    
    return all_available

def check_main_app_structure():
    """Check main.py Flask app structure"""
    print("\n🔧 Main App Structure:")
    
    main_py_exists = check_file_exists("main.py", "Main application file")
    
    if main_py_exists:
        with open("main.py", "r") as f:
            content = f.read()
            
        # Check key requirements
        has_app_var = "app = create_app()" in content
        has_backend_import = "from backend import create_app" in content
        
        print(f"{'✓' if has_app_var else '✗'} Flask app variable (app = create_app())")
        print(f"{'✓' if has_backend_import else '✗'} Backend import structure")
        
        return has_app_var and has_backend_import
    
    return False

def check_replit_config():
    """Check .replit configuration"""
    print("\n⚙️  .replit Configuration:")
    
    replit_exists = check_file_exists(".replit", ".replit configuration file")
    
    if replit_exists:
        with open(".replit", "r") as f:
            content = f.read()
        
        # Check deployment configuration
        has_gunicorn_deploy = "gunicorn" in content and "main:app" in content
        has_port_config = "5000" in content
        has_autoscale = "autoscale" in content
        
        print(f"{'✓' if has_gunicorn_deploy else '✗'} Gunicorn deployment config (main:app)")
        print(f"{'✓' if has_port_config else '✗'} Port 5000 configuration")
        print(f"{'✓' if has_autoscale else '✗'} Autoscale deployment target")
        
        return has_gunicorn_deploy and has_port_config
    
    return False

def check_pyproject_toml():
    """Check pyproject.toml status"""
    print("\n📋 pyproject.toml Status:")
    
    pyproject_exists = Path("pyproject.toml").exists()
    pyproject_disabled = Path("pyproject.toml.disabled").exists()
    
    if pyproject_disabled:
        print("✓ pyproject.toml properly disabled to avoid packaging conflicts")
        return True
    elif not pyproject_exists:
        print("✓ pyproject.toml removed to avoid packaging conflicts")
        return True
    else:
        print("⚠️  pyproject.toml still present - may cause packaging issues")
        return False

def test_health_endpoint():
    """Test health endpoint"""
    print("\n🏥 Health Endpoint Test:")
    
    try:
        import requests
        response = requests.get("http://localhost:5000/health", timeout=5)
        
        if response.status_code == 200:
            print("✓ Health endpoint responding (200 OK)")
            data = response.json()
            print(f"  Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"✗ Health endpoint error (HTTP {response.status_code})")
            return False
            
    except Exception as e:
        print(f"✗ Health endpoint test failed: {e}")
        return False

def main():
    """Run all deployment verification checks"""
    print("🚀 Rhiz Platform Deployment Verification")
    print("=" * 50)
    
    checks = [
        check_main_app_structure(),
        check_replit_config(),
        check_pyproject_toml(),
        check_package_availability(),
        test_health_endpoint()
    ]
    
    passed_checks = sum(checks)
    total_checks = len(checks)
    
    print("\n" + "=" * 50)
    print(f"📊 Deployment Readiness: {passed_checks}/{total_checks} checks passed")
    
    if passed_checks == total_checks:
        print("🎉 All deployment requirements satisfied!")
        print("✅ Platform is ready for deployment")
        return 0
    else:
        print(f"⚠️  {total_checks - passed_checks} issues need attention")
        print("❌ Platform deployment may encounter issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())