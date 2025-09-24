#!/usr/bin/env python3
"""
Basic test for image upload API without external dependencies
"""

import requests
import io

def test_basic_upload():
    """Test image upload with basic file data."""
    
    # Authenticate
    print("🔐 Authenticating...")
    auth_response = requests.post(
        "http://localhost:8000/token",
        data={"username": "superadmin", "password": "superadmin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if auth_response.status_code != 200:
        print(f"❌ Auth failed: {auth_response.status_code} - {auth_response.text}")
        return
    
    token = auth_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authenticated")
    
    # Create fake image data (just some bytes)
    fake_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
    
    # Upload the fake image
    files = {'file': ('test.png', io.BytesIO(fake_image_data), 'image/png')}
    
    print("📤 Testing upload endpoint...")
    try:
        response = requests.post(
            "http://localhost:8000/parts/upload-image",
            headers=headers,
            files=files,
            timeout=10
        )
        
        print(f"📊 Response status: {response.status_code}")
        print(f"📊 Response headers: {dict(response.headers)}")
        print(f"📊 Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Image URL: {data.get('url')}")
            
            # Test if the image is accessible
            image_url = f"http://localhost:8000{data.get('url')}"
            print(f"🔍 Testing image accessibility: {image_url}")
            
            img_response = requests.get(image_url, timeout=5)
            print(f"📊 Image access status: {img_response.status_code}")
            
        else:
            print(f"❌ Upload failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_basic_upload()