#!/bin/bash

# Production Deployment Script for Hybrid Storage
# IMPORTANT: Run this AFTER testing in development

set -e  # Exit on error

echo "============================================================"
echo "PRODUCTION DEPLOYMENT - HYBRID STORAGE"
echo "============================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Confirmation
echo "This will deploy the hybrid storage solution to production."
echo ""
print_warning "IMPORTANT: Make sure you've tested in development first!"
echo ""
read -p "Continue with production deployment? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""

# Step 1: Backup production database
echo "Step 1: Backing up production database..."
echo "------------------------------------------------------------"
ssh root@46.62.153.166 "docker compose exec -T db pg_dump -U abparts_user abparts_prod | gzip > /var/backups/abparts_pre_hybrid_prod_$(date +%Y%m%d_%H%M%S).sql.gz"
print_status "Production database backed up to /var/backups/"
echo ""

# Step 2: Copy files to production
echo "Step 2: Copying files to production..."
echo "------------------------------------------------------------"
rsync -avz --progress \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='backend/static/images' \
    ./ root@46.62.153.166:/root/abparts/
print_status "Files copied to production"
echo ""

# Step 3: Stop production containers
echo "Step 3: Stopping production containers..."
echo "------------------------------------------------------------"
ssh root@46.62.153.166 "cd /root/abparts && docker compose -f docker-compose.prod.yml down"
print_status "Production containers stopped"
echo ""

# Step 4: Rebuild containers
echo "Step 4: Rebuilding production containers..."
echo "------------------------------------------------------------"
ssh root@46.62.153.166 "cd /root/abparts && docker compose -f docker-compose.prod.yml build --no-cache api"
print_status "Containers rebuilt"
echo ""

# Step 5: Start database and redis
echo "Step 5: Starting database and redis..."
echo "------------------------------------------------------------"
ssh root@46.62.153.166 "cd /root/abparts && docker compose -f docker-compose.prod.yml up -d db redis"
sleep 10
print_status "Database and Redis started"
echo ""

# Step 6: Run database migration
echo "Step 6: Running database migration..."
echo "------------------------------------------------------------"
ssh root@46.62.153.166 "cd /root/abparts && docker compose -f docker-compose.prod.yml up -d api"
sleep 10
ssh root@46.62.153.166 "cd /root/abparts && docker compose -f docker-compose.prod.yml exec api alembic upgrade head"
print_status "Database migration completed"
echo ""

# Step 7: Migrate images to database
echo "Step 7: Migrating production images to database..."
echo "------------------------------------------------------------"
ssh root@46.62.153.166 "cd /root/abparts && docker compose -f docker-compose.prod.yml exec api python /app/../migrate_images_to_db.py"
print_status "Production images migrated to database"
echo ""

# Step 8: Start all services
echo "Step 8: Starting all production services..."
echo "------------------------------------------------------------"
ssh root@46.62.153.166 "cd /root/abparts && docker compose -f docker-compose.prod.yml up -d"
print_status "All services started"
echo ""

# Step 9: Restart nginx
echo "Step 9: Restarting nginx..."
echo "------------------------------------------------------------"
ssh root@46.62.153.166 "systemctl restart nginx"
print_status "Nginx restarted"
echo ""

# Step 10: Test production
echo "Step 10: Testing production deployment..."
echo "------------------------------------------------------------"
sleep 5
if curl -s https://abparts.oraseas.com/docs > /dev/null; then
    print_status "Production API is responding"
else
    print_error "Production API is not responding!"
fi
echo ""

# Display status
echo "============================================================"
echo "PRODUCTION DEPLOYMENT COMPLETE!"
echo "============================================================"
echo ""
echo "Services status:"
ssh root@46.62.153.166 "cd /root/abparts && docker compose -f docker-compose.prod.yml ps"
echo ""
echo "Test the application at: https://abparts.oraseas.com"
echo ""
echo "To check logs:"
echo "  ssh root@46.62.153.166"
echo "  cd /root/abparts"
echo "  docker compose -f docker-compose.prod.yml logs -f api"
echo ""
