#!/bin/bash

# Test if translations are actually in the production build

echo "========================================="
echo "Testing Translation in Production Build"
echo "========================================="
echo ""

echo "Searching for 'machineSelected' in production JavaScript bundles..."
echo ""

# Find and search all JS files
FOUND=0
docker compose exec web sh -c "
    for file in /usr/share/nginx/html/static/js/*.js; do
        if grep -q 'machineSelected' \"\$file\" 2>/dev/null; then
            echo \"✓ Found in: \$(basename \$file)\"
            FOUND=1
        fi
    done
    
    if [ \$FOUND -eq 0 ]; then
        echo \"✗ NOT FOUND in any JavaScript bundle\"
        echo \"\"
        echo \"This means the translation files were not included in the build.\"
        echo \"\"
        echo \"Solution:\"
        echo \"1. Verify translation files exist in source\"
        echo \"2. Rebuild the container\"
        echo \"3. Make sure useTranslation.js imports the JSON files\"
    fi
"

echo ""
echo "Checking if translation files are imported in useTranslation.js..."
if grep -q "import.*locales.*json" frontend/src/hooks/useTranslation.js; then
    echo "✓ Translation files are imported in useTranslation.js"
else
    echo "✗ Translation files NOT imported in useTranslation.js"
    echo ""
    echo "This is the problem! useTranslation.js must import the JSON files."
fi

echo ""
echo "========================================="
echo "Test Complete"
echo "========================================="
