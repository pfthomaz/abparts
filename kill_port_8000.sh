#!/bin/bash

echo "=== Finding and killing process on port 8000 ==="
echo ""

# Find what's using port 8000
echo "Checking what's using port 8000..."
sudo lsof -i :8000 || echo "No process found using lsof"
echo ""

# Alternative method using netstat
echo "Checking with netstat..."
sudo netstat -tulpn | grep :8000 || echo "No process found using netstat"
echo ""

# Find and kill the process
echo "Attempting to kill process on port 8000..."
PID=$(sudo lsof -t -i:8000)
if [ -n "$PID" ]; then
    echo "Found process $PID using port 8000"
    sudo kill -9 $PID
    echo "✓ Killed process $PID"
    sleep 2
else
    echo "No process found to kill"
fi
echo ""

# Check if any docker containers are still running
echo "Checking for zombie docker containers..."
docker ps -a | grep abparts_api
echo ""

# Force remove any stopped API containers
echo "Removing any stopped API containers..."
docker rm -f abparts_api 2>/dev/null || echo "No container to remove"
echo ""

# Now try to start the API container
echo "Starting API container..."
docker compose up -d api
echo ""

# Wait a moment
sleep 5

# Check status
echo "Checking container status..."
docker compose ps api
echo ""

# Check logs
echo "API logs (last 15 lines):"
docker compose logs --tail=15 api
echo ""

echo "=== Done ==="
