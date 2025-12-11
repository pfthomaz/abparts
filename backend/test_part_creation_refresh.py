#!/usr/bin/env python3
"""
Test part creation and verify the count updates correctly
"""

import requests
import time

def test_part_creation_and_refresh():
    """Test creating a part and checking if the count updates."""
    
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
    
    # Get initial count
    print("\n📊 Getting initial parts count...")
    response = requests.get(
        "http://localhost:8000/parts/with-inventory?include_count=true&limit=1000",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get initial count: {response.status_code}")
        return
    
    initial_data = response.json()
    initial_count = initial_data.get('total_count', 0)
    print(f"📊 Initial parts count: {initial_count}")
    
    # Create a new part
    print("\n🔧 Creating a new test part...")
    timestamp = int(time.time() * 1000) % 1000000
    
    new_part = {
        "part_number": f"REFRESH-TEST-{timestamp}",
        "name": f"Refresh Test Part {timestamp}",
        "description": "Test part to verify refresh functionality",
        "part_type": "consumable",
        "is_proprietary": False,
        "unit_of_measure": "pieces"
    }
    
    create_response = requests.post(
        "http://localhost:8000/parts",
        headers=headers,
        json=new_part
    )
    
    if create_response.status_code == 201:
        created_part = create_response.json()
        print(f"✅ Created part: {created_part['part_number']}")
    else:
        print(f"❌ Failed to create part: {create_response.status_code} - {create_response.text}")
        return
    
    # Wait a moment for backend processing
    print("⏳ Waiting for backend processing...")
    time.sleep(0.5)
    
    # Get updated count
    print("\n📊 Getting updated parts count...")
    response = requests.get(
        f"http://localhost:8000/parts/with-inventory?include_count=true&limit=1000&_t={int(time.time() * 1000)}",
        headers=headers
    )
    
    if response.status_code == 200:
        updated_data = response.json()
        updated_count = updated_data.get('total_count', 0)
        print(f"📊 Updated parts count: {updated_count}")
        
        if updated_count > initial_count:
            print(f"🎉 SUCCESS: Count increased from {initial_count} to {updated_count}")
            print("✅ The refresh mechanism should work correctly in the frontend!")
        else:
            print(f"⚠️  WARNING: Count did not increase (was {initial_count}, now {updated_count})")
    else:
        print(f"❌ Failed to get updated count: {response.status_code}")

if __name__ == "__main__":
    test_part_creation_and_refresh()