#!/bin/bash
set -e

echo "=== Resetting Alembic Migrations to Clean State (DEVELOPMENT) ==="
echo ""
echo "⚠️  WARNING: This will:"
echo "   - Dump current development database schema"
echo "   - Backup all existing migrations"
echo "   - Clear migration history"
echo "   - Create a single baseline migration"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi
echo ""

# Determine database name from environment
DB_NAME="abparts_dev"
if [ -f .env.development ]; then
    DB_FROM_ENV=$(grep "^POSTGRES_DB=" .env.development | cut -d'=' -f2)
    if [ -n "$DB_FROM_ENV" ]; then
        DB_NAME=$DB_FROM_ENV
    fi
fi

echo "Using database: $DB_NAME"
echo ""

# Step 1: Dump current development schema (structure only, no data)
echo "Step 1: Dumping current development schema..."
docker compose exec -T db pg_dump -U abparts_user -d $DB_NAME --schema-only --no-owner --no-privileges > backend/alembic/baseline_schema.sql

if [ -f backend/alembic/baseline_schema.sql ]; then
    echo "✓ Schema dumped to: backend/alembic/baseline_schema.sql"
    echo "  Size: $(wc -l < backend/alembic/baseline_schema.sql) lines"
else
    echo "✗ Failed to dump schema"
    exit 1
fi
echo ""

# Step 2: Backup old migrations
echo "Step 2: Backing up old migrations..."
BACKUP_DIR="backend/alembic/versions_old_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if ls backend/alembic/versions/*.py 1> /dev/null 2>&1; then
    mv backend/alembic/versions/*.py "$BACKUP_DIR/" 2>/dev/null || true
    echo "✓ Old migrations backed up to: $BACKUP_DIR"
    echo "  Files backed up: $(ls -1 $BACKUP_DIR | wc -l)"
else
    echo "✓ No existing migrations to backup"
fi
echo ""

# Step 3: Clear alembic_version table
echo "Step 3: Clearing alembic version history..."
docker compose exec -T db psql -U abparts_user -d $DB_NAME -c "DELETE FROM alembic_version;" 2>&1 | grep -v "DELETE"
echo "✓ Migration history cleared"
echo ""

# Step 4: Create initial baseline migration
echo "Step 4: Creating baseline migration..."
cat > backend/alembic/versions/00_baseline_schema.py << 'EOF'
"""baseline schema

Revision ID: 00_baseline
Revises: 
Create Date: 2024-12-01

This is a baseline migration created from the current database schema.
All tables and columns already exist in the database.
This migration just marks the starting point for future migrations.

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '00_baseline'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Schema is already in place from existing database
    # This migration just marks the baseline
    pass


def downgrade():
    # Cannot downgrade from baseline migration
    raise Exception("Cannot downgrade from baseline migration")
EOF

echo "✓ Baseline migration created: backend/alembic/versions/00_baseline_schema.py"
echo ""

# Step 5: Stamp database with baseline
echo "Step 5: Stamping database with baseline..."
docker compose exec api alembic stamp 00_baseline
echo "✓ Database stamped at: 00_baseline"
echo ""

# Step 6: Verify
echo "Step 6: Verifying migration status..."
CURRENT_VERSION=$(docker compose exec -T db psql -U abparts_user -d $DB_NAME -c "SELECT version_num FROM alembic_version;" -t 2>/dev/null | tr -d ' \n\r')
if [ "$CURRENT_VERSION" = "00_baseline" ]; then
    echo "✓ Migration status verified: $CURRENT_VERSION"
else
    echo "⚠ Unexpected migration version: $CURRENT_VERSION"
fi
echo ""

echo "========================================="
echo "Migration Reset Complete!"
echo "========================================="
echo ""
echo "Summary:"
echo "  ✓ Current schema saved to: backend/alembic/baseline_schema.sql"
echo "  ✓ Old migrations backed up to: $BACKUP_DIR"
echo "  ✓ Database stamped at: 00_baseline"
echo ""
echo "Next Steps:"
echo ""
echo "1. Commit the baseline migration to git:"
echo "   git add backend/alembic/versions/00_baseline_schema.py"
echo "   git add backend/alembic/baseline_schema.sql"
echo "   git commit -m 'Reset migrations to clean baseline'"
echo ""
echo "2. Push to repository:"
echo "   git push"
echo ""
echo "3. Deploy to production:"
echo "   - SSH to production server"
echo "   - git pull"
echo "   - Run: ./reset_migrations_clean_prod.sh"
echo ""
echo "4. Future migrations will be created from this baseline:"
echo "   docker compose exec api alembic revision --autogenerate -m 'description'"
echo "   docker compose exec api alembic upgrade head"
echo ""
