#!/bin/bash
set -e

echo "=== Resetting Alembic Migrations to Clean State ==="

# Step 1: Dump current production schema (structure only, no data)
echo "Step 1: Dumping current production schema..."
docker compose exec -T db pg_dump -U abparts_user -d abparts_prod --schema-only --no-owner --no-privileges > backend/alembic/baseline_schema.sql

# Step 2: Backup old migrations
echo "Step 2: Backing up old migrations..."
mkdir -p backend/alembic/versions_old
mv backend/alembic/versions/*.py backend/alembic/versions_old/ 2>/dev/null || true

# Step 3: Clear alembic_version table
echo "Step 3: Clearing alembic version history..."
docker compose exec -T db psql -U abparts_user -d abparts_prod -c "DELETE FROM alembic_version;"

# Step 4: Create initial baseline migration
echo "Step 4: Creating baseline migration..."
cat > backend/alembic/versions/00_baseline_schema.py << 'EOF'
"""baseline schema

Revision ID: 00_baseline
Revises: 
Create Date: 2024-12-01

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '00_baseline'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Schema is already in place from production
    # This migration just marks the baseline
    pass


def downgrade():
    # Cannot downgrade from baseline
    raise Exception("Cannot downgrade from baseline migration")
EOF

# Step 5: Stamp database with baseline
echo "Step 5: Stamping database with baseline..."
docker compose exec api alembic stamp 00_baseline

echo ""
echo "=== Migration Reset Complete ==="
echo "- Current schema saved to: backend/alembic/baseline_schema.sql"
echo "- Old migrations backed up to: backend/alembic/versions_old/"
echo "- Database stamped at: 00_baseline"
echo ""
echo "All future migrations will be created from this baseline."
