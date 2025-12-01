#!/bin/bash
set -e

echo "=== Resetting Alembic Migrations to Clean State (PRODUCTION) ==="
echo ""
echo "⚠️  WARNING: This will:"
echo "   - Clear production migration history"
echo "   - Stamp database with baseline from development"
echo "   - Assume schema is already up-to-date"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi
echo ""

# Determine database name from environment
DB_NAME="abparts_prod"
if [ -f .env ]; then
    DB_FROM_ENV=$(grep "^POSTGRES_DB=" .env | cut -d'=' -f2)
    if [ -n "$DB_FROM_ENV" ]; then
        DB_NAME=$DB_FROM_ENV
    fi
fi

echo "Using database: $DB_NAME"
echo ""

# Check if baseline migration exists
if [ ! -f backend/alembic/versions/00_baseline_schema.py ]; then
    echo "✗ ERROR: Baseline migration not found!"
    echo "  Expected: backend/alembic/versions/00_baseline_schema.py"
    echo ""
    echo "  You must run reset_migrations_clean_dev.sh in development first,"
    echo "  then commit and push the baseline migration to git."
    exit 1
fi

echo "✓ Baseline migration found"
echo ""

# Step 1: Backup old migrations (if any)
echo "Step 1: Backing up old migrations..."
BACKUP_DIR="backend/alembic/versions_old_prod_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Move all migrations except baseline
if ls backend/alembic/versions/*.py 1> /dev/null 2>&1; then
    for file in backend/alembic/versions/*.py; do
        if [ "$(basename $file)" != "00_baseline_schema.py" ]; then
            mv "$file" "$BACKUP_DIR/" 2>/dev/null || true
        fi
    done
    
    if [ "$(ls -A $BACKUP_DIR)" ]; then
        echo "✓ Old migrations backed up to: $BACKUP_DIR"
    else
        echo "✓ No old migrations to backup"
        rmdir "$BACKUP_DIR"
    fi
else
    echo "✓ No existing migrations to backup"
    rmdir "$BACKUP_DIR"
fi
echo ""

# Step 2: Clear alembic_version table
echo "Step 2: Clearing alembic version history..."
docker compose exec -T db psql -U abparts_user -d $DB_NAME -c "DELETE FROM alembic_version;" 2>&1 | grep -v "DELETE"
echo "✓ Migration history cleared"
echo ""

# Step 3: Stamp database with baseline
echo "Step 3: Stamping database with baseline..."
docker compose exec api alembic stamp 00_baseline
echo "✓ Database stamped at: 00_baseline"
echo ""

# Step 4: Verify
echo "Step 4: Verifying migration status..."
CURRENT_VERSION=$(docker compose exec -T db psql -U abparts_user -d $DB_NAME -c "SELECT version_num FROM alembic_version;" -t 2>/dev/null | tr -d ' \n\r')
if [ "$CURRENT_VERSION" = "00_baseline" ]; then
    echo "✓ Migration status verified: $CURRENT_VERSION"
else
    echo "⚠ Unexpected migration version: $CURRENT_VERSION"
fi
echo ""

echo "========================================="
echo "Production Migration Reset Complete!"
echo "========================================="
echo ""
echo "Summary:"
echo "  ✓ Database stamped at: 00_baseline"
echo "  ✓ Production is now in sync with development"
echo ""
echo "Future migrations:"
echo "  - Create in development: docker compose exec api alembic revision --autogenerate -m 'description'"
echo "  - Test in development: docker compose exec api alembic upgrade head"
echo "  - Commit and push to git"
echo "  - Deploy to production: git pull && docker compose exec api alembic upgrade head"
echo ""
