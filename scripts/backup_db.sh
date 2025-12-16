#!/bin/bash
# scripts/backup_db.sh
# Automated Database Backup Script for ABParts
# Usage: ./scripts/backup_db.sh

# --- Configuration ---
BACKUP_DIR="./backups"
CONTAINER_NAME="abparts_db_prod"
DB_USER="${POSTGRES_USER:-abparts_user}"
DB_NAME="${POSTGRES_DB:-abparts_prod}"
RETENTION_DAYS=30
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="${BACKUP_DIR}/abparts_dump_${TIMESTAMP}.sql.gz"

# --- Setup ---
# Navigate to project root if script is run from scripts/
cd "$(dirname "$0")/.." || exit 1

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "=========================================="
echo "Starting backup at $(date)"
echo "Target: $FILENAME"

# --- Backup ---
# Execute pg_dump inside the container and pipe to gzip
if docker exec "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$FILENAME"; then
    echo "✅ Backup successful!"
    echo "Size: $(du -sh "$FILENAME" | cut -f1)"
else
    echo "❌ Backup failed!"
    # Remove empty/failed file
    rm -f "$FILENAME"
    exit 1
fi

# --- Rotation ---
echo "--- Cleanup ---"
echo "Deleting backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "abparts_dump_*.sql.gz" -mtime +$RETENTION_DAYS -print -delete
echo "Cleanup complete."

echo "Backup process finished at $(date)"
echo "=========================================="
exit 0
