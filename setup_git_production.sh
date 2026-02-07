#!/bin/bash

# Production Git Setup Script
# This script will backup production files, pull the repository, and restore production configs

set -e

echo "🔧 Setting up Git on production server..."

# Create backup directory
BACKUP_DIR=~/abparts_production_backup_$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

echo "📦 Backing up production files to $BACKUP_DIR..."

# Backup critical production files
cp .env $BACKUP_DIR/ 2>/dev/null || echo "No .env file found"
cp .env.production $BACKUP_DIR/ 2>/dev/null || echo "No .env.production file found"
cp docker-compose.prod.yml $BACKUP_DIR/ 2>/dev/null || echo "No docker-compose.prod.yml file found"
cp nginx-production.conf $BACKUP_DIR/ 2>/dev/null || echo "No nginx-production.conf file found"

# Backup database files if they exist
cp *.sql $BACKUP_DIR/ 2>/dev/null || echo "No SQL backup files found"

echo "✅ Backup complete at: $BACKUP_DIR"
echo ""

# Force checkout from remote
echo "📥 Pulling repository from GitHub..."
git reset --hard
git clean -fd
git checkout -b main origin/main --force

echo ""
echo "✅ Repository pulled successfully!"
echo ""

# Restore production files
echo "📤 Restoring production configuration files..."
cp $BACKUP_DIR/.env . 2>/dev/null && echo "✓ Restored .env" || echo "✗ No .env to restore"
cp $BACKUP_DIR/.env.production . 2>/dev/null && echo "✓ Restored .env.production" || echo "✗ No .env.production to restore"
cp $BACKUP_DIR/docker-compose.prod.yml . 2>/dev/null && echo "✓ Restored docker-compose.prod.yml" || echo "✗ No docker-compose.prod.yml to restore"
cp $BACKUP_DIR/nginx-production.conf . 2>/dev/null && echo "✓ Restored nginx-production.conf" || echo "✗ No nginx-production.conf to restore"

echo ""
echo "🎉 Git setup complete!"
echo ""
echo "Current branch:"
git branch
echo ""
echo "Git status:"
git status
echo ""
echo "📝 Next steps:"
echo "  - To pull updates: git pull origin main"
echo "  - Your backup is at: $BACKUP_DIR"
echo "  - Production files (.env, etc.) are restored and should be in .gitignore"
