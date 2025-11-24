#!/usr/bin/env python3
"""
Test script to verify PartUsage records are being created from consumption transactions.
Run this on the production server to check the database.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, '/root/abparts/backend')

from app.database import SessionLocal
from app import models
from sqlalchemy import desc

def test_part_usage_records():
    """Check if PartUsage records exist for recent consumption transactions."""
    db = SessionLocal()
    
    try:
        print("=" * 80)
        print("CHECKING RECENT CONSUMPTION TRANSACTIONS")
        print("=" * 80)
        
        # Get recent consumption transactions
        recent_transactions = db.query(models.Transaction).filter(
            models.Transaction.transaction_type == 'consumption',
            models.Transaction.machine_id.isnot(None)
        ).order_by(desc(models.Transaction.created_at)).limit(5).all()
        
        print(f"\nFound {len(recent_transactions)} recent consumption transactions with machine_id\n")
        
        for trans in recent_transactions:
            print(f"Transaction ID: {trans.id}")
            print(f"  Machine ID: {trans.machine_id}")
            print(f"  Part ID: {trans.part_id}")
            print(f"  Quantity: {trans.quantity}")
            print(f"  Date: {trans.transaction_date}")
            print(f"  Created: {trans.created_at}")
            
            # Check if corresponding PartUsage record exists
            part_usage = db.query(models.PartUsage).filter(
                models.PartUsage.machine_id == trans.machine_id,
                models.PartUsage.part_id == trans.part_id,
                models.PartUsage.quantity == trans.quantity
            ).first()
            
            if part_usage:
                print(f"  ✅ PartUsage record EXISTS (ID: {part_usage.id})")
            else:
                print(f"  ❌ PartUsage record MISSING")
            print()
        
        print("=" * 80)
        print("CHECKING ALL PART_USAGE RECORDS")
        print("=" * 80)
        
        all_part_usage = db.query(models.PartUsage).order_by(desc(models.PartUsage.created_at)).limit(10).all()
        print(f"\nTotal PartUsage records in database: {db.query(models.PartUsage).count()}")
        print(f"Showing last 10:\n")
        
        for usage in all_part_usage:
            print(f"PartUsage ID: {usage.id}")
            print(f"  Machine ID: {usage.machine_id}")
            print(f"  Part ID: {usage.part_id}")
            print(f"  Quantity: {usage.quantity}")
            print(f"  Usage Date: {usage.usage_date}")
            print(f"  Created: {usage.created_at}")
            print()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_part_usage_records()
