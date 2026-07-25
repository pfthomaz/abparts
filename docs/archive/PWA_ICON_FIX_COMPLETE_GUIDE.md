# PWA Icon Fix - Complete Guide

## Problem Explained

You're experiencing inconsistent icon display because the manifest used `"purpose": "any maskable"` for the same icon. This causes Android to treat the icon in two different ways:

1. **"any"** - Displays icon exactly as-is (your white background PNG)
2. **"maskable"** - Android applies a circular/rounded mask and may add its own background color

When both purposes use the same icon, Android randomly picks which treatment to apply, causing:
- ❌ White background sometimes
- ❌ Black background sometimes  
- ❌ Icon gets cropped at edges
- ❌ Inconsistent appearance across devices

## Solution

Create **TWO separate icon sets**:
1. **Regular icons** (`logo192.png`, `logo512.png`) - Your current icon with white background
2. **Maskable icons** (`logo192-maskable.png`, `logo512-maskable.png`) - Icon with 20% padding safe zone

## What Are Maskable Icons?

Maskable icons are designed to work with Android's adaptive icon system. They have:
- **Safe zone**: 80% center circle where important content must stay
- **Padding**: 10% margin on all sides (20% total safe zone)
- **Full bleed**: Icon can extend to edges, but will be masked

**Visual Guide:**
```
┌─────────────────────────┐
│  10% padding (bleed)    │
│  ┌───────────────────┐  │
│  │                   │  │
│  │   80% safe zone   │  │ ← Your logo goes here
│  │   (visible area)  │  │
│  │                   │  │
│  └───────────────────┘  │
│  10% padding (bleed)    │
└─────────────────────────┘
```

## Step-by-Step Fix

### Step 1: Generate Maskable Icons

I've created a Python script to automatically generate maskable icons from your existing icons:

**File:** `generate_maskable_icons.py`

```python
#!/usr/bin/env python3
"""
Generate maskable PWA icons with proper safe zone padding.
Requires: pip install Pillow
"""

from PIL import Image, ImageDraw
import os

def create_maskable_icon(input_path, output_path, size):
    """
    Create a maskable icon with 20% safe zone padding.
    
    Args:
        input_path: Path to source icon
        output_path: Path to save maskable icon
        size: Output size (192 or 512)
    """
    # Open source image
    img = Image.open(input_path)
    
    # Convert to RGBA if not already
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Calculate dimensions
    # Maskable icons need 20% padding (10% on each side)
    # So the actual icon should be 80% of the canvas
    icon_size = int(size * 0.8)
    padding = int(size * 0.1)
    
    # Resize the source image to fit in safe zone
    img_resized = img.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
    
    # Create new canvas with solid background
    # Use white background to match your current design
    canvas = Image.new('RGBA', (size, size), (255, 255, 255, 255))
    
    # Paste resized icon in center with padding
    canvas.paste(img_resized, (padding, padding), img_resized)
    
    # Save
    canvas.save(output_path, 'PNG', optimize=True)
    print(f"✓ Created {output_path}")

def main():
    # Paths
    base_path = 'frontend/public/favicon/sizes'
    
    # Check if source files exist
    logo192 = os.path.join(base_path, 'logo192.png')
    logo512 = os.path.join(base_path, 'logo512.png')
    
    if not os.path.exists(logo192):
        print(f"❌ Error: {logo192} not found")
        return
    
    if not os.path.exists(logo512):
        print(f"❌ Error: {logo512} not found")
        return
    
    print("Generating maskable icons...")
    print("This adds 20% padding safe zone for Android adaptive icons\n")
    
    # Generate maskable versions
    create_maskable_icon(
        logo192,
        os.path.join(base_path, 'logo192-maskable.png'),
        192
    )
    
    create_maskable_icon(
        logo512,
        os.path.join(base_path, 'logo512-maskable.png'),
        512
    )
    
    print("\n✅ Maskable icons generated successfully!")
    print("\nNext steps:")
    print("1. Review the generated icons in frontend/public/favicon/sizes/")
    print("2. Commit and deploy: git add, git commit, git push")
    print("3. Rebuild production: docker compose -f docker-compose.prod.yml build web")
    print("4. Uninstall old app and reinstall to see new icons")

if __name__ == '__main__':
    try:
        from PIL import Image
    except ImportError:
        print("❌ Error: Pillow library not installed")
        print("Install with: pip install Pillow")
        exit(1)
    
    main()
```

### Step 2: Run the Script

```bash
# Install Pillow if not already installed
pip install Pillow

# Run the script
python3 generate_maskable_icons.py
```

This will create:
- `frontend/public/favicon/sizes/logo192-maskable.png`
- `frontend/public/favicon/sizes/logo512-maskable.png`

