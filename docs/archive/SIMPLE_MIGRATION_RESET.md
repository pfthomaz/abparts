# Simple Migration Reset - The Right Way

## Your Setup

You're building Docker images **on the production server** from source code, not using pre-built images. This means:

- Development: Build and run locally
- Production: `git pull` → `docker compose build` → `docker compose up`

## The Simple Process

### Step 1: Reset in Development (Your Mac)

```bash
# Run the reset script
chmod +x reset_migrations_clean_dev.sh
./reset_migrations_clean_dev.sh
```

This creates:
- `backend/alembic/versions/00_baseline_schema.py` (the baseline migration)
- `backend/alembic/baseline_schema.sql` (schema reference)

### Step 2: Commit and Push

```bash
git add backend/alembic/versions/00_baseline_schema.py
git add backend/alembic/baseline_schema.sql
git commit -m "Reset migrations to clean baseline"
git push
```

### Step 3: Deploy to Production

```bash
# SSH to production
ssh user@your-server
cd ~/abparts

# Pull the new code (includes baseline migration)
git pull

# Rebuild containers (includes new migration file)
docker compose -f docker-compose.prod.yml build api

# Stop services
docker compose -f docker-compose.prod.yml down

# Clear production migration history
docker compose -f docker-compose.prod.yml up -d db
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "DELETE FROM alembic_version;"

# Start all services
docker compose -f docker-compose.prod.yml up -d

# Stamp the database with baseline
docker compose -f docker-compose.prod.yml exec api alembic stamp 00_baseline

# Verify
docker compose -f docker-compose.prod.yml exec db psql -U abparts_user -d abparts_prod -c "SELECT * FROM alembic_version;"
```

## Even Simpler: One-Line Production Deploy

Actually, you can make this even simpler. Let me create a deployment script:

```bash
# In production, after git pull:
./deploy_with_baseline.sh
```

## Why Not Use Pre-Built Images?

You could use pre-built images (build in dev, push to registry, pull in prod), but your current setup is fine for a small team. Pre-built images are better for:
- Large teams
- CI/CD pipelines
- Multiple production servers
- Faster deployments

Your current approach (build on server) is simpler and works well for your scale.

## Future: If You Want Pre-Built Images

If you later want to use pre-built images:

```yaml
# docker-compose.prod.yml
api:
  image: your-registry.com/abparts-api:latest
  # No build section

web:
  image: your-registry.com/abparts-web:latest
  # No build section
```

Then in development:
```bash
docker build -t your-registry.com/abparts-api:latest ./backend
docker push your-registry.com/abparts-api:latest
```

But for now, your current setup is fine!
