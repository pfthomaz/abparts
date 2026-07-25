#!/bin/bash
# Backup Production Database and Download to Local Machine

set -e

echo "=== Production Database Backup and Download ==="
echo ""

# Configuration
PROD_SERVER="diogo@46.62.153.166"
BACKUP_DIR="/tmp"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="abparts_backup_${TIMESTAMP}.sql"

echo "Step 1: Creating backup on production server..."
ssh $PROD_SERVER << 'ENDSSH'
cd ~/abparts
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="abparts_backup_${TIMESTAMP}.sql"

echo "Creating database backup..."
sudo docker exec abparts_db_prod pg_dump -U abparts_user -d abparts_prod > /tmp/${BACKUP_FILE}

echo "Backup created: /tmp/${BACKUP_FILE}"
ls -lh /tmp/${BACKUP_FILE}

# Also backup the images
echo ""
echo "Creating images backup..."
cd /var/lib/abparts
sudo tar -czf /tmp/abparts_images_${TIMESTAMP}.tar.gz images/
echo "Images backup created: /tmp/abparts_images_${TIMESTAMP}.tar.gz"
ls -lh /tmp/abparts_images_${TIMESTAMP}.tar.gz

echo ""
echo "Backups ready for download:"
ls -lh /tmp/abparts_*
ENDSSH

echo ""
echo "Step 2: Downloading backups to local machine..."

# Get the latest backup files
LATEST_SQL=$(ssh $PROD_SERVER "ls -t /tmp/abparts_backup_*.sql | head -1")
LATEST_IMAGES=$(ssh $PROD_SERVER "ls -t /tmp/abparts_images_*.tar.gz | head -1")

echo "Downloading database backup..."
scp $PROD_SERVER:$LATEST_SQL ./

echo "Downloading images backup..."
scp $PROD_SERVER:$LATEST_IMAGES ./

echo ""
echo "Step 3: Cleaning up remote backups..."
ssh $PROD_SERVER "rm -f /tmp/abparts_backup_*.sql /tmp/abparts_images_*.tar.gz"

echo ""
echo "=== Backup Complete ==="
echo ""
echo "Files downloaded:"
ls -lh abparts_backup_*.sql abparts_images_*.tar.gz
echo ""
echo "To restore locally, run:"
echo "  ./restore_to_local.sh $(basename $LATEST_SQL)"
echo ""
