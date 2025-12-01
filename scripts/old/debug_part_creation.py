#!/usr/bin/env python3
import psycopg2
import json

try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="abparts_dev",
        user="abparts_user",
        password="abparts_password"
    )
    cur = conn.cursor()

    print("=== Parts Table Analysis ===")
    
    # Check if parts table exists and get its structure
    cur.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'parts' 
        ORDER BY ordinal_position;
    """)
    columns = cur.fetchall()
    
    if columns:
        print(f"Parts table has {len(columns)} columns:")
        actual_columns = []
        for col in columns:
            actual_columns.append(col[0])
            print(f"  - {col[0]}: {col[1]} (nullable: {col[2]})")
            
        # Check what columns the model expects
        expected_columns = [
            'id', 'part_number', 'name', 'description', 'part_type', 
            'is_proprietary', 'unit_of_measure', 'manufacturer', 'part_code',
            'serial_number', 'manufacturer_part_number', 'manufacturer_delivery_time_days',
            'local_supplier_delivery_time_days', 'image_urls', 'created_at', 'updated_at'
        ]
        
        missing_columns = [col for col in expected_columns if col not in actual_columns]
        extra_columns = [col for col in actual_columns if col not in expected_columns]
        
        print(f"\n=== Column Analysis ===")
        if missing_columns:
            print(f"❌ Missing columns: {missing_columns}")
        if extra_columns:
            print(f"⚠️  Extra columns: {extra_columns}")
        if not missing_columns and not extra_columns:
            print("✅ All expected columns are present")
            
        # Try to create a test part to see what fails
        print(f"\n=== Test Part Creation ===")
        test_data = {
            'part_number': 'TEST-001',
            'name': 'Test Part',
            'description': 'Test description',
            'part_type': 'consumable',
            'is_proprietary': False,
            'unit_of_measure': 'pieces'
        }
        
        # Build INSERT statement with only existing columns
        available_columns = [col for col in test_data.keys() if col in actual_columns]
        missing_required = [col for col in test_data.keys() if col not in actual_columns]
        
        if missing_required:
            print(f"❌ Cannot create part - missing required columns: {missing_required}")
        else:
            print("✅ All required columns are available for part creation")
            
    else:
        print("❌ Parts table does not exist")

    cur.close()
    conn.close()

except Exception as e:
    print(f"Database error: {e}")