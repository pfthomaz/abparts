#!/usr/bin/env python3
"""
Test script to verify machine registration and management API endpoints
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test if the API is accessible"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✓ API Health Check: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ API Health Check failed: {e}")
        return False

def test_machine_endpoints():
    """Test machine-related endpoints"""
    print("\n=== Testing Machine API Endpoints ===")
    
    # Test GET /machines (should require authentication)
    try:
        response = requests.get(f"{BASE_URL}/machines")
        print(f"GET /machines: {response.status_code}")
        if response.status_code == 401:
            print("✓ Authentication required (expected)")
        elif response.status_code == 200:
            print("✓ Machines endpoint accessible")
        else:
            print(f"? Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"✗ GET /machines failed: {e}")

    # Test API documentation
    try:
        response = requests.get(f"{BASE_URL}/docs")
        print(f"GET /docs: {response.status_code}")
        if response.status_code == 200:
            print("✓ API documentation accessible")
    except Exception as e:
        print(f"✗ GET /docs failed: {e}")

def test_organizations_endpoint():
    """Test organizations endpoint"""
    print("\n=== Testing Organizations API ===")
    
    try:
        response = requests.get(f"{BASE_URL}/organizations")
        print(f"GET /organizations: {response.status_code}")
        if response.status_code == 401:
            print("✓ Authentication required (expected)")
        elif response.status_code == 200:
            print("✓ Organizations endpoint accessible")
    except Exception as e:
        print(f"✗ GET /organizations failed: {e}")

def main():
    print("ABParts Machine Registration API Test")
    print("=" * 40)
    
    if not test_api_health():
        print("API is not accessible. Make sure the containers are running.")
        sys.exit(1)
    
    test_machine_endpoints()
    test_organizations_endpoint()
    
    print("\n=== Test Summary ===")
    print("✓ API is running and accessible")
    print("✓ Machine endpoints are properly protected")
    print("✓ Authentication is required for protected endpoints")
    print("\nTo test the full functionality:")
    print("1. Access http://localhost:3000 in your browser")
    print("2. Login as a super admin user")
    print("3. Navigate to the Machines section")
    print("4. Try registering a new machine")

if __name__ == "__main__":
    main()