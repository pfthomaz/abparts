#!/bin/bash

# Step-by-Step Development Deployment
# Run each step manually to see what's happening

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "============================================================"
echo "HYBRID STORAGE - STEP BY STEP DEPLOYMENT"
echo "============================================================"
echo ""

echo -e "${YELLOW}This script will guide you through each step.${NC}"
echo "Press ENTER after each step to continue..."
echo ""

# Step 1
echo "Step 1: Backup development database"
echo "------------------------------------------------------------"
read -p "Press ENTER to backup database..."
mkdir -p ./backups
docker compose exec -T db pg_dump -U abparts_user abparts_dev | gzip > ./backups/abparts_dev_pre_hybrid_$(date +%Y%m%d_%H%M%S).sql.gz
echo -e "${GREEN}✓ Backup created in ./backups/${NC}"
echo ""

# Step 2
echo "Step 2: Stop development containers"
echo "------------------------------------------------------------"
read -p "Press ENTER to stop containers..."
docker compose down
echo -e "${GREEN}✓ Containers stopped${NC}"
echo ""

# Step 3
echo "Step 3: Rebuild API container with new dependencies"
echo "------------------------------------------------------------"
read -p "Press ENTER to rebuild..."
docker compose build api
echo -e "${GREEN}✓ API container rebuilt${NC}"
echo ""

# Step 4
echo "Step 4: Start database and redis"
echo "------------------------------------------------------------"
read -p "Press ENTER to start database..."
docker compose up -d db redis
echo "Waiting for database to be ready..."
sleep 10
echo -e "${GREEN}✓ Database and Redis started${NC}"
echo ""

# Step 5
echo "Step 5: Start API and run database migration"
echo "------------------------------------------------------------"
read -p "Press ENTER to start API and run migration..."
docker compose up -d api
echo "Waiting for API to start..."
sleep 10
echo "Running Alembic migration..."
docker compose exec api alembic upgrade head
echo -e "${GREEN}✓ Database migration completed${NC}"
echo ""

# Step 6
echo "Step 6: Migrate existing images to database"
echo "------------------------------------------------------------"
read -p "Press ENTER to migrate images..."
echo "Copying migration script to container..."
docker compose cp migrate_images_to_db.py api:/tmp/migrate_images_to_db.py
echo "Running migration script..."
docker compose exec api python /tmp/migrate_images_to_db.py
echo -e "${GREEN}✓ Images migrated${NC}"
echo ""

# Step 7
echo "Step 7: Start all services"
echo "------------------------------------------------------------"
read -p "Press ENTER to start all services..."
docker compose up -d
echo "Waiting for services to start..."
sleep 5
echo -e "${GREEN}✓ All services started${NC}"
echo ""

# Step 8
echo "Step 8: Verify deployment"
echo "------------------------------------------------------------"
echo "Checking services..."
docker compose ps
echo ""
echo "Checking image counts in database..."
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
echo "Next steps:"
echo "1. Test at http://localhost:3000"
echo "2. Upload a profile photo"
echo "3. Upload an organization logo"
echo "4. Verify images display correctly"
echo ""
echo "To check logs:"
echo "  docker compose logs -f api"
echo ""
