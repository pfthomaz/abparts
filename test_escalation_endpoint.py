#!/usr/bin/env python3
"""
Test script for escalation endpoint functionality.
"""

import requests
import json
import sys

def test_escalation_endpoint():
    """Test the escalation endpoint directly."""
    
    # Test data
    session_id = "550e8400-e29b-41d4-a716-446655440000"  # Valid UUID format
    escalation_data = {
        "escalation_reason": "user_request",
        "priority": "high",
        "additional_notes": "User needs expert help with hydraulic system troubleshooting"
    }
    
    # Get a token (using the same approach as the frontend)
    # For testing, we'll use a dummy token since the mock auth accepts any token
    token = "test-token-123"
    
    # API endpoint
    base_url = "http://localhost:8001"  # AI Assistant service
    api_url = f"{base_url}/api/ai/sessions/{session_id}/escalate"
    
    print(f"Testing escalation endpoint: {api_url}")
    print(f"Session ID: {session_id}")
    print(f"Escalation data: {json.dumps(escalation_data, indent=2)}")
    print()
    
    try:
        # Make the request
        response = requests.post(
            api_url,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            },
            json=escalation_data,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Escalation created successfully!")
            print(f"Response data: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Escalation failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error response text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = test_escalation_endpoint()
    sys.exit(0 if success else 1)