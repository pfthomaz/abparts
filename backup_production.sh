#!/bin/bash

# ABParts Production Backup Script
# Creates a complete backup of database, images, and configuration

BACKUP_DIR="/var/backups/abparts"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="abparts_backup_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

echo "=== ABParts Production Backup ==="
echo "Backup location: ${BACKUP_PATH}"
echo ""

# Create backup directory
sudo mkdir -p "${BACKUP_PATH}"

echo "1. Backing up database..."
# Try both possible container names
if sudo docker ps --format '{{.Names}}' | grep -q "abparts_db_prod"; then
    DB_CONTAINER="abparts_db_prod"
elif sudo docker ps --format '{{.Names}}' | grep -q "abparts_db"; then
    DB_CONTAINER="abparts_db"
else
    echo "   ❌ Database container not found"
    DB_CONTAINER=""
fi

if [ -n "$DB_CONTAINER" ]; then
    sudo docker exec $DB_CONTAINER pg_dump -U abparts_user abparts_prod | sudo tee "${BACKUP_PATH}/database.sql" > /dev/null
    echo "   ✅ Database backed up from $DB_CONTAINER ($(du -h "${BACKUP_PATH}/database.sql" | cut -f1))"
else
    echo "   ⚠️  Skipping database backup - container not running"
    echo "" | sudo tee "${BACKUP_PATH}/database.sql" > /dev/null
fi

echo ""
echo "2. Backing up images..."
sudo tar -czf "${BACKUP_PATH}/images.tar.gz" -C /var/www abparts_images
echo "   ✅ Images backed up ($(du -h "${BACKUP_PATH}/images.tar.gz" | cut -f1))"

echo ""
echo "3. Backing up configuration..."
sudo cp /etc/nginx/sites-available/abparts.oraseas.com "${BACKUP_PATH}/nginx.conf"
sudo cp ~/abparts/.env.production "${BACKUP_PATH}/.env.production" 2>/dev/null || echo "   ⚠️  .env.production not found"
sudo cp ~/abparts/docker-compose.prod.yml "${BACKUP_PATH}/docker-compose.prod.yml"
echo "   ✅ Configuration backed up"

echo ""
echo "4. Creating backup manifest..."
sudo bash -c "cat > '${BACKUP_PATH}/MANIFEST.txt'" << EOF
ABParts Backup
Created: $(date)
Hostname: $(hostname)
Docker Images:
$(sudo docker images | grep abparts)

Containers:
$(sudo docker ps -a | grep abparts)

Database Size: $(du -h "${BACKUP_PATH}/database.sql" | cut -f1)
Images Size: $(du -h "${BACKUP_PATH}/images.tar.gz" | cut -f1)
Total Backup Size: $(du -sh "${BACKUP_PATH}" | cut -f1)
EOF
echo "   ✅ Manifest created"

echo ""
echo "5. Compressing backup..."
sudo tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" -C "${BACKUP_DIR}" "${BACKUP_NAME}"
sudo rm -rf "${BACKUP_PATH}"
echo "   ✅ Backup compressed"

echo ""
echo "=== Backup Complete ==="
echo "Backup file: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo "Size: $(du -h "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1))"
echo ""
echo "To restore on another server:"
echo "  1. Extract: tar -xzf ${BACKUP_NAME}.tar.gz"
echo "  2. Restore database: psql -U abparts_user abparts_prod < database.sql"
echo "  3. Restore images: tar -xzf images.tar.gz -C /var/www/"
echo "  4. Copy configs and start Docker containers"
echo ""
echo "Cleaning up old backups (keeping last 7 days)..."
sudo find "${BACKUP_DIR}" -name "abparts_backup_*.tar.gz" -mtime +7 -delete
echo "✅ Cleanup complete"
