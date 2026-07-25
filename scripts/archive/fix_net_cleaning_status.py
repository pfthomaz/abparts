#!/usr/bin/env python3
"""
Fix net cleaning records status based on end_time values.
This script updates any records that have end_time but status='in_progress'
or records without end_time but status='completed'.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import SessionLocal
from app.models import NetCleaningRecord


def fix_status():
    """Fix status values for all net cleaning records."""
    db = SessionLocal()
    try:
        # Get all records
        records = db.query(NetCleaningRecord).all()
        
        fixed_count = 0
        for record in records:
            old_status = record.status
            
            # Determine correct status based on end_time
            if record.end_time is not None:
                correct_status = 'completed'
            else:
                correct_status = 'in_progress'
            
            # Update if status is incorrect
            if record.status != correct_status:
                record.status = correct_status
                fixed_count += 1
                print(f"Fixed record {record.id}: {old_status} -> {correct_status}")
        
        if fixed_count > 0:
            db.commit()
            print(f"\n✓ Fixed {fixed_count} record(s)")
        else:
            print("✓ All records have correct status values")
        
        # Show summary
        total = len(records)
        in_progress = sum(1 for r in records if r.status == 'in_progress')
        completed = sum(1 for r in records if r.status == 'completed')
        
        print(f"\nSummary:")
        print(f"  Total records: {total}")
        print(f"  In Progress: {in_progress}")
        print(f"  Completed: {completed}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        db.rollback()
        return 1
    finally:
        db.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(fix_status())
