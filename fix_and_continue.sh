#!/bin/bash

# Fix migration heads and continue deployment

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "============================================================"
echo "FIXING MIGRATION HEADS AND CONTINUING DEPLOYMENT"
echo "============================================================"
echo ""

echo -e "${YELLOW}Checking migration status...${NC}"
echo ""

# Show current heads
echo "Current migration heads:"
docker compose exec api alembic heads
echo ""

# Show current database version
echo "Current database version:"
docker compose exec api alembic current
echo ""

# Option 1: Merge heads automatically
echo "Creating merge migration..."
docker compose exec api alembic merge heads -m "merge_all_heads_before_hybrid_storage"
echo ""

# Apply all migrations including merge
echo "Applying all migrations..."
docker compose exec api alembic upgrade heads
echo -e "${GREEN}✓ All migrations applied${NC}"
echo ""

# Now migrate images
echo "Migrating images to database..."
docker compose cp migrate_images_to_db.py api:/tmp/migrate_images_to_db.py
docker compose exec api python /tmp/migrate_images_to_db.py
echo -e "${GREEN}✓ Images migrated${NC}"
echo ""

# Start all services
echo "Starting all services..."
docker compose up -d
sleep 5
echo -e "${GREEN}✓ All services started${NC}"
echo ""

# Verify
echo "Verifying deployment..."
docker compose ps
echo ""
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
  (SELECT COUNT(*) FROM users WHERE profile_photo_data IS NOT NULL) as users_with_photos,
  (SELECT COUNT(*) FROM organizations WHERE logo_data IS NOT NULL) as orgs_with_logos,
  (SELECT COUNT(*) FROM parts WHERE image_data IS NOT NULL) as parts_with_images;
"
echo ""

echo "============================================================"
echo -e "${GREEN}DEPLOYMENT COMPLETE!${NC}"
echo "============================================================"
echo ""
echo "Test at: http://localhost:3000"
echo ""
