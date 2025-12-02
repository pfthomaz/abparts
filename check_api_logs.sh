#!/bin/bash
echo "Checking API logs for errors..."
docker-compose logs api --tail=50 | grep -A 5 -B 5 "stock-adjustments\|Error\|Exception"
