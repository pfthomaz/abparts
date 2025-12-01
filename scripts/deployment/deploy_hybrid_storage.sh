#!/bin/bash

# Hybrid Storage Deployment Script
# This script implements the hybrid image/video storage solution

set -e  # Exit on error

echo "============================================================"
echo "HYBRID STORAGE DEPLOYMENT"
echo "============================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Step 1: Backup development database
echo "Step 1: Backing up development database..."
echo "------------------------------------------------------------"
mkdir -p ./backups
docker compose exec -T db pg_dump -U abparts_user abparts_dev | gzip > ./backups/abparts_dev_pre_hybrid_$(date +%Y%m%d_%H%M%S).sql.gz
print_status "Development database backed up to ./backups/"
echo ""

# Step 2: Stop development containers
echo "Step 2: Stopping development containers..."
echo "------------------------------------------------------------"
docker compose down
print_status "Development containers stopped"
echo ""

# Step 3: Install Python dependencies
echo "Step 3: Installing Python dependencies..."
echo "------------------------------------------------------------"
docker compose build api
print_status "Dependencies installed"
echo ""

# Step 4: Start database and redis
echo "Step 4: Starting database and redis..."
echo "------------------------------------------------------------"
docker compose up -d db redis
sleep 5
print_status "Database and Redis started"
echo ""

# Step 5: Run database migration
echo "Step 5: Running database migration..."
echo "------------------------------------------------------------"
docker compose up -d api
sleep 5
docker compose exec api alembic upgrade head
print_status "Database migration completed"
echo ""

# Step 6: Migrate images to database
echo "Step 6: Migrating existing images to database..."
echo "------------------------------------------------------------"
docker compose cp migrate_images_to_db.py api:/tmp/migrate_images_to_db.py
docker compose exec api python /tmp/migrate_images_to_db.py
print_status "Images migrated to database"
echo ""

# Step 7: Start all services
echo "Step 7: Starting all development services..."
echo "------------------------------------------------------------"
docker compose up -d
print_status "All services started"
echo ""

# Step 8: Test image serving
echo "Step 8: Testing image serving..."
echo "------------------------------------------------------------"
sleep 5
echo "Waiting for API to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/docs > /dev/null; then
        print_status "API is ready"
        break
    fi
    sleep 1
done
echo ""

# Step 9: Display next steps
echo "============================================================"
echo "DEVELOPMENT DEPLOYMENT COMPLETE!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "1. Test image uploads at: http://localhost:3000"
echo "2. Verify images are displayed correctly"
echo "3. Check that new uploads work"
echo ""
echo "To deploy to production:"
echo "  ./deploy_to_production.sh"
echo ""
echo "Services running:"
docker compose ps
echo ""
