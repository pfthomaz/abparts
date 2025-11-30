#!/bin/bash
echo "Checking API logs for errors..."
docker-compose logs --tail=50 api
