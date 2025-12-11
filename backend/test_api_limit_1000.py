#!/usr/bin/env python3
"""
Test API with limit=1000 to verify it returns all parts
"""

import requests

def test_api_with_high_limit():
    """Test the API with limit=1000."""
    
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
    
    # Test with limit=1000
    print("\n📊 Testing /parts/with-inventory with limit=1000...")
    
    response = requests.get(
        "http://localhost:8000/parts/with-inventory?include_count=true&limit=1000",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API Response with limit=1000:")
        print(f"   - Items returned: {len(data.get('items', []))}")
        print(f"   - Total count: {data.get('total_count', 'Not provided')}")
        print(f"   - Has more: {data.get('has_more', 'Not provided')}")
        
        items_returned = len(data.get('items', []))
        total_count = data.get('total_count', 0)
        
        if items_returned >= 500:
            print("🎉 SUCCESS: API returned 500+ parts!")
        elif items_returned == total_count:
            print(f"✅ GOOD: API returned all available parts ({items_returned})")
        else:
            print(f"⚠️  INFO: API returned {items_returned} out of {total_count} parts")
            
    else:
        print(f"❌ API request failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_api_with_high_limit()