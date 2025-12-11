#!/usr/bin/env python3

import requests
import json

def fix_bossserv_organization_type():
    """Change BossServ Ltd from customer to supplier type"""
    
    # First, get BossServ Ltd organization
    get_url = "http://localhost:8000/organizations/"
    
    try:
        response = requests.get(get_url)
        if response.status_code == 200:
            organizations = response.json()
            
            # Find BossServ Ltd
            bossserv = None
            for org in organizations:
                if org.get('name') == 'BossServ Ltd':
                    bossserv = org
                    break
            
            if not bossserv:
                print("❌ BossServ Ltd not found")
                return False
                
            print(f"🏢 Found BossServ Ltd (ID: {bossserv['id']})")
            print(f"   Current type: {bossserv['organization_type']}")
            
            # Update to supplier type
            update_url = f"http://localhost:8000/organizations/{bossserv['id']}"
            update_data = {
                "organization_type": "supplier"
            }
            
            print("🔄 Updating organization type to 'supplier'...")
            update_response = requests.put(update_url, json=update_data)
            
            if update_response.status_code == 200:
                print("✅ SUCCESS! BossServ Ltd is now a supplier organization")
                print("🎯 You can now create superadmin users for BossServ Ltd")
                return True
            else:
                print(f"❌ Failed to update: {update_response.status_code}")
                print(f"Error: {update_response.text}")
                return False
                
        else:
            print(f"❌ Failed to get organizations: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Make sure the backend is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    fix_bossserv_organization_type()