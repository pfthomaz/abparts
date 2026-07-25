#!/usr/bin/env python3
"""
Test updating an existing part with images
"""

import requests
import json
import time
from io import BytesIO
from PIL import Image

def get_auth_token():
    """Get authentication token"""
    try:
        login_response = requests.post(
            "http://localhost:8000/token",
            data={"username": "dthomaz", "password": "amFT1999!"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            return token
        else:
            print(f"✗ Authentication failed: {login_response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Error during authentication: {e}")
        return None

def create_test_image():
    """Create a simple test image in memory"""
    img = Image.new('RGB', (100, 100), color='orange')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def test_update_existing_part():
    """Test updating an existing part with images"""
    print("=== Testing Update Existing Part with Images ===")
    print()
    
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    headers_json = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    try:
        # Step 1: Create a part without images first
        print("1. Creating initial part without images...")
        initial_part_data = {
            "part_number": f"UPDATE-TEST-{int(time.time())}",
            "name": "Update Test Part",
            "description": "Testing update with images",
            "part_type": "consumable",
            "is_proprietary": False,
            "unit_of_measure": "pieces",
            "image_urls": []  # No images initially
        }
        
        create_response = requests.post('http://localhost:8000/parts/', json=initial_part_data, headers=headers_json)
        
        if create_response.status_code != 201:
            print(f"✗ Failed to create initial part: {create_response.status_code}")
            print(f"  Response: {create_response.text}")
            return False
        
        part = create_response.json()
        part_id = part['id']
        print(f"✓ Created initial part: {part['part_number']} (ID: {part_id})")
        print(f"  Initial images: {part.get('image_urls', [])}")
        print()
        
        # Step 2: Upload an image
        print("2. Uploading image...")
        test_image = create_test_image()
        files = {'file': ('update_test_image.png', test_image, 'image/png')}
        
        upload_response = requests.post('http://localhost:8000/parts/upload-image', files=files, headers=headers)
        
        if upload_response.status_code != 200:
            print(f"✗ Image upload failed: {upload_response.status_code}")
            return False
        
        image_url = upload_response.json()['url']
        print(f"✓ Image uploaded successfully")
        print(f"  Image URL: {image_url[:50]}...")
        print()
        
        # Step 3: Update the part with the image
        print("3. Updating part with image...")
        update_data = {
            "name": "Updated Test Part with Image",
            "description": "Updated description with image",
            "image_urls": [image_url]  # Add the image
        }
        
        update_response = requests.put(f'http://localhost:8000/parts/{part_id}', json=update_data, headers=headers_json)
        
        if update_response.status_code != 200:
            print(f"✗ Part update failed: {update_response.status_code}")
            print(f"  Response: {update_response.text}")
            return False
        
        updated_part = update_response.json()
        print(f"✓ Part updated successfully")
        print(f"  Updated name: {updated_part['name']}")
        print(f"  Updated images: {len(updated_part.get('image_urls', []))} image(s)")
        print()
        
        # Step 4: Retrieve the part to verify the update
        print("4. Verifying updated part...")
        get_response = requests.get(f'http://localhost:8000/parts/{part_id}', headers=headers)
        
        if get_response.status_code != 200:
            print(f"✗ Failed to retrieve updated part: {get_response.status_code}")
            return False
        
        retrieved_part = get_response.json()
        retrieved_images = retrieved_part.get('image_urls', [])
        
        print(f"✓ Retrieved updated part")
        print(f"  Name: {retrieved_part['name']}")
        print(f"  Description: {retrieved_part['description']}")
        print(f"  Images: {len(retrieved_images)} image(s)")
        
        if retrieved_images and image_url in retrieved_images:
            print("✓ Image successfully saved in update!")
            success = True
        else:
            print("✗ Image not found in updated part!")
            print(f"  Expected: {image_url[:50]}...")
            print(f"  Got: {retrieved_images}")
            success = False
        
        print()
        
        # Step 5: Cleanup
        print("5. Cleaning up...")
        delete_response = requests.delete(f'http://localhost:8000/parts/{part_id}', headers=headers)
        if delete_response.status_code in [200, 204]:
            print("✓ Test part cleaned up")
        else:
            print(f"⚠️ Could not clean up test part: {delete_response.status_code}")
        
        return success
        
    except Exception as e:
        print(f"✗ Error during update test: {e}")
        return False

if __name__ == "__main__":
    success = test_update_existing_part()
    
    print()
    print("=== Summary ===")
    if success:
        print("🎉 UPDATE test PASSED!")
        print("Part updates with images work correctly.")
    else:
        print("❌ UPDATE test FAILED!")
        print("There's an issue with updating parts with images.")
    
    exit(0 if success else 1)