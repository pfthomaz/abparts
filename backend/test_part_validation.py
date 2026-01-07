#!/usr/bin/env python3
"""
Test script to verify Part validation works correctly
"""

import sys
import requests
sys.path.append('/app')

def test_part_validation():
    """Test Part validation via API"""
    
    print("Testing Part Validation via API")
    print("=" * 35)
    
    base_url = "http://localhost:8000"
    
    # Get authentication token
    print("Getting authentication token...")
    try:
        login_data = {
            "username": "superadmin",
            "password": "superadmin"
        }
        
        response = requests.post(f"{base_url}/token", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            print("✅ Authentication successful")
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False
    
    # Test 1: Try to create part with too many images (should fail)
    print("\nTest 1: Create part with 21 images (should fail)")
    try:
        invalid_part_data = {
            "part_number": "INVALID-001",
            "name": "Invalid Part",
            "image_urls": [f"https://example.com/image{i}.jpg" for i in range(1, 22)]  # 21 images should fail
        }
        
        response = requests.post(f"{base_url}/parts/", json=invalid_part_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 422:  # Validation error
            print("✅ Correctly rejected part with 21 images")
            error_data = response.json()
            print(f"   Error: {error_data}")
        else:
            print(f"❌ Should have failed with validation error, got: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Try to create part with empty name (should fail)
    print("\nTest 2: Create part with empty name (should fail)")
    try:
        invalid_part_data = {
            "part_number": "INVALID-002",
            "name": "",  # Empty name should fail
            "part_type": "consumable"
        }
        
        response = requests.post(f"{base_url}/parts/", json=invalid_part_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 422:  # Validation error
            print("✅ Correctly rejected part with empty name")
            error_data = response.json()
            print(f"   Error: {error_data}")
        else:
            print(f"❌ Should have failed with validation error, got: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 3: Try to create part with invalid part type (should fail)
    print("\nTest 3: Create part with invalid part type (should fail)")
    try:
        invalid_part_data = {
            "part_number": "INVALID-003",
            "name": "Invalid Part Type",
            "part_type": "invalid_type"  # Invalid part type should fail
        }
        
        response = requests.post(f"{base_url}/parts/", json=invalid_part_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 422:  # Validation error
            print("✅ Correctly rejected part with invalid part type")
            error_data = response.json()
            print(f"   Error: {error_data}")
        else:
            print(f"❌ Should have failed with validation error, got: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 4: Create valid part with exactly 4 images (should succeed)
    print("\nTest 4: Create part with exactly 4 images (should succeed)")
    try:
        valid_part_data = {
            "part_number": "VALID-001",
            "name": "Valid Part with 4 Images",
            "part_type": "bulk_material",
            "manufacturer": "Test Manufacturer",
            "part_code": "VALID-001",
            "serial_number": "VALID-SN123",
            "image_urls": [
                "https://example.com/image1.jpg",
                "https://example.com/image2.jpg",
                "https://example.com/image3.jpg",
                "https://example.com/image4.jpg"
            ]
        }
        
        response = requests.post(f"{base_url}/parts/", json=valid_part_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            created_part = response.json()
            print("✅ Successfully created part with 4 images")
            print(f"   ID: {created_part.get('id')}")
            print(f"   Images: {len(created_part.get('image_urls', []))} images")
            
            # Clean up
            part_id = created_part.get('id')
            if part_id:
                delete_response = requests.delete(f"{base_url}/parts/{part_id}", headers=headers)
                if delete_response.status_code == 204:
                    print("✅ Test part cleaned up successfully")
                    
        else:
            print(f"❌ Should have succeeded, got: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "=" * 35)
    print("✅ Part validation test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_part_validation()
    sys.exit(0 if success else 1)