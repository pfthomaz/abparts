#!/usr/bin/env python3
"""Add checklist items to existing protocols"""

import requests
import json

BASE_URL = "http://localhost:8000"
EMAIL = "dthomaz"
PASSWORD = "amFT1999!"

def get_token():
    response = requests.post(f"{BASE_URL}/token", data={"username": EMAIL, "password": PASSWORD})
    return response.json()["access_token"]

def add_checklist_item(token, protocol_id, data):
    response = requests.post(
        f"{BASE_URL}/maintenance-protocols/{protocol_id}/checklist-items",
        headers={"Authorization": f"Bearer {token}"},
        json=data
    )
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def main():
    token = get_token()
    print("✅ Token obtained\n")
    
    # Get existing protocols
    response = requests.get(
        f"{BASE_URL}/maintenance-protocols",
        headers={"Authorization": f"Bearer {token}"}
    )
    protocols = response.json()
    
    # Find protocols by name
    daily_start = next((p for p in protocols if p['name'] == 'Daily Start of Day'), None)
    daily_end = next((p for p in protocols if p['name'] == 'Daily End of Day'), None)
    service_50 = next((p for p in protocols if p['name'] == '50 Hour Service'), None)
    
    if daily_start and len(daily_start['checklist_items']) == 0:
        print(f"📝 Adding items to Daily Start of Day ({daily_start['id']})...")
        items = [
            {"item_order": 1, "item_description": "Check water level in tank", "item_type": "check", "item_category": "Pre-operation", "is_critical": True, "estimated_duration_minutes": 2},
            {"item_order": 2, "item_description": "Inspect nets for damage or wear", "item_type": "check", "item_category": "Pre-operation", "is_critical": True, "estimated_duration_minutes": 5},
            {"item_order": 3, "item_description": "Check pump operation", "item_type": "check", "item_category": "Pre-operation", "is_critical": True, "estimated_duration_minutes": 3}
        ]
        for item in items:
            add_checklist_item(token, daily_start['id'], item)
        print(f"✅ Added {len(items)} items\n")
    
    if daily_end and len(daily_end['checklist_items']) == 0:
        print(f"📝 Adding items to Daily End of Day ({daily_end['id']})...")
        items = [
            {"item_order": 1, "item_description": "Clean nets thoroughly", "item_type": "service", "item_category": "Cleaning", "is_critical": True, "estimated_duration_minutes": 15},
            {"item_order": 2, "item_description": "Drain and clean water tank", "item_type": "service", "item_category": "Cleaning", "is_critical": True, "estimated_duration_minutes": 10},
            {"item_order": 3, "item_description": "Record machine hours", "item_type": "check", "item_category": "Documentation", "is_critical": True, "estimated_duration_minutes": 2}
        ]
        for item in items:
            add_checklist_item(token, daily_end['id'], item)
        print(f"✅ Added {len(items)} items\n")
    
    if service_50 and len(service_50['checklist_items']) == 0:
        print(f"📝 Adding items to 50 Hour Service ({service_50['id']})...")
        items = [
            {"item_order": 1, "item_description": "Inspect and clean pump filter", "item_type": "service", "item_category": "Pump Maintenance", "is_critical": True, "estimated_duration_minutes": 20},
            {"item_order": 2, "item_description": "Check all hose connections", "item_type": "check", "item_category": "Safety Check", "is_critical": True, "estimated_duration_minutes": 10},
            {"item_order": 3, "item_description": "Lubricate moving parts", "item_type": "service", "item_category": "Lubrication", "is_critical": False, "estimated_duration_minutes": 15}
        ]
        for item in items:
            add_checklist_item(token, service_50['id'], item)
        print(f"✅ Added {len(items)} items\n")
    
    # Show final result
    response = requests.get(
        f"{BASE_URL}/maintenance-protocols",
        headers={"Authorization": f"Bearer {token}"}
    )
    protocols = response.json()
    
    print("📋 Final protocols with checklist items:")
    for p in protocols:
        print(f"\n{p['name']} ({p['protocol_type']}):")
        print(f"  - {len(p['checklist_items'])} checklist items")
        for item in p['checklist_items']:
            print(f"    {item['item_order']}. {item['item_description']} ({item['item_type']})")
    
    print("\n🎉 All done! Check http://localhost:8000/docs")

if __name__ == "__main__":
    main()
