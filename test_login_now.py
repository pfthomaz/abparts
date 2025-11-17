import requests

print("🔐 Testing Login After API Restart")
print("=" * 40)

try:
    # Test health first
    health = requests.get("http://localhost:8000/health", timeout=5)
    print(f"Health check: {health.status_code}")
    
    # Test login
    login_response = requests.post(
        "http://localhost:8000/token",
        data={"username": "superadmin", "password": "superadmin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10
    )
    
    print(f"Login status: {login_response.status_code}")
    if login_response.status_code == 200:
        print("✅ LOGIN WORKING! You can now log in.")
        token = login_response.json()["access_token"]
        
        # Test countries endpoint
        headers = {"Authorization": f"Bearer {token}"}
        countries_response = requests.get(
            "http://localhost:8000/organizations/countries",
            headers=headers,
            timeout=5
        )
        
        print(f"Countries endpoint: {countries_response.status_code}")
        if countries_response.status_code == 200:
            countries = countries_response.json()
            print(f"✅ Available countries: {countries}")
        
    else:
        print(f"❌ Login failed: {login_response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print(f"\n💡 Try logging in to the frontend now!")
print(f"   Username: superadmin")
print(f"   Password: superadmin")