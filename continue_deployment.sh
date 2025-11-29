#!/bin/bash

# Continue deployment after fixing syntax error

set -e

GREEN='\033[0;32m'
NC='\033[0m'

echo "============================================================"
echo "CONTINUING DEPLOYMENT AFTER FIX"
echo "============================================================"
echo ""

echo "Step 1: Rebuild API container with fixed code"
echo "------------------------------------------------------------"
docker compose build api
echo -e "${GREEN}✓ API rebuilt${NC}"
echo ""

echo "Step 2: Restart API"
echo "------------------------------------------------------------"
docker compose up -d api
sleep 10
echo -e "${GREEN}✓ API restarted${NC}"
echo ""

echo "Step 3: Run database migration"
echo "------------------------------------------------------------"
docker compose exec api alembic upgrade head
echo -e "${GREEN}✓ Migration completed${NC}"
echo ""

echo "Step 4: Migrate images to database"
echo "------------------------------------------------------------"
docker compose cp migrate_images_to_db.py api:/tmp/migrate_images_to_db.py
docker compose exec api python /tmp/migrate_images_to_db.py
echo -e "${GREEN}✓ Images migrated${NC}"
echo ""

echo "Step 5: Start all services"
echo "------------------------------------------------------------"
docker compose up -d
sleep 5
echo -e "${GREEN}✓ All services started${NC}"
echo ""

echo "Step 6: Verify deployment"
echo "------------------------------------------------------------"
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
