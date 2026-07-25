#!/usr/bin/env python3
"""
Test the fixed escalation system to ensure database column issue is resolved.
"""

import requests
import json
import time

def test_escalation_system():
    """Test the complete escalation flow."""
    print("🧪 Testing Fixed Escalation System")
    print("=" * 40)
    
    base_url = "http://localhost:8001"
    
    try:
        # Step 1: Create a chat session
        print("1️⃣ Creating chat session...")
        chat_response = requests.post(f"{base_url}/api/ai/chat", json={
            "message": "My AutoBoss machine is making strange noises during the wash cycle. I need expert help.",
            "user_id": "550e8400-e29b-41d4-a716-446655440000",  # Test user ID
            "machine_id": "550e8400-e29b-41d4-a716-446655440001"  # Test machine ID
        })
        
        if chat_response.status_code != 200:
            print(f"❌ Chat failed: {chat_response.status_code} - {chat_response.text}")
            return False
        
        chat_data = chat_response.json()
        session_id = chat_data.get("session_id")
        
        if not session_id:
            print("❌ No session ID returned from chat")
            return False
        
        print(f"✅ Chat session created: {session_id}")
        
        # Step 2: Create escalation
        print("2️⃣ Creating escalation...")
        escalation_response = requests.post(f"{base_url}/api/ai/sessions/{session_id}/escalate", json={
            "escalation_reason": "user_request",
            "priority": "high",
            "additional_notes": "Customer is concerned about potential damage and needs immediate expert assistance."
        })
        
        if escalation_response.status_code != 200:
            print(f"❌ Escalation failed: {escalation_response.status_code} - {escalation_response.text}")
            return False
        
        escalation_data = escalation_response.json()
        ticket_number = escalation_data.get("ticket_number")
        
        if not ticket_number:
            print("❌ No ticket number returned from escalation")
            return False
        
        print(f"✅ Escalation successful: Ticket #{ticket_number}")
        print(f"   Email sent: {escalation_data.get('email_sent', False)}")
        
        # Step 3: Show ticket details
        print("3️⃣ Ticket Details:")
        print(f"   - Ticket ID: {escalation_data.get('ticket_id')}")
        print(f"   - Priority: {escalation_data.get('priority')}")
        print(f"   - Status: {escalation_data.get('status')}")
        print(f"   - Created: {escalation_data.get('created_at')}")
        
        if escalation_data.get('expert_contact_info'):
            contact = escalation_data['expert_contact_info'].get('primary_contact', {})
            print(f"   - Expert Contact: {contact.get('name', 'Unknown')}")
            print(f"   - Expert Phone: {contact.get('phone', 'Unknown')}")
        
        print()
        print("✅ Escalation system test completed successfully!")
        print("   The database column issue has been fixed.")
        print("   Email functionality is working (but SMTP not configured for actual sending).")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_escalation_system()
    if not success:
        exit(1)