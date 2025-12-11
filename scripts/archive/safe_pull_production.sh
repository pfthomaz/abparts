#!/bin/bash
# Safely pull changes on production server with local modifications

set -e

echo "=========================================="
echo "  Safe Git Pull for Production"
echo "=========================================="
echo ""

# Check current status
echo "📋 Checking git status..."
git status

echo ""
echo "🔍 Checking for local changes..."
if git diff --quiet && git diff --cached --quiet; then
    echo "✅ No local changes detected"
else
    echo "⚠️  Local changes detected"
    echo ""
    echo "Modified files:"
    git diff --name-only
    echo ""
fi

echo ""
echo "🔍 Checking for untracked files that would conflict..."
git fetch origin main
CONFLICTS=$(git diff --name-only origin/main 2>/dev/null || echo "")
if [ -n "$CONFLICTS" ]; then
    echo "Files that will be updated:"
    echo "$CONFLICTS"
fi

echo ""
echo "Options:"
echo "1. Stash local changes and pull (recommended)"
echo "2. Backup and force pull (overwrites local changes)"
echo "3. Cancel"
echo ""
read -p "Choose option (1/2/3): " -n 1 -r
echo ""

case $REPLY in
    1)
        echo ""
        echo "📦 Stashing local changes..."
        
        # Remove untracked files that would conflict
        if [ -f "rebuild_frontend.sh" ]; then
            echo "Removing untracked file: rebuild_frontend.sh"
            rm rebuild_frontend.sh
        fi
        
        # Stash any modified files
        git stash push -m "Production local changes before pull $(date +%Y%m%d_%H%M%S)"
        
        echo ""
        echo "⬇️  Pulling latest changes..."
        git pull origin main
        
        echo ""
        echo "✅ Pull complete!"
        echo ""
        echo "Your local changes are stashed. To view them:"
        echo "  git stash list"
        echo ""
        echo "To restore them (if needed):"
        echo "  git stash pop"
        echo ""
        echo "To see what was stashed:"
        echo "  git stash show -p"
        ;;
        
    2)
        echo ""
        echo "💾 Creating backup..."
        BACKUP_DIR="backup_before_pull_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        
        # Backup modified files
        if [ -f "frontend/nginx.conf" ]; then
            cp frontend/nginx.conf "$BACKUP_DIR/"
            echo "Backed up: frontend/nginx.conf"
        fi
        
        # Remove untracked files
        if [ -f "rebuild_frontend.sh" ]; then
            mv rebuild_frontend.sh "$BACKUP_DIR/"
            echo "Backed up: rebuild_frontend.sh"
        fi
        
        echo ""
        echo "🔄 Resetting to remote state..."
        git reset --hard origin/main
        
        echo ""
        echo "⬇️  Pulling latest changes..."
        git pull origin main
        
        echo ""
        echo "✅ Pull complete!"
        echo ""
        echo "Backup saved in: $BACKUP_DIR"
        echo "To restore a file: cp $BACKUP_DIR/<filename> <destination>"
        ;;
        
    3)
        echo ""
        echo "❌ Cancelled"
        exit 0
        ;;
        
    *)
        echo ""
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "  Next Steps"
echo "=========================================="
echo ""
echo "Run the deployment script:"
echo "  chmod +x deploy_images_to_production.sh"
echo "  ./deploy_images_to_production.sh"
echo ""
