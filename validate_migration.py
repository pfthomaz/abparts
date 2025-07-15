#!/usr/bin/env python3
"""
Simple script to validate the migration file syntax without requiring database connection.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    # Try to import the migration file to check for syntax errors
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "migration", 
        "backend/alembic/versions/31e87319dc9a_business_model_alignment_schema_updates.py"
    )
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    print("✅ Migration file syntax is valid")
    
    # Check if upgrade and downgrade functions exist
    if hasattr(migration, 'upgrade') and callable(migration.upgrade):
        print("✅ upgrade() function found")
    else:
        print("❌ upgrade() function missing or not callable")
        
    if hasattr(migration, 'downgrade') and callable(migration.downgrade):
        print("✅ downgrade() function found")
    else:
        print("❌ downgrade() function missing or not callable")
        
    print("✅ Migration validation completed successfully")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except SyntaxError as e:
    print(f"❌ Syntax error in migration file: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)