#!/usr/bin/env python3
"""
Complete test of the production escalation system.
Tests database schema, escalation service, and email functionality.
"""

import os
import sys
import asyncio
import uuid
from datetime import datetime

# Add the AI assistant app to the path
sys.path.append('/app')

from app.database import get_db_session
from app.services.escalation_service import escalation_service
from app.services.email_service import email_service
from sqlalchemy import text


def test_database_schema():
    """Test that all required tables exist with correct schema."""
    print("🔍 Testing Database Schema")
    print("=" * 50)
    
    try:
        with get_db_session() as db:
            # Check that all required tables exist
            required_tables = [
                'ai_sessions', 'ai_messages', 'support_tickets', 
                'escalation_triggers', 'expert_knowledge', 'expert_feedback'
            ]
            
            for table in required_tables:
                result = db.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = '{table}'
                    );
                """)).fetchone()
                
                if result[0]:
                    print(f"✅ Table '{table}' exists")
                else:
                    print(f"❌ Table '{table}' missing")
                    return False
            
            # Check ai_sessions table structure
            columns = db.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'ai_sessions' 
                ORDER BY ordinal_position;
            """)).fetchall()
            
            print(f"\n📋 ai_sessions table structure:")
            for col in columns:
                print(f"   - {col.column_name}: {col.data_type}")
            
            # Verify primary key is 'id'
            pk_result = db.execute(text("""
                SELECT column_name 
                FROM information_schema.key_column_usage 
                WHERE table_name = 'ai_sessions' 
                AND constraint_name LIKE '%pkey%';
            """)).fetchone()
            
            if pk_result and pk_result.column_name == 'id':
                print("✅ Primary key is 'id' (correct)")
            else:
                print(f"❌ Primary key issue: {pk_result.column_name if pk_result else 'None'}")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Database schema test failed: {e}")
        return False


def test_session_creation():
    """Test creating AI sessions with correct schema."""
    print("\n🔧 Testing Session Creation")
    print("=" * 50)
    
    try:
        session_id = str(uuid.uuid4())
        user_id = '45e2bc8a-b780-4886-bc0b-b0ba1655ff93'  # Maria Sefteli
        
        with get_db_session() as db:
            # Create session using 'id' column
            db.execute(text("""
                INSERT INTO ai_sessions (id, user_id, machine_id, status, language, created_at, updated_at)
                VALUES (:id, :user_id, :machine_id, :status, :language, NOW(), NOW())
            """), {
                'id': session_id,
                'user_id': user_id,
                'machine_id': None,
                'status': 'active',
                'language': 'en'
            })
            
            # Verify session was created
            result = db.execute(text("""
                SELECT id, user_id, status, created_at 
                FROM ai_sessions 
                WHERE id = :id
            """), {'id': session_id}).fetchone()
            
            if result:
                print(f"✅ Session created successfully:")
                print(f"   ID: {result.id}")
                print(f"   User: {result.user_id}")
                print(f"   Status: {result.status}")
                print(f"   Created: {result.created_at}")
                return session_id
            else:
                print("❌ Session not found after creation")
                return None
                
    except Exception as e:
        print(f"❌ Session creation failed: {e}")
        return None


