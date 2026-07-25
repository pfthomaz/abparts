#!/bin/bash

# Script to comment out all console.log statements in frontend JavaScript files
# Excludes test files and node_modules

echo "Commenting out console.log statements in frontend..."

# Find all .js files in frontend/src, excluding test files and node_modules
find frontend/src -name "*.js" -type f \
  ! -path "*/node_modules/*" \
  ! -path "*/__tests__/*" \
  ! -name "*.test.js" \
  ! -name "test-*.js" \
  -exec sed -i.bak 's/^\(\s*\)console\.log(/\1\/\/ console.log(/g' {} \;

# Count how many files were modified
modified_count=$(find frontend/src -name "*.js.bak" -type f | wc -l)

echo "Modified $modified_count files"

# Remove backup files
find frontend/src -name "*.js.bak" -type f -delete

echo "Done! All console.log statements have been commented out."
echo "Note: Test files (test-*.js, *.test.js, __tests__/*) were excluded."
