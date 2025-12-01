#!/usr/bin/env python3
import psycopg2

# Database connection
try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        database="abparts_dev",
        user="abparts_user",
        password="abparts_password"
    )
    cur = conn.cursor()

    # Check if inventory table exists
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('inventory', 'warehouses', 'parts');
    """)
    tables = cur.fetchall()
    print("Existing tables:")
    for table in tables:
        print(f"  - {table[0]}")

    # Check parts table structure
    if any('parts' in table for table in tables):
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'parts' ORDER BY ordinal_position;")
        parts_columns = cur.fetchall()
        print(f"\nParts table columns ({len(parts_columns)}):")
        for col in parts_columns:
            print(f"  - {col[0]}: {col[1]}")

    # Check inventory table structure if it exists
    if any('inventory' in table for table in tables):
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'inventory' ORDER BY ordinal_position;")
        inventory_columns = cur.fetchall()
        print(f"\nInventory table columns ({len(inventory_columns)}):")
        for col in inventory_columns:
            print(f"  - {col[0]}: {col[1]}")
    else:
        print("\n❌ Inventory table does not exist")

    # Check warehouses table structure if it exists
    if any('warehouses' in table for table in tables):
        cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'warehouses' ORDER BY ordinal_position;")
        warehouse_columns = cur.fetchall()
        print(f"\nWarehouses table columns ({len(warehouse_columns)}):")
        for col in warehouse_columns:
            print(f"  - {col[0]}: {col[1]}")
    else:
        print("\n❌ Warehouses table does not exist")

    cur.close()
    conn.close()

except Exception as e:
    print(f"Database error: {e}")