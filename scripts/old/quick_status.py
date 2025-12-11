import requests

try:
    # Quick health check
    health = requests.get("http://localhost:8000/health", timeout=5)
    print(f"API Health: {health.status_code}")
    
    # Quick login test
    login = requests.post(
        "http://localhost:8000/token",
        data={"username": "superadmin", "password": "superadmin"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=5
    )
    print(f"Login: {login.status_code}")
    
    if login.status_code == 200:
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test machines endpoint
        machines = requests.get("http://localhost:8000/machines/", headers=headers, timeout=5)
        print(f"Machines List: {machines.status_code}")
        
        if machines.status_code == 200:
            machine_data = machines.json()
            print(f"Found {len(machine_data)} machines")
            
            if machine_data:
                machine_id = machine_data[0]["id"]
                # Test machine details
                details = requests.get(f"http://localhost:8000/machines/{machine_id}", headers=headers, timeout=5)
                print(f"Machine Details: {details.status_code}")
                
                # Test machine maintenance
                maintenance = requests.get(f"http://localhost:8000/machines/{machine_id}/maintenance", headers=headers, timeout=5)
                print(f"Machine Maintenance: {maintenance.status_code}")
                
                # Test machine usage
                usage = requests.get(f"http://localhost:8000/machines/{machine_id}/usage-history", headers=headers, timeout=5)
                print(f"Machine Usage: {usage.status_code}")
                
                # Test machine compatibility
                compatibility = requests.get(f"http://localhost:8000/machines/{machine_id}/compatible-parts", headers=headers, timeout=5)
                print(f"Machine Compatibility: {compatibility.status_code}")
                
                print("✅ All machine endpoints tested!")
            else:
                print("⚠️ No machines in database")
        else:
            print(f"❌ Machines endpoint failed: {machines.text[:100]}")
    else:
        print(f"❌ Login failed: {login.text[:100]}")
        
except Exception as e:
    print(f"❌ Error: {e}")