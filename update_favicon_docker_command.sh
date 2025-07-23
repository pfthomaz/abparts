#!/bin/bash

# This script runs the favicon update inside the Docker container

# Make the update script executable
chmod +x update_favicon_docker.sh

# Copy the script to the Docker container
docker cp update_favicon_docker.sh web:/app/update_favicon_docker.sh

# Execute the script inside the container
docker exec -it web bash -c "chmod +x /app/update_favicon_docker.sh && /app/update_favicon_docker.sh"

echo "Favicon update in Docker container completed!"