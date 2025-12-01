#!/bin/bash

echo "Debugging stock calculation..."
echo ""

docker compose exec -T api python << 'EOF'
import sys
sys.path.insert(0, '/app')

from app.database import SessionLocal
from app import models
from sqlalchemy import and_, or_
import uuid
from decimal import Decimal

db = SessionLocal()
try:
    warehouse_id = uuid.UUID('1e019a80-2852-4269-b3d3-2c5a46ded47f')
    part_id = uuid.UUID('e1457957-9441-48d9-a161-75faff16bd5d')
    
    print("=== STOCK ADJUSTMENTS ===")
    adjustments = db.query(
        models.StockAdjustmentItem.quantity_after,
        models.StockAdjustment.adjustment_date
    ).join(
        models.StockAdjustment,
        models.StockAdjustmentItem.stock_adjustment_id == models.StockAdjustment.id
    ).filter(
        and_(
            models.StockAdjustment.warehouse_id == warehouse_id,
            models.StockAdjustmentItem.part_id == part_id
        )
    ).order_by(
        models.StockAdjustment.adjustment_date.desc()
    ).all()
    
    if adjustments:
        for adj in adjustments:
            print(f"  Date: {adj.adjustment_date}, Quantity After: {adj.quantity_after}")
        baseline_stock = adjustments[0].quantity_after
        baseline_date = adjustments[0].adjustment_date
        print(f"\nBaseline: {baseline_stock} as of {baseline_date}")
    else:
        print("  No adjustments found")
        baseline_stock = Decimal('0')
        baseline_date = None
    
    print("\n=== TRANSACTIONS AFTER BASELINE ===")
    query = db.query(models.Transaction).filter(
        and_(
            models.Transaction.part_id == part_id,
            or_(
                models.Transaction.to_warehouse_id == warehouse_id,
                models.Transaction.from_warehouse_id == warehouse_id
            )
        )
    )
    
    if baseline_date:
        query = query.filter(models.Transaction.transaction_date > baseline_date)
    
    transactions = query.order_by(models.Transaction.transaction_date).all()
    
    total_change = Decimal('0')
    for txn in transactions:
        if txn.to_warehouse_id == warehouse_id:
            change = txn.quantity
            direction = "IN"
        elif txn.from_warehouse_id == warehouse_id:
            change = -txn.quantity
            direction = "OUT"
        else:
            change = Decimal('0')
            direction = "???"
        
        total_change += change
        print(f"  {txn.transaction_date} | {txn.transaction_type:12} | {direction:3} | {change:+8} | Running: {baseline_stock + total_change}")
    
    print(f"\n=== FINAL CALCULATION ===")
    print(f"Baseline: {baseline_stock}")
    print(f"Changes:  {total_change}")
    print(f"Final:    {baseline_stock + total_change}")
    
finally:
    db.close()
EOF
