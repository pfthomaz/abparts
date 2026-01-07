#!/usr/bin/env python3
"""
Test script to verify end-to-end part creation with images
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
            print(f"  Response: {login_response.text}")
            return None
    except Exception as e:
        print(f"✗ Error during authentication: {e}")
        return None

def create_test_image():
    """Create a simple test image in memory"""
    img = Image.new('RGB', (100, 100), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

def upload_test_image(token):
    """Upload a test image and return the URL"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Create test image
        test_image = create_test_image()
        
        # Prepare the file for upload
        files = {
            'file': ('test_part_image.png', test_image, 'image/png')
        }
        
        # Make the upload request
        response = requests.post('http://localhost:8000/parts/upload-image', files=files, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Image uploaded successfully")
            return result['url']
        else:
            print(f"✗ Image upload failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Error during image upload: {e}")
        return None

def create_part_with_image(token, image_url):
    """Create a part with the uploaded image"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    part_data = {
        "part_number": f"TEST-IMG-{int(time.time())}",
        "name": "Test Part with Image",
        "description": "A test part created to verify image functionality",
        "part_type": "consumable",
        "is_proprietary": False,
        "unit_of_measure": "pieces",
        "image_urls": [image_url]  # Include the uploaded image
    }
    
    try:
        response = requests.post('http://localhost:8000/parts/', json=part_data, headers=headers)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✓ Part created successfully with ID: {result['id']}")
            print(f"  Part number: {result['part_number']}")
            print(f"  Image URLs: {result.get('image_urls', [])}")
            return result
        else:
            print(f"✗ Part creation failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Error during part creation: {e}")
        return None

def verify_part_has_image(token, part_id):
    """Verify that the created part has the image"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f'http://localhost:8000/parts/{part_id}', headers=headers)
        
        if response.status_code == 200:
            part = response.json()
            image_urls = part.get('image_urls', [])
            
            if image_urls:
                print(f"✓ Part verification successful - has {len(image_urls)} image(s)")
                print(f"  Image URLs: {image_urls}")
                return True
            else:
                print(f"✗ Part verification failed - no images found")
                return False
        else:
            print(f"✗ Part retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Error during part verification: {e}")
        return False

def cleanup_test_part(token, part_id):
    """Clean up the test part"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f'http://localhost:8000/parts/{part_id}', headers=headers)
        
        if response.status_code in [200, 204]:
            print(f"✓ Test part cleaned up successfully")
        else:
            print(f"⚠️ Could not clean up test part: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️ Error during cleanup: {e}")

def main():
    print("=== Testing End-to-End Part Creation with Images ===")
    print()
    
    # Step 1: Authenticate
    print("1. Authenticating...")
    token = get_auth_token()
    if not token:
        return False
    print()
    
    # Step 2: Upload image
    print("2. Uploading test image...")
    image_url = upload_test_image(token)
    if not image_url:
        return False
    print()
    
    # Step 3: Create part with image
    print("3. Creating part with image...")
    part = create_part_with_image(token, image_url)
    if not part:
        return False
    print()
    
    # Step 4: Verify part has image
    print("4. Verifying part has image...")
    verification_success = verify_part_has_image(token, part['id'])
    print()
    
    # Step 5: Cleanup
    print("5. Cleaning up...")
    cleanup_test_part(token, part['id'])
    print()
    
    # Summary
    print("=== Test Summary ===")
    if verification_success:
        print("🎉 SUCCESS: End-to-end image functionality is working!")
        print("   - Images can be uploaded")
        print("   - Parts can be created with images")
        print("   - Images are properly saved and retrieved")
        return True
    else:
        print("❌ FAILED: Image functionality has issues")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)