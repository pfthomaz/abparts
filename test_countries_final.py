import requests
import json

try:
    # Login
    login = requests.post(
        "http://localhost:8000/token",
        data={"username": "superadmin", "password": "superadmin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if login.status_code == 200:
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("🌍 Testing Countries Endpoint...")
        print("=" * 40)
        
        # Test countries endpoint
        response = requests.get(
            "http://localhost:8000/organizations/countries",
            headers=headers
        )
        
        print(f"Countries endpoint status: {response.status_code}")
        if response.status_code == 200:
            countries = response.json()
            print(f"✅ Available countries: {countries}")
            
            expected_countries = ["GR", "UK", "NO", "CA", "NZ", "TR"]
            if set(countries) == set(expected_countries):
                print("🎉 SUCCESS! All new countries are available!")
                print("   - GR (Greece)")
                print("   - UK (United Kingdom)")
                print("   - NO (Norway)")
                print("   - CA (Canada)")
                print("   - NZ (New Zealand)")
                print("   - TR (Turkey)")
            else:
                print(f"⚠️  Expected: {expected_countries}")
                print(f"⚠️  Got: {countries}")
        else:
            print(f"❌ Countries endpoint failed: {response.text}")
            
        # Test organization creation with country
        print(f"\n🏢 Testing Organization Creation with Country...")
        org_data = {
            "name": "Test UK Organization",
            "organization_type": "customer",
            "country": "UK",
            "address": "123 London Street, London, UK",
            "contact_info": "test@uk-org.com"
        }
        
        create_response = requests.post(
            "http://localhost:8000/organizations/",
            json=org_data,
            headers=headers
        )
        
        print(f"Organization creation status: {create_response.status_code}")
        if create_response.status_code == 201:
            org = create_response.json()
            print(f"✅ SUCCESS! Created organization:")
            print(f"   - Name: {org.get('name')}")
            print(f"   - Country: {org.get('country')}")
            print(f"   - Type: {org.get('organization_type')}")
        else:
            print(f"❌ Organization creation failed: {create_response.text}")
            
    else:
        print(f"❌ Login failed: {login.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print(f"\n📝 Next Steps:")
print("1. Refresh your browser page")
print("2. Try creating a new organization")
print("3. You should now see all 6 countries in the dropdown!")