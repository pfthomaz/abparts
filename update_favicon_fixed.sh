#!/bin/bash

# Script to update the ABParts app favicon with the Oraseas favicon
# This script works with the Docker setup defined in docker-compose.yml

echo "Starting favicon update process..."

# Step 1: Download the favicon locally
echo "Downloading favicon..."
mkdir -p temp_favicon
curl -s "https://img1.wsimg.com/isteam/ip/3b1b8ee9-78a7-478e-b347-06c5258d86c7/Screenshot%202025-02-18%20at%204.26.24%E2%80%AFPM.png/:/rs=w:57,h:57,m" -o temp_favicon/oraseas_favicon.png

# Step 2: Create the favicon directory in the frontend/public folder
mkdir -p frontend/public/favicon

# Step 3: Copy the favicon to the required locations
echo "Creating favicon files..."
cp temp_favicon/oraseas_favicon.png frontend/public/favicon/oraseas_favicon.png
cp temp_favicon/oraseas_favicon.png frontend/public/favicon.ico
cp temp_favicon/oraseas_favicon.png frontend/public/logo192.png
cp temp_favicon/oraseas_favicon.png frontend/public/logo512.png

# Step 4: Update manifest.json
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

# Step 5: Update index.html to ensure favicon references are correct
echo "Updating index.html..."
sed -i 's|<link rel="icon" href="%PUBLIC_URL%/favicon.ico" />|<link rel="icon" href="%PUBLIC_URL%/favicon.ico" />\n    <link rel="icon" type="image/png" sizes="32x32" href="%PUBLIC_URL%/favicon/oraseas_favicon.png" />|' frontend/public/index.html

# Step 6: Clean up temporary files
rm -rf temp_favicon

echo "Favicon files updated locally."
echo "Now updating the Docker container..."

# Step 7: Restart the web container to apply changes
docker-compose restart web

echo "Favicon update completed successfully!"
echo "The new favicon should now be visible in your browser after refreshing the page."