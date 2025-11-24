#!/usr/bin/env python3
"""
Test script to check if PartUsage records are being created locally.
Run from the backend directory.
"""

import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app import models
from sqlalchemy import desc

def check_part_usage():
    db = SessionLocal()
    
    try:
        print("\n" + "=" * 80)
        print("CHECKING PART_USAGE TABLE")
        print("=" * 80)
        
        # Count total PartUsage records
        total_count = db.query(models.PartUsage).count()
        print(f"\nTotal PartUsage records: {total_count}")
        
        if total_count == 0:
            print("❌ No PartUsage records found!")
            print("\nThis means the create_part_usage_from_transaction function is not being called.")
        else:
            print(f"✅ Found {total_count} PartUsage records")
            
            # Show the most recent ones
            recent = db.query(models.PartUsage).order_by(desc(models.PartUsage.created_at)).limit(5).all()
            print("\nMost recent PartUsage records:")
            for pu in recent:
                print(f"\n  ID: {pu.id}")
                print(f"  Machine ID: {pu.machine_id}")
                print(f"  Part ID: {pu.part_id}")
                print(f"  Quantity: {pu.quantity}")
                print(f"  Usage Date: {pu.usage_date}")
                print(f"  Created: {pu.created_at}")
        
        print("\n" + "=" * 80)
        print("CHECKING CONSUMPTION TRANSACTIONS")
        print("=" * 80)
        
        # Check consumption transactions with machine_id
        consumption_count = db.query(models.Transaction).filter(
            models.Transaction.transaction_type == 'consumption',
            models.Transaction.machine_id.isnot(None)
        ).count()
        
        print(f"\nTotal consumption transactions with machine_id: {consumption_count}")
        
        if consumption_count > 0:
            recent_trans = db.query(models.Transaction).filter(
                models.Transaction.transaction_type == 'consumption',
                models.Transaction.machine_id.isnot(None)
            ).order_by(desc(models.Transaction.created_at)).limit(3).all()
            
            print("\nMost recent consumption transactions:")
            for trans in recent_trans:
                print(f"\n  Transaction ID: {trans.id}")
                print(f"  Machine ID: {trans.machine_id}")
                print(f"  Part ID: {trans.part_id}")
                print(f"  Quantity: {trans.quantity}")
                print(f"  Created: {trans.created_at}")
                
                # Check if matching PartUsage exists
                matching_pu = db.query(models.PartUsage).filter(
                    models.PartUsage.machine_id == trans.machine_id,
                    models.PartUsage.part_id == trans.part_id,
                    models.PartUsage.quantity == trans.quantity
                ).first()
                
                if matching_pu:
                    print(f"  ✅ Matching PartUsage found: {matching_pu.id}")
                else:
                    print(f"  ❌ NO matching PartUsage record!")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_part_usage()
