#!/usr/bin/env python3
"""
Debug script to test the exact flow the frontend should be using
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
            print("✓ Authentication successful")
            return token
        else:
            print(f"✗ Authentication failed: {login_response.status_code}")
            return None
    except Exception as e:
        print(f"✗ Error during authentication: {e}")
        return None

def create_test_image():
    """Create a simple test image in memory"""
    img = Image.new('RGB', (100, 100), color='green')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def test_frontend_flow():
    """Test the exact flow the frontend should be using"""
    print("=== Testing Frontend Image Flow ===")
    print()
    
    # Step 1: Get auth token
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Upload image (what PartPhotoGallery does)
    print("1. Testing image upload (PartPhotoGallery)...")
    test_image = create_test_image()
    files = {'file': ('test_frontend_image.png', test_image, 'image/png')}
    
    upload_response = requests.post('http://localhost:8000/parts/upload-image', files=files, headers=headers)
    
    if upload_response.status_code != 200:
        print(f"✗ Image upload failed: {upload_response.status_code}")
        print(f"  Response: {upload_response.text}")
        return False
    
    image_url = upload_response.json()['url']
    print(f"✓ Image uploaded successfully")
    print(f"  Image URL: {image_url[:50]}...")
    print()
    
    # Step 3: Create part with image (what PartForm does)
    print("2. Testing part creation with image (PartForm)...")
    
    part_data = {
        "part_number": f"FRONTEND-TEST-{int(time.time())}",
        "name": "Frontend Test Part",
        "description": "Testing frontend image flow",
        "part_type": "consumable",
        "is_proprietary": False,
        "unit_of_measure": "pieces",
        "image_urls": [image_url]  # This is what PartForm should send
    }
    
    headers_json = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    create_response = requests.post('http://localhost:8000/parts/', json=part_data, headers=headers_json)
    
    if create_response.status_code != 201:
        print(f"✗ Part creation failed: {create_response.status_code}")
        print(f"  Response: {create_response.text}")
        return False
    
    part = create_response.json()
    print(f"✓ Part created successfully")
    print(f"  Part ID: {part['id']}")
    print(f"  Part Number: {part['part_number']}")
    print(f"  Image URLs in response: {part.get('image_urls', [])}")
    print()
    
    # Step 4: Verify part retrieval (what happens when you view the part)
    print("3. Testing part retrieval...")
    
    get_response = requests.get(f'http://localhost:8000/parts/{part["id"]}', headers=headers)
    
    if get_response.status_code != 200:
        print(f"✗ Part retrieval failed: {get_response.status_code}")
        return False
    
    retrieved_part = get_response.json()
    retrieved_images = retrieved_part.get('image_urls', [])
    
    print(f"✓ Part retrieved successfully")
    print(f"  Retrieved image URLs: {retrieved_images}")
    
    if retrieved_images and image_url in retrieved_images:
        print("✓ Image URL correctly saved and retrieved!")
        success = True
    else:
        print("✗ Image URL not found in retrieved part!")
        success = False
    
    print()
    
    # Step 5: Cleanup
    print("4. Cleaning up...")
    delete_response = requests.delete(f'http://localhost:8000/parts/{part["id"]}', headers=headers)
    if delete_response.status_code in [200, 204]:
        print("✓ Test part cleaned up")
    else:
        print(f"⚠️ Could not clean up test part: {delete_response.status_code}")
    
    return success

def main():
    success = test_frontend_flow()
    
    print()
    print("=== Summary ===")
    if success:
        print("🎉 Frontend flow test PASSED!")
        print("The backend is working correctly.")
        print("If images still don't work in the browser, the issue is in the frontend JavaScript.")
    else:
        print("❌ Frontend flow test FAILED!")
        print("There's an issue with the backend API.")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)