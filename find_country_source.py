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
        
        print("🔍 FINDING COUNTRY DATA SOURCE")
        print("=" * 60)
        
        # Test all possible endpoints that might provide countries
        endpoints_to_test = [
            "/organizations/countries",
            "/configuration/",
            "/configuration/all",
            "/configuration/locale.supported_countries",
            "/configuration/localization",
            "/api/countries",
            "/countries",
            "/enums/countries",
            "/schemas/countries"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"http://localhost:8000{endpoint}", headers=headers)
                print(f"\n📍 {endpoint}")
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Look for country data in the response
                    if isinstance(data, list):
                        if all(isinstance(item, str) and len(item) == 2 for item in data):
                            print(f"   🌍 COUNTRIES FOUND: {data}")
                        else:
                            print(f"   📄 List with {len(data)} items")
                    elif isinstance(data, dict):
                        # Look for country-related keys
                        country_keys = []
                        for key, value in data.items():
                            if 'country' in key.lower() or 'countries' in key.lower():
                                country_keys.append(f"{key}: {value}")
                        
                        if country_keys:
                            print(f"   🌍 COUNTRY DATA FOUND:")
                            for key in country_keys:
                                print(f"      {key}")
                        else:
                            print(f"   📄 Dict with keys: {list(data.keys())[:5]}")
                else:
                    print(f"   ❌ Error: {response.text[:100]}")
                    
            except Exception as e:
                print(f"   ❌ Exception: {e}")
        
        print(f"\n🎯 RECOMMENDATION:")
        print(f"1. Check browser Network tab when opening organization modal")
        print(f"2. Look for API calls that return country data")
        print(f"3. The frontend might be using a hardcoded array")
        print(f"4. Try clearing all browser cache/storage")
        
    else:
        print(f"❌ Login failed: {login.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print(f"\n💡 DEBUGGING TIPS:")
print(f"1. Open browser DevTools (F12)")
print(f"2. Go to Network tab")
print(f"3. Open organization creation modal")
print(f"4. Look for API calls that fetch country data")
print(f"5. Check if frontend has hardcoded country list in JavaScript files")