async def test_escalation_service(session_id):
    """Test the escalation service functionality."""
    print("\n🚨 Testing Escalation Service")
    print("=" * 50)
    
    try:
        # Test escalation evaluation
        should_escalate, reason, factors = await escalation_service.evaluate_escalation_need(
            session_id=session_id,
            current_confidence=0.2,  # Low confidence to trigger escalation
            steps_completed=3,
            user_feedback='I need help with this machine issue'
        )
        
        print(f"✅ Escalation evaluation completed:")
        print(f"   Should escalate: {should_escalate}")
        print(f"   Reason: {reason}")
        print(f"   Confidence: {factors.get('confidence_score', 'N/A')}")
        
        if should_escalate:
            # Test support ticket creation
            from app.schemas import EscalationReasonEnum, TicketPriorityEnum
            
            ticket_data = await escalation_service.create_support_ticket(
                session_id=session_id,
                escalation_reason=reason,
                priority=TicketPriorityEnum.medium,
                additional_notes="Production test of escalation system"
            )
            
            print(f"✅ Support ticket created:")
            print(f"   Ticket ID: {ticket_data['ticket_id']}")
            print(f"   Ticket Number: {ticket_data['ticket_number']}")
            print(f"   Priority: {ticket_data['priority']}")
            print(f"   Email Sent: {ticket_data.get('email_sent', False)}")
            
            return ticket_data
        else:
            print("ℹ️  No escalation triggered (unexpected for this test)")
            return None
            
    except Exception as e:
        print(f"❌ Escalation service test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_email_configuration():
    """Test email service configuration."""
    print("\n📧 Testing Email Configuration")
    print("=" * 50)
    
    try:
        # Check SMTP configuration
        smtp_server = os.getenv('SMTP_SERVER')
        smtp_username = os.getenv('SMTP_USERNAME')
        from_email = os.getenv('FROM_EMAIL')
        
        print(f"SMTP Server: {smtp_server}")
        print(f"SMTP Username: {smtp_username}")
        print(f"From Email: {from_email}")
        
        if smtp_server and smtp_username and from_email:
            print("✅ SMTP configuration appears complete")
            
            # Test email service initialization
            email_service_instance = email_service
            print(f"✅ Email service initialized:")
            print(f"   Server: {email_service_instance.smtp_server}")
            print(f"   Port: {email_service_instance.smtp_port}")
            print(f"   Use TLS: {email_service_instance.use_tls}")
            print(f"   Support Email: {email_service_instance.support_email}")
            
            return True
        else:
            print("❌ SMTP configuration incomplete")
            print("   Missing environment variables:")
            if not smtp_server:
                print("   - SMTP_SERVER")
            if not smtp_username:
                print("   - SMTP_USERNAME")
            if not from_email:
                print("   - FROM_EMAIL")
            return False
            
    except Exception as e:
        print(f"❌ Email configuration test failed: {e}")
        return False


def test_user_machine_lookup(session_id):
    """Test user and machine information lookup."""
    print("\n👤 Testing User/Machine Lookup")
    print("=" * 50)
    
    try:
        with get_db_session() as db:
            # Test user lookup
            user_query = text("""
                SELECT s.user_id, u.name, u.email, u.role, o.name as organization_name
                FROM ai_sessions s
                LEFT JOIN users u ON s.user_id = u.id
                LEFT JOIN organizations o ON u.organization_id = o.id
                WHERE s.id = :session_id
            """)
            user_result = db.execute(user_query, {'session_id': session_id}).fetchone()
            
            if user_result:
                print(f"✅ User information found:")
                print(f"   Name: {user_result.name}")
                print(f"   Email: {user_result.email}")
                print(f"   Role: {user_result.role}")
                print(f"   Organization: {user_result.organization_name}")
            else:
                print("❌ User information not found")
                return False
            
            # Test machine lookup (may be None for this test)
            machine_query = text("""
                SELECT s.machine_id, m.name, m.model_type, m.serial_number
                FROM ai_sessions s
                LEFT JOIN machines m ON s.machine_id = m.id
                WHERE s.id = :session_id
            """)
            machine_result = db.execute(machine_query, {'session_id': session_id}).fetchone()
            
            if machine_result and machine_result.machine_id:
                print(f"✅ Machine information found:")
                print(f"   Name: {machine_result.name}")
                print(f"   Model: {machine_result.model_type}")
                print(f"   Serial: {machine_result.serial_number}")
            else:
                print("ℹ️  No machine associated with this session (expected for test)")
            
            return True
            
    except Exception as e:
        print(f"❌ User/Machine lookup test failed: {e}")
        return False


async def run_complete_test():
    """Run the complete escalation system test."""
    print("🚀 Production Escalation System Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print()
    
    # Test results
    results = {
        'database_schema': False,
        'session_creation': False,
        'escalation_service': False,
        'email_configuration': False,
        'user_machine_lookup': False
    }
    
    # 1. Test database schema
    results['database_schema'] = test_database_schema()
    
    # 2. Test session creation
    session_id = test_session_creation()
    results['session_creation'] = session_id is not None
    
    if session_id:
        # 3. Test user/machine lookup
        results['user_machine_lookup'] = test_user_machine_lookup(session_id)
        
        # 4. Test escalation service
        ticket_data = await test_escalation_service(session_id)
        results['escalation_service'] = ticket_data is not None
    
    # 5. Test email configuration
    results['email_configuration'] = test_email_configuration()
    
    # Print final results
    print("\n" + "=" * 60)
    print("🏁 FINAL TEST RESULTS")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - ESCALATION SYSTEM READY FOR PRODUCTION!")
        print("\nNext steps:")
        print("1. Test escalation through the production UI")
        print("2. Verify emails are received at abparts_support@oraseas.com")
        print("3. Enable Microsoft 365 SMTP AUTH if emails fail")
    else:
        print("⚠️  SOME TESTS FAILED - REVIEW ISSUES ABOVE")
        print("\nFailed components need attention before production use.")
    
    print(f"\nTest completed at: {datetime.now()}")
    return all_passed


if __name__ == "__main__":
    # Run the complete test
    result = asyncio.run(run_complete_test())
    sys.exit(0 if result else 1)