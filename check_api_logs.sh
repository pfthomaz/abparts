#!/bin/bash
echo "Checking API logs for errors..."
docker-compose logs api --tail=50 | grep -A 10 "stock-adjustments"
