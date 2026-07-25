#!/bin/bash

echo "========================================="
echo "Cleanup Preview - What Will Be Moved"
echo "========================================="
echo ""

echo "Python files in root:"
echo "--------------------"
find . -maxdepth 1 -name "*.py" -exec ls -lh {} \; | awk '{print $9, "(" $6, $7, $8 ")"}'
echo ""

echo "Files that will be MOVED (>12 hours old):"
echo "----------------------------------------"
echo ""
echo "Old .py files:"
find . -maxdepth 1 -name "*.py" -mtime +0.5 -exec basename {} \;
echo ""
echo "Old .sh files:"
find . -maxdepth 1 -name "*.sh" -mtime +0.5 -exec basename {} \;
echo ""
echo "Old .md files (except README.md):"
find . -maxdepth 1 -name "*.md" ! -name "README.md" -mtime +0.5 -exec basename {} \;
echo ""
echo "Old .sql files:"
find . -maxdepth 1 -name "*.sql" -mtime +0.5 -exec basename {} \;
echo ""

echo "Files that will STAY in root (<12 hours old):"
echo "--------------------------------------------"
echo ""
echo "Recent .py files:"
find . -maxdepth 1 -name "*.py" -mtime -0.5 -exec basename {} \;
echo ""
echo "Recent .sh files:"
find . -maxdepth 1 -name "*.sh" -mtime -0.5 -exec basename {} \;
echo ""
echo "Recent .md files:"
find . -maxdepth 1 -name "*.md" ! -name "README.md" -mtime -0.5 -exec basename {} \;
echo ""

echo "========================================="
echo "Run ./cleanup_everything.sh to proceed"
echo "========================================="
