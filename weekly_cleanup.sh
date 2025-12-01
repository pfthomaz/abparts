#!/bin/bash

echo "========================================="
echo "Weekly Project Cleanup"
echo "========================================="
echo ""
echo "This script keeps your project organized by:"
echo "  1. Moving old files (>2 days) to archive folders"
echo "  2. Organizing test files"
echo "  3. Keeping only recent work visible"
echo ""

# Check if this is an automatic run
if [ "$1" = "--auto" ]; then
    echo "Running automatic cleanup..."
    AUTO_MODE=true
else
    read -p "Continue with cleanup? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 1
    fi
    AUTO_MODE=false
fi

# Create directory structure
mkdir -p docs/archive
mkdir -p scripts/archive
mkdir -p tests/integration

echo ""
echo "Step 1: Moving old documentation (>2 days)..."
MOVED_DOCS=0
for file in *.md; do
    if [ "$file" != "README.md" ] && [ -f "$file" ]; then
        # Check if file is older than 2 days
        if [ $(find "$file" -mtime +2 2>/dev/null | wc -l) -gt 0 ]; then
            mv "$file" docs/archive/
            ((MOVED_DOCS++))
        fi
    fi
done
echo "  Moved $MOVED_DOCS old .md files"

echo ""
echo "Step 2: Moving old scripts (>2 days)..."
MOVED_SCRIPTS=0
for file in *.sh; do
    if [ -f "$file" ] && [ "$file" != "weekly_cleanup.sh" ]; then
        if [ $(find "$file" -mtime +2 2>/dev/null | wc -l) -gt 0 ]; then
            mv "$file" scripts/archive/
            ((MOVED_SCRIPTS++))
        fi
    fi
done
echo "  Moved $MOVED_SCRIPTS old .sh files"

echo ""
echo "Step 3: Moving old Python scripts (>2 days)..."
MOVED_PY=0
for file in *.py; do
    if [ -f "$file" ]; then
        if [ $(find "$file" -mtime +2 2>/dev/null | wc -l) -gt 0 ]; then
            # Move test files to tests/, others to scripts/
            if [[ "$file" == test_* ]] || [[ "$file" == check_* ]] || [[ "$file" == validate_* ]]; then
                mv "$file" tests/integration/
            else
                mv "$file" scripts/archive/
            fi
            ((MOVED_PY++))
        fi
    fi
done
echo "  Moved $MOVED_PY old .py files"

echo ""
echo "Step 4: Moving old SQL files..."
MOVED_SQL=0
for file in *.sql; do
    if [ -f "$file" ]; then
        mv "$file" scripts/archive/
        ((MOVED_SQL++))
    fi
done
echo "  Moved $MOVED_SQL .sql files"

echo ""
echo "Step 5: Cleaning up old archives (>30 days)..."
if [ -d "docs/archive" ]; then
    DELETED_DOCS=$(find docs/archive -type f -mtime +30 -delete -print | wc -l)
    echo "  Deleted $DELETED_DOCS very old docs"
fi
if [ -d "scripts/archive" ]; then
    DELETED_SCRIPTS=$(find scripts/archive -type f -mtime +30 -delete -print | wc -l)
    echo "  Deleted $DELETED_SCRIPTS very old scripts"
fi

echo ""
echo "========================================="
echo "✓ Cleanup Complete!"
echo "========================================="
echo ""
echo "Summary:"
echo "  - Moved $MOVED_DOCS documentation files"
echo "  - Moved $MOVED_SCRIPTS shell scripts"
echo "  - Moved $MOVED_PY Python scripts"
echo "  - Moved $MOVED_SQL SQL files"
echo ""
echo "Current root directory:"
ls -1 | grep -E "\.(md|sh|py|sql)$" | head -10
echo ""
echo "Archives:"
echo "  docs/archive/    - $(ls docs/archive 2>/dev/null | wc -l) files"
echo "  scripts/archive/ - $(ls scripts/archive 2>/dev/null | wc -l) files"
echo ""

# Update last cleanup date
date > .last_cleanup

if [ "$AUTO_MODE" = false ]; then
    echo "💡 Tip: Run this script every few days to keep things tidy!"
    echo "   Or set up a cron job: ./weekly_cleanup.sh --auto"
fi
