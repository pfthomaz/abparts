#!/usr/bin/env python3

"""
Manual script to run the protocol translations migration
Use this if Alembic is having issues detecting the migration
"""

import os
import sys

def run_migration():
    """Run the protocol translations migration manually"""
    
    print("🔄 Running Protocol Translations Migration...")
    print("=" * 50)
    
    # Try the standard Alembic command first
    print("📋 Step 1: Checking current migration status...")
    os.system("docker compose exec api alembic current")
    
    print("\n📋 Step 2: Checking available migrations...")
    os.system("docker compose exec api alembic heads")
    
    print("\n📋 Step 3: Showing migration history...")
    os.system("docker compose exec api alembic history")
    
    print("\n🚀 Step 4: Attempting to run migration to head...")
    result = os.system("docker compose exec api alembic upgrade head")
    
    if result == 0:
        print("✅ Migration completed successfully!")
        
        print("\n📋 Step 5: Verifying migration status...")
        os.system("docker compose exec api alembic current")
        
        print("\n🎉 Protocol translations migration should now be applied!")
        print("You can now use the translation management features.")
        
    else:
        print("❌ Migration failed. Let's try specific migration...")
        print("\n🔧 Attempting specific migration...")
        result2 = os.system("docker compose exec api alembic upgrade 06_add_protocol_translations")
        
        if result2 == 0:
            print("✅ Specific migration completed!")
        else:
            print("❌ Migration still failing. Manual intervention needed.")
            print("\n💡 Troubleshooting steps:")
            print("1. Check if the migration file exists in backend/alembic/versions/")
            print("2. Verify the revision IDs match correctly")
            print("3. Check for Python syntax errors in the migration file")
            print("4. Ensure the database connection is working")

if __name__ == "__main__":
    run_migration()