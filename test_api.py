#!/usr/bin/env python3
import requests
import json

# Test health endpoint first
print("Testing health endpoint...")
try:
    response = requests.get("http://localhost:8000/health")
    print(f"Health Status: {response.status_code}")
    print(f"Health Response: {response.text}")
except Exception as e:
    print(f"Health check failed: {e}")

print("\n" + "="*50 + "\n")

# Test login endpoint
print("Testing login endpoint...")
url = "http://localhost:8000/token"
data = {
    "username": "superadmin",
    "password": "superadmin"
}

try:
    response = requests.post(url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    print(f"Login Status Code: {response.status_code}")
    print(f"Login Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ LOGIN SUCCESS!")
        token_data = response.json()
        print(f"Access Token: {token_data.get('access_token', 'N/A')}")
    else:
        print("❌ LOGIN FAILED!")
        
except Exception as e:
    print(f"❌ LOGIN ERROR: {e}")