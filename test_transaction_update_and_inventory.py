#!/usr/bin/env python3
"""
Test transaction updates and verify inventory calculation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

# Database connection
DATABASE_URL = "postgresql://abparts_user:abparts_secure_password_2024@localhost:5432/abparts_dev"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

print("=" * 80)
print("TRANSACTION UPDATE AND INVENTORY TEST")
print("=" * 80)
print()

session = Session()

try:
    # Find a recent consumption transaction
    print("1. Finding a recent consumption transaction...")
    print("-" * 80)
    
    result = session.execute(text("""
        SELECT 
            t.id,
            t.transaction_type,
            t.part_id,
            t.from_warehouse_id,
            t.quantity,
            t.notes,
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
    
    transaction = result.fetchone()
    
    if not transaction:
        print("❌ No consumption transactions found")
        sys.exit(1)
    
    trans_id = transaction[0]
    part_id = transaction[2]
    warehouse_id = transaction[3]
    original_qty = float(transaction[4])
    
    print(f"✓ Found transaction: {trans_id}")
    print(f"  Part: {transaction[8]} - {transaction[9]}")
    print(f"  Warehouse: {transaction[10]}")
    print(f"  Original Quantity: {original_qty}")
    print(f"  Notes: {transaction[5]}")
    print(f"  Created: {transaction[7]}")
    print()
    
    # Calculate current inventory BEFORE update
    print("2. Calculating inventory BEFORE update...")
    print("-" * 80)
    
    result = session.execute(text("""
        WITH baseline AS (
            SELECT 
                COALESCE(sai.quantity_after, 0) as baseline_stock,
                COALESCE(sa.adjustment_date, '1900-01-01'::timestamp) as baseline_date
            FROM stock_adjustment_items sai
            JOIN stock_adjustments sa ON sai.stock_adjustment_id = sa.id
            WHERE sa.warehouse_id = :warehouse_id
            AND sai.part_id = :part_id
            ORDER BY sa.adjustment_date DESC
            LIMIT 1
        ),
        transaction_sum AS (
            SELECT COALESCE(SUM(
                CASE 
                    WHEN to_warehouse_id = :warehouse_id THEN quantity
                    WHEN from_warehouse_id = :warehouse_id THEN -quantity
                    ELSE 0
                END
            ), 0) as net_change
            FROM transactions
            WHERE part_id = :part_id
            AND transaction_date > (SELECT baseline_date FROM baseline)
            AND (to_warehouse_id = :warehouse_id OR from_warehouse_id = :warehouse_id)
        )
        SELECT 
            COALESCE((SELECT baseline_stock FROM baseline), 0) as baseline,
            (SELECT net_change FROM transaction_sum) as net_change,
            COALESCE((SELECT baseline_stock FROM baseline), 0) + (SELECT net_change FROM transaction_sum) as current_stock
    """), {"warehouse_id": warehouse_id, "part_id": part_id})
    
    before_calc = result.fetchone()
    print(f"  Baseline: {before_calc[0]}")
    print(f"  Net Change from Transactions: {before_calc[1]}")
    print(f"  Current Stock: {before_calc[2]}")
    print()
    
    # Update the transaction quantity
    new_qty = original_qty + 1.0  # Increase by 1
    print(f"3. Updating transaction quantity from {original_qty} to {new_qty}...")
    print("-" * 80)
    
    session.execute(text("""
        UPDATE transactions
        SET quantity = :new_qty,
            notes = COALESCE(notes, '') || ' [Updated for testing]'
        WHERE id = :trans_id
    """), {"new_qty": new_qty, "trans_id": trans_id})
    
    session.commit()
    print(f"✓ Transaction updated")
    print()
    
    # Verify the update
    print("4. Verifying transaction was updated...")
    print("-" * 80)
    
    result = session.execute(text("""
        SELECT quantity, notes
        FROM transactions
        WHERE id = :trans_id
    """), {"trans_id": trans_id})
    
    updated = result.fetchone()
    print(f"  New Quantity: {float(updated[0])}")
    print(f"  Notes: {updated[1]}")
    
    if float(updated[0]) == new_qty:
        print("  ✓ Update confirmed in database")
    else:
        print(f"  ❌ Update failed! Expected {new_qty}, got {float(updated[0])}")
    print()
    
    # Calculate inventory AFTER update
    print("5. Calculating inventory AFTER update...")
    print("-" * 80)
    
    result = session.execute(text("""
        WITH baseline AS (
            SELECT 
                COALESCE(sai.quantity_after, 0) as baseline_stock,
                COALESCE(sa.adjustment_date, '1900-01-01'::timestamp) as baseline_date
            FROM stock_adjustment_items sai
            JOIN stock_adjustments sa ON sai.stock_adjustment_id = sa.id
            WHERE sa.warehouse_id = :warehouse_id
            AND sai.part_id = :part_id
            ORDER BY sa.adjustment_date DESC
            LIMIT 1
        ),
        transaction_sum AS (
            SELECT COALESCE(SUM(
                CASE 
                    WHEN to_warehouse_id = :warehouse_id THEN quantity
                    WHEN from_warehouse_id = :warehouse_id THEN -quantity
                    ELSE 0
                END
            ), 0) as net_change
            FROM transactions
            WHERE part_id = :part_id
            AND transaction_date > (SELECT baseline_date FROM baseline)
            AND (to_warehouse_id = :warehouse_id OR from_warehouse_id = :warehouse_id)
        )
        SELECT 
            COALESCE((SELECT baseline_stock FROM baseline), 0) as baseline,
            (SELECT net_change FROM transaction_sum) as net_change,
            COALESCE((SELECT baseline_stock FROM baseline), 0) + (SELECT net_change FROM transaction_sum) as current_stock
    """), {"warehouse_id": warehouse_id, "part_id": part_id})
    
    after_calc = result.fetchone()
    print(f"  Baseline: {after_calc[0]}")
    print(f"  Net Change from Transactions: {after_calc[1]}")
    print(f"  Current Stock: {after_calc[2]}")
    print()
    
    # Compare
    print("6. Comparison:")
    print("-" * 80)
    print(f"  Stock BEFORE update: {before_calc[2]}")
    print(f"  Stock AFTER update: {after_calc[2]}")
    print(f"  Expected change: -{1.0} (consumption increased by 1)")
    print(f"  Actual change: {float(after_calc[2]) - float(before_calc[2])}")
    
    expected_change = -1.0  # Since we increased consumption, stock should decrease
    actual_change = float(after_calc[2]) - float(before_calc[2])
    
    if abs(actual_change - expected_change) < 0.01:
        print("  ✓ Inventory calculation is CORRECT!")
    else:
        print(f"  ❌ Inventory calculation is WRONG!")
        print(f"     Expected: {expected_change}, Got: {actual_change}")
    
    print()
    print("7. Rolling back test changes...")
    session.rollback()
    print("  ✓ Changes rolled back")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    session.rollback()
finally:
    session.close()

print()
print("=" * 80)
print("TEST COMPLETE")
print("=" * 80)
