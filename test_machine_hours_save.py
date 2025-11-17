#!/usr/bin/env python3
"""
Test script to reproduce machine hours saving error
"""
import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
USERNAME = "superadmin"
PASSWORD = "password123"

def login():
    """Login and get auth token"""
    response = requests.post(
        f"{API_BASE_URL}/token",
        data={
            "username": USERNAME,
            "password": PASSWORD
        }
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("access_token")
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None

def get_machines(token):
    """Get list of machines"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE_URL}/machines/", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get machines: {response.status_code}")
        print(response.text)
        return []

def save_machine_hours(token, machine_id, hours_value, notes=None):
    """Save machine hours"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "hours_value": hours_value,
        "notes": notes
    }
    
    print(f"\nAttempting to save machine hours:")
    print(f"  Machine ID: {machine_id}")
    print(f"  Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{API_BASE_URL}/machines/{machine_id}/hours",
        headers=headers,
        json=payload
    )
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 201:
        print("✅ Machine hours saved successfully!")
        return response.json()
    else:
        print("❌ Failed to save machine hours")
        return None

def main():
    print("=" * 60)
    print("Testing Machine Hours Save Functionality")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1. Logging in...")
    token = login()
    if not token:
        print("❌ Login failed. Exiting.")
        return
    print("✅ Login successful")
    
    # Step 2: Get machines
    print("\n2. Fetching machines...")
    machines = get_machines(token)
    if not machines:
        print("❌ No machines found. Exiting.")
        return
    
    print(f"✅ Found {len(machines)} machine(s)")
    for i, machine in enumerate(machines, 1):
        print(f"   {i}. {machine.get('name')} (ID: {machine.get('id')})")
    
    # Step 3: Save hours for first machine
    if machines:
        machine = machines[0]
        machine_id = machine.get('id')
        machine_name = machine.get('name')
        
        print(f"\n3. Saving hours for machine: {machine_name}")
        result = save_machine_hours(
            token=token,
            machine_id=machine_id,
            hours_value=1234.56,
            notes="Test hours entry from script"
        )
        
        if result:
            print("\n" + "=" * 60)
            print("SUCCESS: Machine hours saved successfully!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("FAILURE: Could not save machine hours")
            print("=" * 60)

if __name__ == "__main__":
    main()
