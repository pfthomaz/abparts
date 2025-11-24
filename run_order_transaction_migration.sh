#!/bin/bash

echo "Running migration to add customer_order_id to transactions..."
docker compose exec api alembic upgrade head

echo "Migration complete!"
