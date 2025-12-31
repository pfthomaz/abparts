#!/bin/bash
# reset_database_schema.sh
# Automated script to reset Alembic migrations using current production schema as baseline

set -e  # Exit on any error

echo "=== ABParts Database Schema Reset Process ==="
echo "This will reset Alembic migrations to use current production schema as baseline"
echo ""

# Configuration
PROD_CONTAINER="abparts_db_prod"
API_CONTAINER="abparts_api_prod"
DB_USER="abparts_user"
DB_NAME="abparts_prod"
BACKUP_DIR="./migration_reset_backups/$(date +%Y%m%d_%H%M%S)"

# Safety check
read -p "⚠️  This will modify your migration files and production database metadata. Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Operation cancelled."
    exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"
echo "📁 Created backup directory: $BACKUP_DIR"

echo ""
echo "Step 1: Creating production database backup..."
if docker exec "$PROD_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_DIR/production_backup.sql"; then
    BACKUP_SIZE=$(du -sh "$BACKUP_DIR/production_backup.sql" | cut -f1)
    echo "✅ Backup created: $BACKUP_DIR/production_backup.sql ($BACKUP_SIZE)"
else
    echo "❌ Failed to create database backup"
    exit 1
fi

echo ""
echo "Step 2: Backing up current migration files..."
if ls backend/alembic/versions/*.py >/dev/null 2>&1; then
    cp backend/alembic/versions/*.py "$BACKUP_DIR/" 2>/dev/null
    MIGRATION_COUNT=$(ls backend/alembic/versions/*.py | wc -l)
    echo "✅ Backed up $MIGRATION_COUNT migration files"
else
    echo "ℹ️  No existing migration files found"
fi

echo ""
echo "Step 3: Getting current Alembic version from production..."
if CURRENT_VERSION=$(docker exec "$PROD_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT version_num FROM alembic_version;" 2>/dev/null | tr -d ' \n'); then
    if [ -n "$CURRENT_VERSION" ]; then
        echo "Current version: $CURRENT_VERSION"
        echo "$CURRENT_VERSION" > "$BACKUP_DIR/original_version.txt"
    else
        echo "⚠️  No alembic_version found in database (this is normal for fresh installs)"
        echo "none" > "$BACKUP_DIR/original_version.txt"
    fi
else
    echo "⚠️  Could not read alembic_version table (this is normal for fresh installs)"
    echo "none" > "$BACKUP_DIR/original_version.txt"
fi

echo ""
echo "Step 4: Removing old migration files..."
if ls backend/alembic/versions/*.py >/dev/null 2>&1; then
    rm -f backend/alembic/versions/*.py
    echo "✅ Old migration files removed"
else
    echo "ℹ️  No migration files to remove"
fi

echo ""
echo "Step 5: Generating new baseline migration from current models..."
cd backend
if docker exec "$API_CONTAINER" alembic revision --autogenerate -m "baseline_from_production_$(date +%Y%m%d)"; then
    echo "✅ New baseline migration generated"
else
    echo "❌ Failed to generate baseline migration"
    cd ..
    exit 1
fi
cd ..

echo ""
echo "Step 6: Getting new baseline revision ID..."
if NEW_REVISION=$(docker exec "$API_CONTAINER" alembic heads 2>/dev/null | head -1 | tr -d ' \n'); then
    if [ -n "$NEW_REVISION" ]; then
        echo "New baseline revision: $NEW_REVISION"
        echo "$NEW_REVISION" > "$BACKUP_DIR/new_version.txt"
    else
        echo "❌ Could not get new revision ID"
        exit 1
    fi
else
    echo "❌ Failed to get new revision ID"
    exit 1
fi

echo ""
echo "Step 7: Updating production alembic_version table..."
# First, ensure the alembic_version table exists
docker exec "$PROD_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);" >/dev/null 2>&1

# Check if there's an existing version
EXISTING_COUNT=$(docker exec "$PROD_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM alembic_version;" 2>/dev/null | tr -d ' \n')

if [ "$EXISTING_COUNT" = "0" ]; then
    # Insert new version
    docker exec "$PROD_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "INSERT INTO alembic_version (version_num) VALUES ('$NEW_REVISION');"
    echo "✅ Inserted new alembic version"
else
    # Update existing version
    docker exec "$PROD_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "UPDATE alembic_version SET version_num = '$NEW_REVISION';"
    echo "✅ Updated existing alembic version"
fi

echo ""
echo "Step 8: Verification..."
UPDATED_VERSION=$(docker exec "$PROD_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT version_num FROM alembic_version;" 2>/dev/null | tr -d ' \n')
if [ "$UPDATED_VERSION" = "$NEW_REVISION" ]; then
    echo "✅ Version update verified: $UPDATED_VERSION"
else
    echo "❌ Version update failed. Expected: $NEW_REVISION, Got: $UPDATED_VERSION"
    exit 1
fi

echo ""
echo "Step 9: Testing Alembic status..."
echo "Current Alembic status:"
docker exec "$API_CONTAINER" alembic current
echo ""
echo "Checking for any issues:"
if docker exec "$API_CONTAINER" alembic check >/dev/null 2>&1; then
    echo "✅ Alembic check passed"
else
    echo "⚠️  Alembic check found some differences (this might be normal)"
fi

echo ""
echo "🎉 Database schema reset completed successfully!"
echo ""
echo "📋 Summary:"
echo "- Production backup: $BACKUP_DIR/production_backup.sql"
echo "- Old migrations backed up to: $BACKUP_DIR/"
echo "- New baseline revision: $NEW_REVISION"
echo "- Original version was: $(cat "$BACKUP_DIR/original_version.txt")"
echo ""
echo "📝 Next steps:"
echo "1. Test creating new migrations:"
echo "   docker exec $API_CONTAINER alembic revision -m 'test_new_migration'"
echo ""
echo "2. Test in development environment:"
echo "   docker exec abparts_api_dev alembic upgrade head"
echo ""
echo "3. Commit the new migration files to git:"
echo "   git add backend/alembic/versions/"
echo "   git commit -m 'Reset migrations to production baseline'"
echo ""
echo "4. Inform team members to pull the new migration files"
echo ""
echo "🔄 If you need to rollback, see the recovery instructions in DATABASE_SCHEMA_RESET_GUIDE.md"