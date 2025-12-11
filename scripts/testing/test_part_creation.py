#!/usr/bin/env python3
"""
Test part creation to debug the 400 error
"""
import requests
import json

def test_part_creation():
    print("🔧 Testing Part Creation")
    print("=" * 40)
    
    try:
        # Login first
        print("1. Authenticating...")
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
        
        # Test part creation with minimal data
        print("\n2. Testing part creation...")
        part_data = {
            "part_number": "TEST-001",
            "name": "Test Part",
            "description": "Test description",
            "part_type": "consumable",
            "is_proprietary": False,
            "unit_of_measure": "pieces",
            "image_urls": []
        }
        
        print(f"Sending data: {json.dumps(part_data, indent=2)}")
        
        response = requests.post(
            "http://localhost:8000/parts/",
            json=part_data,
            headers=headers,
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
        
        if response.status_code == 201:
            print("✅ Part created successfully!")
            created_part = response.json()
            print(f"Created part ID: {created_part.get('id')}")
        else:
            print(f"❌ Part creation failed")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw error response: {response.text}")
                
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_part_creation()