### Step 3: Verify the Icons

Check that the maskable icons have proper padding:
```bash
ls -lh frontend/public/favicon/sizes/logo*maskable.png
```

You should see two new files with similar file sizes to the originals.

### Step 4: Deploy to Production

```bash
# Commit changes
git add frontend/public/manifest.json
git add frontend/public/favicon/sizes/logo192-maskable.png
git add frontend/public/favicon/sizes/logo512-maskable.png
git commit -m "Fix PWA icons - separate any and maskable versions"
git push origin main

# On production server
cd /root/abparts
git pull origin main
docker compose -f docker-compose.prod.yml build web
docker compose -f docker-compose.prod.yml up -d web
```

### Step 5: Test on Tablet

1. **Uninstall existing app completely**:
   - Long press app icon → App info → Uninstall
   - Or: Settings → Apps → ABParts → Uninstall

2. **Clear browser data**:
   - Chrome → Settings → Privacy → Clear browsing data
   - Select "Cached images and files" and "Site settings"
   - Clear data

3. **Reinstall**:
   - Visit `https://abparts.oraseas.com`
   - Wait for install prompt
   - Install app
   - Check home screen icon

## Expected Results

After this fix:

✅ **Consistent icon appearance** - Same icon every time
✅ **No cropping** - Icon stays within safe zone
✅ **Proper background** - White background as designed
✅ **Works on all Android versions** - Adaptive icon support
✅ **No black background** - Maskable version has white background built-in

## Understanding the Manifest Changes

**Before (Broken):**
```json
{
  "src": "logo192.png",
  "purpose": "any maskable"  ← Same icon for both purposes
}
```

**After (Fixed):**
```json
{
  "src": "logo192.png",
  "purpose": "any"  ← Regular icon
},
{
  "src": "logo192-maskable.png",
  "purpose": "maskable"  ← Padded icon for adaptive
}
```

## Alternative: Manual Icon Creation

If you prefer to create maskable icons manually:

### Using Figma/Canva:
1. Create 512x512 canvas with white background
2. Place your logo in center 410x410 area (80% of 512)
3. Leave 51px margin on all sides (10% padding)
4. Export as PNG
5. Resize to 192x192 for smaller version

### Using Online Tool:
- Visit: https://maskable.app/editor
- Upload your logo192.png
- Adjust padding to 20% (10% on each side)
- Download both 192x192 and 512x512 versions
- Rename to logo192-maskable.png and logo512-maskable.png

## Troubleshooting

### Icons still inconsistent after deployment?

**Check 1: Verify files exist**
```bash
ls -la frontend/public/favicon/sizes/logo*maskable.png
```
Should show both maskable files.

**Check 2: Verify manifest is correct**
```bash
cat frontend/public/manifest.json | grep -A 5 maskable
```
Should show separate entries for "any" and "maskable".

**Check 3: Clear service worker cache**
On tablet:
- DevTools → Application → Service Workers → Unregister
- Application → Clear storage → Clear site data

**Check 4: Verify icons are being served**
Visit in browser:
- `https://abparts.oraseas.com/favicon/sizes/logo192-maskable.png`
- `https://abparts.oraseas.com/favicon/sizes/logo512-maskable.png`

Should display the padded icons.

### Icon still gets cropped?

The maskable icon might not have enough padding. Increase padding to 25% (12.5% on each side):
```python
icon_size = int(size * 0.75)  # 75% instead of 80%
padding = int(size * 0.125)   # 12.5% instead of 10%
```

### Want different background color?

Edit the script line:
```python
canvas = Image.new('RGBA', (size, size), (255, 255, 255, 255))
#                                         ↑    ↑    ↑    ↑
#                                         R    G    B    A
```

Examples:
- Black: `(0, 0, 0, 255)`
- Blue: `(37, 99, 235, 255)` (matches theme_color)
- Transparent: `(255, 255, 255, 0)` (not recommended for maskable)

## Testing Maskable Icons

Use Google's Maskable Icon Checker:
1. Visit: https://maskable.app
2. Upload your `logo512-maskable.png`
3. Toggle through different mask shapes
4. Verify logo stays visible in all masks

## Best Practices

1. **Keep logo centered** - Don't rely on corners
2. **Use solid background** - Transparency can cause issues
3. **Test on real device** - Emulators may not show accurate results
4. **Provide both versions** - "any" for iOS, "maskable" for Android
5. **Use high contrast** - Ensure logo is visible on any background

---

**Status:** Manifest updated, script ready to generate maskable icons
**Next Step:** Run `python3 generate_maskable_icons.py` to create the icons
**Result:** Consistent, properly displayed PWA icon on all Android devices
