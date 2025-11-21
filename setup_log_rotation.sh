#!/bin/bash
# Setup Docker Log Rotation to Prevent Disk Space Issues

echo "=== Setting Up Docker Log Rotation ==="
echo ""

# Create Docker daemon config if it doesn't exist
if [ ! -f /etc/docker/daemon.json ]; then
    echo "Creating /etc/docker/daemon.json..."
    sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF
else
    echo "WARNING: /etc/docker/daemon.json already exists."
    echo "Current content:"
    sudo cat /etc/docker/daemon.json
    echo ""
    echo "You may need to manually add log rotation settings."
    echo "Recommended settings:"
    echo '{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}'
    exit 1
fi

echo ""
echo "Restarting Docker daemon..."
sudo systemctl restart docker

echo ""
echo "Waiting for Docker to restart..."
sleep 5

echo ""
echo "Docker daemon restarted. Log rotation is now active."
echo "New containers will have logs limited to 3 files of 10MB each (30MB total per container)."
echo ""
echo "To apply to existing containers, you need to recreate them:"
echo "  cd ~/abparts"
echo "  sudo docker compose -f docker-compose.prod.yml down"
echo "  sudo docker compose -f docker-compose.prod.yml up -d"
echo ""
