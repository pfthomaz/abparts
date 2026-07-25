#!/usr/bin/env python3
"""
Test script to verify image upload functionality
"""

import requests
import json
import os
from io import BytesIO
from PIL import Image

# Create a simple test image
def create_test_image():
    """Create a simple test image in memory"""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    return img_bytes

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

def test_image_upload():
    """Test the image upload endpoint"""
    
    # First, let's test if we can access the API
    try:
        response = requests.get('http://localhost:8000/docs')
        print(f"✓ Backend API is accessible (status: {response.status_code})")
    except Exception as e:
        print(f"✗ Cannot access backend API: {e}")
        return False
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test the image upload endpoint
    try:
        # Create test image
        test_image = create_test_image()
        
        # Prepare the file for upload
        files = {
            'file': ('test_image.png', test_image, 'image/png')
        }
        
        # Make the upload request
        response = requests.post('http://localhost:8000/parts/upload-image', files=files, headers=headers)
        
        print(f"Upload response status: {response.status_code}")
        print(f"Upload response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Image upload successful!")
            print(f"  Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"✗ Image upload failed!")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error during image upload test: {e}")
        return False

def test_parts_endpoint():
    """Test if we can access the parts endpoint"""
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get('http://localhost:8000/parts/', headers=headers)
        print(f"Parts endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Parts endpoint is accessible")
            return True
        else:
            print(f"✗ Parts endpoint returned {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error accessing parts endpoint: {e}")
        return False

if __name__ == "__main__":
    print("=== Testing Image Upload Functionality ===")
    print()
    
    # Test basic connectivity
    print("1. Testing API connectivity...")
    parts_ok = test_parts_endpoint()
    print()
    
    # Test image upload
    print("2. Testing image upload...")
    upload_ok = test_image_upload()
    print()
    
    # Summary
    print("=== Test Summary ===")
    print(f"Parts endpoint: {'✓ OK' if parts_ok else '✗ FAILED'}")
    print(f"Image upload: {'✓ OK' if upload_ok else '✗ FAILED'}")
    
    if parts_ok and upload_ok:
        print("\n🎉 All tests passed! Image upload functionality is working.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")