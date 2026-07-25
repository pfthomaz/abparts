#!/bin/bash

echo "🚀 Deploying Tour System to Production"
echo "======================================"

# Step 1: Add tour translations to locale files
echo "Step 1: Adding tour translations..."
python3 add_tour_translations.py
python3 add_enhanced_tour_translations.py

# Step 2: Add common.scope translation (if not already done)
echo "Step 2: Adding common.scope translation..."
python3 add_common_scope_translation.py

# Step 3: Update package.json to include new dependencies
echo "Step 3: Updating package.json with new dependencies..."
cd frontend

# Check if dependencies are already in package.json
if ! grep -q "react-joyride" package.json; then
    echo "Adding react-joyride to package.json..."
    # Use docker to run npm install inside a temporary container
    docker run --rm -v $(pwd):/app -w /app node:18-alpine npm install react-joyride --save
fi

if ! grep -q "@heroicons/react" package.json; then
    echo "Adding @heroicons/react to package.json..."
    # Use docker to run npm install inside a temporary container  
    docker run --rm -v $(pwd):/app -w /app node:18-alpine npm install @heroicons/react --save
fi

cd ..

# Step 4: Rebuild frontend container (this will install the new dependencies)
echo "Step 4: Rebuilding frontend container with new dependencies..."
docker-compose -f docker-compose.prod.yml build --no-cache web

# Step 5: Restart services
echo "Step 5: Restarting services..."
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
echo ""
echo "🔍 To verify deployment:"
echo "1. Check that the help (?) button appears in the top navigation"
echo "2. Click the help button to see the tour menu"
echo "3. Test a tour workflow to ensure it works properly"
echo "4. Test in different languages to verify translations"