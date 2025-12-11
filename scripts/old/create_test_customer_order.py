#!/usr/bin/env python3
"""Create a test customer order for testing the workflow."""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def create_test_order():
    """Create a test customer order."""
    
    print("=" * 60)
    print("Creating Test Customer Order")
    print("=" * 60)
    
    # Step 1: Login as a customer admin (BossServ Cyprus)
    print("\n1. Logging in as BossServ Cyprus admin...")
    login_response = requests.post(
        f"{BASE_URL}/login",
        data={
            "username": "bossserv_cyprus_admin",
            "password": "admin123"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print("   Note: You may need to create this user first")
        print("   Or use a different customer user")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Logged in successfully")
    
    # Step 2: Get organizations to find IDs
    print("\n2. Fetching organizations...")
    orgs_response = requests.get(f"{BASE_URL}/organizations", headers=headers)
    orgs = orgs_response.json()
    
    # Find Oraseas EE and customer org
    oraseas_org = next((org for org in orgs if 'Oraseas' in org['name'] or 'BossServ LLC' in org['name']), None)
    customer_org = next((org for org in orgs if org['organization_type'] == 'customer'), None)
    
    if not oraseas_org or not customer_org:
        print("❌ Could not find required organizations")
        return
    
    print(f"✅ Found Oraseas EE: {oraseas_org['name']}")
    print(f"✅ Found Customer: {customer_org['name']}")
    
    # Step 3: Get parts
    print("\n3. Fetching parts...")
    parts_response = requests.get(f"{BASE_URL}/parts", headers=headers)
    parts_data = parts_response.json()
    parts = parts_data.get('items', parts_data) if isinstance(parts_data, dict) else parts_data
    
    if not parts or len(parts) == 0:
        print("❌ No parts found in the system")
        return
    
    print(f"✅ Found {len(parts)} parts")
    
    # Step 4: Create customer order
    print("\n4. Creating customer order...")
    order_data = {
        "customer_organization_id": customer_org['id'],
        "oraseas_organization_id": oraseas_org['id'],
        "order_date": datetime.now().isoformat(),
        "expected_delivery_date": (datetime.now() + timedelta(days=7)).isoformat(),
        "status": "Requested",
        "notes": "Test order created by script"
    }
    
    order_response = requests.post(
        f"{BASE_URL}/customer_orders",
        headers=headers,
        json=order_data
    )
    
    if order_response.status_code != 201:
        print(f"❌ Failed to create order: {order_response.status_code}")
        print(order_response.text)
        return
    
    order = order_response.json()
    print(f"✅ Order created: {order['id']}")
    
    # Step 5: Add order items
    print("\n5. Adding order items...")
    for i, part in enumerate(parts[:2]):  # Add first 2 parts
        item_data = {
            "customer_order_id": order['id'],
            "part_id": part['id'],
            "quantity": (i + 1) * 5,
            "unit_price": 10.00 + (i * 5)
        }
        
        item_response = requests.post(
            f"{BASE_URL}/customer_order_items",
            headers=headers,
            json=item_data
        )
        
        if item_response.status_code == 201:
            print(f"   ✅ Added {item_data['quantity']} x {part['name']}")
        else:
            print(f"   ⚠️  Failed to add item: {item_response.status_code}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ TEST ORDER CREATED SUCCESSFULLY")
    print("=" * 60)
    print(f"\nOrder ID: {order['id']}")
    print(f"Customer: {customer_org['name']}")
    print(f"Receiver: {oraseas_org['name']}")
    print(f"Status: {order['status']}")
    print(f"\nNow:")
    print("1. Refresh the Orders page")
    print("2. Login as Oraseas EE admin to see the order")
    print("3. Approve it (status → Pending)")
    print("4. Mark as Shipped")
    print("5. Login as customer to confirm receipt")
    print("=" * 60)

if __name__ == "__main__":
    try:
        create_test_order()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
