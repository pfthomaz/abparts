#!/bin/bash
set -e

echo "========================================="
echo "Resolving Git Conflicts on Production"
echo "========================================="
echo ""

echo "Conflicting files:"
echo "  - backend/alembic/versions/20241130_merge_heads.py"
echo "  - docker-compose.yml"
echo ""

echo "These files will be deleted/reset because:"
echo "  1. 20241130_merge_heads.py - Old migration, will be replaced by baseline"
echo "  2. docker-compose.yml - Production uses docker-compose.prod.yml"
echo ""

read -p "Reset these files and pull? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    echo ""
    echo "Manual resolution:"
    echo "  git checkout backend/alembic/versions/20241130_merge_heads.py"
    echo "  git checkout docker-compose.yml"
    echo "  git pull"
    exit 1
fi
echo ""

# Backup the files first
echo "Backing up conflicting files..."
if [ -f backend/alembic/versions/20241130_merge_heads.py ]; then
    cp backend/alembic/versions/20241130_merge_heads.py backend/alembic/versions/20241130_merge_heads.py.backup
    echo "✓ Backed up 20241130_merge_heads.py"
fi

if [ -f docker-compose.yml ]; then
    cp docker-compose.yml docker-compose.yml.backup
    echo "✓ Backed up docker-compose.yml"
fi
echo ""

# Reset the files to remote version
echo "Resetting files to remote version..."
git checkout backend/alembic/versions/20241130_merge_heads.py
git checkout docker-compose.yml
echo "✓ Files reset"
echo ""

# Pull from remote
echo "Pulling from remote..."
git pull
echo "✓ Pull complete"
echo ""

echo "========================================="
echo "Conflict Resolved!"
echo "========================================="
echo ""
echo "Backups saved:"
echo "  - backend/alembic/versions/20241130_merge_heads.py.backup"
echo "  - docker-compose.yml.backup"
echo ""
echo "Next step: Deploy baseline migration"
echo "  chmod +x deploy_baseline_to_prod.sh"
echo "  ./deploy_baseline_to_prod.sh"
echo ""
