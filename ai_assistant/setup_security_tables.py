#!/usr/bin/env python3
"""
Setup script for security and privacy database tables.

This script creates the necessary tables for:
- Security audit logs
- Data retention tracking
- User data deletion requests
- Sensitive data detection logs
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def setup_security_tables():
    """Create security and privacy tables in the database."""
    
    # Get database connection details from environment
    db_host = os.getenv('DATABASE_HOST', 'localhost')
    db_port = os.getenv('DATABASE_PORT', '5432')
    db_name = os.getenv('DATABASE_NAME', 'abparts_dev')
    db_user = os.getenv('DATABASE_USER', 'abparts_user')
    db_password = os.getenv('DATABASE_PASSWORD', 'abparts_password')
    
    print(f"Connecting to database: {db_name} at {db_host}:{db_port}")
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("Connected successfully!")
        
        # Read and execute SQL file
        sql_file = os.path.join(os.path.dirname(__file__), 'create_security_tables.sql')
        
        if not os.path.exists(sql_file):
            print(f"Error: SQL file not found: {sql_file}")
            return False
        
        print(f"Reading SQL from: {sql_file}")
        
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        print("Executing SQL statements...")
        cursor.execute(sql_content)
        
        print("✓ Security tables created successfully!")
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN (
                'security_audit_logs',
                'data_retention_tracking',
                'user_data_deletion_requests',
                'sensitive_data_detections'
            )
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        print(f"\nCreated {len(tables)} security tables:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check if ai_messages table has is_encrypted column
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'ai_messages' 
            AND column_name = 'is_encrypted'
        """)
        
        if cursor.fetchone():
            print("\n✓ ai_messages table updated with is_encrypted column")
        
        # Check if ai_sessions table has retention_expires_at column
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'ai_sessions' 
            AND column_name = 'retention_expires_at'
        """)
        
        if cursor.fetchone():
            print("✓ ai_sessions table updated with retention_expires_at column")
        
        cursor.close()
        conn.close()
        
        print("\n✅ Security and privacy setup completed successfully!")
        return True
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = setup_security_tables()
    sys.exit(0 if success else 1)
