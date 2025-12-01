#!/bin/bash

# Cleanup Old ABParts Files
# This script removes old non-Docker ABParts files

set -e

echo "========================================="
echo "Cleaning Up Old ABParts Files"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

echo "WARNING: This will remove old ABParts files from /var/www/"
echo "The following directories will be removed:"
echo "  - /var/www/abparts_frontend_dist"
echo "  - /var/www/abparts_images"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Creating backup..."
BACKUP_DIR="/root/abparts_files_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup old files
if [ -d /var/www/abparts_frontend_dist ]; then
    echo "Backing up /var/www/abparts_frontend_dist..."
    tar -czf "$BACKUP_DIR/abparts_frontend_dist.tar.gz" -C /var/www abparts_frontend_dist
    echo "✓ Backed up frontend files"
fi

if [ -d /var/www/abparts_images ]; then
    echo "Backing up /var/www/abparts_images..."
    tar -czf "$BACKUP_DIR/abparts_images.tar.gz" -C /var/www abparts_images
    echo "✓ Backed up image files"
fi

echo "Backups saved to: $BACKUP_DIR"
echo ""

echo "Removing old files..."

# Remove old frontend
if [ -d /var/www/abparts_frontend_dist ]; then
    rm -rf /var/www/abparts_frontend_dist
    echo "✓ Removed /var/www/abparts_frontend_dist"
fi

# Note: Keep abparts_images for now as they might be referenced
# You can manually remove later if not needed
echo ""
echo "Note: /var/www/abparts_images was backed up but NOT removed"
echo "      (images might still be referenced by the database)"
echo "      You can manually remove it later if not needed:"
echo "      sudo rm -rf /var/www/abparts_images"
echo ""

echo "========================================="
echo "✓ Cleanup Complete!"
echo "========================================="
echo ""
echo "Backups saved to: $BACKUP_DIR"
echo ""
