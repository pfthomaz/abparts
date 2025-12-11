import psycopg2

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
    
    print("Running migration...")
    
    # Create enum
    cur.execute("CREATE TYPE countrycode AS ENUM ('GR', 'UK', 'NO', 'CA', 'NZ', 'TR');")
    print("Enum created")
    
    # Add column
    cur.execute("ALTER TABLE organizations ADD COLUMN country countrycode;")
    print("Column added")
    
    # Update existing orgs
    cur.execute("UPDATE organizations SET country = 'GR' WHERE country IS NULL;")
    print("Updated existing organizations")
    
    print("Migration completed!")
    
except Exception as e:
    print(f"Migration result: {e}")
    # This might fail if already exists, which is OK