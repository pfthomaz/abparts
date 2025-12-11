#!/usr/bin/env python3
"""
Debug script to test login and see the actual error
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_login():
    """Test login endpoint"""
    print("Testing login endpoint...")
    
    # Try to login
    response = requests.post(
        f"{API_URL}/token",
        data={
            "username": "admin",  # Change to your test username
            "password": "admin123"  # Change to your test password
        }
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"\n✓ Login successful! Token: {token[:50]}...")
        
        # Try to get user info
        print("\nTesting /users/me endpoint...")
        me_response = requests.get(
            f"{API_URL}/users/me/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        print(f"Status Code: {me_response.status_code}")
        print(f"Response: {me_response.text}")
        
    else:
        print(f"\n✗ Login failed!")
        try:
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            pass

if __name__ == "__main__":
    test_login()
