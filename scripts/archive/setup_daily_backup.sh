#!/bin/bash

# Setup daily database backup crontab
# Run this on the production server: sudo ./setup_daily_backup.sh

SCRIPT_PATH="/home/diogo/abparts/backup_abparts_db.sh"
BACKUP_DIR="/home/diogo/abparts/backups/daily"

# Create backup directories
mkdir -p "$BACKUP_DIR"

# Make backup script executable
chmod +x "$SCRIPT_PATH"

# Add crontab entry (runs daily at 2:00 AM)
# Check if entry already exists
EXISTING=$(crontab -l 2>/dev/null | grep "backup_abparts_db.sh" | wc -l)

if [ "$EXISTING" -gt 0 ]; then
    echo "Crontab entry already exists. Replacing..."
    crontab -l 2>/dev/null | grep -v "backup_abparts_db.sh" | crontab -
fi

# Add new crontab entry
(crontab -l 2>/dev/null; echo "0 2 * * * ${SCRIPT_PATH} >> /home/diogo/abparts/backups/backup.log 2>&1") | crontab -

echo "✓ Daily backup configured!"
echo ""
echo "Schedule: Every day at 2:00 AM"
echo "Backup dir: ${BACKUP_DIR}"
echo "Retention: 30 days"
echo ""
echo "Current crontab:"
crontab -l
echo ""
echo "Useful commands:"
echo "  Manual backup:  ./backup_abparts_db.sh"
echo "  View backups:   ls -lh ${BACKUP_DIR}"
echo "  View log:       tail -20 /home/diogo/abparts/backups/backup.log"
echo "  Edit crontab:   crontab -e"
