#!/usr/bin/env python3
import requests
import json

# Test login endpoint
url = "http://localhost:8000/token"
data = {
    "username": "superadmin",
    "password": "superadmin"
}

try:
    response = requests.post(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ LOGIN SUCCESS!")
        token_data = response.json()
        print(f"Access Token: {token_data.get('access_token', 'N/A')}")
    else:
        print("❌ LOGIN FAILED!")
        
except Exception as e:
    print(f"❌ ERROR: {e}")