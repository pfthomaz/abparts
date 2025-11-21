#!/usr/bin/env python3
"""Run the database migration to add shipped_date column."""

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
    
    # Add shipped_date column
    print("Adding shipped_date column to customer_orders table...")
    cursor.execute("""
        ALTER TABLE customer_orders 
        ADD COLUMN IF NOT EXISTS shipped_date TIMESTAMP WITH TIME ZONE;
    """)
    
    conn.commit()
    print("✅ Migration completed successfully!")
    
    # Verify the column was added
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'customer_orders' AND column_name = 'shipped_date';
    """)
    
    result = cursor.fetchone()
    if result:
        print(f"✅ Verified: shipped_date column exists ({result[1]})")
    else:
        print("❌ Error: shipped_date column not found after migration")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
