#!/usr/bin/env python3
"""
Fix status for existing net cleaning records.
Updates records that have end_time but status is still 'in_progress'.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import NetCleaningRecord

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://abparts_user:abparts_password@localhost:5432/abparts_dev')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fix_cleaning_record_statuses():
    """Update status for records that have end_time but are marked as in_progress."""
    db = SessionLocal()
    try:
        # Find records with end_time but status = 'in_progress'
        records_to_fix = db.query(NetCleaningRecord).filter(
            NetCleaningRecord.end_time.isnot(None),
            NetCleaningRecord.status == 'in_progress'
        ).all()
        
        print(f"Found {len(records_to_fix)} records to fix")
        
        for record in records_to_fix:
            print(f"Fixing record {record.id}: setting status to 'completed'")
            record.status = 'completed'
        
        db.commit()
        print(f"Successfully updated {len(records_to_fix)} records")
        
        # Also fix records without end_time but status = 'completed'
        records_to_revert = db.query(NetCleaningRecord).filter(
            NetCleaningRecord.end_time.is_(None),
            NetCleaningRecord.status == 'completed'
        ).all()
        
        if records_to_revert:
            print(f"\nFound {len(records_to_revert)} records with no end_time but marked completed")
            for record in records_to_revert:
                print(f"Fixing record {record.id}: setting status to 'in_progress'")
                record.status = 'in_progress'
            
            db.commit()
            print(f"Successfully updated {len(records_to_revert)} records")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_cleaning_record_statuses()
