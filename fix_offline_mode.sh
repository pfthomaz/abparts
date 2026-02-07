#!/bin/bash

# Fix Offline Mode Script
# Rebuilds frontend with service worker properly included

echo "=========================================="
echo "Fixing Offline Mode"
echo "=========================================="
echo ""

echo "1. Checking if copy-sw.js exists..."
if [ -f "frontend/copy-sw.js" ]; then
    echo "   ✓ Copy script exists"
else
    echo "   ✗ Copy script missing - creating it..."
    cat > frontend/copy-sw.js << 'EOF'
const fs = require('fs');
const path = require('path');

const source = path.join(__dirname, 'public', 'service-worker.js');
const dest = path.join(__dirname, 'build', 'service-worker.js');

if (fs.existsSync(source)) {
  fs.copyFileSync(source, dest);
  console.log('✓ Service worker copied to build folder');
} else {
  console.warn('⚠ Service worker source file not found at:', source);
}
EOF
    echo "   ✓ Copy script created"
fi
echo ""

echo "2. Updating package.json build script..."
if grep -q "build && node copy-sw.js" frontend/package.json; then
    echo "   ✓ Build script already updated"
else
    echo "   Updating build script..."
    # Backup package.json
    cp frontend/package.json frontend/package.json.backup
    # Update the build script
    sed -i 's/"build": "react-scripts build"/"build": "react-scripts build \&\& node copy-sw.js"/' frontend/package.json
    echo "   ✓ Build script updated"
fi
echo ""

echo "3. Rebuilding frontend..."
echo "   This will take a few minutes..."
echo ""

# Check if running in Docker or native
if [ -f "docker-compose.yml" ]; then
    echo "   Building in Docker..."
    docker compose build web --no-cache
    echo "   ✓ Docker build complete"
else
    echo "   Building natively..."
    cd frontend && npm run build
    echo "   ✓ Native build complete"
fi
echo ""

echo "4. Verifying service worker in build..."
if [ -f "frontend/build/service-worker.js" ]; then
    echo "   ✓ Service worker found in build folder"
    echo "   Size: $(wc -c < frontend/build/service-worker.js) bytes"
else
    echo "   ✗ Service worker NOT found in build folder"
    echo "   Trying manual copy..."
    cp frontend/public/service-worker.js frontend/build/service-worker.js
    if [ -f "frontend/build/service-worker.js" ]; then
        echo "   ✓ Manual copy successful"
    else
        echo "   ✗ Manual copy failed"
    fi
fi
echo ""

echo "=========================================="
echo "Fix Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "For LOCAL:"
echo "  1. Restart dev server: docker compose restart web"
echo "  2. Hard refresh browser: Ctrl+Shift+R (or Cmd+Shift+R on Mac)"
echo "  3. Check DevTools > Application > Service Workers"
echo ""
echo "For PRODUCTION:"
echo "  1. Rebuild and restart: docker compose -f docker-compose.prod.yml up -d --build web"
echo "  2. Hard refresh browser on production site"
echo "  3. Check DevTools > Application > Service Workers"
echo ""
echo "To test offline mode:"
echo "  1. Open DevTools > Network tab"
echo "  2. Set throttling to 'Offline'"
echo "  3. Try creating a maintenance execution or net cleaning record"
echo "  4. Should save locally and show in pending sync"
echo ""

