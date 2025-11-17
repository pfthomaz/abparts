#!/usr/bin/env python3

import requests
import json

def check_bossserv_organization():
    """Check the organization type of BossServ Ltd"""
    
    # Get all organizations
    url = "http://localhost:8000/organizations/"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            organizations = response.json()
            
            # Find BossServ Ltd
            bossserv = None
            for org in organizations:
                if org.get('name') == 'BossServ Ltd':
                    bossserv = org
                    break
            
            if bossserv:
                print("🏢 Found BossServ Ltd:")
                print(f"   📋 Name: {bossserv['name']}")
                print(f"   🏷️  Type: {bossserv['organization_type']}")
                print(f"   🆔 ID: {bossserv['id']}")
                
                if bossserv['organization_type'] == 'customer':
                    print("\n❌ ISSUE FOUND:")
                    print("   BossServ Ltd is created as 'customer' type")
                    print("   But superadmins are only allowed for:")
                    print("   - oraseas_ee organizations")
                    print("   - bossaqua organizations") 
                    print("   - supplier organizations named 'BossServ Ltd' or 'BossAqua'")
                    print("\n💡 SOLUTION:")
                    print("   Change BossServ Ltd to 'supplier' type")
                elif bossserv['organization_type'] == 'supplier':
                    print("\n✅ Organization type is correct for superadmin users")
                else:
                    print(f"\n🤔 Organization type: {bossserv['organization_type']}")
                    
            else:
                print("❌ BossServ Ltd not found in organizations")
                print("📋 Available organizations:")
                for org in organizations:
                    print(f"   - {org['name']} ({org['organization_type']})")
        else:
            print(f"❌ Failed to get organizations: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Make sure the backend is running on localhost:8000")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    check_bossserv_organization()