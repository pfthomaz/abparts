#!/usr/bin/env python3
"""
Test production image functionality after deployment
"""

import requests
import json
import uuid
from datetime import datetime

def test_production_api():
    """Test production API endpoints"""
    
    # Production API base URL
    base_url = "http://46.62.153.166:8000"
    
    print("=== Testing Production Image Functionality ===")
    print(f"API Base URL: {base_url}")
    print(f"Test Time: {datetime.now()}")
    print()
    
    try:
        # Test 1: Login
        print("1. Testing Login...")
        login_data = {
            "username": "dthomaz",
            "password": "amFT1999!"
        }
        
        response = requests.post(f"{base_url}/token", data=login_data, timeout=10)
        print(f"   Login Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ Login failed: {response.text}")
            return False
            
        token_data = response.json()
        token = token_data.get("access_token")
        print(f"   ✅ Login successful")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 2: Parts API with inventory
        print("\n2. Testing Parts API...")
        parts_response = requests.get(f"{base_url}/parts/with-inventory?limit=5&include_count=true", 
                                    headers=headers, timeout=10)
        print(f"   Parts API Status: {parts_response.status_code}")
        
        if parts_response.status_code != 200:
            print(f"   ❌ Parts API failed: {parts_response.text}")
            return False
            
        parts_data = parts_response.json()
        items = parts_data.get('items', [])
        total_count = parts_data.get('total_count', 0)
        
        print(f"   ✅ Parts API working")
        print(f"   📊 Total parts: {total_count}")
        print(f"   📋 Retrieved: {len(items)} parts")
        
        # Test 3: Check parts sorting (newest first)
        print("\n3. Testing Parts Sorting...")
        if len(items) >= 2:
            first_part_date = items[0].get('created_at', '')
            second_part_date = items[1].get('created_at', '')
            
            if first_part_date >= second_part_date:
                print(f"   ✅ Parts correctly sorted by creation date (newest first)")
            else:
                print(f"   ⚠️  Parts sorting may be incorrect")
                print(f"      First: {first_part_date}")
                print(f"      Second: {second_part_date}")
        else:
            print(f"   ℹ️  Not enough parts to test sorting")
        
        # Test 4: Check image functionality
        print("\n4. Testing Image Data...")
        parts_with_images = 0
        total_images = 0
        
        for i, part in enumerate(items[:5]):  # Check first 5 parts
            part_number = part.get('part_number', 'Unknown')
            part_name = part.get('name', 'Unknown')
            image_urls = part.get('image_urls', [])
            image_count = len(image_urls) if image_urls else 0
            
            print(f"   📦 {part_number}: {part_name}")
            print(f"      Images: {image_count}")
            
            if image_count > 0:
                parts_with_images += 1
                total_images += image_count
                
                # Check if images are base64 data URLs or regular URLs
                first_image = image_urls[0]
                if first_image.startswith('data:image/'):
                    print(f"      Type: Base64 data URL")
                elif first_image.startswith('http'):
                    print(f"      Type: HTTP URL")
                else:
                    print(f"      Type: Unknown format")
        
        print(f"\n   📊 Summary:")
        print(f"      Parts with images: {parts_with_images}")
        print(f"      Total images: {total_images}")
        
        if parts_with_images > 0:
            print(f"   ✅ Image functionality appears to be working")
        else:
            print(f"   ⚠️  No parts with images found (may be normal if no images uploaded)")
        
        # Test 5: Create a simple test part (optional)
        print("\n5. Testing Part Creation...")
        test_part_data = {
            "part_number": f"PROD-TEST-{str(uuid.uuid4())[:8]}",
            "name": "Production Test Part",
            "description": "Test part created to verify production functionality",
            "part_type": "consumable",
            "is_proprietary": False,
            "unit_of_measure": "pieces",
            "manufacturer": "Test Manufacturer",
            "image_urls": []  # No images for this test
        }
        
        create_response = requests.post(f"{base_url}/parts/", json=test_part_data, 
                                      headers=headers, timeout=10)
        print(f"   Create Status: {create_response.status_code}")
        
        if create_response.status_code in [200, 201]:
            created_part = create_response.json()
            print(f"   ✅ Part creation successful")
            print(f"      ID: {created_part.get('id')}")
            print(f"      Part Number: {created_part.get('part_number')}")
            
            # Verify it appears in the list
            print("\n6. Verifying New Part in List...")
            verify_response = requests.get(f"{base_url}/parts/with-inventory?limit=3", 
                                         headers=headers, timeout=10)
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                recent_parts = verify_data.get('items', [])
                
                # Check if our test part is in the first few results
                found = False
                for part in recent_parts:
                    if part.get('part_number') == test_part_data['part_number']:
                        print(f"   ✅ New part found at top of list")
                        found = True
                        break
                
                if not found:
                    print(f"   ⚠️  New part not found in recent results")
                    print(f"      This may indicate sorting issues")
            else:
                print(f"   ❌ Failed to verify new part: {verify_response.status_code}")
        else:
            print(f"   ❌ Part creation failed: {create_response.text}")
        
        print(f"\n=== Production Test Complete ===")
        return True
        
    except requests.exceptions.Timeout:
        print(f"❌ Request timeout - production server may be slow or down")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - cannot reach production server")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_frontend_access():
    """Test if frontend is accessible"""
    print("\n=== Testing Frontend Access ===")
    
    try:
        frontend_url = "http://46.62.153.166:3001"
        response = requests.get(frontend_url, timeout=10)
        print(f"Frontend Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Frontend accessible at {frontend_url}")
            return True
        else:
            print(f"⚠️  Frontend returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Production Image Functionality Test")
    print("=" * 50)
    
    # Test API
    api_success = test_production_api()
    
    # Test Frontend
    frontend_success = test_frontend_access()
    
    print("\n" + "=" * 50)
    print("📋 FINAL RESULTS:")
    print(f"   API Tests: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"   Frontend: {'✅ PASS' if frontend_success else '❌ FAIL'}")
    
    if api_success and frontend_success:
        print("\n🎉 Production image functionality appears to be working!")
        print("\n📝 Next Steps:")
        print("   1. Login to production frontend")
        print("   2. Test creating parts with images")
        print("   3. Verify images display correctly")
    else:
        print("\n⚠️  Issues detected. Check the deployment and logs.")
        print("\n🔍 Debugging:")
        print("   - Check container logs: docker-compose -f docker-compose.prod.yml logs")
        print("   - Verify containers are running: docker-compose -f docker-compose.prod.yml ps")
        print("   - Check database connectivity")