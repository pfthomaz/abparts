#!/usr/bin/env python3
"""
Simple test script to verify the get_warehouse_analytics function works correctly.
"""

import sys
import os
import uuid
from datetime import datetime, timedelta

from app.database import SessionLocal
from app.crud.inventory import get_warehouse_analytics
from app import models

def test_warehouse_analytics():
    """Test the get_warehouse_analytics function with a sample warehouse."""
    db = SessionLocal()
    
    try:
        # Get the first warehouse from the database
        warehouse = db.query(models.Warehouse).first()
        
        if not warehouse:
            print("No warehouses found in database. Please add some test data first.")
            return
        
        print(f"Testing analytics for warehouse: {warehouse.name} (ID: {warehouse.id})")
        
        # Test the analytics function
        analytics = get_warehouse_analytics(
            db=db,
            warehouse_id=warehouse.id,
            days=30
        )
        
        print("\n=== Warehouse Analytics Results ===")
        print(f"Warehouse: {analytics['warehouse_name']}")
        print(f"Period: {analytics['analytics_period']['days']} days")
        
        print(f"\nInventory Summary:")
        print(f"  Total Parts: {analytics['inventory_summary']['total_parts']}")
        print(f"  Total Value: ${analytics['inventory_summary']['total_value']:.2f}")
        print(f"  Low Stock Parts: {analytics['inventory_summary']['low_stock_parts']}")
        print(f"  Out of Stock Parts: {analytics['inventory_summary']['out_of_stock_parts']}")
        
        print(f"\nTop Parts by Value:")
        for i, part in enumerate(analytics['top_parts_by_value'][:5], 1):
            print(f"  {i}. {part['part_name']}: {part['quantity']} @ ${part['unit_price']:.2f} = ${part['total_value']:.2f}")
        
        print(f"\nStock Movements:")
        print(f"  Total Inbound: {analytics['stock_movements']['total_inbound']}")
        print(f"  Total Outbound: {analytics['stock_movements']['total_outbound']}")
        print(f"  Net Change: {analytics['stock_movements']['net_change']}")
        
        print(f"\nTurnover Metrics:")
        print(f"  Average Turnover Days: {analytics['turnover_metrics']['average_turnover_days']}")
        print(f"  Fast Moving Parts: {analytics['turnover_metrics']['fast_moving_parts']}")
        print(f"  Slow Moving Parts: {analytics['turnover_metrics']['slow_moving_parts']}")
        
        print("\n✅ Analytics function completed successfully!")
        
    except Exception as e:
        print(f"❌ Error testing analytics function: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_warehouse_analytics()