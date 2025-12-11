#!/usr/bin/env python3
"""
Run migration to add logo_url and profile_photo_url columns
"""

import psycopg2
import os

# Database connection parameters
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'abparts_dev')
DB_USER = os.getenv('DB_USER', 'abparts_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'abparts_password')

def run_migration():
    """Run the migration to add image columns"""
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        cursor = conn.cursor()
        
        print("Running migration to add image columns...")
        
        # Add logo_url to organizations
        cursor.execute("""
            ALTER TABLE organizations 
            ADD COLUMN IF NOT EXISTS logo_url VARCHAR(500);
        """)
        print("✓ Added logo_url to organizations table")
        
        # Add profile_photo_url to users
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS profile_photo_url VARCHAR(500);
        """)
        print("✓ Added profile_photo_url to users table")
        
        # Commit changes
        conn.commit()
        print("\n✓ Migration completed successfully!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n✗ Migration failed: {e}")
        raise

if __name__ == "__main__":
    run_migration()
