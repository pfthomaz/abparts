#!/usr/bin/env python3
"""
Quick script to check if preferred_language column exists in users table
"""

import sys
import os

# Add the backend app to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, inspect
from app.database import SQLALCHEMY_DATABASE_URL

def check_column():
    """Check if preferred_language column exists"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    inspector = inspect(engine)
    
    columns = inspector.get_columns('users')
    column_names = [col['name'] for col in columns]
    
    print("📋 Users table columns:")
    for col in columns:
        marker = "✅" if col['name'] == 'preferred_language' else "  "
        print(f"{marker} {col['name']}: {col['type']}")
    
    if 'preferred_language' in column_names:
        print("\n✅ SUCCESS: preferred_language column exists!")
        print("The localization system is ready to use.")
        return True
    else:
        print("\n❌ ERROR: preferred_language column not found!")
        print("Please run the migration.")
        return False

if __name__ == "__main__":
    success = check_column()
    sys.exit(0 if success else 1)
