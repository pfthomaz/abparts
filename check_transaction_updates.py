#!/usr/bin/env python3
"""
Check if transaction updates are being saved to the database
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

# Database connection
DATABASE_URL = "postgresql://abparts_user:abparts_secure_password_2024@localhost:5432/abparts_dev"
engine = create_engine(DATABASE_URL)

print("=" * 80)
print("TRANSACTION UPDATE DIAGNOSTIC")
print("=" * 80)
print()

with engine.connect() as conn:
    # Check recent transactions
    print("1. Recent Transactions (last 10):")
    print("-" * 80)
    result = conn.execute(text("""
        SELECT 
            id,
            transaction_type,
            part_id,
            quantity,
            transaction_date,
            notes,
            created_at,
            updated_at
        FROM transactions
        ORDER BY created_at DESC
        LIMIT 10
    """))
    
    transactions = result.fetchall()
    if transactions:
        for t in transactions:
            print(f"ID: {t[0]}")
            print(f"  Type: {t[1]}")
            print(f"  Quantity: {t[3]}")
            print(f"  Date: {t[4]}")
            print(f"  Notes: {t[6]}")
            print(f"  Created: {t[7]}")
            print(f"  Updated: {t[8]}")
            if t[7] != t[8]:
                print(f"  ⚠️  UPDATED AFTER CREATION!")
            print()
    else:
        print("No transactions found")
    
    print()
    print("2. Transactions Updated in Last Hour:")
    print("-" * 80)
    one_hour_ago = datetime.now() - timedelta(hours=1)
    result = conn.execute(text("""
        SELECT 
            id,
            transaction_type,
            quantity,
            notes,
            created_at,
            updated_at
        FROM transactions
        WHERE updated_at > created_at
        AND updated_at > :one_hour_ago
        ORDER BY updated_at DESC
    """), {"one_hour_ago": one_hour_ago})
    
    updated = result.fetchall()
    if updated:
        for t in updated:
            print(f"ID: {t[0]}")
            print(f"  Type: {t[1]}")
            print(f"  Quantity: {t[2]}")
            print(f"  Notes: {t[3]}")
            print(f"  Created: {t[4]}")
            print(f"  Updated: {t[5]}")
            print(f"  Time since update: {datetime.now() - t[5]}")
            print()
    else:
        print("No transactions updated in the last hour")
    
    print()
    print("3. Check if 'updated_at' column exists and has trigger:")
    print("-" * 80)
    result = conn.execute(text("""
        SELECT column_name, data_type, column_default
        FROM information_schema.columns
        WHERE table_name = 'transactions'
        AND column_name IN ('created_at', 'updated_at')
    """))
    
    columns = result.fetchall()
    for col in columns:
        print(f"Column: {col[0]}, Type: {col[1]}, Default: {col[2]}")
    
    print()
    print("4. Check for update triggers on transactions table:")
    print("-" * 80)
    result = conn.execute(text("""
        SELECT 
            trigger_name,
            event_manipulation,
            action_statement
        FROM information_schema.triggers
        WHERE event_object_table = 'transactions'
    """))
    
    triggers = result.fetchall()
    if triggers:
        for trig in triggers:
            print(f"Trigger: {trig[0]}")
            print(f"  Event: {trig[1]}")
            print(f"  Action: {trig[2][:100]}...")
            print()
    else:
        print("No triggers found on transactions table")
    
    print()
    print("5. Check part_usage table (if it exists):")
    print("-" * 80)
    result = conn.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'part_usage'
        )
    """))
    
    table_exists = result.fetchone()[0]
    if table_exists:
        print("✓ part_usage table exists")
        
        result = conn.execute(text("""
            SELECT 
                id,
                transaction_id,
                machine_id,
                part_id,
                quantity,
                created_at
            FROM part_usage
            ORDER BY created_at DESC
            LIMIT 5
        """))
        
        usage_records = result.fetchall()
        if usage_records:
            print("\nRecent part_usage records:")
            for rec in usage_records:
                print(f"  ID: {rec[0]}, Transaction: {rec[1]}, Quantity: {rec[4]}")
        else:
            print("No part_usage records found")
    else:
        print("✗ part_usage table does NOT exist")
        print("  Note: Part usage is tracked via transactions table with type='consumption'")

print()
print("=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
