#!/usr/bin/env python3
"""
Direct test of maintenance CRUD functions to isolate the datetime serialization issue.
"""

import sys
import os
import uuid
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import get_db
from app.crud import machines
from app import schemas
from app.models import MaintenanceType

def test_maintenance_crud():
    """Test maintenance CRUD functions directly."""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Test getting maintenance history
        print("Testing get_machine_maintenance_history...")
        machine_id = "fcbf094f-a852-4d80-940a-e38d4da739e8"
        
        maintenance_history = machines.get_machine_maintenance_history(db, machine_id, 0, 10)
        print(f"Retrieved {len(maintenance_history)} maintenance records")
        
        if maintenance_history:
            first_record = maintenance_history[0]
            print(f"First record type: {type(first_record)}")
            print(f"First record attributes: {dir(first_record)}")
            print(f"Maintenance date: {first_record.maintenance_date} (type: {type(first_record.maintenance_date)})")
            print(f"Maintenance type: {first_record.maintenance_type} (type: {type(first_record.maintenance_type)})")
        
        # Test creating maintenance
        print("\nTesting create_machine_maintenance...")
        maintenance_data = schemas.MaintenanceCreate(
            machine_id=uuid.UUID(machine_id),
            maintenance_date=datetime.utcnow(),
            maintenance_type=MaintenanceType.SCHEDULED,
            performed_by_user_id=uuid.UUID("f6abc555-5b6c-6f7a-8b9c-0d123456789a"),
            description="Direct test maintenance"
        )
        
        new_maintenance = machines.create_machine_maintenance(db, maintenance_data)
        print(f"Created maintenance record: {new_maintenance.id}")
        print(f"Created record type: {type(new_maintenance)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_maintenance_crud()