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

    print("=== Machine Hours Table Analysis ===")
    
    # Check if machine_hours table exists
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'machine_hours';
    """)
    table_exists = cur.fetchone()
    
    if table_exists:
        print("✅ machine_hours table exists")
        
        # Get table structure
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'machine_hours' 
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        
        print(f"\nmachine_hours table has {len(columns)} columns:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} (nullable: {col[2]})")
            
        # Check if there are any records
        cur.execute("SELECT COUNT(*) FROM machine_hours;")
        count = cur.fetchone()[0]
        print(f"\nTable has {count} records")
        
        # Check expected columns
        expected_columns = [
            'id', 'machine_id', 'recorded_by_user_id', 'hours_value', 
            'recorded_date', 'notes', 'created_at', 'updated_at'
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
        print("❌ machine_hours table does not exist")
        print("\nThe table needs to be created for machine hours functionality to work.")

    cur.close()
    conn.close()

except Exception as e:
    print(f"Database error: {e}")