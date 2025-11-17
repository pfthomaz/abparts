#!/usr/bin/env python3
"""
Final test for part creation after schema and CRUD fixes
"""
import requests
import json

def test_part_creation():
    print("🔧 Testing Part Creation - Final Fix")
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
        
        # Test part creation with only valid fields (no manufacturer, part_code, serial_number)
        print("\n2. Testing part creation with valid fields only...")
        part_data = {
            "part_number": "TEST-FINAL-001",
            "name": "Test Filter Bag",
            "description": "Final test part creation",
            "part_type": "consumable",
            "is_proprietary": False,
            "unit_of_measure": "pieces",
            "manufacturer_part_number": "MPN-001",
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
            
            # Test with invalid fields to ensure they're rejected
            print("\n3. Testing with invalid fields (should fail)...")
            invalid_part_data = {
                "part_number": "TEST-INVALID-001",
                "name": "Invalid Test Part",
                "description": "Should fail",
                "part_type": "consumable",
                "is_proprietary": False,
                "unit_of_measure": "pieces",
                "manufacturer": "Should be rejected",  # This field should be rejected
                "part_code": "Should be rejected",     # This field should be rejected
                "image_urls": []
            }
            
            invalid_response = requests.post(
                "http://localhost:8000/parts/",
                json=invalid_part_data,
                headers=headers,
                timeout=10
            )
            
            if invalid_response.status_code == 422:
                print("✅ Invalid fields properly rejected (422 Validation Error)")
            elif invalid_response.status_code == 400:
                print("✅ Invalid fields properly rejected (400 Bad Request)")
            else:
                print(f"⚠️  Unexpected response for invalid fields: {invalid_response.status_code}")
                print(f"Response: {invalid_response.text}")
                
        else:
            print(f"❌ Part creation failed")
            print(f"Response text: {response.text}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw error response: {response.text}")
                
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_part_creation()