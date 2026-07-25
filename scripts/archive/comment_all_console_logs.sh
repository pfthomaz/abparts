#!/bin/bash

# Script to comment out all console.log statements in frontend JavaScript files
# Handles console.log at any position in the line
# Excludes test files and node_modules

echo "Commenting out console.log statements in frontend..."

# Find all .js files in frontend/src, excluding test files and node_modules
find frontend/src -name "*.js" -type f \
  ! -path "*/node_modules/*" \
  ! -path "*/__tests__/*" \
  ! -name "*.test.js" \
  ! -name "test-*.js" \
  -print0 | while IFS= read -r -d '' file; do
    # Use perl for more powerful regex replacement
    # This will comment out any line containing console.log that isn't already commented
    perl -i -pe 's/^(\s*)(?!\/\/)(.*)console\.log\(/$1\/\/ $2console.log(/g' "$file"
done

echo "Done! All console.log statements have been commented out."
echo "Note: Test files (test-*.js, *.test.js, __tests__/*) were excluded."
echo "Note: console.warn and console.error statements were preserved for production debugging."
