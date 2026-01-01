#!/bin/bash

echo "🚀 Deploying Tour System to Production"
echo "======================================"

# Step 1: Add tour translations to locale files
echo "Step 1: Adding tour translations..."
python3 add_tour_translations.py
echo ""
python3 add_enhanced_tour_translations.py
echo ""
python3 add_common_scope_translation.py
echo ""

# Step 2: Verify dependencies are in package.json
echo "Step 2: Verifying dependencies..."
if grep -q "react-joyride" frontend/package.json && grep -q "@heroicons/react" frontend/package.json; then
    echo "✅ All required dependencies found in package.json"
else
    echo "❌ Missing dependencies in package.json"
    exit 1
fi

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
echo "🎯 Features now available:"
echo "- Help (?) button in top navigation"
echo "- Guided tours for 4 key workflows"
echo "- Full multilingual support (6 languages)"
echo "- Interactive and Quick Guide modes"
echo "- Auto-dismissing maintenance success toast"
echo ""
echo "🔍 Test the deployment:"
echo "1. Look for the help (?) button in the navigation"
echo "2. Click it to see the tour menu"
echo "3. Try a tour workflow"
echo "4. Test in different languages"