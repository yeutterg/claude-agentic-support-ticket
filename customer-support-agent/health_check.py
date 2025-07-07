#!/usr/bin/env python3
"""
Health check script for Docker containers
"""

import sys
import os
import json
from datetime import datetime

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["ANTHROPIC_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment variables configured")
    return True

def check_data_files():
    """Check if required data files exist"""
    required_files = [
        "data/sample_tickets/tickets.json",
        "data/knowledge_base/articles.json",
        "data/customer_profiles/profiles.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing data files: {', '.join(missing_files)}")
        return False
    
    print("✅ Data files present")
    return True

def check_dependencies():
    """Check if key dependencies can be imported"""
    try:
        import anthropic
        import dotenv
        print("✅ Core dependencies available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def run_basic_test():
    """Run a basic functionality test"""
    try:
        from config.env_config import EnvConfig
        
        # Test configuration loading
        env_config = EnvConfig()
        config = env_config.get_pipeline_config()
        
        # Check if we can load sample data
        with open("data/sample_tickets/tickets.json", 'r') as f:
            tickets = json.load(f)
        
        if not tickets:
            print("❌ No sample tickets found")
            return False
        
        print(f"✅ Basic functionality test passed ({len(tickets)} tickets loaded)")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def main():
    """Main health check function"""
    print("Customer Support Agent - Health Check")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    checks = [
        ("Environment Configuration", check_environment),
        ("Data Files", check_data_files),
        ("Dependencies", check_dependencies),
        ("Basic Functionality", run_basic_test)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"Checking {check_name}...")
        if not check_func():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All health checks passed!")
        print("System is ready to process support tickets.")
        sys.exit(0)
    else:
        print("💥 Some health checks failed!")
        print("Please fix the issues above before running the system.")
        sys.exit(1)

if __name__ == "__main__":
    main()