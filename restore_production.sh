#!/bin/bash

# ABParts Production Restore Script
# Restores from a backup created by backup_production.sh

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    echo ""
    echo "Available backups:"
    ls -lh /var/backups/abparts/*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"
RESTORE_DIR="/tmp/abparts_restore_$$"

echo "=== ABParts Production Restore ==="
echo "Backup file: ${BACKUP_FILE}"
echo ""

if [ ! -f "${BACKUP_FILE}" ]; then
    echo "❌ Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

echo "⚠️  WARNING: This will overwrite existing data!"
read -p "Continue? (yes/no) " -r
if [[ ! $REPLY == "yes" ]]; then
    echo "Restore cancelled"
    exit 0
fi

echo ""
echo "1. Extracting backup..."
mkdir -p "${RESTORE_DIR}"
tar -xzf "${BACKUP_FILE}" -C "${RESTORE_DIR}"
BACKUP_NAME=$(ls "${RESTORE_DIR}")
BACKUP_PATH="${RESTORE_DIR}/${BACKUP_NAME}"
echo "   ✅ Backup extracted"

echo ""
echo "2. Stopping Docker containers..."
cd ~/abparts
sudo docker compose -f docker-compose.prod.yml down
echo "   ✅ Containers stopped"

echo ""
echo "3. Restoring database..."
sudo docker compose -f docker-compose.prod.yml up -d db
sleep 10
cat "${BACKUP_PATH}/database.sql" | sudo docker exec -i abparts_db_prod psql -U abparts_user abparts_prod
echo "   ✅ Database restored"

echo ""
echo "4. Restoring images..."
sudo tar -xzf "${BACKUP_PATH}/images.tar.gz" -C /var/www/
sudo chown -R www-data:www-data /var/www/abparts_images
echo "   ✅ Images restored"

echo ""
echo "5. Restoring configuration..."
sudo cp "${BACKUP_PATH}/nginx.conf" /etc/nginx/sites-available/abparts.oraseas.com
sudo cp "${BACKUP_PATH}/.env.production" ~/abparts/.env.production 2>/dev/null || echo "   ⚠️  .env.production not in backup"
sudo nginx -t
echo "   ✅ Configuration restored"

echo ""
echo "6. Starting all services..."
sudo docker compose -f docker-compose.prod.yml up -d
sudo systemctl restart nginx
echo "   ✅ Services started"

echo ""
echo "7. Waiting for services..."
sleep 15

echo ""
echo "8. Checking status..."
sudo docker compose -f docker-compose.prod.yml ps

echo ""
echo "=== Restore Complete ==="
echo "✅ Application restored from backup"
echo "✅ Frontend: https://abparts.oraseas.com"
echo ""
echo "Cleaning up..."
rm -rf "${RESTORE_DIR}"
echo "✅ Done"
