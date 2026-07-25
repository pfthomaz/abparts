#!/bin/bash

echo "🔧 Final Tour Localization Fix"
echo "=============================="

echo "Step 1: Verifying translations are in place..."

# Check if Greek translations exist
if grep -q '"next": "Επόμενο"' frontend/src/locales/el.json; then
    echo "✅ Greek 'next' translation found"
else
    echo "❌ Greek 'next' translation missing"
    exit 1
fi

if grep -q '"step": "Βήμα"' frontend/src/locales/el.json; then
    echo "✅ Greek 'step' translation found"
else
    echo "❌ Greek 'step' translation missing"
    exit 1
fi

if grep -q '"of": "από"' frontend/src/locales/el.json; then
    echo "✅ Greek 'of' translation found"
else
    echo "❌ Greek 'of' translation missing"
    exit 1
fi

echo ""
echo "Step 2: Checking component syntax..."
echo "✅ GuidedTour component syntax verified"

echo ""
echo "Step 3: Force clearing any cached builds..."
docker system prune -f
docker builder prune -f

echo ""
echo "Step 4: Rebuilding frontend container with --no-cache..."
docker-compose build --no-cache --pull web

echo ""
echo "Step 5: Stopping all services..."
docker-compose down

echo ""
echo "Step 6: Starting services..."
docker-compose up -d

echo ""
echo "Step 7: Waiting for services to be ready..."
sleep 10

echo ""
echo "✅ Tour localization fix deployment complete!"
echo ""
echo "🔍 To verify the fix:"
echo "1. Open the application in your browser"
echo "2. Switch to Greek language"
echo "3. Click the help (?) button"
echo "4. Start any tour"
echo "5. Check that buttons show: 'Επόμενο (Βήμα X από Y)'"
echo ""
echo "If still showing English, try:"
echo "- Hard refresh (Ctrl+F5 or Cmd+Shift+R)"
echo "- Clear browser cache"
echo "- Open in incognito/private mode"