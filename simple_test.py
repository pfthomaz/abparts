import requests
import json

# Test machine endpoints
def test_machine_endpoints():
    # Login first
    login_response = requests.post(
        "http://localhost:8000/token",
        data={"username": "superadmin", "password": "superadmin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if login_response.status_code != 200:
        print("Login failed")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test endpoints
    endpoints = [
        "/machines/1",
        "/machines/1/maintenance", 
        "/machines/1/usage-history",
        "/machines/1/compatible-parts"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", headers=headers)
            print(f"{endpoint}: {response.status_code}")
            if response.status_code != 200:
                print(f"  Error: {response.text[:100]}")
        except Exception as e:
            print(f"{endpoint}: ERROR - {e}")

if __name__ == "__main__":
    test_machine_endpoints()