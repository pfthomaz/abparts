#!/usr/bin/env python3
"""
Diagnose why inventory isn't updating after transaction edits
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from decimal import Decimal

# Database connection
DATABASE_URL = "postgresql://abparts_user:abparts_secure_password_2024@localhost:5432/abparts_dev"
engine = create_engine(DATABASE_URL)

print("=" * 80)
print("INVENTORY CALCULATION DIAGNOSTIC")
print("=" * 80)
print()

with engine.connect() as conn:
    # Find a recent consumption transaction
    print("1. Finding recent consumption transaction...")
    print("-" * 80)
    
    result = conn.execute(text("""
        SELECT 
            t.id,
            t.part_id,
            t.from_warehouse_id,
            t.quantity,
            t.transaction_date,
            t.created_at,
            p.part_number,
            p.name as part_name,
            w.name as warehouse_name
        FROM transactions t
        JOIN parts p ON t.part_id = p.id
        LEFT JOIN warehouses w ON t.from_warehouse_id = w.id
        WHERE t.transaction_type = 'consumption'
        AND t.from_warehouse_id IS NOT NULL
        ORDER BY t.created_at DESC
        LIMIT 1
    """))
    
    trans = result.fetchone()
    if not trans:
        print("No consumption transactions found")
        sys.exit(1)
    
    trans_id, part_id, warehouse_id, quantity, trans_date, created_at, part_num, part_name, wh_name = trans
    
    print(f"Transaction ID: {trans_id}")
    print(f"Part: {part_num} - {part_name}")
    print(f"Warehouse: {wh_name}")
    print(f"Quantity: {quantity}")
    print(f"Date: {trans_date}")
    print()
    
    # Calculate inventory using the same logic as inventory_calculator.py
    print("2. Calculating inventory (same logic as backend)...")
    print("-" * 80)
    
    # Find last stock adjustment
    result = conn.execute(text("""
        SELECT 
            sai.quantity_after,
            sa.adjustment_date
        FROM stock_adjustment_items sai
        JOIN stock_adjustments sa ON sai.stock_adjustment_id = sa.id
        WHERE sa.warehouse_id = :warehouse_id
        AND sai.part_id = :part_id
        ORDER BY sa.adjustment_date DESC
        LIMIT 1
    """), {"warehouse_id": warehouse_id, "part_id": part_id})
    
    adjustment = result.fetchone()
    if adjustment:
        baseline_stock = float(adjustment[0])
        baseline_date = adjustment[1]
        print(f"Baseline from adjustment: {baseline_stock} (date: {baseline_date})")
    else:
        baseline_stock = 0.0
        baseline_date = '1900-01-01'
        print(f"No adjustment found, baseline: {baseline_stock}")
    
    # Sum all transactions after baseline
    result = conn.execute(text("""
        SELECT 
            SUM(CASE 
                WHEN to_warehouse_id = :warehouse_id THEN quantity
                WHEN from_warehouse_id = :warehouse_id THEN -quantity
                ELSE 0
            END) as net_change,
            COUNT(*) as transaction_count
        FROM transactions
        WHERE part_id = :part_id
        AND transaction_date > :baseline_date
        AND (to_warehouse_id = :warehouse_id OR from_warehouse_id = :warehouse_id)
    """), {
        "warehouse_id": warehouse_id,
        "part_id": part_id,
        "baseline_date": baseline_date
    })
    
    trans_sum = result.fetchone()
    net_change = float(trans_sum[0] or 0)
    trans_count = trans_sum[1]
    
    print(f"Transactions after baseline: {trans_count}")
    print(f"Net change from transactions: {net_change}")
    print(f"Calculated stock: {baseline_stock + net_change}")
    print()
    
    # Check what the inventory table shows
    print("3. Checking inventory table (cached value)...")
    print("-" * 80)
    
    result = conn.execute(text("""
        SELECT 
            current_stock,
            last_updated
        FROM inventory
        WHERE warehouse_id = :warehouse_id
        AND part_id = :part_id
    """), {"warehouse_id": warehouse_id, "part_id": part_id})
    
    inv = result.fetchone()
    if inv:
        print(f"Cached stock: {float(inv[0])}")
        print(f"Last updated: {inv[1]}")
        
        if float(inv[0]) != (baseline_stock + net_change):
            print(f"⚠️  MISMATCH! Cached: {float(inv[0])}, Calculated: {baseline_stock + net_change}")
        else:
            print("✓ Cached value matches calculated value")
    else:
        print("No inventory record found")
    print()
    
    # List all transactions for this part/warehouse
    print("4. All transactions for this part/warehouse:")
    print("-" * 80)
    
    result = conn.execute(text("""
        SELECT 
            id,
            transaction_type,
            CASE 
                WHEN to_warehouse_id = :warehouse_id THEN '+' || quantity::text
                WHEN from_warehouse_id = :warehouse_id THEN '-' || quantity::text
                ELSE '0'
            END as impact,
            transaction_date,
            notes
        FROM transactions
        WHERE part_id = :part_id
        AND (to_warehouse_id = :warehouse_id OR from_warehouse_id = :warehouse_id)
        ORDER BY transaction_date DESC
        LIMIT 10
    """), {"warehouse_id": warehouse_id, "part_id": part_id})
    
    transactions = result.fetchall()
    for t in transactions:
        print(f"  {t[0][:8]}... | {t[1]:12} | {t[2]:10} | {t[3]} | {t[4] or ''}")
    
    print()
    
    # Check if there's a part_usage_item for this transaction
    print("5. Checking for linked part_usage_item...")
    print("-" * 80)
    
    result = conn.execute(text("""
        SELECT 
            pui.id,
            pui.quantity,
            pur.usage_date,
            pur.machine_id
        FROM part_usage_items pui
        JOIN part_usage_records pur ON pui.usage_record_id = pur.id
        WHERE pur.machine_id = (
            SELECT machine_id FROM transactions WHERE id = :trans_id
        )
        AND pui.part_id = :part_id
        AND pur.usage_date BETWEEN :trans_date - INTERVAL '5 minutes' 
                                AND :trans_date + INTERVAL '5 minutes'
        ORDER BY ABS(EXTRACT(EPOCH FROM (pur.usage_date - :trans_date)))
        LIMIT 1
    """), {"trans_id": trans_id, "part_id": part_id, "trans_date": trans_date})
    
    usage_item = result.fetchone()
    if usage_item:
        print(f"✓ Found linked part_usage_item: {usage_item[0]}")
        print(f"  Quantity: {float(usage_item[1])}")
        print(f"  Usage date: {usage_item[2]}")
        
        if float(usage_item[1]) != float(quantity):
            print(f"  ⚠️  MISMATCH! Transaction: {quantity}, Part usage item: {usage_item[1]}")
    else:
        print("✗ No linked part_usage_item found")

print()
print("=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
print()
print("KEY FINDINGS:")
print("- Inventory calculation uses transactions table")
print("- Cached inventory in 'inventory' table may be stale")
print("- Part_usage_items may be out of sync with transactions")
print()
print("SOLUTION:")
print("1. Ensure transaction updates work")
print("2. Refresh cached inventory after updates")
print("3. Keep part_usage_items in sync")
print()
