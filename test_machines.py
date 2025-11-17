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
print(f"✅ Login successful!")

# Test machines endpoint
print("\nTesting machines endpoint...")
headers = {"Authorization": f"Bearer {token}"}

try:
    response = requests.get("http://localhost:8000/machines/", headers=headers)
    print(f"Machines Status: {response.status_code}")
    
    if response.status_code == 200:
        machines = response.json()
        print(f"✅ Machines loaded successfully!")
        print(f"Found {len(machines)} machines:")
        for machine in machines:
            print(f"  - {machine.get('name', 'Unknown')} ({machine.get('model_type', 'Unknown model')})")
    else:
        print(f"❌ Machines failed: {response.text}")
        
except Exception as e:
    print(f"❌ Machines error: {e}")