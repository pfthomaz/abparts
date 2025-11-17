#!/usr/bin/env python3
import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="abparts_dev",
        user="abparts_user",
        password="abparts_password"
    )
    cur = conn.cursor()

    # Check if parts table exists
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'parts';
    """)
    table_exists = cur.fetchone()
    
    if table_exists:
        print("✅ Parts table exists")
        
        # Get parts table columns
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'parts' 
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        
        print(f"\nParts table has {len(columns)} columns:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
            
        # Try a simple count query
        cur.execute("SELECT COUNT(*) FROM parts;")
        count = cur.fetchone()[0]
        print(f"\nParts table has {count} records")
        
        # Check for any missing columns that the model expects
        expected_columns = [
            'id', 'part_number', 'name', 'description', 'part_type', 
            'is_proprietary', 'unit_of_measure', 'manufacturer', 'part_code',
            'serial_number', 'manufacturer_part_number', 'manufacturer_delivery_time_days',
            'local_supplier_delivery_time_days', 'image_urls', 'created_at', 'updated_at'
        ]
        
        actual_columns = [col[0] for col in columns]
        missing_columns = [col for col in expected_columns if col not in actual_columns]
        extra_columns = [col for col in actual_columns if col not in expected_columns]
        
        if missing_columns:
            print(f"\n❌ Missing columns: {missing_columns}")
        if extra_columns:
            print(f"\n⚠️  Extra columns: {extra_columns}")
        if not missing_columns and not extra_columns:
            print("\n✅ All expected columns are present")
            
    else:
        print("❌ Parts table does not exist")

    cur.close()
    conn.close()

except Exception as e:
    print(f"Database error: {e}")