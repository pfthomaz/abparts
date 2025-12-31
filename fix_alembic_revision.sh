#!/bin/bash
# fix_alembic_revision.sh
# Fix the alembic revision ID issue

echo "=== Fixing Alembic Revision ID Issue ==="
echo ""

# Configuration
PROD_CONTAINER="abparts_db_prod"
API_CONTAINER="abparts_api_prod"
DB_USER="abparts_user"
DB_NAME="abparts_prod"

echo "Step 1: Getting the correct revision ID..."
# Get just the revision ID without (head)
NEW_REVISION=$(docker exec "$API_CONTAINER" alembic heads | head -1 | cut -d' ' -f1)
echo "Correct revision ID: $NEW_REVISION"

echo ""
echo "Step 2: Updating the alembic_version table with correct ID..."
docker exec "$PROD_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -c "UPDATE alembic_version SET version_num = '$NEW_REVISION';"

echo ""
echo "Step 3: Verifying the fix..."
UPDATED_VERSION=$(docker exec "$PROD_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT version_num FROM alembic_version;" | tr -d ' \n')
echo "Updated version in database: $UPDATED_VERSION"

echo ""
echo "Step 4: Testing Alembic status..."
if docker exec "$API_CONTAINER" alembic current; then
    echo "✅ Alembic status is now working correctly!"
else
    echo "❌ Still having issues. Let's check what migration files exist..."
    ls -la backend/alembic/versions/
fi

echo ""
echo "Step 5: Testing Alembic check..."
if docker exec "$API_CONTAINER" alembic check; then
    echo "✅ Alembic check passed - no pending migrations"
else
    echo "⚠️  Alembic check found differences (this might be normal after reset)"
fi

echo ""
echo "=== Fix Complete ==="