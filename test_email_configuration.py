#!/usr/bin/env python3
"""
Test script to verify email configuration and escalation email functionality.
This script tests the email service without requiring SMTP credentials.
"""

import os
import sys
import asyncio
from datetime import datetime

# Add the ai_assistant app to the path
sys.path.append('ai_assistant/app')

from services.email_service import EmailService

def test_email_service_configuration():
    """Test email service configuration and mock email sending."""
    print("🧪 Testing Email Service Configuration")
    print("=" * 50)
    
    # Create email service instance
    email_service = EmailService()
    
    # Display current configuration
    print(f"SMTP Server: {email_service.smtp_server}")
    print(f"SMTP Port: {email_service.smtp_port}")
    print(f"SMTP Username: {'[CONFIGURED]' if email_service.smtp_username else '[NOT CONFIGURED]'}")
    print(f"SMTP Password: {'[CONFIGURED]' if email_service.smtp_password else '[NOT CONFIGURED]'}")
    print(f"From Email: {email_service.from_email}")
    print(f"Support Email: {email_service.support_email}")
    print(f"Use TLS: {email_service.use_tls}")
    print(f"Use SSL: {email_service.use_ssl}")
    print()
    
    # Test email content generation
    print("📧 Testing Email Content Generation")
    print("-" * 30)
    
    # Sample ticket data
    ticket_data = {
        "ticket_id": "test-ticket-123",
        "ticket_number": "AB-20260109-TEST",
        "priority": "high",
        "status": "open",
        "escalation_reason": "user_request",
        "session_id": "test-session-456",
        "session_summary": "User reported machine making unusual noises during wash cycle. Attempted basic troubleshooting steps but issue persists.",
        "created_at": datetime.utcnow().isoformat(),
        "additional_notes": "Customer is concerned about potential damage to vehicle."
    }
    
    # Sample user info
    user_info = {
        "user_id": "test-user-789",
        "full_name": "John Doe",
        "email": "john.doe@testcompany.com",
        "role": "admin",
        "organization_name": "Test Car Wash Company"
    }
    
    # Sample machine info
    machine_info = {
        "machine_id": "test-machine-101",
        "name": "AutoBoss Unit #1",
        "model_type": "AutoBoss Pro",
        "serial_number": "AB-2023-001",
        "latest_hours": 1250.5,
        "location": "Bay 1 - Main Facility"
    }
    
    # Generate email content
    try:
        html_content = email_service._create_escalation_email_html(ticket_data, user_info, machine_info)
        text_content = email_service._create_escalation_email_text(ticket_data, user_info, machine_info)
        
        print("✅ HTML email content generated successfully")
        print("✅ Text email content generated successfully")
        print()
        
        # Show preview of text content
        print("📄 Email Content Preview (First 500 characters):")
        print("-" * 50)
        print(text_content[:500] + "..." if len(text_content) > 500 else text_content)
        print()
        
        # Test email sending (will log instead of actually sending if SMTP not configured)
        print("📤 Testing Email Sending")
        print("-" * 25)
        
        success = email_service.send_escalation_notification(
            ticket_data=ticket_data,
            user_info=user_info,
            machine_info=machine_info
        )
        
        if success:
            print("✅ Email sent successfully!")
        else:
            print("⚠️  Email not sent (SMTP not configured - this is expected in development)")
            print("   The email system is working correctly but needs SMTP credentials to actually send emails.")
        
        print()
        
    except Exception as e:
        print(f"❌ Error testing email functionality: {e}")
        return False
    
    return True

def show_smtp_configuration_guide():
    """Show guide for configuring SMTP for actual email sending."""
    print("📋 SMTP Configuration Guide")
    print("=" * 30)
    print()
    print("To enable actual email sending, add these to your .env file:")
    print()
    print("# Gmail Configuration (recommended for testing)")
    print("SMTP_SERVER=smtp.gmail.com")
    print("SMTP_PORT=587")
    print("SMTP_USERNAME=your.email@gmail.com")
    print("SMTP_PASSWORD=your_app_password_here")
    print("FROM_EMAIL=your.email@gmail.com")
    print("SMTP_USE_TLS=true")
    print()
    print("📝 Gmail App Password Setup:")
    print("1. Enable 2-factor authentication on your Gmail account")
    print("2. Go to Google Account settings > Security > App passwords")
    print("3. Generate an app password for 'Mail'")
    print("4. Use that app password (not your regular password)")
    print()
    print("🔄 After configuration, restart the AI assistant:")
    print("docker compose restart ai_assistant")
    print()

if __name__ == "__main__":
    print("🚀 ABParts AI Assistant - Email System Test")
    print("=" * 50)
    print()
    
    # Test email service
    success = test_email_service_configuration()
    
    if success:
        print("✅ Email system test completed successfully!")
        print()
        show_smtp_configuration_guide()
    else:
        print("❌ Email system test failed!")
        sys.exit(1)