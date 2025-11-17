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
        
        # Test organizations list
        response = requests.get(
            "http://localhost:8000/organizations/",
            headers=headers
        )
        
        print(f"Organizations list: {response.status_code}")
        if response.status_code == 200:
            orgs = response.json()
            print(f"Found {len(orgs)} organizations")
            for org in orgs:
                print(f"  - {org.get('name')} ({org.get('organization_type')})")
        else:
            print(f"Error: {response.text}")
            
        # Test organization creation without country
        org_data = {
            "name": "Test Organization Basic",
            "organization_type": "customer",
            "address": "Test Address",
            "contact_info": "test@example.com"
        }
        
        create_response = requests.post(
            "http://localhost:8000/organizations/",
            json=org_data,
            headers=headers
        )
        
        print(f"Organization creation: {create_response.status_code}")
        if create_response.status_code == 201:
            org = create_response.json()
            print(f"Created: {org.get('name')}")
        else:
            print(f"Creation error: {create_response.text}")
            
    else:
        print(f"Login failed: {login.status_code}")
        
except Exception as e:
    print(f"Error: {e}")