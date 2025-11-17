#!/usr/bin/env python3
"""Test the customer order workflow implementation."""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_workflow():
    """Test the complete customer order workflow."""
    
    print("=" * 60)
    print("Customer Order Workflow Test")
    print("=" * 60)
    
    # Step 1: Login as Oraseas EE admin
    print("\n1. Logging in as Oraseas EE admin...")
    login_response = requests.post(
        f"{BASE_URL}/login",
        data={
            "username": "oraseasee_admin",
            "password": "admin123"
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Logged in successfully")
    
    # Step 2: Get customer orders
    print("\n2. Fetching customer orders...")
    orders_response = requests.get(
        f"{BASE_URL}/customer_orders",
        headers=headers
    )
    
    if orders_response.status_code != 200:
        print(f"❌ Failed to fetch orders: {orders_response.status_code}")
        return
    
    orders = orders_response.json()
    print(f"✅ Found {len(orders)} customer orders")
    
    # Find a Pending order to ship
    pending_order = None
    for order in orders:
        if order['status'] == 'Pending':
            pending_order = order
            break
    
    if not pending_order:
        print("⚠️  No Pending orders found to test shipping")
        print("   Create a customer order and approve it first")
        return
    
    print(f"\n3. Found Pending order: {pending_order['id']}")
    print(f"   Customer: {pending_order.get('customer_organization_name', 'Unknown')}")
    print(f"   Order Date: {pending_order['order_date']}")
    
    # Step 3: Ship the order
    print("\n4. Marking order as shipped...")
    ship_data = {
        "shipped_date": datetime.now().isoformat(),
        "tracking_number": "TEST123456789",
        "notes": "Test shipment via automated test"
    }
    
    ship_response = requests.patch(
        f"{BASE_URL}/customer_orders/{pending_order['id']}/ship",
        headers=headers,
        json=ship_data
    )
    
    if ship_response.status_code != 200:
        print(f"❌ Failed to ship order: {ship_response.status_code}")
        print(ship_response.text)
        return
    
    shipped_order = ship_response.json()
    print("✅ Order marked as shipped")
    print(f"   Status: {shipped_order['status']}")
    print(f"   Shipped Date: {shipped_order.get('shipped_date', 'Not set')}")
    
    # Step 4: Login as customer user
    print("\n5. Logging in as customer user...")
    customer_login = requests.post(
        f"{BASE_URL}/login",
        data={
            "username": "bossserv_cyprus_admin",
            "password": "admin123"
        }
    )
    
    if customer_login.status_code != 200:
        print(f"❌ Customer login failed: {customer_login.status_code}")
        print("   Note: You may need to create this user first")
        return
    
    customer_token = customer_login.json()["access_token"]
    customer_headers = {"Authorization": f"Bearer {customer_token}"}
    print("✅ Logged in as customer")
    
    # Step 5: Get customer's warehouses
    print("\n6. Fetching customer warehouses...")
    warehouses_response = requests.get(
        f"{BASE_URL}/warehouses",
        headers=customer_headers
    )
    
    if warehouses_response.status_code != 200:
        print(f"❌ Failed to fetch warehouses: {warehouses_response.status_code}")
        return
    
    warehouses = warehouses_response.json()
    if not warehouses:
        print("⚠️  No warehouses found for customer")
        print("   Create a warehouse first")
        return
    
    warehouse_id = warehouses[0]['id']
    print(f"✅ Found warehouse: {warehouses[0]['name']}")
    
    # Step 6: Confirm receipt
    print("\n7. Confirming order receipt...")
    receipt_data = {
        "actual_delivery_date": datetime.now().isoformat(),
        "receiving_warehouse_id": warehouse_id,
        "notes": "All items received in good condition - automated test"
    }
    
    receipt_response = requests.patch(
        f"{BASE_URL}/customer_orders/{pending_order['id']}/confirm-receipt",
        headers=customer_headers,
        json=receipt_data
    )
    
    if receipt_response.status_code != 200:
        print(f"❌ Failed to confirm receipt: {receipt_response.status_code}")
        print(receipt_response.text)
        return
    
    received_order = receipt_response.json()
    print("✅ Order receipt confirmed")
    print(f"   Status: {received_order['status']}")
    print(f"   Delivered Date: {received_order.get('actual_delivery_date', 'Not set')}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ WORKFLOW TEST COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("\nOrder Timeline:")
    print(f"  Order Date:    {received_order['order_date']}")
    print(f"  Shipped Date:  {received_order.get('shipped_date', 'N/A')}")
    print(f"  Received Date: {received_order.get('actual_delivery_date', 'N/A')}")
    print(f"  Final Status:  {received_order['status']}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_workflow()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
