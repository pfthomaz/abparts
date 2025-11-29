#!/bin/bash
echo "Restarting API container..."
docker-compose restart api
echo "Waiting for API to be ready..."
sleep 3
docker-compose ps api
echo "Done!"
