#!/bin/bash
echo "Checking migration heads..."
docker-compose exec api alembic heads
echo ""
echo "Checking migration branches..."
docker-compose exec api alembic branches
