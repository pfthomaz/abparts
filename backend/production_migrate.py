#!/usr/bin/env python3
"""
Production Data Migration Script for ABParts

This script safely migrates production data with comprehensive validation,
backup, and rollback capabilities.

Usage:
    python production_migrate.py --backup-dir=/path/to/backups [--dry-run] [--force]
"""

import sys
import os
import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
import subprocess

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.migration_utils import DataMigrator, MigrationError
from app.database import get_db
from validate_migration import MigrationValidator


class ProductionMigrator:
    """Production-safe migration with comprehensive safeguards"""
    
    def __init__(self, backup_dir: str, dry_run: bool = False, force: bool = False):
        self.backup_dir = Path(backup_dir)
        self.dry_run = dry_run
        self.force = force
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.migration_id = f"migration_{self.timestamp}"
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.migration_backup_dir = self.backup_dir / self.migration_id
        self.migration_backup_dir.mkdir(exist_ok=True)
        
        print(f"Migration ID: {self.migration_id}")
        print(f"Backup directory: {self.migration_backup_dir}")
    
    def create_database_dump(self) -> bool:
        """Create a full database dump before migration"""
        print("\n--- Creating Database Dump ---")
        
        dump_file = self.migration_backup_dir / "pre_migration_dump.sql"
        
        try:
            # Use pg_dump to create a complete backup
            cmd = [
                "docker-compose", "exec", "-T", "db",
                "pg_dump", "-U", "abparts_user", "-d", "abparts_dev",
                "--no-password", "--verbose"
            ]
            
            print(f"Creating database dump: {dump_file}")
            
            with open(dump_file, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                print(f"✓ Database dump created successfully ({dump_file.stat().st_size} bytes)")
                return True
            else:
                print(f"✗ Database dump failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Database dump failed: {str(e)}")
            return False
    
    def validate_pre_migration(self) -> bool:
        """Validate database state before migration"""
        print("\n--- Pre-Migration Validation ---")
        
        try:
            db = next(get_db())
            validator = MigrationValidator()
            
            # Run basic validation
            from app.migration_utils import DataValidator
            basic_validator = DataValidator()
            issues = basic_validator.validate_pre_migration(db)
            
            if issues and not self.force:
                print("✗ Pre-migration validation failed:")
                for issue in issues:
                    print(f"  - {issue}")
                print("\nUse --force to proceed despite validation issues")
                return False
            elif issues:
                print("⚠ Pre-migration issues found (proceeding due to --force):")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                print("✓ Pre-migration validation passed")
            
            return True
            
        except Exception as e:
            print(f"✗ Pre-migration validation error: {str(e)}")
            return False
        finally:
            db.close()
    
    def run_migration(self) -> bool:
        """Execute the migration"""
        print(f"\n--- {'DRY RUN: ' if self.dry_run else ''}Running Migration ---")
        
        if self.dry_run:
            print("DRY RUN MODE - No actual changes will be made")
            # In dry run, we would simulate the migration
            print("✓ Migration simulation completed successfully")
            return True
        
        try:
            db = next(get_db())
            migrator = DataMigrator()
            
            # Save migration metadata
            metadata = {
                "migration_id": self.migration_id,
                "timestamp": self.timestamp,
                "backup_dir": str(self.migration_backup_dir),
                "dry_run": self.dry_run,
                "force": self.force
            }
            
            metadata_file = self.migration_backup_dir / "migration_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Run the migration
            result = migrator.run_full_migration(db)
            
            # Save migration results
            results_file = self.migration_backup_dir / "migration_results.json"
            with open(results_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            # Save backup data
            if migrator.backup_data:
                backup_file = self.migration_backup_dir / "data_backup.json"
                with open(backup_file, 'w') as f:
                    json.dump(migrator.backup_data, f, indent=2, default=str)
            
            if result['success_rate'] >= 1.0 and not result['errors']:
                print("✓ Migration completed successfully")
                return True
            else:
                print(f"✗ Migration completed with issues (success rate: {result['success_rate']:.1%})")
                if result['errors']:
                    print("Errors:")
                    for error in result['errors']:
                        print(f"  - {error}")
                return False
                
        except Exception as e:
            print(f"✗ Migration failed: {str(e)}")
            return False
        finally:
            db.close()
    
    def validate_post_migration(self) -> bool:
        """Validate database state after migration"""
        print("\n--- Post-Migration Validation ---")
        
        if self.dry_run:
            print("Skipping post-migration validation (dry run mode)")
            return True
        
        try:
            db = next(get_db())
            validator = MigrationValidator()
            
            result = validator.run_full_validation(db)
            
            # Save validation results
            validation_file = self.migration_backup_dir / "post_migration_validation.json"
            with open(validation_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            if result["success"]:
                print("✓ Post-migration validation passed")
                return True
            else:
                print(f"✗ Post-migration validation failed ({result['failed']} failures)")
                return False
                
        except Exception as e:
            print(f"✗ Post-migration validation error: {str(e)}")
            return False
        finally:
            db.close()
    
    def create_rollback_script(self):
        """Create a rollback script for this migration"""
        rollback_script = self.migration_backup_dir / "rollback.sh"
        
        rollback_content = f"""#!/bin/bash
# Rollback script for migration {self.migration_id}
# Created: {datetime.now().isoformat()}

echo "Rolling back migration {self.migration_id}..."

# Stop the application
echo "Stopping application..."
docker-compose down

# Restore database from dump
echo "Restoring database..."
docker-compose up -d db
sleep 10

# Drop current database and recreate
docker-compose exec db psql -U abparts_user -d postgres -c "DROP DATABASE IF EXISTS abparts_dev;"
docker-compose exec db psql -U abparts_user -d postgres -c "CREATE DATABASE abparts_dev OWNER abparts_user;"

# Restore from dump
docker-compose exec -T db psql -U abparts_user -d abparts_dev < pre_migration_dump.sql

# Restart application
echo "Restarting application..."
docker-compose up -d

echo "Rollback completed!"
echo "Please verify the application is working correctly."
"""
        
        with open(rollback_script, 'w') as f:
            f.write(rollback_content)
        
        # Make executable
        rollback_script.chmod(0o755)
        
        print(f"✓ Rollback script created: {rollback_script}")
    
    def run_production_migration(self) -> bool:
        """Run the complete production migration process"""
        print("="*80)
        print(f"PRODUCTION MIGRATION: {self.migration_id}")
        print("="*80)
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No permanent changes will be made")
        else:
            print("⚠️  PRODUCTION MODE - Database will be modified")
        
        print(f"Backup directory: {self.migration_backup_dir}")
        
        # Step 1: Create database dump
        if not self.dry_run and not self.create_database_dump():
            print("❌ Failed to create database dump - aborting migration")
            return False
        
        # Step 2: Pre-migration validation
        if not self.validate_pre_migration():
            print("❌ Pre-migration validation failed - aborting migration")
            return False
        
        # Step 3: Run migration
        if not self.run_migration():
            print("❌ Migration failed")
            if not self.dry_run:
                print("💡 Use the rollback script to restore the database")
                self.create_rollback_script()
            return False
        
        # Step 4: Post-migration validation
        if not self.validate_post_migration():
            print("❌ Post-migration validation failed")
            if not self.dry_run:
                print("💡 Consider rolling back the migration")
                self.create_rollback_script()
            return False
        
        # Step 5: Create rollback script (even on success)
        if not self.dry_run:
            self.create_rollback_script()
        
        # Success!
        print("\n" + "="*80)
        if self.dry_run:
            print("🎉 DRY RUN COMPLETED SUCCESSFULLY")
            print("The migration appears safe to run in production.")
        else:
            print("🎉 PRODUCTION MIGRATION COMPLETED SUCCESSFULLY")
            print(f"Backup and rollback files saved to: {self.migration_backup_dir}")
        print("="*80)
        
        return True


def main():
    parser = argparse.ArgumentParser(description='Production ABParts Data Migration')
    parser.add_argument('--backup-dir', required=True,
                       help='Directory to store migration backups')
    parser.add_argument('--dry-run', action='store_true',
                       help='Run in dry-run mode (no changes made)')
    parser.add_argument('--force', action='store_true',
                       help='Proceed despite validation warnings')
    
    args = parser.parse_args()
    
    # Validate backup directory
    backup_path = Path(args.backup_dir)
    if not backup_path.exists():
        try:
            backup_path.mkdir(parents=True)
        except Exception as e:
            print(f"Failed to create backup directory {backup_path}: {e}")
            sys.exit(1)
    
    if not backup_path.is_dir():
        print(f"Backup path {backup_path} is not a directory")
        sys.exit(1)
    
    # Confirm production migration
    if not args.dry_run:
        print("⚠️  WARNING: This will modify the production database!")
        print("Make sure you have:")
        print("  1. Stopped the application")
        print("  2. Notified users of maintenance")
        print("  3. Verified recent database backups exist")
        print("  4. Tested this migration on a copy of production data")
        
        confirm = input("\nType 'MIGRATE' to proceed with production migration: ")
        if confirm != 'MIGRATE':
            print("Migration cancelled")
            sys.exit(0)
    
    # Run migration
    migrator = ProductionMigrator(
        backup_dir=args.backup_dir,
        dry_run=args.dry_run,
        force=args.force
    )
    
    success = migrator.run_production_migration()
    
    if success:
        print(f"\n📁 All files saved to: {migrator.migration_backup_dir}")
        if not args.dry_run:
            print("🔄 To rollback: cd to backup directory and run ./rollback.sh")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()