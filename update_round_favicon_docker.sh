#!/bin/bash

# Script to create a round favicon and update it in the Docker container

echo "Starting round favicon update process..."

# Step 1: Download the favicon locally
echo "Downloading favicon..."
mkdir -p temp_favicon
curl -s "https://img1.wsimg.com/isteam/ip/3b1b8ee9-78a7-478e-b347-06c5258d86c7/Screenshot%202025-02-18%20at%204.26.24%E2%80%AFPM.png/:/rs=w:57,h:57,m" -o temp_favicon/original_favicon.png

# Step 2: Create the favicon directory in the frontend/public folder
mkdir -p frontend/public/favicon

# Step 3: Copy the original favicon (we'll convert it inside Docker)
echo "Copying original favicon..."
cp temp_favicon/original_favicon.png frontend/public/favicon/original_favicon.png

# Step 4: Create a script to run inside the Docker container
cat > temp_favicon/docker_convert_script.sh << 'EOL'
#!/bin/bash

# This script runs inside the Docker container to create round favicons

# Install ImageMagick
echo "Installing ImageMagick in Docker container..."
apt-get update && apt-get install -y imagemagick --no-install-recommends

# Create round versions of the favicon
echo "Creating round favicons..."
cd /app
convert public/favicon/original_favicon.png \
    -resize 512x512 \
    \( +clone -alpha extract \
       -draw 'fill black polygon 0,0 0,512 512,0 fill white circle 256,256 256,0' \
       \( +clone -flip \) -compose Multiply -composite \
       \( +clone -flop \) -compose Multiply -composite \
    \) -alpha off -compose CopyOpacity -composite \
    public/logo512.png

# Create different sizes
convert public/logo512.png -resize 192x192 public/logo192.png
convert public/logo512.png -resize 64x64 public/favicon/favicon-64.png
convert public/logo512.png -resize 32x32 public/favicon/favicon-32x32.png
convert public/logo512.png -resize 16x16 public/favicon/favicon-16x16.png

# Create favicon.ico with multiple sizes
convert public/favicon/favicon-16x16.png public/favicon/favicon-32x32.png public/favicon/favicon-64.png public/favicon.ico

echo "Round favicon creation completed inside Docker container!"
EOL

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

# Step 7: Copy the conversion script to the Docker container and execute it
echo "Copying script to Docker container..."
docker cp temp_favicon/docker_convert_script.sh abparts_web:/app/docker_convert_script.sh

echo "Running conversion script in Docker container..."
docker exec abparts_web bash -c "chmod +x /app/docker_convert_script.sh && /app/docker_convert_script.sh"

# Step 8: Clean up temporary files
rm -rf temp_favicon

echo "Round favicon update completed!"
echo "The new round favicon should now be visible in your browser after refreshing the page."