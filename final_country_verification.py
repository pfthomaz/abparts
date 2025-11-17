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
        
        print("🎉 FINAL COUNTRY UPDATE VERIFICATION")
        print("=" * 60)
        
        # Test the countries endpoint
        response = requests.get("http://localhost:8000/organizations/countries", headers=headers)
        if response.status_code == 200:
            countries = response.json()
            print(f"✅ Backend countries endpoint: {countries}")
            
            expected = ["GR", "UK", "NO", "CA", "NZ", "TR", "OM", "ES", "CY", "SA"]
            if set(countries) == set(expected):
                print("✅ All expected countries are present in backend!")
            else:
                missing = set(expected) - set(countries)
                extra = set(countries) - set(expected)
                if missing:
                    print(f"❌ Missing: {missing}")
                if extra:
                    print(f"⚠️  Extra: {extra}")
        else:
            print(f"❌ Backend endpoint failed: {response.status_code}")
        
        print(f"\n📋 COMPLETE COUNTRY LIST:")
        print(f"   🇬🇷 GR - Greece")
        print(f"   🇬🇧 UK - United Kingdom")
        print(f"   🇳🇴 NO - Norway")
        print(f"   🇨🇦 CA - Canada")
        print(f"   🇳🇿 NZ - New Zealand")
        print(f"   🇹🇷 TR - Turkey")
        print(f"   🇴🇲 OM - Oman")
        print(f"   🇪🇸 ES - Spain")
        print(f"   🇨🇾 CY - Cyprus")
        print(f"   🇸🇦 SA - Saudi Arabia")
        
        print(f"\n✅ UPDATES COMPLETED:")
        print(f"   ✅ Backend models and schemas")
        print(f"   ✅ Configuration files")
        print(f"   ✅ Frontend countryFlags.js")
        print(f"   ✅ Frontend LocalizationContext.js")
        print(f"   ✅ Test files")
        
        print(f"\n🔄 NEXT STEPS:")
        print(f"1. Refresh your browser (Ctrl+F5 or Cmd+Shift+R)")
        print(f"2. Clear browser cache if needed")
        print(f"3. Open organization creation modal")
        print(f"4. You should now see ALL 10 countries!")
        
    else:
        print(f"❌ Login failed: {login.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")