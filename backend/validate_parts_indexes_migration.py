#!/usr/bin/env python3
"""
Validation script for parts performance indexes migration.
This script validates that the migration file is correctly structured.
"""

import os
import sys
import importlib.util


def validate_migration_file():
    """Validate the parts performance indexes migration file."""
    
    migration_file = "backend/alembic/versions/add_parts_performance_indexes.py"
    
    if not os.path.exists(migration_file):
        print("✗ Migration file not found")
        return False
    
    print("✓ Migration file exists")
    
    # Load the migration module
    spec = importlib.util.spec_from_file_location("migration", migration_file)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    
    # Check required attributes
    required_attrs = ['revision', 'down_revision', 'upgrade', 'downgrade']
    for attr in required_attrs:
        if not hasattr(migration, attr):
            print(f"✗ Missing required attribute: {attr}")
            return False
        print(f"✓ Has {attr}")
    
    # Check revision ID
    if migration.revision != 'add_parts_perf_idx':
        print(f"✗ Incorrect revision ID: {migration.revision}")
        return False
    print(f"✓ Correct revision ID: {migration.revision}")
    
    # Check down_revision
    if migration.down_revision != '3bef488d9675':
        print(f"✗ Incorrect down_revision: {migration.down_revision}")
        return False
    print(f"✓ Correct down_revision: {migration.down_revision}")
    
    # Read the file content to check for index creation
    with open(migration_file, 'r') as f:
        content = f.read()
    
    # Check for required index operations
    required_operations = [
        'idx_parts_type_proprietary',
        'idx_parts_manufacturer', 
        'idx_parts_name_fulltext',
        'CREATE INDEX',
        'to_tsvector',
        'gin'
    ]
    
    for operation in required_operations:
        if operation not in content:
            print(f"✗ Missing operation: {operation}")
            return False
        print(f"✓ Contains: {operation}")
    
    print("\n✓ Migration file validation passed!")
    return True


def validate_model_documentation():
    """Validate that the Part model has been updated with index documentation."""
    
    models_file = "backend/app/models.py"
    
    if not os.path.exists(models_file):
        print("✗ Models file not found")
        return False
    
    with open(models_file, 'r') as f:
        content = f.read()
    
    # Check for index documentation in Part model
    required_docs = [
        'Performance Indexes:',
        'idx_parts_type_proprietary',
        'idx_parts_manufacturer',
        'idx_parts_name_fulltext',
        'multilingual search'
    ]
    
    for doc in required_docs:
        if doc not in content:
            print(f"✗ Missing documentation: {doc}")
            return False
        print(f"✓ Contains documentation: {doc}")
    
    print("\n✓ Model documentation validation passed!")
    return True


if __name__ == "__main__":
    print("Validating parts performance indexes implementation...\n")
    
    migration_valid = validate_migration_file()
    print()
    model_valid = validate_model_documentation()
    
    if migration_valid and model_valid:
        print("\n🎉 All validations passed! The parts performance indexes are properly implemented.")
        print("\nNext steps:")
        print("1. Run the migration: docker-compose exec api alembic upgrade head")
        print("2. Test the indexes: python backend/test_parts_indexes.py")
    else:
        print("\n❌ Some validations failed. Please review the implementation.")
        sys.exit(1)