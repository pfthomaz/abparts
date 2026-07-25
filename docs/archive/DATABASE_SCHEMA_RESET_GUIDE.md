# Database Schema Reset Guide

## Overview
This guide will help you reset your Alembic migration history to use the current production database schema as the new baseline (head). This is safe and won't lose any production data.

## What We'll Do
1. **Backup production database** (safety first!)
2. **Generate new baseline migration** from current production schema
3. **Replace existing migrations** with the new baseline
4. **Test in development** environment
5. **Update production** Alembic version table
6. **Verify everything works**

## Step-by-Step Process

### Phase 1: Safety Backup

```bash
# 1. Create a full backup of production database
docker exec abparts_db_prod pg_dump -U abparts_user abparts_prod > production_backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Verify backup was created successfully
ls -la production_backup_*.sql
```

### Phase 2: Examine Current State

```bash
# Check current Alembic version in production
docker exec abparts_db_prod psql -U abparts_user -d abparts_prod -c "SELECT * FROM alembic_version;"

# List current migration files
ls -la backend/alembic/versions/
```

### Phase 3: Generate New Baseline Migration

```bash
# 1. First, let's see what migrations exist
cd backend
docker exec abparts_api_prod alembic history

# 2. Generate schema from current production database
docker exec abparts_db_prod pg_dump -U abparts_user -d abparts_prod --schema-only > current_production_schema.sql

# 3. Create a backup of current migration files
mkdir -p migration_backups/$(date +%Y%m%d_%H%M%S)
cp -r alembic/versions/* migration_backups/$(date +%Y%m%d_%H%M%S)/

# 4. Remove all existing migration files
rm -f alembic/versions/*.py

# 5. Generate new baseline migration from current models
docker exec abparts_api_prod alembic revision --autogenerate -m "baseline_from_production_schema"
```

### Phase 4: Test in Development

```bash
# 1. Create a test database from production backup
docker exec abparts_db_dev createdb -U abparts_user abparts_test_reset

# 2. Restore production data to test database
docker exec -i abparts_db_dev psql -U abparts_user abparts_test_reset < production_backup_*.sql

# 3. Test the new migration on a fresh database
docker exec abparts_db_dev createdb -U abparts_user abparts_fresh_test
docker exec abparts_api_dev alembic upgrade head

# 4. Compare schemas to ensure they match
docker exec abparts_db_dev pg_dump -U abparts_user -d abparts_test_reset --schema-only > test_prod_schema.sql
docker exec abparts_db_dev pg_dump -U abparts_user -d abparts_fresh_test --schema-only > test_fresh_schema.sql

# Compare the schemas (they should be identical)
diff test_prod_schema.sql test_fresh_schema.sql
```

### Phase 5: Update Production Alembic Version

```bash
# 1. Get the revision ID of your new baseline migration
NEW_REVISION=$(docker exec abparts_api_prod alembic heads)
echo "New baseline revision: $NEW_REVISION"

# 2. Update the alembic_version table in production to point to new baseline
docker exec abparts_db_prod psql -U abparts_user -d abparts_prod -c "UPDATE alembic_version SET version_num = '$NEW_REVISION';"

# 3. Verify the update
docker exec abparts_db_prod psql -U abparts_user -d abparts_prod -c "SELECT * FROM alembic_version;"
```

### Phase 6: Verification

```bash
# 1. Check that Alembic thinks production is up to date
docker exec abparts_api_prod alembic current
docker exec abparts_api_prod alembic check

# 2. Test that new migrations can be created
docker exec abparts_api_prod alembic revision -m "test_migration_after_reset"

# 3. Remove the test migration (we don't need it)
rm backend/alembic/versions/*test_migration_after_reset*.py
```

## Alternative Automated Script

Here's a script that automates the entire process:

