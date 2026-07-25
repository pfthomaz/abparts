#!/bin/bash
# Apply net cleaning migration manually via SQL

set -e

echo "=========================================="
echo "Manual Net Cleaning Migration"
echo "=========================================="
echo ""

echo "Step 1: Backing up current alembic_version..."
docker compose exec db psql -U abparts_user -d abparts_prod -c "SELECT * FROM alembic_version;" > alembic_version_backup.txt
echo "✓ Backup saved to alembic_version_backup.txt"
echo ""

echo "Step 2: Running manual migration SQL..."
docker compose exec -T db psql -U abparts_user -d abparts_prod < create_net_cleaning_tables_manual.sql
echo "✓ Migration SQL executed"
echo ""

echo "Step 3: Verifying tables created..."
echo ""
echo "Farm Sites table:"
docker compose exec db psql -U abparts_user -d abparts_prod -c "\d farm_sites"
echo ""
echo "Nets table:"
docker compose exec db psql -U abparts_user -d abparts_prod -c "\d nets"
echo ""
echo "Net Cleaning Records table:"
docker compose exec db psql -U abparts_user -d abparts_prod -c "\d net_cleaning_records"
echo ""

echo "Step 4: Checking Alembic version..."
docker compose exec db psql -U abparts_user -d abparts_prod -c "SELECT * FROM alembic_version;"
echo ""

echo "Step 5: Verifying Alembic sees correct state..."
docker compose exec api alembic current
echo ""

echo "=========================================="
echo "✓ MANUAL MIGRATION COMPLETE"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Rebuild frontend: docker compose build --no-cache web"
echo "2. Restart services: docker compose restart"
echo "3. Test the feature in the UI"
