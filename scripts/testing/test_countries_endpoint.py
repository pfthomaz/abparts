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
        
        # Test countries endpoint
        response = requests.get(
            "http://localhost:8000/organizations/countries",
            headers=headers
        )
        
        print(f"Countries endpoint: {response.status_code}")
        if response.status_code == 200:
            countries = response.json()
            print(f"Available countries: {countries}")
        else:
            print(f"Error: {response.text}")
            
    else:
        print(f"Login failed: {login.status_code}")
        
except Exception as e:
    print(f"Error: {e}")