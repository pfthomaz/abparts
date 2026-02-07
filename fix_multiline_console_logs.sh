#!/bin/bash

# Fix files with broken multi-line console.log statements
# These need to have the entire console.log block commented or removed

echo "Fixing multi-line console.log syntax errors..."

# List of files with syntax errors
files=(
  "frontend/src/components/ExecutionHistory.js"
  "frontend/src/components/InventoryTransferHistory.js"
  "frontend/src/components/StockResetTab.js"
  "frontend/src/contexts/OfflineContext.js"
  "frontend/src/utils/serviceWorkerRegistration.js"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "Fixing $file..."
    # Use perl to remove entire multi-line console.log blocks
    perl -i -0pe 's/\/\/\s*console\.log\([^)]*\n[^)]*\);?//gs' "$file"
  fi
done

echo "Done fixing syntax errors!"
