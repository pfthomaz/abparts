#!/usr/bin/env python3
"""
Comprehensive test for organization creation with country support
"""
import requests
import json

def test_organization_functionality():
    print("🏢 Testing Complete Organization Functionality")
    print("=" * 60)
    
    try:
        # Login first
        print("1. Authenticating...")
        login_response = requests.post(
            "http://localhost:8000/token",
            data={"username": "superadmin", "password": "superadmin"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code}")
            return False
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        print("✅ Authentication successful")
        
        # Test 1: Create BossServ Ltd (UK)
        print("\n2. Creating BossServ Ltd (UK)...")
        bossserv_data = {
            "name": "BossServ Ltd",
            "organization_type": "supplier",
            "country": "UK",
            "address": "123 London Street, London, UK",
            "contact_info": "contact@bossserv.co.uk, +44-20-1234-5678"
        }
        
        bossserv_response = requests.post(
            "http://localhost:8000/organizations/",
            json=bossserv_data,
            headers=headers,
            timeout=10
        )
        
        print(f"BossServ Ltd creation status: {bossserv_response.status_code}")
        if bossserv_response.status_code == 201:
            bossserv_org = bossserv_response.json()
            print("✅ BossServ Ltd created successfully!")
            print(f"   - ID: {bossserv_org.get('id')}")
            print(f"   - Country: {bossserv_org.get('country')}")
            bossserv_id = bossserv_org.get('id')
        else:
            print(f"❌ BossServ Ltd creation failed: {bossserv_response.text}")
            bossserv_id = None
        
        # Test 2: Create BossAqua NZ (New Zealand)
        print("\n3. Creating BossAqua NZ (New Zealand)...")
        bossaqua_nz_data = {
            "name": "BossAqua",
            "organization_type": "supplier", 
            "country": "NZ",
            "address": "456 Auckland Road, Auckland, New Zealand",
            "contact_info": "contact@bossaqua.co.nz, +64-9-1234-567"
        }
        
        bossaqua_response = requests.post(
            "http://localhost:8000/organizations/",
            json=bossaqua_nz_data,
            headers=headers,
            timeout=10
        )
        
        print(f"BossAqua NZ creation status: {bossaqua_response.status_code}")
        if bossaqua_response.status_code == 201:
            bossaqua_org = bossaqua_response.json()
            print("✅ BossAqua NZ created successfully!")
            print(f"   - ID: {bossaqua_org.get('id')}")
            print(f"   - Country: {bossaqua_org.get('country')}")
            bossaqua_nz_id = bossaqua_org.get('id')
        else:
            print(f"❌ BossAqua NZ creation failed: {bossaqua_response.text}")
            bossaqua_nz_id = None
        
        # Test 3: Create customer organizations in different countries
        print("\n4. Creating customer organizations...")
        
        customers = [
            {
                "name": "AutoClean UK Ltd",
                "organization_type": "customer",
                "country": "UK",
                "address": "789 Manchester Ave, Manchester, UK",
                "contact_info": "info@autoclean.co.uk"
            },
            {
                "name": "CleanTech Norway AS",
                "organization_type": "customer", 
                "country": "NO",
                "address": "321 Oslo Street, Oslo, Norway",
                "contact_info": "info@cleantech.no"
            },
            {
                "name": "Maple Clean Canada Inc",
                "organization_type": "customer",
                "country": "CA", 
                "address": "654 Toronto Blvd, Toronto, Canada",
                "contact_info": "info@mapleclean.ca"
            }
        ]
        
        created_customers = []
        for customer_data in customers:
            response = requests.post(
                "http://localhost:8000/organizations/",
                json=customer_data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 201:
                customer = response.json()
                created_customers.append(customer)
                print(f"   ✅ {customer_data['name']} ({customer_data['country']}) created")
            else:
                print(f"   ❌ {customer_data['name']} creation failed: {response.status_code}")
        
        # Test 4: Test superadmin user creation in key organizations
        print("\n5. Testing superadmin user creation...")
        
        if bossserv_id:
            print("   Testing superadmin creation in BossServ Ltd...")
            superadmin_data = {
                "username": "bossserv_admin",
                "email": "admin@bossserv.co.uk",
                "name": "BossServ Administrator",
                "password": "SecurePass123!",
                "role": "super_admin",
                "organization_id": bossserv_id
            }
            
            user_response = requests.post(
                "http://localhost:8000/users/",
                json=superadmin_data,
                headers=headers,
                timeout=10
            )
            
            if user_response.status_code == 201:
                print("   ✅ Superadmin created in BossServ Ltd")
            else:
                print(f"   ❌ Superadmin creation failed: {user_response.text}")
        
        # Test 5: List all organizations
        print("\n6. Listing all organizations...")
        list_response = requests.get(
            "http://localhost:8000/organizations/",
            headers=headers,
            timeout=10
        )
        
        if list_response.status_code == 200:
            orgs = list_response.json()
            print(f"✅ Found {len(orgs)} organizations:")
            
            # Group by country
            by_country = {}
            for org in orgs:
                country = org.get('country', 'Unknown')
                if country not in by_country:
                    by_country[country] = []
                by_country[country].append(org)
            
            for country, country_orgs in by_country.items():
                print(f"\n   📍 {country}:")
                for org in country_orgs:
                    print(f"      - {org.get('name')} ({org.get('organization_type')})")
        
        print("\n🎉 Organization functionality testing completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_organization_functionality()
    if not success:
        exit(1)