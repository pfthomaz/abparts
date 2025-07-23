#!/bin/bash

# Script to update the ABParts app favicon with a round Oraseas favicon
# This script requires ImageMagick to be installed

echo "Starting round favicon update process..."

# Check if ImageMagick is installed
if ! command -v convert &> /dev/null; then
    echo "ImageMagick is not installed. Please install it first."
    echo "On Ubuntu/Debian: sudo apt-get install imagemagick"
    echo "On macOS: brew install imagemagick"
    echo "On Windows: Install from https://imagemagick.org/script/download.php"
    exit 1
fi

# Step 1: Download the favicon locally
echo "Downloading favicon..."
mkdir -p temp_favicon
curl -s "https://img1.wsimg.com/isteam/ip/3b1b8ee9-78a7-478e-b347-06c5258d86c7/Screenshot%202025-02-18%20at%204.26.24%E2%80%AFPM.png/:/rs=w:57,h:57,m" -o temp_favicon/original_favicon.png

# Step 2: Create a round version of the favicon using ImageMagick
echo "Creating round favicon..."
convert temp_favicon/original_favicon.png \
    -resize 512x512 \
    \( +clone -alpha extract \
       -draw 'fill black polygon 0,0 0,512 512,0 fill white circle 256,256 256,0' \
       \( +clone -flip \) -compose Multiply -composite \
       \( +clone -flop \) -compose Multiply -composite \
    \) -alpha off -compose CopyOpacity -composite \
    temp_favicon/round_favicon_512.png

# Create different sizes
convert temp_favicon/round_favicon_512.png -resize 192x192 temp_favicon/round_favicon_192.png
convert temp_favicon/round_favicon_512.png -resize 64x64 temp_favicon/round_favicon_64.png
convert temp_favicon/round_favicon_512.png -resize 32x32 temp_favicon/round_favicon_32.png
convert temp_favicon/round_favicon_512.png -resize 16x16 temp_favicon/round_favicon_16.png

# Create favicon.ico with multiple sizes
convert temp_favicon/round_favicon_16.png temp_favicon/round_favicon_32.png temp_favicon/round_favicon_64.png temp_favicon/favicon.ico

# Step 3: Create the favicon directory in the frontend/public folder
mkdir -p frontend/public/favicon

# Step 4: Copy the favicon to the required locations
echo "Copying favicon files..."
cp temp_favicon/round_favicon_32.png frontend/public/favicon/favicon-32x32.png
cp temp_favicon/round_favicon_16.png frontend/public/favicon/favicon-16x16.png
cp temp_favicon/favicon.ico frontend/public/favicon.ico
cp temp_favicon/round_favicon_192.png frontend/public/logo192.png
cp temp_favicon/round_favicon_512.png frontend/public/logo512.png

# Step 5: Update manifest.json
echo "Updating manifest.json..."
cat > frontend/public/manifest.json << EOL
{
  "short_name": "ABParts",
  "name": "ABParts Inventory Management",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    },
    {
      "src": "logo192.png",
      "type": "image/png",
      "sizes": "192x192"
    },
    {
      "src": "logo512.png",
      "type": "image/png",
      "sizes": "512x512"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#ffffff"
}
EOL

# Step 6: Update index.html to ensure favicon references are correct
echo "Updating index.html..."
sed -i 's|<link rel="icon" href="%PUBLIC_URL%/favicon.ico" />|<link rel="icon" href="%PUBLIC_URL%/favicon.ico" />\n    <link rel="icon" type="image/png" sizes="32x32" href="%PUBLIC_URL%/favicon/favicon-32x32.png" />\n    <link rel="icon" type="image/png" sizes="16x16" href="%PUBLIC_URL%/favicon/favicon-16x16.png" />|' frontend/public/index.html

# Step 7: Clean up temporary files
rm -rf temp_favicon

echo "Round favicon files updated locally."
echo "Now updating the Docker container..."

# Step 8: Restart the web container to apply changes
docker-compose restart web

echo "Round favicon update completed successfully!"
echo "The new round favicon should now be visible in your browser after refreshing the page."