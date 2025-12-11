#!/bin/bash
echo "Running migration to make execution fields nullable..."
docker-compose exec api alembic upgrade head
echo "Migration complete!"
