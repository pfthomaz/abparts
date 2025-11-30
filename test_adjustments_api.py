#!/usr/bin/env python3
"""Test the stock adjustments API"""

import requests
import sys

BASE_URL = "http://localhost:8000"

# Try to authenticate
credentials = [
    ("admin@oraseas.com", "admin123"),
    ("super@oraseas.com", "super123"),
]

print("=== Testing Stock Adjustments API ===\n")

token = None
for username, password in credentials:
    try:
        response = requests.post(
            f"{BASE_URL}/token",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✅ Authenticated as {username}")
            break
    except:
        pass

if not token:
    print("❌ Could not authenticate")
    sys.exit(1)

headers = {"Authorization": f"Bearer {token}"}

# Test the list endpoint
print("\n📋 Testing GET /stock-adjustments")
response = requests.get(f"{BASE_URL}/stock-adjustments", headers=headers)

print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

if response.status_code == 200:
    data = response.json()
    print(f"\n✅ Found {len(data)} adjustments")
    
    if data:
        print("\nFirst adjustment:")
        import json
        print(json.dumps(data[0], indent=2, default=str))
else:
    print(f"\n❌ Error: {response.status_code}")
    print(response.text)
