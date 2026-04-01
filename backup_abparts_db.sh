#!/bin/bash

# ABParts Daily Database Backup Script
# Runs via crontab to backup the production database daily
# Keeps last 30 days of backups

BACKUP_DIR="/home/diogo/abparts/backups/daily"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="abparts_prod_${TIMESTAMP}.sql.gz"
LOG_FILE="/home/diogo/abparts/backups/backup.log"
RETENTION_DAYS=30

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "[$(date)] Starting backup..." >> "$LOG_FILE"

# Dump database from Docker container, compress with gzip
docker exec abparts_db_prod pg_dump -U abparts_user -d abparts_prod | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"

# Check if backup succeeded
if [ $? -eq 0 ] && [ -s "${BACKUP_DIR}/${BACKUP_FILE}" ]; then
    SIZE=$(du -h "${BACKUP_DIR}/${BACKUP_FILE}" | cut -f1)
    echo "[$(date)] Backup successful: ${BACKUP_FILE} (${SIZE})" >> "$LOG_FILE"
else
    echo "[$(date)] ERROR: Backup failed!" >> "$LOG_FILE"
    rm -f "${BACKUP_DIR}/${BACKUP_FILE}"
    exit 1
fi

# Remove backups older than retention period
DELETED=$(find "$BACKUP_DIR" -name "abparts_prod_*.sql.gz" -mtime +${RETENTION_DAYS} -delete -print | wc -l)
if [ "$DELETED" -gt 0 ]; then
    echo "[$(date)] Cleaned up ${DELETED} old backup(s)" >> "$LOG_FILE"
fi

echo "[$(date)] Backup complete" >> "$LOG_FILE"
