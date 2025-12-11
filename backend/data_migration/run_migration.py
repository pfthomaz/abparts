#!/usr/bin/env python3
"""
Migration Runner Script for ABParts Business Model Realignment
Task 18: Data Migration and Seeding

This script orchestrates all migration tasks in the correct order.
"""

import os
import sys
import argparse
from datetime import datetime

# Add the current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from migrate_existing_data import DataMigrationManager
from seed_default_data import DefaultDataSeeder
from validate_schema_compliance import SchemaComplianceValidator

class MigrationRunner:
    """Orchestrates the complete migration process."""
    
    def __init__(self, database_url=None):
        """Initialize the migration runner."""
        self.database_url = database_url
        self.migration_manager = DataMigrationManager(database_url)
        self.seeder = DefaultDataSeeder(database_url)
        self.validator = SchemaComplianceValidator(database_url)
        
    def run_full_migration(self, skip_validation=False):
        """Run the complete migration process."""
        print("🚀 Starting ABParts Business Model Realignment Migration")
        print("=" * 65)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # Step 1: Run data migration
            print("STEP 1: Data Migration")
            print("-" * 30)
            self.migration_manager.migrate_existing_data()
            print("✅ Data migration completed\n")
            
            # Step 2: Seed default data
            print("STEP 2: Default Data Seeding")
            print("-" * 30)
            self.seeder.seed_all()
            print("✅ Default data seeding completed\n")
            
            # Step 3: Validate schema compliance (unless skipped)
            if not skip_validation:
                print("STEP 3: Schema Compliance Validation")
                print("-" * 40)
                validation_status = self.validator.validate_all()
                
                if validation_status == 'PASS':
                    print("✅ Schema validation passed\n")
                elif validation_status == 'WARNING':
                    print("⚠️  Schema validation completed with warnings\n")
                else:
                    print("❌ Schema validation failed\n")
                    return False
            else:
                print("STEP 3: Schema Validation (SKIPPED)")
                print("-" * 40)
                print("⏭️  Schema validation was skipped as requested\n")
            
            # Final summary
            print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            print("=" * 40)
            print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return True
            
        except Exception as e:
            print(f"\n💥 Migration failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_migration_only(self):
        """Run only the data migration step."""
        print("🔄 Running Data Migration Only")
        print("=" * 35)
        
        try:
            self.migration_manager.migrate_existing_data()
            print("✅ Data migration completed successfully!")
            return True
        except Exception as e:
            print(f"❌ Data migration failed: {str(e)}")
            return False
    
    def run_seeding_only(self):
        """Run only the default data seeding step."""
        print("🌱 Running Default Data Seeding Only")
        print("=" * 40)
        
        try:
            self.seeder.seed_all()
            print("✅ Default data seeding completed successfully!")
            return True
        except Exception as e:
            print(f"❌ Default data seeding failed: {str(e)}")
            return False
    
    def run_validation_only(self):
        """Run only the schema compliance validation."""
        print("🔍 Running Schema Compliance Validation Only")
        print("=" * 50)
        
        try:
            validation_status = self.validator.validate_all()
            
            if validation_status == 'PASS':
                print("✅ Schema validation passed!")
                return True
            elif validation_status == 'WARNING':
                print("⚠️  Schema validation completed with warnings.")
                return True
            else:
                print("❌ Schema validation failed.")
                return False
                
        except Exception as e:
            print(f"❌ Schema validation failed: {str(e)}")
            return False
    
    def get_migration_status(self):
        """Get the current migration status."""
        print("📊 Checking Migration Status")
        print("=" * 30)
        
        try:
            with self.migration_manager.get_session() as session:
                # Check if default organizations exist
                from models import Organization, OrganizationType
                
                oraseas_count = session.query(Organization).filter(
                    Organization.organization_type == OrganizationType.oraseas_ee
                ).count()
                
                bossaqua_count = session.query(Organization).filter(
                    Organization.organization_type == OrganizationType.bossaqua
                ).count()
                
                # Check if warehouses exist for required organizations
                from sqlalchemy import text
                orgs_without_warehouses = session.execute(text("""
                    SELECT COUNT(*) FROM organizations o
                    WHERE o.organization_type IN ('oraseas_ee', 'bossaqua', 'customer')
                    AND NOT EXISTS (
                        SELECT 1 FROM warehouses w WHERE w.organization_id = o.id
                    )
                """)).scalar()
                
                # Check if machine hours table has data
                machine_hours_count = session.execute(text("""
                    SELECT COUNT(*) FROM machine_hours
                """)).scalar()
                
                print(f"Oraseas EE organizations: {oraseas_count}")
                print(f"BossAqua organizations: {bossaqua_count}")
                print(f"Organizations without warehouses: {orgs_without_warehouses}")
                print(f"Machine hours records: {machine_hours_count}")
                
                # Determine migration status
                if oraseas_count == 1 and bossaqua_count == 1 and orgs_without_warehouses == 0:
                    print("\n✅ Migration appears to be complete")
                    return True
                else:
                    print("\n⚠️  Migration appears to be incomplete")
                    return False
                    
        except Exception as e:
            print(f"❌ Could not check migration status: {str(e)}")
            return False


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(
        description="ABParts Business Model Realignment Migration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_migration.py                    # Run full migration
  python run_migration.py --migrate-only    # Run only data migration
  python run_migration.py --seed-only       # Run only default data seeding
  python run_migration.py --validate-only   # Run only schema validation
  python run_migration.py --status          # Check migration status
  python run_migration.py --skip-validation # Run migration without validation
        """
    )
    
    parser.add_argument(
        '--migrate-only',
        action='store_true',
        help='Run only the data migration step'
    )
    
    parser.add_argument(
        '--seed-only',
        action='store_true',
        help='Run only the default data seeding step'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Run only the schema compliance validation'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Check the current migration status'
    )
    
    parser.add_argument(
        '--skip-validation',
        action='store_true',
        help='Skip schema validation in full migration'
    )
    
    parser.add_argument(
        '--database-url',
        type=str,
        help='Database URL (defaults to environment configuration)'
    )
    
    args = parser.parse_args()
    
    # Initialize migration runner
    runner = MigrationRunner(args.database_url)
    
    # Determine which operation to run
    if args.status:
        success = runner.get_migration_status()
    elif args.migrate_only:
        success = runner.run_migration_only()
    elif args.seed_only:
        success = runner.run_seeding_only()
    elif args.validate_only:
        success = runner.run_validation_only()
    else:
        # Run full migration (default)
        success = runner.run_full_migration(skip_validation=args.skip_validation)
    
    # Return appropriate exit code
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())