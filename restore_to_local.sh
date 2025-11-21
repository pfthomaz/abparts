#!/bin/bash
# Restore Production Backup to Local Development Database

set -e

if [ -z "$1" ]; then
    echo "Usage: ./restore_to_local.sh <backup_file.sql>"
    echo ""
    echo "Available backups:"
    ls -lh abparts_backup_*.sql 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE=$1
IMAGES_FILE="${BACKUP_FILE%.sql}"
IMAGES_FILE="${IMAGES_FILE/backup/images}.tar.gz"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "=== Restoring Production Database to Local Development ==="
echo ""
echo "WARNING: This will REPLACE your local development database!"
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

echo ""
echo "Step 1: Stopping local development containers..."
docker-compose down

echo ""
echo "Step 2: Starting database container..."
docker-compose up -d db
sleep 5

echo ""
echo "Step 3: Dropping and recreating database..."
docker-compose exec -T db psql -U abparts_user -d postgres << EOF
DROP DATABASE IF EXISTS abparts_dev;
CREATE DATABASE abparts_dev;
EOF

echo ""
echo "Step 4: Restoring database from backup..."
cat $BACKUP_FILE | docker-compose exec -T db psql -U abparts_user -d abparts_dev

echo ""
echo "Step 5: Restoring images..."
if [ -f "$IMAGES_FILE" ]; then
    echo "Extracting images to backend/static/..."
    mkdir -p backend/static
    tar -xzf $IMAGES_FILE -C backend/static/
    echo "Images restored"
else
    echo "Warning: Images backup not found: $IMAGES_FILE"
    echo "Skipping images restore"
fi

echo ""
echo "Step 6: Starting all containers..."
docker-compose up -d

echo ""
echo "Step 7: Waiting for services to start..."
sleep 10

echo ""
echo "=== Restore Complete ==="
echo ""
echo "Your local development environment now has production data!"
echo ""
echo "Access the application at: http://localhost:3000"
echo "API docs at: http://localhost:8000/docs"
echo ""
echo "Note: You may need to update .env.development if credentials differ"
echo ""
