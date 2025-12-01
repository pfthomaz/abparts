import requests
import time

def check_api_status():
    print("🔍 Checking API Status...")
    print("=" * 40)
    
    # Test different endpoints
    endpoints = [
        "http://localhost:8000/health",
        "http://localhost:8000/",
        "http://localhost:8000/docs"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\nTesting {endpoint}...")
            response = requests.get(endpoint, timeout=5)
            print(f"✅ Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.text[:100]}")
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error - API not reachable")
        except requests.exceptions.Timeout:
            print(f"❌ Timeout - API not responding")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test login endpoint specifically
    print(f"\n🔐 Testing login endpoint...")
    try:
        login_data = {
            "username": "superadmin",
            "password": "superadmin"
        }
        response = requests.post(
            "http://localhost:8000/token",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        print(f"Login endpoint status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Login endpoint working!")
        else:
            print(f"❌ Login failed: {response.text}")
    except Exception as e:
        print(f"❌ Login endpoint error: {e}")

if __name__ == "__main__":
    check_api_status()