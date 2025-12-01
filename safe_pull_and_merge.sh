#!/bin/bash
set -e

echo "========================================="
echo "Safe Pull with Local Changes"
echo "========================================="
echo ""

# Show what files have local changes
echo "Files with local changes:"
git status --short
echo ""

# Stash local changes
echo "Stashing local changes..."
git stash push -m "Local changes before pull $(date +%Y%m%d_%H%M%S)"
echo "✓ Local changes stashed"
echo ""

# Pull from remote
echo "Pulling from remote..."
git pull
echo "✓ Pull complete"
echo ""

# Try to apply stashed changes
echo "Attempting to apply stashed changes..."
if git stash pop; then
    echo "✓ Stashed changes applied successfully"
    echo ""
    echo "Check for any conflicts:"
    git status
else
    echo "⚠ Conflicts detected when applying stashed changes"
    echo ""
    echo "Your stashed changes are preserved. To see them:"
    echo "  git stash list"
    echo ""
    echo "To manually apply them later:"
    echo "  git stash apply stash@{0}"
    echo ""
    echo "To see what's in the stash:"
    echo "  git stash show -p stash@{0}"
    echo ""
    echo "Current conflicts:"
    git status
fi
echo ""
