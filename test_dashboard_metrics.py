#!/usr/bin/env python3
"""
Test script to verify dashboard metrics are working correctly.
Run this to check if farm sites and nets are being counted.
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
USERNAME = "dthomaz"  # Change to your username
PASSWORD = "amFT1999!"  # Change to your password

def test_dashboard_metrics():
    """Test the dashboard metrics endpoint"""
    
    # Step 1: Login
    print("Step 1: Logging in...")
    login_response = requests.post(
        f"{API_BASE_URL}/token",
        data={"username": USERNAME, "password": PASSWORD}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    print(f"✅ Login successful")
    
    # Step 2: Get dashboard metrics
    print("\nStep 2: Fetching dashboard metrics...")
    headers = {"Authorization": f"Bearer {token}"}
    metrics_response = requests.get(
        f"{API_BASE_URL}/dashboard/metrics",
        headers=headers
    )
    
    if metrics_response.status_code != 200:
        print(f"❌ Failed to fetch metrics: {metrics_response.status_code}")
        print(metrics_response.text)
        return
    
    metrics = metrics_response.json()
    print(f"✅ Metrics fetched successfully")
    
    # Step 3: Display relevant metrics
    print("\n" + "="*50)
    print("DASHBOARD METRICS")
    print("="*50)
    print(f"Total Parts: {metrics.get('total_parts', 'N/A')}")
    print(f"Total Machines: {metrics.get('total_machines', 'N/A')}")
    print(f"Total Farm Sites: {metrics.get('total_farm_sites', 'N/A')}")
    print(f"Total Nets (Cages): {metrics.get('total_nets', 'N/A')}")
    print("="*50)
    
    # Step 4: Check if farm sites and nets are zero
    if metrics.get('total_farm_sites', 0) == 0:
        print("\n⚠️  WARNING: total_farm_sites is 0")
        print("   This could mean:")
        print("   1. No farm sites have been created yet")
        print("   2. The migration hasn't been applied (tables don't exist)")
        print("   3. There's an error in the counting logic")
    
    if metrics.get('total_nets', 0) == 0:
        print("\n⚠️  WARNING: total_nets is 0")
        print("   This could mean:")
        print("   1. No nets have been created yet")
        print("   2. The migration hasn't been applied (tables don't exist)")
        print("   3. There's an error in the counting logic")
    
    # Step 5: Try to fetch farm sites directly
    print("\nStep 3: Checking if farm sites endpoint works...")
    farm_sites_response = requests.get(
        f"{API_BASE_URL}/farm-sites",
        headers=headers
    )
    
    if farm_sites_response.status_code == 200:
        farm_sites = farm_sites_response.json()
        print(f"✅ Farm sites endpoint works: {len(farm_sites)} farm sites found")
        if len(farm_sites) > 0:
            print(f"   First farm site: {farm_sites[0].get('name', 'N/A')}")
    else:
        print(f"❌ Farm sites endpoint failed: {farm_sites_response.status_code}")
        print(f"   Error: {farm_sites_response.text}")
        print("\n   💡 This likely means the migration hasn't been applied yet!")
        print("   Run: docker-compose exec api alembic upgrade head")
    
    # Step 6: Try to fetch nets directly
    print("\nStep 4: Checking if nets endpoint works...")
    nets_response = requests.get(
        f"{API_BASE_URL}/nets",
        headers=headers
    )
    
    if nets_response.status_code == 200:
        nets = nets_response.json()
        print(f"✅ Nets endpoint works: {len(nets)} nets found")
        if len(nets) > 0:
            print(f"   First net: {nets[0].get('name', 'N/A')}")
    else:
        print(f"❌ Nets endpoint failed: {nets_response.status_code}")
        print(f"   Error: {nets_response.text}")
        print("\n   💡 This likely means the migration hasn't been applied yet!")
        print("   Run: docker-compose exec api alembic upgrade head")
    
    print("\n" + "="*50)
    print("FULL METRICS RESPONSE:")
    print("="*50)
    print(json.dumps(metrics, indent=2, default=str))

if __name__ == "__main__":
    try:
        test_dashboard_metrics()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
