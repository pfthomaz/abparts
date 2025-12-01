#!/usr/bin/env python3

import requests
import json
from datetime import date

def test_reminder_system():
    """Simple test of the reminder system"""
    
    print("🧪 Testing Machine Hours Reminder System...")
    
    # Check if today should show reminders
    today = date.today()
    print(f"📅 Today is: {today} (day {today.day})")
    
    # Test the API without authentication first
    try:
        print("📡 Testing reminder API...")
        response = requests.get("http://localhost:8000/machines/hours-reminder-check")
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 401:
            print("🔐 API requires authentication (expected)")
            print("💡 To test with authentication:")
            print("   1. Login to the app in browser")
            print("   2. Open Developer Tools → Application → Local Storage")
            print("   3. Copy the 'token' value")
            print("   4. Run: curl -H 'Authorization: Bearer YOUR_TOKEN' http://localhost:8000/machines/hours-reminder-check")
        else:
            print(f"📄 Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Backend not running on localhost:8000")
        print("💡 Make sure Docker containers are running:")
        print("   docker-compose up")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

    # Check if reminder logic is working
    print("\n🔍 Checking reminder logic...")
    reminder_days = [1, 2, 3, 15, 16, 17]
    is_reminder_day = today.day in reminder_days
    
    print(f"📅 Reminder days: {reminder_days}")
    print(f"📅 Today ({today.day}) is reminder day: {is_reminder_day}")
    
    if not is_reminder_day:
        print("❌ Today is NOT a reminder day in production logic")
        print("✅ But I set it to show EVERY day for testing")
    else:
        print("✅ Today IS a reminder day")

if __name__ == "__main__":
    test_reminder_system()