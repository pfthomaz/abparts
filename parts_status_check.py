import requests

try:
    # Login
    login = requests.post(
        "http://localhost:8000/token",
        data={"username": "superadmin", "password": "superadmin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10
    )
    
    if login.status_code == 200:
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test the problematic endpoint
        parts_response = requests.get(
            "http://localhost:8000/parts/with-inventory?include_count=true&limit=10", 
            headers=headers, 
            timeout=10
        )
        
        print(f"Parts with inventory endpoint: {parts_response.status_code}")
        if parts_response.status_code == 200:
            data = parts_response.json()
            print(f"✅ SUCCESS! Returned {len(data.get('items', []))} items")
            if 'total_count' in data:
                print(f"Total count: {data['total_count']}")
        else:
            print(f"❌ FAILED: {parts_response.text[:200]}")
    else:
        print(f"Login failed: {login.status_code}")
        
except Exception as e:
    print(f"Error: {e}")