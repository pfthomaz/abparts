#!/usr/bin/env python3
"""
Simple test for image upload API
"""

import requests
import io
from PIL import Image

def test_simple_upload():
    """Test image upload with a simple in-memory image."""
    
    # Authenticate
    auth_response = requests.post(
        "http://localhost:8000/token",
        data={"username": "superadmin", "password": "superadmin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if auth_response.status_code != 200:
        print(f"❌ Auth failed: {auth_response.status_code}")
        return
    
    token = auth_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authenticated")
    
    # Create a simple image in memory
    img = Image.new('RGB', (50, 50), color='blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Upload the image
    files = {'file': ('test.png', img_bytes, 'image/png')}
    
    print("📤 Uploading image...")
    response = requests.post(
        "http://localhost:8000/parts/upload-image",
        headers=headers,
        files=files
    )
    
    print(f"📊 Response status: {response.status_code}")
    print(f"📊 Response body: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Image URL: {data.get('url')}")
    else:
        print(f"❌ Failed: {response.status_code}")

if __name__ == "__main__":
    test_simple_upload()