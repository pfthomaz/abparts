#!/usr/bin/env python3
"""
Debug part creation with detailed logging
"""
import requests
import json

def test_part_creation_debug():
    print("🔧 Debug Part Creation")
    print("=" * 40)
    
    try:
        # Login first
        login_response = requests.post(
            "http://localhost:8000/token",
            data={"username": "superadmin", "password": "superadmin"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        print("✅ Authentication successful")
        
        # Test with minimal data first
        print("\n2. Testing with minimal data...")
        minimal_data = {
            "part_number": "DEBUG-001",
            "name": "Debug Part",
            "part_type": "consumable",
            "is_proprietary": False
        }
        
        print(f"Sending minimal data: {json.dumps(minimal_data, indent=2)}")
        
        response = requests.post(
            "http://localhost:8000/parts/",
            json=minimal_data,
            headers=headers,
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code != 201:
            print("❌ Even minimal data failed")
        else:
            print("✅ Minimal data worked!")
            
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_part_creation_debug()