#!/bin/bash

echo "🔧 Tour Localization Fix for Development"
echo "======================================="

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
echo "Step 2: Checking component exists..."
if [ -f "frontend/src/components/GuidedTour.js" ]; then
    echo "✅ GuidedTour component found"
else
    echo "❌ GuidedTour component missing"
    exit 1
fi

echo ""
echo "Step 3: Force clearing all caches..."
docker system prune -f
docker builder prune -f

# Clear npm cache in container if it exists
docker-compose exec web npm cache clean --force 2>/dev/null || true

echo ""
echo "Step 4: Rebuilding frontend container with complete cache clear..."
docker-compose build --no-cache --pull web

echo ""
echo "Step 5: Stopping all services..."
docker-compose down

echo ""
echo "Step 6: Starting services with fresh containers..."
docker-compose up -d

echo ""
echo "Step 7: Waiting for services to be ready..."
sleep 15

echo ""
echo "Step 8: Verifying frontend is running..."
if curl -f http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ Frontend is responding"
else
    echo "⚠️  Frontend may still be starting up"
fi

echo ""
echo "✅ Tour localization fix deployment complete!"
echo ""
echo "🔍 To verify the fix:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Switch to Greek language (Ελληνικά)"
echo "3. Click the help (?) button in the bottom right"
echo "4. Start any tour (e.g., 'Πώς να Παραγγείλετε Ανταλλακτικά')"
echo "5. Check that buttons show: 'Επόμενο (Βήμα X από Y)'"
echo ""
echo "🐛 If still showing English, try:"
echo "- Hard refresh (Ctrl+F5 or Cmd+Shift+R)"
echo "- Clear browser cache completely"
echo "- Open in incognito/private mode"
echo "- Check browser console for any errors"
echo ""
echo "📋 Debug commands:"
echo "- Check logs: docker-compose logs web"
echo "- Restart frontend: docker-compose restart web"
echo "- Check translations: curl http://localhost:3000/locales/el.json"