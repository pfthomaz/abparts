#!/bin/bash

# Fix divergent branches on production server
# Run this on production as root

echo "============================================================"
echo "FIXING DIVERGENT BRANCHES ON PRODUCTION"
echo "============================================================"
echo ""

cd /root/abparts

echo "Step 1: Check current status"
echo "------------------------------------------------------------"
git status
echo ""

echo "Step 2: Show what changes exist locally"
echo "------------------------------------------------------------"
git diff --stat
echo ""

echo "Step 3: Stash any local changes"
echo "------------------------------------------------------------"
git stash save "local_changes_before_hybrid_storage_$(date +%Y%m%d_%H%M%S)"
echo ""

echo "Step 4: Pull with rebase"
echo "------------------------------------------------------------"
git pull --rebase origin main
echo ""

echo "Step 5: Check if stash has anything"
echo "------------------------------------------------------------"
git stash list
echo ""

echo "Step 6: Show current status"
echo "------------------------------------------------------------"
git status
echo ""

echo "============================================================"
echo "Git branches reconciled!"
echo "============================================================"
echo ""
echo "Local changes (if any) are stashed."
echo "You can review them with: git stash show -p"
echo ""
echo "Now you can proceed with deployment."
echo ""
