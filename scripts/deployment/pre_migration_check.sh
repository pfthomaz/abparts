#!/bin/bash
# Pre-Migration Checklist - Run this BEFORE creating a new migration

echo "=========================================="
echo "  Pre-Migration Checklist"
echo "=========================================="
echo ""

echo "1️⃣  Current migration status:"
docker-compose exec api alembic current
echo ""

echo "2️⃣  Checking for multiple heads..."
HEADS=$(docker-compose exec api alembic heads 2>&1)
HEAD_COUNT=$(echo "$HEADS" | grep -c "^[a-f0-9]")

if [ "$HEAD_COUNT" -eq 1 ]; then
    echo "✅ Single head - OK to create new migration"
    echo "$HEADS"
else
    echo "⚠️  WARNING: Multiple heads detected!"
    echo "$HEADS"
    echo ""
    echo "❌ You must create a MERGE migration first!"
    echo "   Run: docker-compose exec api alembic merge -m 'merge heads' <head1> <head2>"
    exit 1
fi
echo ""

echo "3️⃣  Latest migration file:"
LATEST_FILE=$(ls -t backend/alembic/versions/*.py 2>/dev/null | grep -v __pycache__ | head -1)
if [ -n "$LATEST_FILE" ]; then
    echo "   File: $(basename $LATEST_FILE)"
    REVISION=$(grep "^revision = " "$LATEST_FILE" | cut -d"'" -f2)
    echo "   Revision ID: $REVISION"
    REVISION_LENGTH=${#REVISION}
    echo "   Length: $REVISION_LENGTH characters"
    
    if [ $REVISION_LENGTH -gt 32 ]; then
        echo "   ⚠️  WARNING: This revision ID is too long!"
    fi
else
    echo "   No migration files found"
fi
echo ""

echo "4️⃣  Migration naming guidelines:"
echo "   ✅ Revision ID: ≤ 32 characters (e.g., '20241130_short_name')"
echo "   ✅ Use actual revision ID for down_revision (not filename)"
echo "   ✅ File name: YYYYMMDD_descriptive_name.py"
echo ""

echo "5️⃣  Next steps:"
echo "   1. Create migration: docker-compose exec api alembic revision -m 'description'"
echo "   2. Edit the file and ensure revision ID ≤ 32 chars"
echo "   3. Set correct down_revision: '$REVISION'"
echo "   4. Test: ./test_migration.sh"
echo ""

echo "=========================================="
echo "  Ready to create migration!"
echo "=========================================="
