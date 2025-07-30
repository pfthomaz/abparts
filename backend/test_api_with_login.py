#!/usr/bin/env python3
"""
Test script to verify the API works with the new Part model fields using login
"""

import sys
import requests
sys.path.append('/app')

def test_api_with_login():
    """Test the API with new Part model fields using login"""
    
    print("Testing API with New Part Fields (Login)")
    print("=" * 45)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Login to get token
    print("Test 1: Login with superadmin credentials")
    try:
        login_data = {
            "username": "superadmin",
            "password": "superadmin"
        }
        
        response = requests.post(f"{base_url}/token", data=login_data)
        print(f"Login Status Code: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Test 2: Get parts endpoint
    print("\nTest 2: GET /parts")
    try:
        response = requests.get(f"{base_url}/parts/", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            parts = response.json()
            print(f"✅ Retrieved {len(parts)} parts")
            
            if len(parts) > 0:
                sample_part = parts[0]
                print("Sample part fields:")
                for key, value in sample_part.items():
                    print(f"  - {key}: {value}")
                    
                # Check for new fields
                new_fields = ['manufacturer', 'part_code', 'serial_number']
                for field in new_fields:
                    if field in sample_part:
                        print(f"✅ New field '{field}' present: {sample_part[field]}")
                    else:
                        print(f"❌ New field '{field}' missing")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: Create a new part with new fields
    print("\nTest 3: POST /parts (create with new fields)")
    try:
        new_part_data = {
            "part_number": "API-TEST-001",
            "name": "API Test Part EN|Pieza de Prueba API ES",
            "description": "Test part created via API with new fields",
            "part_type": "consumable",
            "is_proprietary": False,
            "unit_of_measure": "pieces",
            "manufacturer": "API Test Manufacturer",
            "part_code": "API-001",
            "serial_number": "API-SN123456",
            "manufacturer_part_number": "API-MPN-001",
            "image_urls": [
                "https://example.com/api-image1.jpg",
                "https://example.com/api-image2.jpg"
            ]
        }
        
        response = requests.post(f"{base_url}/parts/", json=new_part_data, headers=headers)
        print(f"Create Status Code: {response.status_code}")
        
        if response.status_code == 201:
            created_part = response.json()
            print("✅ Part created successfully via API")
            print(f"   ID: {created_part.get('id')}")
            print(f"   Manufacturer: {created_part.get('manufacturer')}")
            print(f"   Part Code: {created_part.get('part_code')}")
            print(f"   Serial Number: {created_part.get('serial_number')}")
            
            # Store the ID for cleanup
            part_id = created_part.get('id')
            
        else:
            print(f"❌ Failed to create part: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 4: Clean up - delete the test part
    if 'part_id' in locals():
        print(f"\nTest 4: DELETE /parts/{part_id} (cleanup)")
        try:
            response = requests.delete(f"{base_url}/parts/{part_id}", headers=headers)
            print(f"Delete Status Code: {response.status_code}")
            
            if response.status_code == 204:
                print("✅ Test part deleted successfully")
            else:
                print(f"⚠️ Delete failed: {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
    
    print("\n" + "=" * 45)
    print("✅ API test with login completed successfully!")
    return True

if __name__ == "__main__":
    success = test_api_with_login()
    sys.exit(0 if success else 1)