```bash
#!/bin/bash
# reset_database_schema.sh

set -e  # Exit on any error

echo "=== Database Schema Reset Process ==="
echo "This will reset Alembic migrations to use current production schema as baseline"
echo ""

# Configuration
PROD_CONTAINER="abparts_db_prod"
API_CONTAINER="abparts_api_prod"
DB_USER="abparts_user"
DB_NAME="abparts_prod"
BACKUP_DIR="./migration_reset_backups/$(date +%Y%m%d_%H%M%S)"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "Step 1: Creating production database backup..."
docker exec "$PROD_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_DIR/production_backup.sql"
echo "✅ Backup created: $BACKUP_DIR/production_backup.sql"

echo "Step 2: Backing up current migration files..."
cp -r backend/alembic/versions/* "$BACKUP_DIR/" 2>/dev/null || echo "No migration files to backup"
echo "✅ Migration files backed up"

echo "Step 3: Getting current Alembic version..."
CURRENT_VERSION=$(docker exec "$PROD_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT version_num FROM alembic_version;" | tr -d ' ')
echo "Current version: $CURRENT_VERSION"
echo "$CURRENT_VERSION" > "$BACKUP_DIR/original_version.txt"

echo "Step 4: Removing old migration files..."
rm -f backend/alembic/versions/*.py
echo "✅ Old migration files removed"

echo "Step 5: Generating new baseline migration..."
cd backend
docker exec "$API_CONTAINER" alembic revision --autogenerate -m "baseline_from_production_$(date +%Y%m%d)"
cd ..

echo "Step 6: Getting new baseline revision ID..."
NEW_REVISION=$(docker exec "$API_CONTAINER" alembic heads | tr -d ' ')
echo "New baseline revision: $NEW_REVISION"
echo "$NEW_REVISION" > "$BACKUP_DIR/new_version.txt"

echo "Step 7: Updating production alembic_version table..."
docker exec "$PROD_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "UPDATE alembic_version SET version_num = '$NEW_REVISION';"
echo "✅ Production alembic_version updated"

echo "Step 8: Verification..."
UPDATED_VERSION=$(docker exec "$PROD_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT version_num FROM alembic_version;" | tr -d ' ')
if [ "$UPDATED_VERSION" = "$NEW_REVISION" ]; then
    echo "✅ Version update verified: $UPDATED_VERSION"
else
    echo "❌ Version update failed. Expected: $NEW_REVISION, Got: $UPDATED_VERSION"
    exit 1
fi

echo "Step 9: Testing Alembic status..."
docker exec "$API_CONTAINER" alembic current
docker exec "$API_CONTAINER" alembic check

echo ""
echo "🎉 Database schema reset completed successfully!"
echo ""
echo "Summary:"
echo "- Production backup: $BACKUP_DIR/production_backup.sql"
echo "- Old migrations backed up to: $BACKUP_DIR/"
echo "- New baseline revision: $NEW_REVISION"
echo "- Original version was: $CURRENT_VERSION"
echo ""
echo "Next steps:"
echo "1. Test creating new migrations: docker exec $API_CONTAINER alembic revision -m 'test'"
echo "2. Test in development environment"
echo "3. Monitor production for any issues"
```

## Recovery Plan (If Something Goes Wrong)

If you need to rollback:

```bash
# 1. Restore original migration files
cp migration_backups/TIMESTAMP/* backend/alembic/versions/

# 2. Restore original alembic version
ORIGINAL_VERSION=$(cat migration_backups/TIMESTAMP/original_version.txt)
docker exec abparts_db_prod psql -U abparts_user -d abparts_prod -c "UPDATE alembic_version SET version_num = '$ORIGINAL_VERSION';"

# 3. If database is corrupted, restore from backup
docker exec -i abparts_db_prod psql -U abparts_user abparts_prod < migration_backups/TIMESTAMP/production_backup.sql
```

## Important Notes

1. **No Data Loss**: This process only changes migration files and the alembic_version table. Your actual data remains untouched.

2. **Downtime**: Minimal downtime required - just the few seconds to update the alembic_version table.

3. **Team Coordination**: Make sure all developers pull the new migration files after this process.

4. **Future Migrations**: After this reset, all new migrations will be based on your current production schema.

5. **Testing**: Always test the process in development first!

## Terminology

- **Head**: The latest migration in your migration chain
- **Baseline**: A starting point migration that represents your current schema
- **Revision**: A unique identifier for each migration file

This process essentially makes your current production schema the new "revision 1" and all future changes will be "revision 2, 3, 4..." etc.