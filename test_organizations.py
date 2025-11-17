#!/usr/bin/env python3
import requests
import json

# First login to get token
print("Logging in...")
login_response = requests.post(
    "http://localhost:8000/token",
    data={"username": "superadmin", "password": "superadmin"},
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
print(f"✅ Login successful! Token: {token[:20]}...")

# Test organizations endpoint
print("\nTesting organizations endpoint...")
headers = {"Authorization": f"Bearer {token}"}

try:
    response = requests.get("http://localhost:8000/organizations/", headers=headers)
    print(f"Organizations Status: {response.status_code}")
    
    if response.status_code == 200:
        organizations = response.json()
        print(f"✅ Organizations loaded successfully!")
        print(f"Found {len(organizations)} organizations:")
        for org in organizations:
            print(f"  - {org.get('name', 'Unknown')} ({org.get('organization_type', 'Unknown type')})")
    else:
        print(f"❌ Organizations failed: {response.text}")
        
except Exception as e:
    print(f"❌ Organizations error: {e}")