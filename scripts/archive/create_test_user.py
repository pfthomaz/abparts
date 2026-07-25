#!/usr/bin/env python3

"""
Create a test super admin user for translation testing
"""

import requests
import json

BASE_URL = "http://localhost:8000"

# Try to create a test user directly via API
def create_test_user():
    print("🔧 Creating test super admin user...")
    
    # First, let's try to get existing users to see the API structure
    try:
        response = requests.get(f"{BASE_URL}/users")
        print(f"Users endpoint status: {response.status_code}")
        
        if response.status_code == 401:
            print("❌ Need authentication to access users endpoint")
            
        # Let's try the registration endpoint if it exists
        user_data = {
            "username": "test_admin",
            "email": "test_admin@oraseas.com",
            "password": "test123",
            "name": "Test Administrator",
            "role": "super_admin"
        }
        
        response = requests.post(f"{BASE_URL}/users", json=user_data)
        print(f"User creation status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    create_test_user()