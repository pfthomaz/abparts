#!/usr/bin/env python3
"""
Check if users have preferred_language set in the database
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from app.database import SQLALCHEMY_DATABASE_URL

def check_users():
    """Check users table for preferred_language"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if column exists
        result = conn.execute(text("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'preferred_language'
        """))
        
        column_info = result.fetchone()
        
        if column_info:
            print("✅ Column 'preferred_language' exists!")
            print(f"   Type: {column_info[1]}")
            print(f"   Default: {column_info[2]}")
            print()
            
            # Check actual user data
            result = conn.execute(text("""
                SELECT id, username, email, preferred_language
                FROM users
                LIMIT 10
            """))
            
            users = result.fetchall()
            print(f"📋 Found {len(users)} users:")
            print()
            for user in users:
                lang = user[3] if user[3] else "NULL"
                print(f"  - {user[1]} ({user[2]}): preferred_language = {lang}")
            
            # Count by language
            result = conn.execute(text("""
                SELECT preferred_language, COUNT(*) as count
                FROM users
                GROUP BY preferred_language
            """))
            
            print()
            print("📊 Language distribution:")
            for row in result.fetchall():
                lang = row[0] if row[0] else "NULL"
                print(f"  - {lang}: {row[1]} users")
                
        else:
            print("❌ Column 'preferred_language' does NOT exist!")
            print("   Run the migration: docker-compose exec api alembic upgrade head")

if __name__ == "__main__":
    check_users()
