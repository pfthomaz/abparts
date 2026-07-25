#!/usr/bin/env python3
"""
Test script for chat and escalation functionality.
"""

import requests
import json
import sys
import uuid

def test_chat_and_escalation():
    """Test the complete chat and escalation flow."""
    
    # Test data
    user_id = "f6abc555-5b6c-6f7a-8b9c-0d123456789a"  # Superadmin user
    machine_id = None  # No specific machine for this test
    
    # Chat request
    chat_data = {
        "message": "My AutoBoss machine is making strange noises and losing pressure. I need help troubleshooting this issue.",
        "user_id": user_id,
        "machine_id": machine_id,
        "language": "en",
        "conversation_history": []
    }
    
    # Get a token (using the same approach as the frontend)
    token = "test-token-123"
    
    # API endpoints
    base_url = "http://localhost:8001"
    chat_url = f"{base_url}/api/ai/chat"
    
    print("=== Testing Chat API ===")
    print(f"Chat URL: {chat_url}")
    print(f"User ID: {user_id}")
    print(f"Message: {chat_data['message']}")
    print()
    
    try:
        # Make chat request
        response = requests.post(
            chat_url,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            },
            json=chat_data,
            timeout=30
        )
        
        print(f"Chat response status: {response.status_code}")
        
        if response.status_code == 200:
            chat_result = response.json()
            session_id = chat_result.get('session_id')
            print("✅ Chat request successful!")
            print(f"Session ID: {session_id}")
            print(f"AI Response: {chat_result.get('response', '')[:100]}...")
            print()
            
            if session_id:
                # Now test escalation
                print("=== Testing Escalation API ===")
                escalation_data = {
                    "escalation_reason": "user_request",
                    "priority": "high",
                    "additional_notes": "User reports strange noises and pressure loss. Needs expert assistance with troubleshooting."
                }
                
                escalation_url = f"{base_url}/api/ai/sessions/{session_id}/escalate"
                print(f"Escalation URL: {escalation_url}")
                print(f"Escalation data: {json.dumps(escalation_data, indent=2)}")
                print()
                
                escalation_response = requests.post(
                    escalation_url,
                    headers={
                        'Content-Type': 'application/json',
                        'Authorization': f'Bearer {token}'
                    },
                    json=escalation_data,
                    timeout=30
                )
                
                print(f"Escalation response status: {escalation_response.status_code}")
                
                if escalation_response.status_code == 201:
                    escalation_result = escalation_response.json()
                    print("✅ Escalation successful!")
                    print(f"Ticket ID: {escalation_result.get('ticket_id')}")
                    print(f"Ticket Number: {escalation_result.get('ticket_number')}")
                    print(f"Status: {escalation_result.get('status')}")
                    return True
                else:
                    print(f"❌ Escalation failed with status {escalation_response.status_code}")
                    try:
                        error_data = escalation_response.json()
                        print(f"Error response: {json.dumps(error_data, indent=2)}")
                    except:
                        print(f"Error response text: {escalation_response.text}")
                    return False
            else:
                print("❌ No session ID returned from chat")
                return False
        else:
            print(f"❌ Chat failed with status {response.status_code}")
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
    success = test_chat_and_escalation()
    sys.exit(0 if success else 1)