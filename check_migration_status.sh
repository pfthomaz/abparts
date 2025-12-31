#!/bin/bash
# check_migration_status.sh
# Quick script to check current migration status before reset

echo "=== Current Migration Status Check ==="
echo ""

# Configuration
PROD_CONTAINER="abparts_db_prod"
API_CONTAINER="abparts_api_prod"
DB_USER="abparts_user"
DB_NAME="abparts_prod"

echo "1. Checking if containers are running..."
if docker ps --format "{{.Names}}" | grep -q "$PROD_CONTAINER"; then
    echo "✅ Database container ($PROD_CONTAINER) is running"
else
    echo "❌ Database container ($PROD_CONTAINER) is not running"
    exit 1
fi

if docker ps --format "{{.Names}}" | grep -q "$API_CONTAINER"; then
    echo "✅ API container ($API_CONTAINER) is running"
else
    echo "❌ API container ($API_CONTAINER) is not running"
    exit 1
fi

echo ""
echo "2. Current migration files:"
if ls backend/alembic/versions/*.py >/dev/null 2>&1; then
    echo "Found $(ls backend/alembic/versions/*.py | wc -l) migration files:"
    ls -la backend/alembic/versions/*.py | awk '{print "  " $9 " (" $5 " bytes, " $6 " " $7 " " $8 ")"}'
else
    echo "❌ No migration files found"
fi

echo ""
echo "3. Current Alembic version in production database:"
if CURRENT_VERSION=$(docker exec "$PROD_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT version_num FROM alembic_version;" 2>/dev/null | tr -d ' \n'); then
    if [ -n "$CURRENT_VERSION" ]; then
        echo "✅ Current version: $CURRENT_VERSION"
    else
        echo "⚠️  alembic_version table exists but is empty"
    fi
else
    echo "⚠️  alembic_version table does not exist (normal for fresh installs)"
fi

echo ""
echo "4. Alembic history:"
if docker exec "$API_CONTAINER" alembic history 2>/dev/null; then
    echo "✅ Alembic history retrieved"
else
    echo "❌ Could not retrieve Alembic history"
fi

echo ""
echo "5. Current Alembic status:"
if docker exec "$API_CONTAINER" alembic current 2>/dev/null; then
    echo "✅ Current status retrieved"
else
    echo "❌ Could not retrieve current status"
fi

echo ""
echo "6. Database schema check:"
TABLE_COUNT=$(docker exec "$PROD_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | tr -d ' \n')
echo "✅ Found $TABLE_COUNT tables in public schema"

echo ""
echo "7. Database size:"
DB_SIZE=$(docker exec "$PROD_CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" 2>/dev/null | tr -d ' \n')
echo "✅ Database size: $DB_SIZE"

echo ""
echo "=== Status Check Complete ==="
echo ""
echo "Ready to proceed with schema reset? Run: ./reset_database_schema.sh"