# Fix Translation Keys in Production - Simple Guide

## Problem
Translation keys like `aiAssistant.messages.machineSelected` are showing instead of actual text.

## Root Cause
Production uses a pre-built static frontend served by nginx. The container needs to be rebuilt with the latest translation files.

## Solution

Run this on the production server:

```bash
cd ~/abparts
./rebuild_frontend_production.sh
```

**Time: 3-5 minutes**

## What It Does

1. Verifies translation files exist
2. Stops the web container
3. Rebuilds the web container (includes npm build inside Docker)
4. Starts the web container
5. Verifies it's running

## After Running

**IMPORTANT: You MUST hard refresh your browser!**

- **Windows/Linux**: `Ctrl + Shift + R`
- **Mac**: `Cmd + Shift + R`

Then test:
1. Open AI Assistant
2. Select a machine
3. Should see: **"Selected machine: AutoBoss 1 (V3.1B)"**
4. NOT: ~~"aiAssistant.messages.machineSelected"~~

## Why Hard Refresh is Required

Your browser has cached the old JavaScript bundle. A hard refresh forces it to download the new one.

## Alternative: Clear Browser Cache

If hard refresh doesn't work:
1. Open browser settings
2. Clear browsing data
3. Select "Cached images and files"
4. Clear data
5. Reload the page

## How Production Works

Production uses a multi-stage Docker build:
1. **Build stage**: Runs `npm run build` to compile React app
2. **Production stage**: Serves static files with nginx

Translation files are bundled into the JavaScript during the build stage, so changes require a container rebuild.

## Files Created

- `rebuild_frontend_production.sh` - Automated rebuild script (executable)

## Manual Alternative

If the script doesn't work:

```bash
# Stop web container
docker compose stop web

# Rebuild with no cache
docker compose build --no-cache web

# Start web container
docker compose up -d web

# Check status
docker compose ps web
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker compose logs web

# Check if port 3000 is in use
sudo netstat -tulpn | grep 3000
```

### Still showing translation keys after rebuild
1. Hard refresh browser (Ctrl+Shift+R)
2. Try incognito/private window
3. Clear browser cache completely
4. Check browser console for errors (F12)

### Build fails
```bash
# Check if translation files exist
ls -la frontend/src/locales/

# Check disk space
df -h

# Try rebuilding without cache
docker compose build --no-cache --pull web
```

## Summary

The fix is straightforward:
1. Rebuild the frontend container
2. Hard refresh your browser
3. Test the translations

The container rebuild includes the latest translation files in the production build.
