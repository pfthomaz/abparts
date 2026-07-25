#!/usr/bin/env python3
"""
Test script for escalation email functionality.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the AI assistant path to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_assistant'))

from ai_assistant.app.services.email_service import email_service


async def test_escalation_email():
    """Test sending an escalation email."""
    
    # Sample ticket data
    ticket_data = {
        "ticket_id": "test-ticket-123",
        "ticket_number": "AB-20260109-0001",
        "priority": "high",
        "status": "open",
        "escalation_reason": "user_request",
        "session_id": "test-session-456",
        "session_summary": """=== TROUBLESHOOTING SESSION SUMMARY ===
Session ID: test-session-456
Created: 2026-01-09 14:30:00
Language: en
Machine ID: test-machine-789

=== INITIAL DIAGNOSTIC ASSESSMENT ===
Problem Category: hydraulic
Confidence Level: low
Likely Causes: pressure_loss, seal_failure
Safety Warnings: high_pressure_system
Requires Expert: True

=== TROUBLESHOOTING STEPS ATTEMPTED ===
Step 1: Check hydraulic fluid level - ✓ Completed (Unsuccessful)
  User Feedback: Fluid level is normal but pressure still low
Step 2: Inspect hydraulic connections - ✓ Completed (Unsuccessful)
  User Feedback: No visible leaks found
Step 3: Test pressure relief valve - ⏳ In Progress
  User Feedback: Not sure how to test this safely

=== CONVERSATION HIGHLIGHTS ===
User Message 1: The machine is losing hydraulic pressure during operation
User Message 2: I checked the fluid and connections but can't find the problem
User Message 3: I need expert help with the pressure system""",
        "machine_context": {
            "machine_details": {
                "name": "AutoBoss Pro 3000",
                "model_type": "AB-3000",
                "serial_number": "AB3000-2023-001"
            }
        },
        "expert_contact_info": {
            "primary_contact": {
                "name": "AutoBoss Hydraulic Systems",
                "phone": "+1-800-AUTOBOSS ext. 202",
                "email": "hydraulic@autoboss.com",
                "hours": "Monday-Friday 9AM-5PM EST",
                "specialization": "Hydraulic systems and pressure issues"
            }
        },
        "created_at": datetime.utcnow().isoformat(),
        "additional_notes": "User reports intermittent pressure loss during high-load operations. Safety concern due to high-pressure hydraulic system."
    }
    
    # Sample user info
    user_info = {
        "user_id": "user-123",
        "full_name": "John Technician",
        "email": "john.tech@customer.com",
        "role": "user",
        "organization_name": "Customer Organization Ltd"
    }
    
    # Sample machine info
    machine_info = {
        "machine_id": "machine-789",
        "name": "AutoBoss Pro 3000",
        "model_type": "AB-3000",
        "serial_number": "AB3000-2023-001",
        "latest_hours": 1250.5,
        "location": "Production Floor A"
    }
    
    print("Testing escalation email functionality...")
    print(f"Support email: {email_service.support_email}")
    print(f"SMTP server: {email_service.smtp_server}:{email_service.smtp_port}")
    print(f"From email: {email_service.from_email}")
    print()
    
    # Test email sending
    success = email_service.send_escalation_notification(
        ticket_data=ticket_data,
        user_info=user_info,
        machine_info=machine_info
    )
    
    if success:
        print("✅ Escalation email sent successfully!")
        print(f"Email sent to: {email_service.support_email}")
        print(f"Ticket number: {ticket_data['ticket_number']}")
    else:
        print("❌ Failed to send escalation email")
        print("Check SMTP configuration and credentials")
    
    return success


if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_escalation_email())
    sys.exit(0 if result else 1)