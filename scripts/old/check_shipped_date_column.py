#!/usr/bin/env python3
"""Check if shipped_date column was added to customer_orders table."""

import psycopg2
import os

# Database connection parameters
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'abparts_dev')
DB_USER = os.getenv('DB_USER', 'abparts_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'abparts_password')

try:
    # Connect to database
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    cursor = conn.cursor()
    
    # Check customer_orders table structure
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'customer_orders'
        ORDER BY ordinal_position;
    """)
    
    print("✅ customer_orders table columns:")
    print("-" * 60)
    for row in cursor.fetchall():
        print(f"  {row[0]:<30} {row[1]:<20} nullable={row[2]}")
    
    # Check if shipped_date exists
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'customer_orders' AND column_name = 'shipped_date';
    """)
    
    result = cursor.fetchone()
    if result:
        print("\n✅ SUCCESS: shipped_date column exists!")
    else:
        print("\n❌ ERROR: shipped_date column NOT found!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
