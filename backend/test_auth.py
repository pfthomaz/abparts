#!/usr/bin/env python3
"""
Simple authentication test to find working credentials
"""

import requests
import sys

API_BASE_URL = "http://localhost:8000"

def test_auth(username, password):
    """Test authentication with given credentials"""
    login_data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(f"{API_BASE_URL}/token", data=login_data)
    
    if response.status_code == 200:
        print(f"✅ SUCCESS: {username} / {password}")
        return True
    else:
        print(f"❌ FAILED: {username} / {password} - {response.status_code}")
        return False

def main():
    """Test common password combinations"""
    usernames = ["superadmin", "oraseasee_admin", "autoboss_admin"]
    passwords = ["password123", "admin123", "admin", "password", "123456", "test123"]
    
    print("Testing authentication combinations...")
    
    for username in usernames:
        for password in passwords:
            if test_auth(username, password):
                print(f"\n🎉 Found working credentials: {username} / {password}")
                return
    
    print("\n❌ No working credentials found")

if __name__ == "__main__":
    main()