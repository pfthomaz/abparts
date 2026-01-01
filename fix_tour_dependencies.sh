#!/bin/bash
# fix_tour_dependencies.sh
# Quick fix for missing dependencies

echo "=== Tour System Dependency Fix ==="
echo ""

# Check if we're in the right directory
if [ ! -f "frontend/package.json" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

echo "Option 1: Install missing dependencies (recommended)"
echo "cd frontend && npm install react-joyride @heroicons/react"
echo ""

echo "Option 2: Use simple version without icons"
echo "This will temporarily replace TourButton with a version that doesn't need Heroicons"
echo ""

read -p "Choose option (1 or 2): " choice

case $choice in
    1)
        echo "Installing dependencies..."
        cd frontend
        npm install react-joyride @heroicons/react
        echo "✅ Dependencies installed!"
        echo "You can now start your development server: npm start"
        ;;
    2)
        echo "Using simple version..."
        # Backup original TourButton
        cp frontend/src/components/TourButton.js frontend/src/components/TourButton.js.backup
        # Replace with simple version
        cp frontend/src/components/TourButtonSimple.js frontend/src/components/TourButton.js
        echo "✅ Using simple version without Heroicons"
        echo "Note: Install dependencies later with: cd frontend && npm install react-joyride @heroicons/react"
        echo "Then restore original: cp frontend/src/components/TourButton.js.backup frontend/src/components/TourButton.js"
        ;;
    *)
        echo "Invalid choice. Please run again and choose 1 or 2."
        exit 1
        ;;
esac

echo ""
echo "🎉 Tour system should now work!"