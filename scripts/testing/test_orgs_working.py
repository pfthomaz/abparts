import requests

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
        
        # Test organizations list (this was failing before)
        print("Testing organizations list...")
        response = requests.get(
            "http://localhost:8000/organizations/",
            headers=headers
        )
        
        print(f"Organizations list: {response.status_code}")
        if response.status_code == 200:
            orgs = response.json()
            print(f"✅ SUCCESS! Found {len(orgs)} organizations")
            for org in orgs:
                print(f"  - {org.get('name')} ({org.get('organization_type')})")
        else:
            print(f"❌ FAILED: {response.text}")
            
        # Test countries endpoint (should return new countries)
        print("\nTesting countries endpoint...")
        countries_response = requests.get(
            "http://localhost:8000/organizations/countries",
            headers=headers
        )
        
        print(f"Countries endpoint: {countries_response.status_code}")
        if countries_response.status_code == 200:
            countries = countries_response.json()
            print(f"✅ Available countries: {countries}")
            
            expected = ["GR", "UK", "NO", "CA", "NZ", "TR"]
            if set(countries) == set(expected):
                print("✅ All new countries are configured!")
            else:
                print(f"⚠️  Expected: {expected}, Got: {countries}")
        else:
            print(f"❌ Countries failed: {countries_response.text}")
            
    else:
        print(f"❌ Login failed: {login.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")