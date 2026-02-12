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
