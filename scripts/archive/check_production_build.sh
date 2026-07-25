#!/bin/bash

# Check Production Build Contents
# This script inspects what's actually in the production build

echo "========================================="
echo "Production Build Diagnostics"
echo "========================================="
echo ""

# Check 1: Is web container running?
echo "Check 1: Web container status..."
docker compose ps web
echo ""

# Check 2: What files are being served?
echo "Check 2: Files in nginx html directory..."
docker compose exec web ls -lh /usr/share/nginx/html/ | head -20
echo ""

# Check 3: Check if JavaScript bundles exist
echo "Check 3: JavaScript bundles..."
docker compose exec web find /usr/share/nginx/html/static/js -name "*.js" | head -10
echo ""

# Check 4: Search for machineSelected in the built JavaScript
echo "Check 4: Searching for 'machineSelected' in JavaScript bundles..."
docker compose exec web sh -c "grep -r 'machineSelected' /usr/share/nginx/html/static/js/ 2>/dev/null | head -5"
echo ""

# Check 5: Check if translation files are in the source
echo "Check 5: Translation files in source directory..."
ls -lh frontend/src/locales/
echo ""

# Check 6: Verify machineSelected key in source
echo "Check 6: machineSelected in en.json source..."
grep "machineSelected" frontend/src/locales/en.json
echo ""

# Check 7: Check build timestamp
echo "Check 7: Build timestamp..."
docker compose exec web stat /usr/share/nginx/html/index.html | grep Modify
echo ""

# Check 8: Check if useTranslation hook is in source
echo "Check 8: useTranslation hook exists..."
ls -lh frontend/src/hooks/useTranslation.js
echo ""

# Check 9: Check LocalizationContext
echo "Check 9: LocalizationContext exists..."
ls -lh frontend/src/contexts/LocalizationContext.js
echo ""

# Check 10: Check nginx config
echo "Check 10: Nginx configuration..."
docker compose exec web cat /etc/nginx/conf.d/default.conf
echo ""

echo "========================================="
echo "Diagnostics Complete"
echo "========================================="
echo ""
echo "Key things to check:"
echo "1. Are JavaScript bundles recent (Check 7)?"
echo "2. Is 'machineSelected' in the bundles (Check 4)?"
echo "3. Are translation files in source (Check 5-6)?"
echo ""
