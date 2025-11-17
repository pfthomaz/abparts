#!/usr/bin/env python3
import psycopg2
import sys

def run_migration():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432", 
            database="abparts_dev",
            user="abparts_user",
            password="abparts_password"
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        print("Connected to database")
        
        # Check if country column already exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'organizations' 
            AND column_name = 'country';
        """)
        
        if cur.fetchone():
            print("Country column already exists")
            return True
        
        print("Creating country enum...")
        try:
            cur.execute("CREATE TYPE countrycode AS ENUM ('GR', 'UK', 'NO', 'CA', 'NZ', 'TR');")
            print("Country enum created")
        except psycopg2.errors.DuplicateObject:
            print("Country enum already exists")
        
        print("Adding country column...")
        cur.execute("ALTER TABLE organizations ADD COLUMN country countrycode;")
        print("Country column added")
        
        print("Updating existing organizations...")
        cur.execute("UPDATE organizations SET country = 'GR' WHERE country IS NULL;")
        updated_count = cur.rowcount
        print(f"Updated {updated_count} organizations with default country")
        
        print("Creating index...")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_organizations_country ON organizations(country);")
        print("Index created")
        
        cur.close()
        conn.close()
        
        print("Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Migration error: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)