#!/usr/bin/env python3
"""Quick test for stock adjustments feature"""

import requests
import sys

BASE_URL = "http://localhost:8000"

# Try different credentials
credentials = [
    ("admin@oraseas.com", "admin123"),
    ("admin@example.com", "admin123"),
    ("super@oraseas.com", "super123"),
]

print("=== Stock Adjustments Quick Test ===\n")

# Test 1: Find working credentials
print("Step 1: Finding working credentials...")
token = None
working_creds = None

for username, password in credentials:
    try:
        response = requests.post(
            f"{BASE_URL}/token",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            working_creds = (username, password)
            print(f"✅ Found working credentials: {username}")
            break
    except:
        pass

if not token:
    print("❌ Could not authenticate with any credentials")
    print("\nTried:")
    for u, _ in credentials:
        print(f"  - {u}")
    print("\nPlease check your database for valid admin credentials")
    sys.exit(1)

print()

# Test 2: List stock adjustments
print("Step 2: Testing GET /stock-adjustments...")
headers = {"Authorization": f"Bearer {token}"}

try:
    response = requests.get(f"{BASE_URL}/stock-adjustments", headers=headers)
    
    if response.status_code == 200:
        adjustments = response.json()
        print(f"✅ API working - Found {len(adjustments)} stock adjustments")
        
        if adjustments:
            print("\nRecent adjustments:")
            for adj in adjustments[:3]:
                print(f"  - {adj['adjustment_date'][:10]} | {adj['warehouse_name']} | {adj['adjustment_type']} | {adj['total_items_adjusted']} items")
    else:
        print(f"❌ API returned status {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print()

# Test 3: Get warehouses (needed for creating adjustments)
print("Step 3: Checking warehouses...")
try:
    response = requests.get(f"{BASE_URL}/warehouses", headers=headers)
    if response.status_code == 200:
        warehouses = response.json()
        print(f"✅ Found {len(warehouses)} warehouses")
    else:
        print(f"⚠️  Could not fetch warehouses (status {response.status_code})")
except Exception as e:
    print(f"⚠️  Error fetching warehouses: {e}")

print()

# Test 4: Get parts (needed for creating adjustments)
print("Step 4: Checking parts...")
try:
    response = requests.get(f"{BASE_URL}/parts", headers=headers)
    if response.status_code == 200:
        parts = response.json()
        print(f"✅ Found {len(parts)} parts")
    else:
        print(f"⚠️  Could not fetch parts (status {response.status_code})")
except Exception as e:
    print(f"⚠️  Error fetching parts: {e}")

print()
print("=" * 60)
print("✅ Stock Adjustments API is working!")
print("=" * 60)
print()
print("Next steps:")
print("1. Open http://localhost:3000 in your browser")
print(f"2. Login with: {working_creds[0]} / {working_creds[1]}")
print("3. Look for 'Stock Adjustments' in the Inventory menu")
print("4. Try creating a new adjustment")
print()
