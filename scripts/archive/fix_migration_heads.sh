#!/bin/bash

# Fix multiple migration heads issue

set -e

echo "============================================================"
echo "FIXING MULTIPLE MIGRATION HEADS"
echo "============================================================"
echo ""

echo "Step 1: Check current migration heads"
echo "------------------------------------------------------------"
docker compose exec api alembic heads
echo ""

echo "Step 2: Check current database version"
echo "------------------------------------------------------------"
docker compose exec api alembic current
echo ""

echo "Step 3: Show migration history"
echo "------------------------------------------------------------"
docker compose exec api alembic history | head -30
echo ""

echo "Step 4: Merge heads"
echo "------------------------------------------------------------"
echo "Creating merge migration..."
docker compose exec api alembic merge heads -m "merge_migration_heads"
echo ""

echo "Step 5: Apply merged migration"
echo "------------------------------------------------------------"
docker compose exec api alembic upgrade head
echo ""

echo "Step 6: Apply hybrid storage migration"
echo "------------------------------------------------------------"
docker compose exec api alembic upgrade head
echo ""

echo "============================================================"
echo "Migration heads merged successfully!"
echo "============================================================"
