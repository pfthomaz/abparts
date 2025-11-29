# Rebuild Development Database - Clean Process

## Step 1: Get Production Schema as Init Script

```bash
# Get production schema (structure only)
ssh diogo@46.62.153.166 "sudo docker compose -f /home/abparts/abparts/docker-compose.prod.yml exec -T db pg_dump -U abparts_user --schema-only abparts_prod" > init_db/01_schema.sql

# Get minimal seed data (just what's needed to login and test)
ssh diogo@46.62.153.166 "sudo docker compose -f /home/abparts/abparts/docker-compose.prod.yml exec -T db pg_dump -U abparts_user --data-only --column-inserts -t users -t organizations -t warehouses abparts_prod" > init_db/02_seed_data.sql

# Optional: Get all production data for full copy
ssh diogo@46.62.153.166 "sudo docker compose -f /home/abparts/abparts/docker-compose.prod.yml exec -T db pg_dump -U abparts_user --data-only --column-inserts abparts_prod" > init_db/03_full_data.sql
```

## Step 2: Clean Old Init Scripts

```bash
# Remove old conflicting init scripts
rm init_db/init.sql 2>/dev/null || true
rm init_db/*.sh 2>/dev/null || true

# Keep only the new ones
ls -la init_db/
```

## Step 3: Test Clean Rebuild

```bash
# Stop and remove everything
docker-compose down -v

# Start fresh - init scripts will run automatically
docker-compose up -d db

# Wait for database to initialize
sleep 15

# Check if schema was created
docker-compose exec db psql -U abparts_user -d abparts_dev -c "\dt" | wc -l

# Start all services
docker-compose up -d

# Mark migrations as applied (since schema is from production)
docker-compose exec api alembic stamp head

# Test login at http://localhost:3000
```

## Step 4: Verify and Commit

```bash
# If everything works, commit the new init scripts
git add init_db/
git commit -m "Add production-based init scripts for dev database"
git push
```

## Future: Quick Reset

Anytime you want to reset your dev database:

```bash
docker-compose down -v
docker-compose up -d
# Wait 15 seconds for init scripts to run
# Done! Fresh database with seed data
```

## Notes

- `01_schema.sql` - Creates all tables, types, functions (from production)
- `02_seed_data.sql` - Minimal data to login and test (users, orgs, warehouses)
- `03_full_data.sql` - Optional full production data copy
- Scripts run in alphabetical order automatically
- No more migration conflicts!
