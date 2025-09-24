#!/usr/bin/env python3
"""
Test to simulate frontend upload behavior
"""

import requests
import io

def test_frontend_upload_simulation():
    """Simulate the exact upload process the frontend should do."""
    
    # Authenticate
    print("🔐 Authenticating...")
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
    
    # Create a simple test image (1x1 PNG)
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc\xf8\x00\x00\x00\x01\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
    
    # Test upload exactly as frontend would do it
    files = {'file': ('test-image.png', io.BytesIO(png_data), 'image/png')}
    
    print("📤 Testing upload (simulating frontend)...")
    try:
        response = requests.post(
            "http://localhost:8000/parts/upload-image",
            headers=headers,
            files=files,
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        print(f"📊 Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            image_url = data.get('url')
            print(f"✅ Upload successful!")
            print(f"🖼️  Image URL: {image_url}")
            
            # Test image accessibility
            full_url = f"http://localhost:8000{image_url}"
            img_response = requests.get(full_url)
            print(f"🔍 Image accessible: {img_response.status_code == 200}")
            
            return True
        else:
            print(f"❌ Upload failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_frontend_upload_simulation()
    if success:
        print("\n🎉 Frontend upload simulation successful!")
        print("The backend is ready for frontend image uploads.")
    else:
        print("\n❌ Frontend upload simulation failed!")
        print("There may be an issue with the upload endpoint.")