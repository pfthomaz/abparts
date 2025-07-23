#!/bin/bash

# Simple script to update the ABParts app favicon with the Oraseas favicon
# This script doesn't require ImageMagick

# Create directory for favicon files if it doesn't exist
mkdir -p frontend/public/favicon

# Download the favicon from the provided URL
echo "Downloading favicon..."
curl -s "https://img1.wsimg.com/isteam/ip/3b1b8ee9-78a7-478e-b347-06c5258d86c7/Screenshot%202025-02-18%20at%204.26.24%E2%80%AFPM.png/:/rs=w:57,h:57,m" -o frontend/public/favicon/oraseas_favicon.png

# Copy the favicon to the required locations
echo "Creating favicon files..."
cp frontend/public/favicon/oraseas_favicon.png frontend/public/favicon.ico
cp frontend/public/favicon/oraseas_favicon.png frontend/public/logo192.png
cp frontend/public/favicon/oraseas_favicon.png frontend/public/logo512.png

# Update manifest.json
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

echo "Favicon update completed successfully!"