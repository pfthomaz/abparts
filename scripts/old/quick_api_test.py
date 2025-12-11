import requests
import time

print("🔍 Quick API Test")
print("Waiting for API to start...")

# Wait a bit for services to start
time.sleep(10)

try:
    # Test health endpoint
    response = requests.get("http://localhost:8000/health", timeout=5)
    print(f"✅ API Health: {response.status_code}")
    
    # Test login
    login_response = requests.post(
        "http://localhost:8000/token",
        data={"username": "superadmin", "password": "superadmin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=5
    )
    print(f"✅ Login: {login_response.status_code}")
    
    if login_response.status_code == 200:
        print("🎉 API is working! Login should work now.")
    else:
        print(f"❌ Login failed: {login_response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ API not reachable - still starting up or crashed")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n💡 If API is not working:")
print("1. Wait 1-2 minutes for all services to start")
print("2. Check if there are database schema errors")
print("3. Try refreshing the login page")