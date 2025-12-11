#!/usr/bin/env python3
"""
Test API limit validation to understand the 422 errors
"""

import requests

def test_api_limits():
    """Test different limit values to see what works."""
    
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
    
    # Test different limits
    limits_to_test = [100, 500, 1000, 1001, 10000]
    
    for limit in limits_to_test:
        print(f"\n📊 Testing limit={limit}...")
        
        response = requests.get(
            f"http://localhost:8000/parts/with-inventory?include_count=true&limit={limit}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            items_count = len(data.get('items', []))
            total_count = data.get('total_count', 'N/A')
            print(f"✅ SUCCESS: {items_count} items returned, total: {total_count}")
        else:
            print(f"❌ FAILED: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_api_limits()