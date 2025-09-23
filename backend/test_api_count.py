#!/usr/bin/env python3
"""
Quick test to verify the API returns correct total count with include_count=true
"""

import requests
import json

def test_api_count():
    """Test the API count functionality."""
    
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
    
    # Test parts with inventory endpoint with count
    print("\n📊 Testing /parts/with-inventory with include_count=true...")
    
    response = requests.get(
        "http://localhost:8000/parts/with-inventory?include_count=true&limit=100",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API Response structure:")
        print(f"   - Items returned: {len(data.get('items', []))}")
        print(f"   - Total count: {data.get('total_count', 'Not provided')}")
        print(f"   - Has more: {data.get('has_more', 'Not provided')}")
        
        if data.get('total_count', 0) > 200:
            print("🎉 SUCCESS: Total count shows more than 200 parts!")
        else:
            print("⚠️  WARNING: Total count is not showing the expected value")
            
    else:
        print(f"❌ API request failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_api_count()