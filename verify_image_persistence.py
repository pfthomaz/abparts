#!/usr/bin/env python3
"""
Verify that images are being saved and retrieved correctly
"""

import requests
import json

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

def check_recent_parts_with_images():
    """Check if recent parts have images saved"""
    token = get_auth_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Get recent parts
        response = requests.get('http://localhost:8000/parts/?limit=10', headers=headers)
        
        if response.status_code != 200:
            print(f"✗ Failed to get parts: {response.status_code}")
            return
        
        parts = response.json()
        
        # Handle different response formats
        if isinstance(parts, dict) and 'items' in parts:
            parts = parts['items']
        elif not isinstance(parts, list):
            print(f"✗ Unexpected response format: {type(parts)}")
            print(f"Response: {parts}")
            return
        
        print("=== Recent Parts with Images ===")
        print()
        
        parts_with_images = 0
        
        for part in parts:
            image_urls = part.get('image_urls', [])
            if image_urls:
                parts_with_images += 1
                print(f"✅ Part: {part['part_number']} - {part['name']}")
                print(f"   ID: {part['id']}")
                print(f"   Images: {len(image_urls)} image(s)")
                print(f"   First image: {image_urls[0][:50]}..." if image_urls else "   No images")
                print()
        
        print(f"Summary: {parts_with_images} out of {len(parts)} parts have images")
        
        if parts_with_images == 0:
            print("❌ No parts found with images - there might be a persistence issue")
        else:
            print("✅ Images are being saved correctly!")
            
    except Exception as e:
        print(f"✗ Error checking parts: {e}")

def check_specific_part(part_number):
    """Check a specific part by part number"""
    token = get_auth_token()
    if not token:
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Search for the specific part
        response = requests.get(f'http://localhost:8000/parts/?limit=100', headers=headers)
        
        if response.status_code != 200:
            print(f"✗ Failed to get parts: {response.status_code}")
            return
        
        parts = response.json()
        
        # Handle different response formats
        if isinstance(parts, dict) and 'items' in parts:
            parts = parts['items']
        elif not isinstance(parts, list):
            print(f"✗ Unexpected response format: {type(parts)}")
            print(f"Response: {parts}")
            return
        
        # Find the part
        target_part = None
        for part in parts:
            if part['part_number'] == part_number:
                target_part = part
                break
        
        if not target_part:
            print(f"❌ Part '{part_number}' not found")
            return
        
        print(f"=== Part Details: {part_number} ===")
        print(f"ID: {target_part['id']}")
        print(f"Name: {target_part['name']}")
        print(f"Description: {target_part.get('description', 'N/A')}")
        
        image_urls = target_part.get('image_urls', [])
        print(f"Images: {len(image_urls)} image(s)")
        
        if image_urls:
            print("✅ Images found:")
            for i, url in enumerate(image_urls, 1):
                print(f"  {i}. {url[:50]}...")
        else:
            print("❌ No images found for this part")
            
    except Exception as e:
        print(f"✗ Error checking part: {e}")

if __name__ == "__main__":
    print("=== Verifying Image Persistence ===")
    print()
    
    # Check recent parts
    check_recent_parts_with_images()
    print()
    
    # Check the specific part you were working with
    print("Checking specific part 'HPW-002'...")
    check_specific_part('HPW-002')