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
        
        print("🔍 Debugging Countries API...")
        print("=" * 50)
        
        # Test our countries endpoint
        print("1. Testing /organizations/countries endpoint:")
        response = requests.get("http://localhost:8000/organizations/countries", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            countries = response.json()
            print(f"   Countries: {countries}")
        else:
            print(f"   Error: {response.text}")
        
        # Test configuration endpoint (might be what frontend uses)
        print("\n2. Testing configuration endpoints:")
        
        # Check if there's a config endpoint
        config_response = requests.get("http://localhost:8000/configuration/", headers=headers)
        print(f"   /configuration/ Status: {config_response.status_code}")
        
        # Check for locale config
        try:
            locale_response = requests.get("http://localhost:8000/configuration/locale.supported_countries", headers=headers)
            print(f"   /configuration/locale.supported_countries Status: {locale_response.status_code}")
            if locale_response.status_code == 200:
                locale_data = locale_response.json()
                print(f"   Locale countries: {locale_data}")
        except:
            print("   No locale endpoint found")
        
        # Check all configuration
        try:
            all_config_response = requests.get("http://localhost:8000/configuration/all", headers=headers)
            print(f"   /configuration/all Status: {all_config_response.status_code}")
            if all_config_response.status_code == 200:
                all_config = all_config_response.json()
                # Look for country-related config
                for config in all_config:
                    if 'country' in config.get('key', '').lower() or 'countries' in config.get('key', '').lower():
                        print(f"   Found country config: {config.get('key')} = {config.get('value')}")
        except:
            print("   No all config endpoint found")
            
    else:
        print(f"❌ Login failed: {login.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print(f"\n💡 Tip: Check browser Network tab to see which API the frontend is calling!")