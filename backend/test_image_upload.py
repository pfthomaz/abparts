#!/usr/bin/env python3
"""
Test image upload functionality
"""

import requests
import os
import tempfile
from PIL import Image

def create_test_image():
    """Create a simple test image."""
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img.save(temp_file.name, 'PNG')
    return temp_file.name

def test_image_upload():
    """Test the image upload API endpoint."""
    
    # Test authentication
    print("🔐 Authenticating...")
    auth_response = requests.post(
        "http://localhost:8000/token",
        data={"username": "superadmin", "password": "superadmin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if auth_response.status_code != 200:
        print(f"❌ Authentication failed: {auth_response.status_code}")
        return
    
    token = auth_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Authentication successful")
    
    # Create a test image
    print("\n📷 Creating test image...")
    test_image_path = create_test_image()
    
    try:
        # Test image upload
        print("📤 Testing image upload...")
        
        with open(test_image_path, 'rb') as image_file:
            files = {'file': ('test_image.png', image_file, 'image/png')}
            
            response = requests.post(
                "http://localhost:8000/parts/upload-image",
                headers=headers,
                files=files
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful!")
            print(f"   - Image URL: {data.get('url')}")
            print(f"   - Message: {data.get('message', 'N/A')}")
            
            # Test if the uploaded image is accessible
            image_url = f"http://localhost:8000{data.get('url')}"
            image_response = requests.get(image_url)
            
            if image_response.status_code == 200:
                print(f"✅ Image is accessible at: {image_url}")
            else:
                print(f"⚠️  Image upload succeeded but image not accessible: {image_response.status_code}")
                
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    finally:
        # Clean up test image
        if os.path.exists(test_image_path):
            os.unlink(test_image_path)

if __name__ == "__main__":
    test_image_upload()