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
