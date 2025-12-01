#!/usr/bin/env python3
"""
Test script to verify parts endpoints are working after fixes
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def get_auth_token():
    """Get authentication token"""
    try:
        response = requests.post(
            f"{BASE_URL}/token",
            data={"username": "superadmin", "password": "superadmin"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Login error: {e}")
        return None

def test_endpoint(url, headers, endpoint_name):
    """Test a single endpoint"""
    try:
        response = requests.get(url, headers=headers)
        status = "✅ PASS" if response.status_code == 200 else "❌ FAIL"
        print(f"{status} {endpoint_name}: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "items" in data:
                print(f"    Returned {len(data['items'])} items")
                if data.get('total_count') is not None:
                    print(f"    Total count: {data['total_count']}")
            elif isinstance(data, list):
                print(f"    Returned {len(data)} items")
            elif isinstance(data, dict):
                print(f"    Returned object with keys: {list(data.keys())[:5]}")
        else:
            print(f"    Error: {response.text[:200]}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"❌ ERROR {endpoint_name}: {e}")
        return False

def main():
    print("🔧 Testing Parts Endpoints After Fixes")
    print("=" * 50)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test basic endpoints first
    print("\n📋 Testing Basic Endpoints:")
    test_endpoint(f"{BASE_URL}/health", {}, "Health Check")
    
    # Test parts endpoints
    print("\n📦 Testing Parts Endpoints:")
    
    endpoints_to_test = [
        (f"{BASE_URL}/parts/", "Parts List"),
        (f"{BASE_URL}/parts/with-inventory?include_count=true&limit=10", "Parts with Inventory"),
        (f"{BASE_URL}/parts/with-inventory?limit=5", "Parts with Inventory (no count)"),
    ]
    
    results = []
    for url, name in endpoints_to_test:
        success = test_endpoint(url, headers, name)
        results.append((name, success))
    
    # Summary
    print("\n📊 Summary:")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"Passed: {passed}/{total} parts endpoints")
    
    if passed == total:
        print("🎉 All parts endpoints are working!")
    else:
        print("⚠️  Some endpoints need attention")

if __name__ == "__main__":
    main()