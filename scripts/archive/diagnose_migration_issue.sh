#!/bin/bash
# Diagnose why Alembic isn't detecting the migration

echo "=== Migration Detection Diagnostic ==="
echo ""

echo "1. Checking if migration file exists in container..."
docker compose exec api ls -la /app/alembic/versions/net_cleaning_001_add_net_cleaning_tables.py
echo ""

echo "2. Checking Python cache directory..."
docker compose exec api ls -la /app/alembic/versions/__pycache__/ | grep net_cleaning || echo "No cache files found"
echo ""

echo "3. Testing if Python can import the migration..."
docker compose exec api python -c "
import sys
sys.path.insert(0, '/app')
try:
    from alembic.versions.net_cleaning_001_add_net_cleaning_tables import revision, down_revision
    print(f'✓ Import successful')
    print(f'  Revision: {revision}')
    print(f'  Down revision: {down_revision}')
except Exception as e:
    print(f'✗ Import failed: {e}')
"
echo ""

echo "4. Checking Alembic configuration..."
docker compose exec api python -c "
from alembic.config import Config
from alembic.script import ScriptDirectory

config = Config('/app/alembic.ini')
script = ScriptDirectory.from_config(config)

print('Available revisions:')
for rev in script.walk_revisions():
    print(f'  {rev.revision} -> {rev.down_revision}: {rev.doc}')
"
echo ""

echo "5. Current Alembic status..."
docker compose exec api alembic current
echo ""

echo "6. Alembic heads..."
docker compose exec api alembic heads
echo ""

echo "7. Alembic history (last 5)..."
docker compose exec api alembic history | head -15
echo ""

echo "=== Diagnostic Complete ==="
echo ""
echo "If migration is not showing in step 4 or 7:"
echo "  → Run: docker compose exec api rm -rf /app/alembic/versions/__pycache__"
echo "  → Run: docker compose restart api"
echo "  → Run this diagnostic again"
