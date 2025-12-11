#!/usr/bin/env python3
"""Validate the maintenance protocols migration file."""

import sys
import importlib.util

def validate_migration():
    """Load and validate the migration file."""
    print("🔍 Validating maintenance protocols migration...")
    
    try:
        # Load the migration file
        spec = importlib.util.spec_from_file_location(
            "add_maintenance_protocols",
            "backend/alembic/versions/add_maintenance_protocols.py"
        )
        migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migration)
        
        # Check required attributes
        required_attrs = ['revision', 'down_revision', 'upgrade', 'downgrade']
        for attr in required_attrs:
            if not hasattr(migration, attr):
                print(f"❌ Missing required attribute: {attr}")
                return False
        
        print(f"✅ Migration file is valid")
        print(f"   Revision: {migration.revision}")
        print(f"   Down Revision: {migration.down_revision}")
        print(f"   Has upgrade function: {callable(migration.upgrade)}")
        print(f"   Has downgrade function: {callable(migration.downgrade)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading migration: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if validate_migration():
        print("\n✅ Migration validation passed!")
        print("\nTo run the migration:")
        print("  docker compose exec api alembic upgrade head")
        sys.exit(0)
    else:
        print("\n❌ Migration validation failed!")
        sys.exit(1)
