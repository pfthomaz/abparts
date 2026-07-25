#!/bin/bash

echo "🚀 Deploying Tour System to Production (Docker-based)"
echo "===================================================="

# Step 1: Add tour translations to locale files
echo "Step 1: Adding tour translations..."
python3 add_tour_translations.py
python3 add_enhanced_tour_translations.py
python3 add_common_scope_translation.py

# Step 2: Check if dependencies are in package.json
echo "Step 2: Checking package.json dependencies..."
cd frontend

if ! grep -q "react-joyride" package.json; then
    echo "❌ react-joyride not found in package.json"
    echo "Please add the following to your package.json dependencies:"
    echo '  "react-joyride": "^2.5.2",'
    echo '  "@heroicons/react": "^2.0.18",'
    echo ""
    echo "Then run: docker-compose -f docker-compose.prod.yml build --no-cache web"
    exit 1
else
    echo "✅ react-joyride found in package.json"
fi

if ! grep -q "@heroicons/react" package.json; then
    echo "❌ @heroicons/react not found in package.json"
    echo "Please add the following to your package.json dependencies:"
    echo '  "@heroicons/react": "^2.0.18",'
    echo ""
    echo "Then run: docker-compose -f docker-compose.prod.yml build --no-cache web"
    exit 1
else
    echo "✅ @heroicons/react found in package.json"
fi

cd ..

# Step 3: Rebuild frontend container
echo "Step 3: Rebuilding frontend container..."
docker-compose -f docker-compose.prod.yml build --no-cache web

# Step 4: Restart services
echo "Step 4: Restarting services..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "✅ Tour System Deployment Complete!"
echo ""
echo "🎯 What's been deployed:"
echo "- React Joyride tour system"
echo "- Help button with guided tours menu"
echo "- 4 tour workflows: Parts Ordering, Parts Usage, Daily Operations, Scheduled Maintenance"
echo "- Full localization support for all 6 languages"
echo "- Interactive and Quick Guide tour types"
echo "- Auto-dismissing success toast for maintenance completion"