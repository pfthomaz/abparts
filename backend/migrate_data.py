#!/usr/bin/env python3
"""
ABParts Data Migration Script

This script migrates existing data to align with the new business model schema.
It includes validation, progress tracking, and rollback capabilities.

Usage:
    python migrate_data.py [--dry-run] [--backup-file=path] [--rollback]
"""

import sys
import argparse
import json
import os
from datetime import datetime
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.migration_utils import DataMigrator, MigrationError
from app.database import get_db


def save_backup_to_file(backup_data: dict, filepath: str):
    """Save backup data to a JSON file"""
    try:
        # Convert datetime objects to strings for JSON serialization
        def serialize_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        with open(filepath, 'w') as f:
            json.dump(backup_data, f, indent=2, default=serialize_datetime)
        print(f"Backup saved to: {filepath}")
        return True
    except Exception as e:
        print(f"Failed to save backup: {str(e)}")
        return False


def load_backup_from_file(filepath: str) -> dict:
    """Load backup data from a JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Failed to load backup: {str(e)}")
        return {}


def run_dry_run():
    """Run a dry-run migration to check what would be changed"""
    print("="*60)
    print("DRY RUN MODE - No changes will be made")
    print("="*60)
    
    migrator = DataMigrator()
    
    try:
        db = next(get_db())
        
        # Run pre-migration validation
        print("\n1. Pre-migration validation...")
        pre_issues = migrator.validator.validate_pre_migration(db)
        if pre_issues:
            print("Issues found:")
            for issue in pre_issues:
                print(f"  - {issue}")
        else:
            print("No issues found.")
        
        # Check current data state
        print("\n2. Current data summary...")
        
        # Count records by type
        from app.models import Organization, User, Part, Warehouse, Inventory, Machine
        
        org_count = db.query(Organization).count()
        user_count = db.query(User).count()
        part_count = db.query(Part).count()
        warehouse_count = db.query(Warehouse).count()
        inventory_count = db.query(Inventory).count()
        machine_count = db.query(Machine).count()
        
        print(f"  Organizations: {org_count}")
        print(f"  Users: {user_count}")
        print(f"  Parts: {part_count}")
        print(f"  Warehouses: {warehouse_count}")
        print(f"  Inventory records: {inventory_count}")
        print(f"  Machines: {machine_count}")
        
        # Analyze organization types
        print("\n3. Organization analysis...")
        orgs = db.query(Organization).all()
        for org in orgs:
            org_type = getattr(org, 'organization_type', 'Not set')
            print(f"  {org.name}: {org_type}")
        
        # Analyze user roles
        print("\n4. User role analysis...")
        users = db.query(User).all()
        role_counts = {}
        for user in users:
            role = getattr(user, 'role', 'Not set')
            role_counts[role] = role_counts.get(role, 0) + 1
        
        for role, count in role_counts.items():
            print(f"  {role}: {count} users")
        
        # Check inventory without warehouses
        print("\n5. Inventory analysis...")
        inventory_without_warehouse = 0
        for inv in db.query(Inventory).all():
            if not hasattr(inv, 'warehouse_id') or not inv.warehouse_id:
                inventory_without_warehouse += 1
        
        print(f"  Inventory records needing warehouse assignment: {inventory_without_warehouse}")
        
        print("\n6. Migration impact summary...")
        print("  The migration would:")
        print("  - Assign organization types based on names")
        print("  - Update user roles and ensure proper constraints")
        print("  - Classify parts as consumable/bulk_material")
        print("  - Create default warehouses where needed")
        print("  - Migrate inventory to warehouse-based model")
        print("  - Create initial transaction records")
        
        print("\nDry run completed. Use --run to execute the migration.")
        
    except Exception as e:
        print(f"Dry run failed: {str(e)}")
    finally:
        db.close()


def run_migration(backup_file: str = None):
    """Run the actual migration"""
    print("="*60)
    print("RUNNING DATA MIGRATION")
    print("="*60)
    
    migrator = DataMigrator()
    
    try:
        db = next(get_db())
        
        # Run migration
        result = migrator.run_full_migration(db)
        
        # Save backup if requested
        if backup_file and migrator.backup_data:
            save_backup_to_file(migrator.backup_data, backup_file)
        
        # Print detailed results
        print("\n" + "="*50)
        print("MIGRATION COMPLETED SUCCESSFULLY")
        print("="*50)
        
        print(f"Duration: {result['duration_seconds']:.2f} seconds")
        print(f"Steps completed: {result['steps_completed']}/{result['total_steps']}")
        print(f"Success rate: {result['success_rate']:.1%}")
        
        if result['errors']:
            print(f"\nErrors ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"  - {error}")
                
        if result['warnings']:
            print(f"\nWarnings ({len(result['warnings'])}):")
            for warning in result['warnings']:
                print(f"  - {warning}")
                
        print(f"\nDetailed Results:")
        for step, stats in result['migration_results'].items():
            print(f"  {step.replace('_', ' ').title()}:")
            for key, value in stats.items():
                print(f"    {key}: {value}")
        
        return True
        
    except MigrationError as e:
        print(f"\nMIGRATION FAILED: {str(e)}")
        print("\nAttempting rollback...")
        
        if migrator.rollback_migration(db):
            print("Rollback completed successfully.")
        else:
            print("Rollback failed. Manual intervention required.")
            print("Check the database state and restore from backup if necessary.")
        
        return False
        
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {str(e)}")
        return False
        
    finally:
        db.close()


def run_rollback(backup_file: str):
    """Run rollback from backup file"""
    print("="*60)
    print("RUNNING MIGRATION ROLLBACK")
    print("="*60)
    
    if not os.path.exists(backup_file):
        print(f"Backup file not found: {backup_file}")
        return False
    
    backup_data = load_backup_from_file(backup_file)
    if not backup_data:
        print("Failed to load backup data")
        return False
    
    migrator = DataMigrator()
    migrator.backup_data = backup_data
    
    try:
        db = next(get_db())
        
        if migrator.rollback_migration(db):
            print("Rollback completed successfully")
            return True
        else:
            print("Rollback failed")
            return False
            
    except Exception as e:
        print(f"Rollback error: {str(e)}")
        return False
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description='ABParts Data Migration Tool')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Run in dry-run mode (no changes made)')
    parser.add_argument('--run', action='store_true',
                       help='Execute the migration')
    parser.add_argument('--backup-file', type=str,
                       help='Path to save/load backup file')
    parser.add_argument('--rollback', action='store_true',
                       help='Rollback migration from backup file')
    
    args = parser.parse_args()
    
    # Default backup file
    if not args.backup_file:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.backup_file = f"migration_backup_{timestamp}.json"
    
    if args.rollback:
        if not args.backup_file:
            print("Backup file required for rollback")
            sys.exit(1)
        success = run_rollback(args.backup_file)
    elif args.dry_run:
        run_dry_run()
        success = True
    elif args.run:
        success = run_migration(args.backup_file)
    else:
        print("Please specify --dry-run, --run, or --rollback")
        parser.print_help()
        sys.exit(1)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()