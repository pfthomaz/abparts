#!/usr/bin/env python3

from datetime import date
import requests
import json

def debug_reminder_system():
    """Debug why the reminder isn't showing for zisis"""
    
    # Check if today is a reminder day
    today = date.today()
    reminder_days = [1, 2, 3, 15, 16, 17]
    is_reminder_day = today.day in reminder_days
    
    print(f"📅 Today is: {today}")
    print(f"📅 Day of month: {today.day}")
    print(f"📅 Is reminder day: {is_reminder_day}")
    print(f"📅 Reminder days: {reminder_days}")
    
    if not is_reminder_day:
        print("❌ Today is NOT a reminder day - that's why no reminder shows")
        print("💡 To test, you can:")
        print("   1. Temporarily modify the reminder_days list to include today")
        print("   2. Or wait for a reminder day (1st, 2nd, 3rd, 15th, 16th, 17th)")
        return False
    
    print("✅ Today IS a reminder day - let's check the API")
    
    # Test the reminder API
    try:
        # You'll need to get zisis's token
        token = "ZISIS_TOKEN_HERE"  # Replace with actual token
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get("http://localhost:8000/machines/hours-reminder-check", headers=headers)
        
        print(f"📥 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📄 Response: {json.dumps(data, indent=2)}")
            
            if data.get('should_show_reminder'):
                print("✅ Reminder should show!")
            else:
                print(f"❌ Reminder won't show. Reason: {data.get('reminder_reason')}")
        else:
            print(f"❌ API Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")
    
    return True

if __name__ == "__main__":
    debug_reminder_system()