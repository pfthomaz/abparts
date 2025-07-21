#!/usr/bin/env python3
"""
ABParts Data Migration CLI

Command-line interface for running data migration with comprehensive
progress tracking, validation, and rollback capabilities.
"""

import argparse
import logging
import sys
import json
from datetime import datetime
from pathlib import Path

from migration_manager import DataMigrationManager, MigrationStatus
from data_validator import DataValidator, run_validation
from migration_tester import MigrationTester


def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration."""
    # Create logs directory if it doesn't exist
    Path("backend/data_migration/logs").mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.FileHandler('backend/data_migration/logs/migration.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def print_banner():
    """Print application banner."""
    print("=" * 60)
    print("🚀 ABParts Data Migration Tool")
    print("   Business Model Alignment Migration")
    print("=" * 60)


def print_step_progress(step_name: str, current: int, total: int, status: str = ""):
    """Print step progress with visual indicator."""
    if total > 0:
        percentage = (current / total) * 100
        bar_length = 30
        filled_length = int(bar_length * current // total)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        print(f"   [{bar}] {percentage:6.1f}% | {step_name} {status}")
    else:
        print(f"   [{'█' * 30}] 100.0% | {step_name} {status}")


def run_validation_command(args):
    """Run data validation command."""
    print("🔍 Running data validation...")
    
    try:
        report = run_validation()
        
        print(f"\n📊 {report.summary}")
        print("-" * 50)
        
        # Group results by severity
        critical_issues = [r for r in report.results if r.severity.value == 'critical']
        errors = [r for r in report.results if r.severity.value == 'error']
        warnings = [r for r in report.results if r.severity.value == 'warning']
        
        if critical_issues:
            print("🚨 CRITICAL ISSUES:")
            for result in critical_issues:
                print(f"   • {result}")
        
        if errors:
            print("❌ ERRORS:")
            for result in errors:
                print(f"   • {result}")
        
        if warnings:
            print("⚠️  WARNINGS:")
            for result in warnings:
                print(f"   • {result}")
        
        if report.is_valid:
            print("\n✅ Data validation passed!")
            return True
        else:
            print(f"\n❌ Data validation failed with {report.errors} errors and {report.critical_issues} critical issues")
            return False
            
    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
        return False


def run_migration_command(args):
    """Run data migration command."""
    print("🔄 Starting data migration...")
    
    if not args.force:
        # Run validation first
        print("\n1️⃣  Pre-migration validation...")
        if not run_validation_command(args):
            if not args.skip_validation:
                print("❌ Pre-migration validation failed. Use --skip-validation to proceed anyway.")
                return False
            else:
                print("⚠️  Proceeding despite validation issues (--skip-validation used)")
    
    try:
        # Create migration manager
        manager = DataMigrationManager()
        
        # Run dry run first unless forced
        if not args.force and not args.dry_run:
            print("\n2️⃣  Running migration dry run...")
            dry_run_report = manager.run_migration(dry_run=True)
            
            if dry_run_report.status != MigrationStatus.COMPLETED:
                print("❌ Dry run failed. Check logs for details.")
                print_migration_summary(dry_run_report)
                return False
            
            print("✅ Dry run completed successfully!")
            
            # Ask for confirmation
            if not args.yes:
                response = input("\n🤔 Proceed with actual migration? (yes/no): ")
                if response.lower() not in ['yes', 'y']:
                    print("Migration cancelled by user.")
                    return False
        
        # Run actual migration
        print(f"\n3️⃣  Running {'dry run' if args.dry_run else 'actual'} migration...")
        
        # Create a simple progress tracker
        def progress_callback(step_name, current, total):
            print_step_progress(step_name, current, total)
        
        report = manager.run_migration(dry_run=args.dry_run)
        
        # Print results
        print_migration_summary(report)
        
        if report.status == MigrationStatus.COMPLETED:
            print("✅ Migration completed successfully!")
            
            # Run post-migration validation
            if not args.dry_run:
                print("\n4️⃣  Post-migration validation...")
                validation_success = run_validation_command(args)
                if not validation_success:
                    print("⚠️  Post-migration validation found issues. Check the report above.")
            
            return True
        else:
            print(f"❌ Migration failed with status: {report.status.value}")
            return False
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        return False


def run_test_command(args):
    """Run migration testing command."""
    print("🧪 Running migration tests...")
    
    try:
        tester = MigrationTester()
        
        if args.test_type == 'rollback':
            print("Testing rollback capability...")
            success = tester.test_rollback_capability()
            print(f"Rollback test: {'✅ PASSED' if success else '❌ FAILED'}")
            return success
            
        elif args.test_type == 'sample':
            print(f"Testing with {args.sample_size} sample...")
            samples = tester.create_test_samples()
            
            # Find the requested sample
            sample = next((s for s in samples if s.name == args.sample_size), None)
            if not sample:
                print(f"❌ Unknown sample size: {args.sample_size}")
                print(f"Available samples: {', '.join(s.name for s in samples)}")
                return False
            
            result = tester.test_migration_with_sample(sample)
            
            if result.success:
                print(f"✅ Test passed in {result.performance_metrics.migration_duration:.2f}s")
                return True
            else:
                print(f"❌ Test failed: {result.error_message}")
                return False
                
        elif args.test_type == 'comprehensive':
            print("Running comprehensive tests...")
            results = tester.run_comprehensive_tests()
            
            # Print summary
            passed = sum(1 for r in results if r.success)
            total = len(results)
            
            print(f"\n📊 Test Results: {passed}/{total} passed")
            
            for result in results:
                status = "✅" if result.success else "❌"
                duration = f"{result.performance_metrics.migration_duration:.2f}s" if result.performance_metrics else "N/A"
                print(f"   {status} {result.sample.name}: {duration}")
            
            return passed == total
            
    except Exception as e:
        print(f"❌ Testing failed: {str(e)}")
        return False


def print_migration_summary(report):
    """Print migration summary."""
    print(f"\n📋 Migration Summary:")
    print(f"   Migration ID: {report.migration_id}")
    print(f"   Status: {report.status.value}")
    print(f"   Started: {report.started_at}")
    print(f"   Completed: {report.completed_at}")
    
    if report.steps:
        print(f"\n📝 Step Details:")
        for step in report.steps:
            status_icon = {
                'completed': '✅',
                'failed': '❌',
                'in_progress': '🔄',
                'not_started': '⏸️'
            }.get(step.status.value, '❓')
            
            print(f"   {status_icon} {step.name}: {step.description}")
            if step.records_processed > 0:
                print(f"      Records processed: {step.records_processed}/{step.records_total}")
            if step.error_message:
                print(f"      Error: {step.error_message}")
    
    if report.validation_errors:
        print(f"\n⚠️  Validation Issues:")
        for error in report.validation_errors:
            print(f"   • {error}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ABParts Data Migration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run validation only
  python run_migration.py validate
  
  # Run migration with dry run first
  python run_migration.py migrate
  
  # Force migration without validation or confirmation
  python run_migration.py migrate --force --yes
  
  # Run dry run only
  python run_migration.py migrate --dry-run
  
  # Test rollback capability
  python run_migration.py test --type rollback
  
  # Test with specific sample size
  python run_migration.py test --type sample --sample-size medium_sample
  
  # Run comprehensive tests
  python run_migration.py test --type comprehensive
        """
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Run data validation')
    
    # Migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Run data migration')
    migrate_parser.add_argument('--dry-run', action='store_true', help='Run migration dry run only')
    migrate_parser.add_argument('--force', action='store_true', help='Skip validation and dry run')
    migrate_parser.add_argument('--yes', action='store_true', help='Skip confirmation prompts')
    migrate_parser.add_argument('--skip-validation', action='store_true', help='Skip pre-migration validation')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run migration tests')
    test_parser.add_argument('--type', choices=['rollback', 'sample', 'comprehensive'], 
                           default='comprehensive', help='Type of test to run')
    test_parser.add_argument('--sample-size', 
                           choices=['minimal_sample', 'small_sample', 'medium_sample', 'large_sample', 'production_scale'],
                           default='small_sample', help='Sample size for testing')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Setup logging
    setup_logging(args.log_level)
    
    # Print banner
    print_banner()
    
    # Execute command
    success = False
    
    try:
        if args.command == 'validate':
            success = run_validation_command(args)
        elif args.command == 'migrate':
            success = run_migration_command(args)
        elif args.command == 'test':
            success = run_test_command(args)
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        logging.exception("Unexpected error occurred")
        return 1
    
    # Return appropriate exit code
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())