#!/usr/bin/env python3
"""
Check if the database migration has been completed
"""
import psycopg2

def check_migration():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="abparts_dev",
            user="abparts_user",
            password="abparts_password"
        )
        cur = conn.cursor()
        
        print("🔍 Checking Migration Status...")
        print("=" * 40)
        
        # Check if country column exists
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'organizations' 
            AND column_name = 'country';
        """)
        
        country_column = cur.fetchone()
        if country_column:
            print(f"✅ Country column exists: {country_column[0]} ({country_column[1]})")
        else:
            print("❌ Country column does NOT exist - migration needed")
            return False
        
        # Check if enum exists
        cur.execute("""
            SELECT typname, enumlabel 
            FROM pg_type t 
            JOIN pg_enum e ON t.oid = e.enumtypid 
            WHERE typname = 'countrycode'
            ORDER BY enumlabel;
        """)
        
        enum_values = cur.fetchall()
        if enum_values:
            print("✅ Country enum exists with values:")
            for enum_val in enum_values:
                print(f"   - {enum_val[1]}")
        else:
            print("❌ Country enum does NOT exist - migration needed")
            return False
        
        # Check current organizations
        cur.execute("""
            SELECT name, organization_type, country 
            FROM organizations 
            ORDER BY name;
        """)
        
        orgs = cur.fetchall()
        print(f"\n📊 Current organizations ({len(orgs)}):")
        for org in orgs:
            country_display = org[2] if org[2] else "NULL"
            print(f"   - {org[0]} ({org[1]}) → {country_display}")
        
        cur.close()
        conn.close()
        
        print("\n🎉 Migration check completed!")
        print("✅ Database is ready for country support!")
        return True
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

if __name__ == "__main__":
    success = check_migration()
    if success:
        print("\n📝 Next steps:")
        print("1. Uncomment country fields in models.py and schemas.py")
        print("2. API will restart automatically")
        print("3. New countries will appear in frontend")
    else:
        print("\n📝 You need to run the migration first:")
        print("1. Open pgAdmin: http://localhost:8080")
        print("2. Run the SQL from step_by_step_migration.md")
        print("3. Then uncomment the country fields")