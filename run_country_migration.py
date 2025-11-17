#!/usr/bin/env python3
"""
Run the country support migration
"""
import psycopg2
import os

def run_migration():
    print("🗄️  Running Country Support Migration")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="abparts_dev",
            user="abparts_user",
            password="abparts_password"
        )
        
        # Enable autocommit for DDL operations
        conn.autocommit = True
        cur = conn.cursor()
        
        print("1. Connected to database successfully")
        
        # Read and execute migration script
        with open('add_country_support.sql', 'r') as f:
            migration_sql = f.read()
        
        print("2. Executing migration script...")
        cur.execute(migration_sql)
        
        print("3. Migration completed successfully!")
        
        # Verify the migration
        print("\n4. Verifying migration...")
        
        # Check if country column exists
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'organizations' 
            AND column_name = 'country';
        """)
        
        country_column = cur.fetchone()
        if country_column:
            print(f"   ✅ Country column added: {country_column[0]} ({country_column[1]})")
        else:
            print("   ❌ Country column not found")
        
        # Check enum type
        cur.execute("""
            SELECT typname 
            FROM pg_type 
            WHERE typname = 'countrycode';
        """)
        
        enum_type = cur.fetchone()
        if enum_type:
            print(f"   ✅ Country enum created: {enum_type[0]}")
        else:
            print("   ❌ Country enum not found")
        
        # Show current organizations
        cur.execute("""
            SELECT name, organization_type, country 
            FROM organizations 
            ORDER BY organization_type, name;
        """)
        
        orgs = cur.fetchall()
        print(f"\n5. Current organizations ({len(orgs)}):")
        for org in orgs:
            country_display = org[2] if org[2] else "Not set"
            print(f"   - {org[0]} ({org[1]}) - Country: {country_display}")
        
        cur.close()
        conn.close()
        
        print("\n🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = run_migration()
    if not success:
        exit(1)