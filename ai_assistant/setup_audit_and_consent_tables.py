"""
Setup script for audit logging and consent management tables.

This script creates the necessary database tables for:
- AI interaction audit logs
- Data access logs
- User consent records
- Privacy policy acceptances
- Compliance reports

Run this script after setting up the AI Assistant database.
"""

import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_tables():
    """Create audit and consent management tables."""
    
    # Database connection parameters
    db_params = {
        'host': os.getenv('AI_DB_HOST', 'localhost'),
        'port': os.getenv('AI_DB_PORT', '5432'),
        'database': os.getenv('AI_DB_NAME', 'ai_assistant'),
        'user': os.getenv('AI_DB_USER', 'ai_user'),
        'password': os.getenv('AI_DB_PASSWORD', 'ai_password')
    }
    
    print("Connecting to database...")
    print(f"Host: {db_params['host']}")
    print(f"Database: {db_params['database']}")
    
    try:
        # Connect to database
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        print("\nReading SQL file...")
        with open('create_audit_and_consent_tables.sql', 'r') as f:
            sql_script = f.read()
        
        print("Executing SQL script...")
        cursor.execute(sql_script)
        conn.commit()
        
        print("\n✅ Tables created successfully!")
        
        # Verify tables were created
        print("\nVerifying tables...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN (
                'ai_interaction_audit_logs',
                'data_access_logs',
                'user_consent_records',
                'privacy_policy_acceptances',
                'compliance_reports'
            )
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\nFound {len(tables)} tables:")
        for table in tables:
            print(f"  ✓ {table[0]}")
        
        # Check for triggers
        print("\nVerifying triggers...")
        cursor.execute("""
            SELECT trigger_name, event_object_table
            FROM information_schema.triggers
            WHERE trigger_name IN ('ai_message_audit_trigger', 'ai_session_audit_trigger')
        """)
        
        triggers = cursor.fetchall()
        print(f"\nFound {len(triggers)} triggers:")
        for trigger in triggers:
            print(f"  ✓ {trigger[0]} on {trigger[1]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("Setup completed successfully!")
        print("="*60)
        print("\nNext steps:")
        print("1. Restart the AI Assistant service")
        print("2. Test the audit logging endpoints")
        print("3. Configure consent management in the frontend")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check database connection parameters in .env")
        print("2. Ensure PostgreSQL is running")
        print("3. Verify database user has CREATE TABLE permissions")
        raise


if __name__ == "__main__":
    print("="*60)
    print("AI Assistant - Audit & Consent Tables Setup")
    print("="*60)
    setup_tables()
