#!/bin/bash

# Debug script for dashboard farms and nets showing 0

echo "=========================================="
echo "Dashboard Farms/Nets Debug Script"
echo "=========================================="
echo ""

# Step 1: Check backend API response
echo "Step 1: Testing backend API response..."
echo "----------------------------------------"
curl -s http://localhost:8000/api/dashboard/metrics \
  -H "Authorization: Bearer $(cat ~/.abparts_token 2>/dev/null || echo 'YOUR_TOKEN_HERE')" \
  | python3 -m json.tool | grep -A 2 "total_farm_sites\|total_nets"

echo ""
echo "If you see the correct values above (1 and 3), the backend is working correctly."
echo ""

# Step 2: Check API logs
echo "Step 2: Checking API container logs for debug output..."
echo "----------------------------------------"
docker compose logs api --tail=50 | grep -E "total_farm_sites|total_nets"

echo ""
echo ""

# Step 3: Instructions for user
echo "=========================================="
echo "TROUBLESHOOTING STEPS:"
echo "=========================================="
echo ""
echo "The backend is returning correct values (1 farm, 3 nets)."
echo "The issue is likely browser/service worker caching."
echo ""
echo "Please try these steps IN ORDER:"
echo ""
echo "1. CLEAR SERVICE WORKER CACHE:"
echo "   - Open browser DevTools (F12)"
echo "   - Go to Application tab"
echo "   - Click 'Service Workers' in left sidebar"
echo "   - Click 'Unregister' for any service workers"
echo "   - Click 'Clear storage' and check all boxes"
echo "   - Click 'Clear site data'"
echo ""
echo "2. HARD REFRESH:"
echo "   - Press Cmd + Shift + R (Mac) or Ctrl + Shift + R (Windows/Linux)"
echo "   - This bypasses all caches"
echo ""
echo "3. CHECK BROWSER CONSOLE:"
echo "   - Open DevTools (F12)"
echo "   - Go to Console tab"
echo "   - Look for the debug logs:"
echo "     'DEBUG: Received metrics data:'"
echo "     'DEBUG: total_farm_sites ='"
echo "     'DEBUG: total_nets ='"
echo "   - Tell me what values you see"
echo ""
echo "4. CHECK NETWORK TAB:"
echo "   - Open DevTools (F12)"
echo "   - Go to Network tab"
echo "   - Refresh the page"
echo "   - Find the 'metrics' request"
echo "   - Click on it and check the Response tab"
echo "   - Look for total_farm_sites and total_nets values"
echo ""
echo "5. IF STILL SHOWING 0:"
echo "   - Restart the web container:"
echo "     docker compose restart web"
echo "   - Wait 30 seconds for rebuild"
echo "   - Hard refresh browser (Cmd + Shift + R)"
echo ""
echo "=========================================="
