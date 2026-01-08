#!/bin/bash

echo "=== Resolving Production Git Conflicts ==="

# Remove the conflicting untracked file
echo "1. Removing conflicting untracked file..."
if [ -f "fix_production_deployment.sh" ]; then
    rm fix_production_deployment.sh
    echo "✅ Removed fix_production_deployment.sh"
fi

# Stash local changes to conflicting files
echo "2. Stashing local changes..."
git stash push -m "Production local changes before AI admin fix" ai_assistant/app/static/admin.html docker-compose.prod.yml

# Pull latest changes
echo "3. Pulling latest changes from main..."
git pull origin main

# Check if we need to apply any stashed changes
echo "4. Checking stashed changes..."
if git stash list | grep -q "Production local changes"; then
    echo "Found stashed changes. Checking if they're still needed..."
    
    # Show what's in the stash
    echo "Stashed changes:"
    git stash show -p stash@{0}
    
    echo ""
    echo "The remote repository should now have the latest AI admin fix."
    echo "Your local production changes have been stashed."
    echo "You can review them with: git stash show -p stash@{0}"
    echo "If needed, apply them with: git stash pop"
else
    echo "No relevant stashed changes found."
fi

echo "✅ Git conflicts resolved!"
echo "📝 Ready to deploy AI Assistant admin fix"