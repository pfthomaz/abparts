import requests

# Test organization creation
try:
    # Login
    login = requests.post(
        "http://localhost:8000/token",
        data={"username": "superadmin", "password": "superadmin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if login.status_code == 200:
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # Test org creation
        org_data = {
            "name": "Test UK Organization",
            "organization_type": "customer",
            "country": "UK",
            "address": "Test Address",
            "contact_info": "test@example.com"
        }
        
        response = requests.post(
            "http://localhost:8000/organizations/",
            json=org_data,
            headers=headers
        )
        
        print(f"Organization creation: {response.status_code}")
        if response.status_code == 201:
            org = response.json()
            print(f"Created: {org.get('name')} in {org.get('country')}")
        else:
            print(f"Error: {response.text}")
            
    else:
        print(f"Login failed: {login.status_code}")
        
except Exception as e:
    print(f"Error: {e}")