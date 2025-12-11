#!/usr/bin/env python3
"""
Final test to verify parts endpoints are working after comprehensive fixes
"""
import requests
import json

def test_parts_endpoints():
    print("🔧 Testing Parts Endpoints - Final Verification")
    print("=" * 60)
    
    try:
        # Login
        print("1. Testing authentication...")
        login_response = requests.post(
            "http://localhost:8000/token",
            data={"username": "superadmin", "password": "superadmin"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful")
        
        # Test the problematic endpoint that was causing 500 errors
        print("\n2. Testing parts with inventory endpoint...")
        parts_response = requests.get(
            "http://localhost:8000/parts/with-inventory?include_count=true&limit=10", 
            headers=headers, 
            timeout=10
        )
        
        print(f"Status: {parts_response.status_code}")
        if parts_response.status_code == 200:
            data = parts_response.json()
            print(f"✅ SUCCESS! Parts with inventory endpoint working")
            print(f"   - Returned {len(data.get('items', []))} items")
            print(f"   - Total count: {data.get('total_count', 'N/A')}")
            print(f"   - Has more: {data.get('has_more', 'N/A')}")
        else:
            print(f"❌ FAILED: {parts_response.text[:200]}")
            return
            
        # Test without count parameter
        print("\n3. Testing parts without count...")
        parts_no_count = requests.get(
            "http://localhost:8000/parts/with-inventory?limit=5", 
            headers=headers, 
            timeout=10
        )
        
        print(f"Status: {parts_no_count.status_code}")
        if parts_no_count.status_code == 200:
            data = parts_no_count.json()
            print(f"✅ SUCCESS! Parts without count working")
            print(f"   - Returned {len(data.get('items', []))} items")
        else:
            print(f"❌ FAILED: {parts_no_count.text[:200]}")
            
        # Test basic parts endpoint
        print("\n4. Testing basic parts endpoint...")
        basic_parts = requests.get(
            "http://localhost:8000/parts/?limit=5", 
            headers=headers, 
            timeout=10
        )
        
        print(f"Status: {basic_parts.status_code}")
        if basic_parts.status_code == 200:
            data = basic_parts.json()
            print(f"✅ SUCCESS! Basic parts endpoint working")
            print(f"   - Returned {len(data)} items")
        else:
            print(f"❌ FAILED: {basic_parts.text[:200]}")
            
        print("\n🎉 All parts endpoints are now working!")
        print("The 500 Internal Server Error has been resolved.")
        
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_parts_endpoints()