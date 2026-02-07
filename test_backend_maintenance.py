#!/usr/bin/env python3
"""
Test script to verify backend maintenance endpoints are working
Run with: docker-compose exec api python test_backend_maintenance.py
"""

import sys
from app.database import SessionLocal
from app.models import Machine, MaintenanceProtocol, User

def test_database_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        # Simple query to test connection
        db.execute("SELECT 1")
        print("✅ Database connection: OK")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database connection: FAILED - {e}")
        return False

def test_machines_data():
    """Test if machines exist in database"""
    try:
        db = SessionLocal()
        machines = db.query(Machine).all()
        count = len(machines)
        
        if count > 0:
            print(f"✅ Machines in database: {count}")
            for machine in machines[:3]:  # Show first 3
                print(f"   - {machine.name or machine.model} ({machine.serial_number})")
            if count > 3:
                print(f"   ... and {count - 3} more")
        else:
            print("⚠️  No machines in database")
            print("   You need to create at least one machine to use maintenance features")
        
        db.close()
        return count > 0
    except Exception as e:
        print(f"❌ Failed to query machines: {e}")
        return False

def test_protocols_data():
    """Test if maintenance protocols exist in database"""
    try:
        db = SessionLocal()
        protocols = db.query(MaintenanceProtocol).all()
        count = len(protocols)
        
        if count > 0:
            print(f"✅ Maintenance protocols in database: {count}")
            for protocol in protocols[:3]:  # Show first 3
                print(f"   - {protocol.name} ({protocol.protocol_type})")
            if count > 3:
                print(f"   ... and {count - 3} more")
        else:
            print("⚠️  No maintenance protocols in database")
            print("   Run: docker-compose exec api python add_sample_protocols.py")
        
        db.close()
        return count > 0
    except Exception as e:
        print(f"❌ Failed to query protocols: {e}")
        return False

def test_users_data():
    """Test if users exist in database"""
    try:
        db = SessionLocal()
        users = db.query(User).filter(User.is_active == True).all()
        count = len(users)
        
        if count > 0:
            print(f"✅ Active users in database: {count}")
        else:
            print("⚠️  No active users in database")
        
        db.close()
        return count > 0
    except Exception as e:
        print(f"❌ Failed to query users: {e}")
        return False

def main():
    print("=" * 60)
    print("Backend Maintenance Endpoints Test")
    print("=" * 60)
    print()
    
    # Test database connection
    if not test_database_connection():
        print("\n❌ Database connection failed. Check your .env file and database container.")
        sys.exit(1)
    
    print()
    
    # Test data
    has_machines = test_machines_data()
    print()
    has_protocols = test_protocols_data()
    print()
    has_users = test_users_data()
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    if has_machines and has_protocols and has_users:
        print("✅ All checks passed! Backend should be working.")
        print()
        print("If the frontend still shows errors:")
        print("1. Hard refresh the browser (Cmd+Shift+R or Ctrl+Shift+R)")
        print("2. Check browser console for JavaScript errors")
        print("3. Check Network tab for failed API requests")
    else:
        print("⚠️  Some data is missing:")
        if not has_machines:
            print("   - Create machines in the Machines page")
        if not has_protocols:
            print("   - Run: docker-compose exec api python add_sample_protocols.py")
        if not has_users:
            print("   - Create a user account")

if __name__ == "__main__":
    main()
