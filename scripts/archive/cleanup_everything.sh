#!/bin/bash

echo "========================================="
echo "Complete Project Cleanup"
echo "========================================="
echo ""
echo "This will move old scripts and docs to organized folders."
echo "Files newer than 12 hours will stay in root."
echo "Only essential config files will remain in root."
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Cancelled."
    exit 1
fi

# Create directory structure
echo ""
echo "Creating directory structure..."
mkdir -p docs
mkdir -p scripts

echo "✓ Directories created"

# Move old .md files (older than 12 hours) except README.md
echo ""
echo "Moving old documentation (>12 hours)..."
find . -maxdepth 1 -name "*.md" ! -name "README.md" -mtime +0.5 -exec mv {} docs/ \;
RECENT_DOCS=$(find . -maxdepth 1 -name "*.md" ! -name "README.md" -mtime -0.5 | wc -l)
echo "✓ Old .md files moved to docs/ ($RECENT_DOCS recent files kept in root)"

# Move old .sh files (older than 12 hours)
echo ""
echo "Moving old shell scripts (>12 hours)..."
find . -maxdepth 1 -name "*.sh" -mtime +0.5 -exec mv {} scripts/ \;
RECENT_SCRIPTS=$(find . -maxdepth 1 -name "*.sh" -mtime -0.5 | wc -l)
echo "✓ Old .sh files moved to scripts/ ($RECENT_SCRIPTS recent files kept in root)"

# Move old .py files (older than 12 hours)
echo ""
echo "Moving old Python scripts (>12 hours)..."
find . -maxdepth 1 -name "*.py" -mtime +0.5 -exec mv {} scripts/ \;
RECENT_PY=$(find . -maxdepth 1 -name "*.py" -mtime -0.5 | wc -l)
echo "✓ Old .py files moved to scripts/ ($RECENT_PY recent files kept in root)"

# Move old .sql files (older than 12 hours)
echo ""
echo "Moving old SQL files (>12 hours)..."
find . -maxdepth 1 -name "*.sql" -mtime +0.5 -exec mv {} scripts/ \;
RECENT_SQL=$(find . -maxdepth 1 -name "*.sql" -mtime -0.5 | wc -l)
echo "✓ Old .sql files moved to scripts/ ($RECENT_SQL recent files kept in root)"

# Move old .txt files (older than 12 hours)
echo ""
echo "Moving old text files (>12 hours)..."
find . -maxdepth 1 -name "*.txt" -mtime +0.5 -exec mv {} docs/ \;
RECENT_TXT=$(find . -maxdepth 1 -name "*.txt" -mtime -0.5 | wc -l)
echo "✓ Old .txt files moved to docs/ ($RECENT_TXT recent files kept in root)"

# Create README files
cat > docs/README.md << 'EOF'
# Documentation

All project documentation has been moved here for better organization.

## Finding What You Need

- Look for files by name or search within this directory
- Most recent work is typically at the top when sorted by date
- Files are named descriptively (e.g., PART_USAGE_FIX_FINAL_SUMMARY.md)

## Cleanup

You can delete old/obsolete documentation files as needed.
EOF

cat > scripts/README.md << 'EOF'
# Scripts

All project scripts have been moved here for better organization.

## Types of Scripts

- **Deployment scripts**: deploy_*.sh
- **Fix scripts**: fix_*.sh
- **Test scripts**: test_*.py, check_*.py
- **Maintenance scripts**: restart_*.sh, rebuild_*.sh
- **SQL scripts**: *.sql

## Usage

Run scripts from the project root:
```bash
./scripts/script_name.sh
```

## Cleanup

You can delete old/obsolete scripts as needed.
EOF

# List what remains in root
echo ""
echo "========================================="
echo "✓ Cleanup Complete!"
echo "========================================="
echo ""
echo "Files kept in root (recent or essential):"
echo ""
echo "Recent files (< 12 hours):"
find . -maxdepth 1 \( -name "*.md" -o -name "*.sh" -o -name "*.py" -o -name "*.sql" -o -name "*.txt" \) ! -name "README.md" -mtime -0.5 -exec basename {} \;
echo ""
echo "Essential config files:"
ls -1 | grep -E "^(docker-compose|\.env|\.gitignore|nginx|README)"
echo ""
echo "Old files moved to:"
echo "  docs/ - $(ls docs/ 2>/dev/null | wc -l) files"
echo "  scripts/ - $(ls scripts/ 2>/dev/null | wc -l) files"
echo ""
echo "To see what was moved:"
echo "  ls -lt docs/ | head -20"
echo "  ls -lt scripts/ | head -20"
echo ""
