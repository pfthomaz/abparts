#!/bin/bash

# Script to comment out ALL remaining console.log statements in frontend
# This catches the ones that were missed by the first cleanup

echo "Commenting out remaining console.log statements..."

# Find all JS files (excluding node_modules, tests, and build directories)
find frontend/src -name "*.js" -type f \
  ! -path "*/node_modules/*" \
  ! -path "*/build/*" \
  ! -path "*/__tests__/*" \
  ! -name "*.test.js" \
  ! -name "test-*.js" | while read file; do
  
  # Check if file contains console.log
  if grep -q "console\.log" "$file"; then
    echo "Processing: $file"
    
    # Use sed to comment out console.log lines
    # This handles both single-line and the start of multi-line console.log statements
    sed -i.bak -E 's/^([[:space:]]*)console\.log\(/\1\/\/ console.log(/g' "$file"
    
    # Remove backup file
    rm -f "${file}.bak"
  fi
done

echo "Done! Remaining console.log statements commented out."
echo ""
echo "Checking for any remaining uncommented console.log..."
remaining=$(find frontend/src -name "*.js" -type f ! -path "*/node_modules/*" ! -path "*/__tests__/*" ! -name "*.test.js" ! -name "test-*.js" -exec grep -l "^[[:space:]]*console\.log" {} \; | wc -l)
echo "Files with uncommented console.log: $remaining"
