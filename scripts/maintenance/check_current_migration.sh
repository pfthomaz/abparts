#!/bin/bash
echo "Current migration head:"
docker-compose exec -T api alembic current

echo ""
echo "Migration history:"
docker-compose exec -T api alembic history | head -20
