#!/usr/bin/env python3
"""
Test part creation after fixing missing columns
"""
import requests
import json

def test_part_creation():
    print("🔧 Testing Part Creation - After Column Fix")
    print("=" * 50)
    
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
        
        # Test part creation with only available columns
        print("\n2. Testing part creation...")
        part_data = {
            "part_number": "CPW-002",
            "name": "Filter Bag",
            "description": "filter bag",
            "part_type": "consumable",
            "is_proprietary": False,
            "unit_of_measure": "pieces",
            "manufacturer_part_number": "FB-001",
            "manufacturer_delivery_time_days": 7,
            "local_supplier_delivery_time_days": 3,
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
        
        if response.status_code == 201:
            print("✅ Part created successfully!")
            created_part = response.json()
            print(f"Created part:")
            print(f"  - ID: {created_part.get('id')}")
            print(f"  - Part Number: {created_part.get('part_number')}")
            print(f"  - Name: {created_part.get('name')}")
            print(f"  - Type: {created_part.get('part_type')}")
        else:
            print(f"❌ Part creation failed")
            print(f"Response text: {response.text}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw error response: {response.text}")
                
        # Test getting parts list to verify it's in the database
        print("\n3. Verifying part in database...")
        parts_response = requests.get(
            "http://localhost:8000/parts/?limit=5",
            headers=headers,
            timeout=10
        )
        
        if parts_response.status_code == 200:
            parts = parts_response.json()
            print(f"✅ Found {len(parts)} parts in database")
            for part in parts:
                print(f"  - {part.get('part_number')}: {part.get('name')}")
        else:
            print(f"❌ Failed to get parts list: {parts_response.status_code}")
                
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_part_creation()