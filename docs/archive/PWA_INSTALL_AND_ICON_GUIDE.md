# PWA Install Prompt & Custom Icon Guide

## Issue Fixed: Install App Prompt Not Appearing

**Problem:** The manifest.json was referencing icon files at incorrect paths (`logo192.png` and `logo512.png` in root), but the actual files are in `favicon/sizes/` subdirectory.

**Solution Applied:** Updated `frontend/public/manifest.json` to point to correct icon paths:
- `logo192.png` → `favicon/sizes/logo192.png`
- `logo512.png` → `favicon/sizes/logo512.png`

## PWA Install Requirements

For the "Install app" prompt to appear on Android/iOS, ALL of these must be met:

### 1. Valid Manifest (✅ Fixed)
- Must have valid `manifest.json` with correct icon paths
- Icons must exist at specified paths
- Must have `display: "standalone"`
- Must have `start_url` defined

### 2. Service Worker (✅ Already Working)
- Service worker must be registered and active
- Currently using `frontend/public/service-worker.js`

### 3. HTTPS (✅ Production Has This)
- Site must be served over HTTPS
- `abparts.oraseas.com` uses HTTPS ✓

### 4. User Engagement Criteria
- User must visit the site at least twice
- Visits must be at least 5 minutes apart
- User must interact with the page (click, scroll, etc.)

### 5. Not Already Installed
- If the app is already installed, the prompt won't show
- Check: Settings → Apps → ABParts (uninstall if exists)

## How to Customize the App Icon

The app icon that appears on Android home screen comes from the manifest icons. Here's how to customize it:

### Step 1: Prepare Your Icon Images

You need TWO icon sizes:
- **192x192 pixels** - Used for app icon on home screen
- **512x512 pixels** - Used for splash screen and high-res displays

**Design Guidelines:**
- Use PNG format with transparency
- Square aspect ratio (1:1)
- Simple, recognizable design
- High contrast for visibility
- Avoid text (it becomes unreadable at small sizes)

### Step 2: Replace Icon Files

Replace these files in `frontend/public/favicon/sizes/`:

```bash
# On your local machine or production server
cd /root/abparts/frontend/public/favicon/sizes/

# Backup existing icons
cp logo192.png logo192.png.backup
cp logo512.png logo512.png.backup

# Upload your new icons (use scp, sftp, or direct upload)
# Make sure they're named exactly:
# - logo192.png (192x192 pixels)
# - logo512.png (512x512 pixels)
```

### Step 3: Update Manifest (Optional - for branding)

Edit `frontend/public/manifest.json` to customize app name and colors:

```json
{
  "short_name": "ABParts",           // ← Name shown under icon (max 12 chars)
  "name": "ABParts - AutoBoss Parts", // ← Full name in app drawer
  "theme_color": "#2563eb",          // ← Status bar color (currently blue)
  "background_color": "#ffffff",     // ← Splash screen background
  ...
}
```

**Color Recommendations:**
- `theme_color`: Match your brand color (shows in status bar)
- `background_color`: Usually white or your brand color
- Use hex codes like `#2563eb` or `#ffffff`

### Step 4: Rebuild and Deploy

```bash
# Commit changes
git add frontend/public/manifest.json
git add frontend/public/favicon/sizes/logo192.png
git add frontend/public/favicon/sizes/logo512.png
git commit -m "Update PWA icons and manifest"
git push origin main

# On production server
cd /root/abparts
git pull origin main
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d web
```

### Step 5: Clear Cache and Reinstall

On your tablet:

1. **Uninstall existing app** (if installed):
   - Settings → Apps → ABParts → Uninstall

2. **Clear browser cache**:
   - Chrome: Settings → Privacy → Clear browsing data
   - Check "Cached images and files"
   - Click "Clear data"

3. **Visit site again**:
   - Go to `https://abparts.oraseas.com`
   - Interact with the page (scroll, click)
   - Wait for install prompt (may take 30 seconds)

4. **Install app**:
   - Tap "Install" or "Add to Home Screen"
   - New icon should appear on home screen

## Icon Design Tools

### Online Tools (Free):
- **Canva** - https://www.canva.com (easy drag-and-drop)
- **Figma** - https://www.figma.com (professional design)
- **GIMP** - https://www.gimp.org (desktop app, like Photoshop)

### Icon Generators:
- **PWA Asset Generator** - https://www.pwabuilder.com/imageGenerator
  - Upload one image, generates all sizes automatically
  - Recommended for quick setup

### Design Tips:
1. Start with 512x512 canvas
2. Keep important elements in center 80% (safe zone)
3. Use solid background or transparency
4. Test at small size (192px) to ensure readability
5. Avoid gradients (can look muddy at small sizes)

## Current Icon Status

**Current Icons:**
- Location: `frontend/public/favicon/sizes/`
- Files: `logo192.png`, `logo512.png`
- These are the default React icons (blue atom logo)

**To Use Custom Icon:**
1. Create/obtain your 192x192 and 512x512 PNG icons
2. Replace the files in `favicon/sizes/` directory
3. Rebuild and deploy
4. Users must uninstall old app and reinstall to see new icon

## Troubleshooting Install Prompt

### Prompt Still Not Showing?

**Check 1: Verify manifest is loading**
- Open DevTools (F12) on tablet
- Go to Application tab → Manifest
- Should show "ABParts - AutoBoss Parts Management"
- Check for errors in red

**Check 2: Verify service worker**
- DevTools → Application → Service Workers
- Should show "activated and running"
- Status should be green

**Check 3: Check installability**
- DevTools → Application → Manifest
- Look for "Installability" section
- Should say "✓ Installable"
- If not, shows specific errors

**Check 4: Force install prompt (testing only)**
- DevTools → Application → Manifest
- Click "Add to home screen" link
- This bypasses engagement criteria

### Common Issues:

**"Icons not found"**
- Solution: Verify icon files exist at paths in manifest
- Run: `ls -la frontend/public/favicon/sizes/*.png`

**"Service worker not registered"**
- Solution: Check browser console for errors
- Verify service-worker.js is being served

**"Not served over HTTPS"**
- Solution: Ensure using `https://abparts.oraseas.com`
- HTTP sites cannot install as PWA

**"Already installed"**
- Solution: Uninstall app first, then revisit site

## Testing Install Prompt

### On Android Chrome:
1. Visit `https://abparts.oraseas.com`
2. Wait 30 seconds while interacting with page
3. Look for banner at bottom: "Add ABParts to Home screen"
4. Or tap menu (⋮) → "Install app" or "Add to Home screen"

### On iOS Safari:
1. Visit `https://abparts.oraseas.com`
2. Tap Share button (square with arrow)
3. Scroll down and tap "Add to Home Screen"
4. Tap "Add" in top right

Note: iOS doesn't show automatic install prompts like Android

## After Installation

**App Features:**
- ✅ Launches in fullscreen (no browser UI)
- ✅ Has app icon on home screen
- ✅ Works offline with cached data
- ✅ Receives updates automatically
- ✅ Can be uninstalled like native app

**Updating the App:**
- Users don't need to reinstall
- Service worker auto-updates on next visit
- New icon requires reinstall

---

**Status:** PWA manifest fixed and ready for deployment
**Next Step:** Deploy to production, then test install on tablet
**Custom Icon:** Replace logo192.png and logo512.png files to customize
