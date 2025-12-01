#!/usr/bin/env python3

import requests
import json

def test_reminder_api():
    """Test the reminder API to see if it's working"""
    
    print("🧪 Testing Machine Hours Reminder API...")
    
    # You'll need to replace this with a valid token for zisis
    # You can get this from the browser's developer tools -> Application -> Local Storage -> token
    token = input("Enter zisis's auth token (from browser localStorage): ").strip()
    
    if not token:
        print("❌ No token provided. Please get the token from browser localStorage.")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("📡 Calling reminder check API...")
        response = requests.get("http://localhost:8000/machines/hours-reminder-check", headers=headers)
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API Response:")
            print(json.dumps(data, indent=2, default=str))
            
            if data.get('should_show_reminder'):
                print("🎯 Reminder SHOULD show!")
                print(f"📋 Machines needing updates: {len(data.get('reminder_machines', []))}")
            else:
                print(f"❌ Reminder won't show. Reason: {data.get('reminder_reason')}")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📄 Error details: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Backend not running on localhost:8000")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    test_reminder_api()