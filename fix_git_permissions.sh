#!/bin/bash
# fix_git_permissions.sh
# Fix Git permissions issue

echo "=== Fixing Git Permissions Issue ==="
echo ""

# Check current user and git directory ownership
echo "Current user: $(whoami)"
echo "Git directory ownership:"
ls -la .git/ | head -5

echo ""
echo "Checking problematic file:"
ls -la .git/logs/refs/remotes/origin/main 2>/dev/null || echo "File doesn't exist yet"

echo ""
echo "Step 1: Fix ownership of entire .git directory..."
sudo chown -R $(whoami):$(whoami) .git/

echo ""
echo "Step 2: Fix permissions..."
chmod -R u+w .git/

echo ""
echo "Step 3: Recreate the problematic directory structure if needed..."
mkdir -p .git/logs/refs/remotes/origin/
touch .git/logs/refs/remotes/origin/main

echo ""
echo "Step 4: Set correct permissions..."
chmod 644 .git/logs/refs/remotes/origin/main

echo ""
echo "Step 5: Verify permissions..."
ls -la .git/logs/refs/remotes/origin/main

echo ""
echo "✅ Git permissions fixed. Try 'git pull' again."