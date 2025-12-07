#!/usr/bin/env python3
"""
Manually set a user's preferred_language
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from app.database import SQLALCHEMY_DATABASE_URL

def set_language(username, language='el'):
    """Set user's preferred language"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if user exists
        result = conn.execute(
            text("SELECT id, username, email FROM users WHERE username = :username"),
            {"username": username}
        )
        user = result.fetchone()
        
        if not user:
            print(f"❌ User '{username}' not found!")
            return False
        
        print(f"✅ Found user: {user[1]} ({user[2]})")
        
        # Update preferred_language
        conn.execute(
            text("UPDATE users SET preferred_language = :language WHERE username = :username"),
            {"language": language, "username": username}
        )
        conn.commit()
        
        print(f"✅ Set preferred_language to '{language}' for user '{username}'")
        
        # Verify
        result = conn.execute(
            text("SELECT preferred_language FROM users WHERE username = :username"),
            {"username": username}
        )
        new_lang = result.fetchone()[0]
        print(f"✅ Verified: preferred_language = {new_lang}")
        
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python set_user_language.py <username> [language]")
        print("Example: python set_user_language.py admin el")
        print()
        print("Available languages: en, el, ar, es")
        sys.exit(1)
    
    username = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else 'el'
    
    set_language(username, language)
