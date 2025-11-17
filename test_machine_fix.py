#!/usr/bin/env python3
"""
Test script to verify machine endpoints are working after fixes
"""
import requests
import json
import sys

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
            if isinstance(data, list):
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
    print("🔧 Testing Machine Endpoints After Fixes")
    print("=" * 50)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        sys.exit(1)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test basic endpoints first
    print("\n📋 Testing Basic Endpoints:")
    test_endpoint(f"{BASE_URL}/health", {}, "Health Check")
    test_endpoint(f"{BASE_URL}/organizations/", headers, "Organizations List")
    
    # Test machine endpoints
    print("\n🔧 Testing Machine Endpoints:")
    
    # First get list of machines
    machines_response = requests.get(f"{BASE_URL}/machines/", headers=headers)
    if machines_response.status_code == 200:
        machines = machines_response.json()
        print(f"✅ PASS Machines List: {machines_response.status_code}")
        print(f"    Found {len(machines)} machines")
        
        if machines:
            # Test with first machine
            machine_id = machines[0]["id"]
            print(f"\n🔍 Testing Machine Details for ID: {machine_id}")
            
            endpoints_to_test = [
                (f"{BASE_URL}/machines/{machine_id}", "Machine Details"),
                (f"{BASE_URL}/machines/{machine_id}/maintenance", "Machine Maintenance"),
                (f"{BASE_URL}/machines/{machine_id}/usage-history", "Machine Usage History"),
                (f"{BASE_URL}/machines/{machine_id}/compatible-parts", "Machine Compatible Parts")
            ]
            
            results = []
            for url, name in endpoints_to_test:
                success = test_endpoint(url, headers, name)
                results.append((name, success))
            
            # Summary
            print("\n📊 Summary:")
            passed = sum(1 for _, success in results if success)
            total = len(results)
            print(f"Passed: {passed}/{total} machine detail endpoints")
            
            if passed == total:
                print("🎉 All machine endpoints are working!")
            else:
                print("⚠️  Some endpoints need attention")
                
        else:
            print("⚠️  No machines found in database")
            print("    Creating a test machine might be needed")
    else:
        print(f"❌ FAIL Machines List: {machines_response.status_code}")
        print(f"    Error: {machines_response.text[:200]}")

if __name__ == "__main__":
    main()