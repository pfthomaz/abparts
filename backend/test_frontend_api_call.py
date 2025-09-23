#!/usr/bin/env python3
"""
Test the exact API call that the frontend should be making
"""

import requests

def test_frontend_api_call():
    """Test the API call with the exact parameters the frontend uses."""
    
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
    
    # Test the exact call the frontend should make
    print("\n📊 Testing frontend API call...")
    print("URL: /parts/with-inventory?include_count=true&limit=1000")
    
    response = requests.get(
        "http://localhost:8000/parts/with-inventory?include_count=true&limit=1000",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
        total_count = data.get('total_count', 0)
        has_more = data.get('has_more', False)
        
        print(f"✅ SUCCESS!")
        print(f"   - Status: {response.status_code}")
        print(f"   - Items returned: {len(items)}")
        print(f"   - Total count: {total_count}")
        print(f"   - Has more: {has_more}")
        print(f"   - Response structure: {list(data.keys())}")
        
        if len(items) >= 500:
            print("🎉 PERFECT: Frontend should now see 500+ parts!")
        else:
            print(f"⚠️  WARNING: Only {len(items)} parts returned")
            
    else:
        print(f"❌ FAILED: {response.status_code}")
        print(f"   Response: {response.text}")

if __name__ == "__main__":
    test_frontend_api_call()