#!/bin/bash

echo "========================================="
echo "Aggressive Cleanup - Move All Old Files"
echo "========================================="
echo ""
echo "This will move ALL files older than today to organized folders."
echo "Only files from today will stay in root."
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Cancelled."
    exit 1
fi

# Create directory structure
mkdir -p docs/old
mkdir -p scripts/old

echo ""
echo "Moving files..."

# Get today's date for comparison
TODAY=$(date +%Y-%m-%d)

# Count files
MOVED_MD=0
MOVED_SH=0
MOVED_PY=0
MOVED_SQL=0
MOVED_OTHER=0

# Move .md files (except README.md) that are NOT from today
for file in *.md; do
    if [ "$file" != "README.md" ] && [ -f "$file" ]; then
        FILE_DATE=$(date -r "$file" +%Y-%m-%d)
        if [ "$FILE_DATE" != "$TODAY" ]; then
            mv "$file" docs/old/
            ((MOVED_MD++))
        fi
    fi
done

# Move .sh files that are NOT from today
for file in *.sh; do
    if [ -f "$file" ]; then
        FILE_DATE=$(date -r "$file" +%Y-%m-%d)
        if [ "$FILE_DATE" != "$TODAY" ]; then
            mv "$file" scripts/old/
            ((MOVED_SH++))
        fi
    fi
done

# Move .py files that are NOT from today
for file in *.py; do
    if [ -f "$file" ]; then
        FILE_DATE=$(date -r "$file" +%Y-%m-%d)
        if [ "$FILE_DATE" != "$TODAY" ]; then
            mv "$file" scripts/old/
            ((MOVED_PY++))
        fi
    fi
done

# Move .sql files
for file in *.sql; do
    if [ -f "$file" ]; then
        mv "$file" scripts/old/
        ((MOVED_SQL++))
    fi
done

# Move other old files (.txt, .json, .html, .bat, .ini, .conf that are not essential)
for file in *.txt *.json *.html *.bat *.ini; do
    if [ -f "$file" ]; then
        # Skip essential files
        if [[ "$file" != "package.json" && "$file" != "pytest.ini" ]]; then
            FILE_DATE=$(date -r "$file" +%Y-%m-%d 2>/dev/null || echo "$TODAY")
            if [ "$FILE_DATE" != "$TODAY" ]; then
                mv "$file" docs/old/ 2>/dev/null
                ((MOVED_OTHER++))
            fi
        fi
    fi
done

# Move .tar.gz files
for file in *.tar.gz; do
    if [ -f "$file" ]; then
        mv "$file" backups/ 2>/dev/null || mv "$file" scripts/old/
    fi
done

echo ""
echo "========================================="
echo "✓ Cleanup Complete!"
echo "========================================="
echo ""
echo "Files moved:"
echo "  - $MOVED_MD .md files → docs/old/"
echo "  - $MOVED_SH .sh files → scripts/old/"
echo "  - $MOVED_PY .py files → scripts/old/"
echo "  - $MOVED_SQL .sql files → scripts/old/"
echo "  - $MOVED_OTHER other files → docs/old/"
echo ""
echo "Files remaining in root (from today or essential):"
ls -1 | grep -E "\.(md|sh|py|sql|txt)$" | head -20
echo ""
echo "To see what was moved:"
echo "  ls -lt docs/old/ | head -20"
echo "  ls -lt scripts/old/ | head -20"
echo ""
echo "To delete old files (if you don't need them):"
echo "  rm -rf docs/old/"
echo "  rm -rf scripts/old/"
echo ""
