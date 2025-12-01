#!/usr/bin/env python3

import requests

def test_backend():
    """Test if backend is responding"""
    
    print("🧪 Testing Backend Connection...")
    
    try:
        # Test basic connection
        response = requests.get("http://localhost:8000/")
        print(f"📡 Root endpoint: {response.status_code}")
        
        # Test machines endpoint (should require auth)
        response = requests.get("http://localhost:8000/machines/")
        print(f"📡 Machines endpoint: {response.status_code}")
        
        # Test reminder endpoint (should require auth)
        response = requests.get("http://localhost:8000/machines/hours-reminder-check")
        print(f"📡 Reminder endpoint: {response.status_code}")
        
        if response.status_code == 401:
            print("✅ Backend is running and endpoints exist (401 = needs auth)")
        else:
            print(f"❓ Unexpected status: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend not running on localhost:8000")
        print("💡 Start with: docker-compose up")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_backend()