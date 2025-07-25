#!/usr/bin/env python3
"""
Migration status checker for ABParts
Usage: python check_migrations.py [environment]
"""

import sys
import subprocess
import os
from datetime import datetime

def run_command(cmd, capture_output=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_migration_status():
    """Check the current migration status."""
    print("=== ABParts Migration Status Check ===")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check if we can connect to the database
    print("1. Checking database connection...")
    success, stdout, stderr = run_command("docker-compose exec -T api alembic current")
    
    if not success:
        print("❌ Cannot connect to database or alembic")
        print(f"Error: {stderr}")
        return False
    
    print("✅ Database connection successful")
    print()
    
    # Show current migration
    print("2. Current migration status:")
    print(stdout.strip())
    print()
    
    # Check for pending migrations
    print("3. Checking for pending migrations...")
    success, stdout, stderr = run_command("docker-compose exec -T api alembic show head")
    
    if success:
        print("Pending migrations:")
        print(stdout.strip())
    else:
        print("❌ Error checking pending migrations")
        print(f"Error: {stderr}")
    
    print()
    
    # Show migration history (last 5)
    print("4. Recent migration history:")
    success, stdout, stderr = run_command("docker-compose exec -T api alembic history -r -5:")
    
    if success:
        print(stdout.strip())
    else:
        print("❌ Error getting migration history")
        print(f"Error: {stderr}")
    
    print()
    
    # Check for multiple heads
    print("5. Checking for migration conflicts...")
    success, stdout, stderr = run_command("docker-compose exec -T api alembic heads")
    
    if success:
        heads = stdout.strip().split('\n')
        if len(heads) > 1:
            print("⚠️  Multiple migration heads detected:")
            for head in heads:
                print(f"  - {head}")
            print("Consider running: alembic merge heads")
        else:
            print("✅ No migration conflicts detected")
    else:
        print("❌ Error checking migration heads")
        print(f"Error: {stderr}")
    
    print()
    print("=== Status check completed ===")
    return True

def main():
    """Main function."""
    environment = sys.argv[1] if len(sys.argv) > 1 else "development"
    
    # Set environment variable
    os.environ['ENVIRONMENT'] = environment
    
    print(f"Environment: {environment}")
    print()
    
    success = check_migration_status()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()