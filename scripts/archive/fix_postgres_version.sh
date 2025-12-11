#!/bin/bash

echo "========================================="
echo "Fixing PostgreSQL Version Issue"
echo "========================================="
echo ""

# Stop all containers
echo "Step 1: Stopping all containers..."
docker compose down
echo "✓ Containers stopped"
echo ""

# Remove the specific database container
echo "Step 2: Removing old database container..."
docker rm -f abparts_db 2>/dev/null || echo "Container already removed"
echo "✓ Container removed"
echo ""

# Remove old PostgreSQL 15 images
echo "Step 3: Removing PostgreSQL 15 images..."
docker rmi postgres:15 2>/dev/null || echo "No postgres:15 image found"
docker rmi postgres:15.15 2>/dev/null || echo "No postgres:15.15 image found"
echo "✓ Old images removed"
echo ""

# Verify docker-compose.yml has postgres:16
echo "Step 4: Verifying docker-compose.yml..."
if grep -q "image: postgres:16" docker-compose.yml; then
    echo "✓ docker-compose.yml correctly specifies postgres:16"
else
    echo "✗ ERROR: docker-compose.yml does not specify postgres:16"
    echo "Current postgres images in docker-compose.yml:"
    grep "image: postgres" docker-compose.yml
    exit 1
fi
echo ""

# Pull PostgreSQL 16 explicitly
echo "Step 5: Pulling PostgreSQL 16 image..."
docker pull postgres:16
echo "✓ PostgreSQL 16 pulled"
echo ""

# List available postgres images
echo "Step 6: Available PostgreSQL images:"
docker images | grep postgres
echo ""

# Start only the database first
echo "Step 7: Starting database container..."
docker compose up -d db
echo "Waiting 5 seconds for database to initialize..."
sleep 5
echo ""

# Check database logs
echo "Step 8: Checking database logs..."
docker compose logs db | tail -20
echo ""

# Check database status
echo "Step 9: Checking database status..."
docker compose ps db
echo ""

echo "========================================="
echo "Done!"
echo "========================================="
echo ""
echo "If the database started successfully, start all services:"
echo "  docker compose up -d"
echo ""
echo "If it still fails, check logs:"
echo "  docker compose logs db"
echo ""
