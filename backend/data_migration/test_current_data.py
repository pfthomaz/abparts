#!/usr/bin/env python3
"""
Test script to validate migration with current production data.

This script runs validation and a dry run migration against the current
database to ensure the migration will work correctly.
"""

import sys
import logging
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from data_migration.data_validator import run_validation
from data_migration.migration_manager import DataMigrationManager, MigrationStatus


def setup_logging():
    """Setup basic logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def test_current_data():
    """Test migration with current production data."""
    print("🧪 Testing migration with current production data")
    print("=" * 50)
    
    # Step 1: Run validation
    print("\n1️⃣  Running data validation...")
    try:
        validation_report = run_validation()
        print(f"   {validation_report.summary}")
        
        if validation_report.critical_issues > 0:
            print("   🚨 CRITICAL ISSUES FOUND:")
            for result in validation_report.results:
                if result.severity.value == 'critical':
                    print(f"      • {result}")
        
        if validation_report.errors > 0:
            print("   ❌ ERRORS FOUND:")
            for result in validation_report.results:
                if result.severity.value == 'error':
                    print(f"      • {result}")
        
        if validation_report.warnings > 0:
            print("   ⚠️  WARNINGS FOUND:")
            for result in validation_report.results:
                if result.severity.value == 'warning':
                    print(f"      • {result}")
        
        if validation_report.is_valid:
            print("   ✅ Validation passed!")
        else:
            print(f"   ❌ Validation failed with {validation_report.errors} errors and {validation_report.critical_issues} critical issues")
            
    except Exception as e:
        print(f"   ❌ Validation failed with error: {str(e)}")
        return False
    
    # Step 2: Run dry run migration
    print("\n2️⃣  Running migration dry run...")
    try:
        manager = DataMigrationManager()
        migration_report = manager.run_migration(dry_run=True)
        
        print(f"   Migration status: {migration_report.status.value}")
        
        if migration_report.status == MigrationStatus.COMPLETED:
            print("   ✅ Dry run completed successfully!")
            
            # Print step summary
            print("\n   📋 Step Summary:")
            for step in migration_report.steps:
                status_icon = {
                    'completed': '✅',
                    'failed': '❌',
                    'in_progress': '🔄',
                    'not_started': '⏸️'
                }.get(step.status.value, '❓')
                
                print(f"      {status_icon} {step.name}: {step.records_processed}/{step.records_total} records")
                if step.error_message:
                    print(f"         Error: {step.error_message}")
            
            return True
        else:
            print(f"   ❌ Dry run failed with status: {migration_report.status.value}")
            
            # Print failed steps
            print("\n   📋 Failed Steps:")
            for step in migration_report.steps:
                if step.status.value == 'failed':
                    print(f"      ❌ {step.name}: {step.error_message}")
            
            return False
            
    except Exception as e:
        print(f"   ❌ Dry run failed with error: {str(e)}")
        return False


def main():
    """Main function."""
    setup_logging()
    
    print("🚀 ABParts Migration Test")
    print("Testing migration compatibility with current data")
    
    success = test_current_data()
    
    if success:
        print("\n🎉 SUCCESS!")
        print("The migration is ready to run with your current data.")
        print("\nTo run the actual migration:")
        print("  cd backend/data_migration")
        print("  python run_migration.py migrate")
    else:
        print("\n⚠️  ISSUES FOUND!")
        print("Please review the errors above before running the migration.")
        print("You may need to fix data issues or contact support.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())