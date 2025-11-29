#!/bin/bash
echo "Checking API logs for errors..."
docker-compose logs --tail=100 api | tail -50
