# Fix PWA Icons - Quick Start

## The Problem
Your PWA icon appears inconsistently (white background, black background, cropped) because the manifest uses the same icon for both "any" and "maskable" purposes. Android treats these differently, causing random appearance.

## The Solution
✅ Manifest updated to use separate icons for "any" and "maskable"
✅ Script created to generate proper maskable icons with safe zone padding

## Run These Commands Now

### 1. Install Pillow (if not installed)
```bash
pip install Pillow
```

### 2. Generate Maskable Icons
```bash
python3 generate_maskable_icons.py
```

This creates:
- `frontend/public/favicon/sizes/logo192-maskable.png` (with 20% padding)
- `frontend/public/favicon/sizes/logo512-maskable.png` (with 20% padding)

### 3. Commit and Deploy
```bash
git add frontend/public/manifest.json
git add frontend/public/favicon/sizes/logo192-maskable.png
git add frontend/public/favicon/sizes/logo512-maskable.png
git add generate_maskable_icons.py
git commit -m "Fix PWA icons - add maskable versions with safe zone padding"
git push origin main
```

### 4. Deploy to Production
```bash
# On production server
ssh diogo@ubuntu-8gb-hel1-2
cd /root/abparts
git pull origin main
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d web
```

### 5. Test on Tablet
1. Uninstall old app completely
2. Clear browser cache (Chrome → Settings → Privacy → Clear data)
3. Visit `https://abparts.oraseas.com`
4. Install app
5. Icon should now appear consistently with white background

## What Changed

**Manifest.json:**
- Split icon definitions into separate "any" and "maskable" entries
- "any" = your current icon (for iOS and regular display)
- "maskable" = padded icon (for Android adaptive icons)

**Maskable Icons:**
- 20% padding (10% on all sides) creates safe zone
- Logo scaled to 80% of canvas size
- White background matches your design
- Prevents cropping on Android

## Expected Result
✅ Consistent icon appearance every time
✅ No more black backgrounds
✅ No cropping at edges
✅ Works on all Android versions

## Troubleshooting

**Script fails?**
- Make sure you're in the project root directory
- Check that `frontend/public/favicon/sizes/logo192.png` exists

**Icons still inconsistent?**
- Uninstall app completely (not just clear cache)
- Clear browser data including "Site settings"
- Verify maskable files exist: `ls frontend/public/favicon/sizes/*maskable.png`

**Want different background color?**
- Edit `generate_maskable_icons.py` line 32
- Change `(255, 255, 255, 255)` to your RGB color
- Re-run the script

---

**Files Modified:**
- ✅ `frontend/public/manifest.json` - Split icon purposes
- ✅ `generate_maskable_icons.py` - Icon generator script

**Files to Create:**
- ⏳ `frontend/public/favicon/sizes/logo192-maskable.png` - Run script
- ⏳ `frontend/public/favicon/sizes/logo512-maskable.png` - Run script

**Status:** Ready to generate and deploy
**Time:** ~5 minutes total
