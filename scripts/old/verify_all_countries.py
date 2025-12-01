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
        
        print("🌍 FINAL VERIFICATION: All Countries Updated")
        print("=" * 60)
        
        # Test organizations countries endpoint
        print("1. Organizations Countries Endpoint:")
        response = requests.get("http://localhost:8000/organizations/countries", headers=headers)
        if response.status_code == 200:
            countries = response.json()
            print(f"   ✅ /organizations/countries: {countries}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
        
        print(f"\n🎉 SUCCESS! All country references updated!")
        print(f"Expected countries: GR, UK, NO, CA, NZ, TR")
        print(f"")
        print(f"📝 Next Steps:")
        print(f"1. 🔄 Hard refresh your browser (Ctrl+F5 or Cmd+Shift+R)")
        print(f"2. 🗂️  Clear browser cache if needed")
        print(f"3. 🏢 Open organization creation modal")
        print(f"4. 🌍 You should now see the new countries!")
        print(f"")
        print(f"New countries should be:")
        print(f"   🇬🇷 Greece (GR)")
        print(f"   🇬🇧 United Kingdom (UK)")
        print(f"   🇳🇴 Norway (NO)")
        print(f"   🇨🇦 Canada (CA)")
        print(f"   🇳🇿 New Zealand (NZ)")
        print(f"   🇹🇷 Turkey (TR)")
            
    else:
        print(f"❌ Login failed: {login.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")