#!/bin/bash
# resolve_git_divergent_branches.sh
# Script to resolve divergent branches in production

echo "=== Resolving Git Divergent Branches ==="
echo ""

# Check current status
echo "Current git status:"
git status

echo ""
echo "Recent commits on local branch:"
git log --oneline -5

echo ""
echo "Recent commits on remote branch:"
git log --oneline -5 origin/main

echo ""
echo "=== Resolution Options ==="
echo "1. MERGE (recommended for production): Combines both branches"
echo "2. REBASE: Replays your commits on top of remote changes"
echo "3. RESET: Discards local changes and matches remote exactly"
echo ""

read -p "Choose resolution method (1=merge, 2=rebase, 3=reset): " choice

case $choice in
    1)
        echo "Using merge strategy..."
        git config pull.rebase false
        git pull origin main
        echo "✅ Merge completed. Check for any merge conflicts above."
        ;;
    2)
        echo "Using rebase strategy..."
        git config pull.rebase true
        git pull origin main
        echo "✅ Rebase completed. Check for any conflicts above."
        ;;
    3)
        echo "⚠️  WARNING: This will discard ALL local changes!"
        read -p "Are you sure? Type 'yes' to continue: " confirm
        if [ "$confirm" = "yes" ]; then
            git reset --hard origin/main
            echo "✅ Reset to match remote exactly."
        else
            echo "Reset cancelled."
        fi
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "Final status:"
git status