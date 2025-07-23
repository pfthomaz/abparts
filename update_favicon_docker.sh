#!/bin/bash

# Script to update the ABParts app favicon with the Oraseas favicon
# This script is designed to be run inside the Docker container

# Install required packages
echo "Installing required packages..."
apt-get update && apt-get install -y curl wget imagemagick --no-install-recommends

# Create directory for favicon files if it doesn't exist
mkdir -p /app/frontend/public/favicon

# Download the favicon from the provided URL
echo "Downloading favicon..."
curl -s "https://img1.wsimg.com/isteam/ip/3b1b8ee9-78a7-478e-b347-06c5258d86c7/Screenshot%202025-02-18%20at%204.26.24%E2%80%AFPM.png/:/rs=w:57,h:57,m" -o /app/frontend/public/favicon/oraseas_favicon.png

# Create different sizes of the favicon
echo "Creating different sizes of the favicon..."
mkdir -p /app/frontend/public/favicon/sizes

# Create different sizes using ImageMagick
convert /app/frontend/public/favicon/oraseas_favicon.png -resize 16x16 /app/frontend/public/favicon/favicon-16x16.png
convert /app/frontend/public/favicon/oraseas_favicon.png -resize 32x32 /app/frontend/public/favicon/favicon-32x32.png
convert /app/frontend/public/favicon/oraseas_favicon.png -resize 48x48 /app/frontend/public/favicon/favicon-48x48.png
convert /app/frontend/public/favicon/oraseas_favicon.png -resize 192x192 /app/frontend/public/logo192.png
convert /app/frontend/public/favicon/oraseas_favicon.png -resize 512x512 /app/frontend/public/logo512.png

# Create favicon.ico (multi-size icon)
convert /app/frontend/public/favicon/favicon-16x16.png /app/frontend/public/favicon/favicon-32x32.png /app/frontend/public/favicon/favicon-48x48.png /app/frontend/public/favicon.ico

# Update manifest.json
echo "Updating manifest.json..."
cat > /app/frontend/public/manifest.json << EOL
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

# Update index.html to ensure favicon references are correct
echo "Updating index.html..."
sed -i 's|<link rel="icon" href="%PUBLIC_URL%/favicon.ico" />|<link rel="icon" href="%PUBLIC_URL%/favicon.ico" />\n    <link rel="icon" type="image/png" sizes="32x32" href="%PUBLIC_URL%/favicon/favicon-32x32.png" />\n    <link rel="icon" type="image/png" sizes="16x16" href="%PUBLIC_URL%/favicon/favicon-16x16.png" />|' /app/frontend/public/index.html

echo "Favicon update completed successfully!"