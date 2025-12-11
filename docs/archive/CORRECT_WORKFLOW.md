# Correct Migration Reset Workflow

## Understanding Your Setup

Your production deployment works like this:

```
Development (Mac)          Production (Server)
─────────────────         ──────────────────
1. Write code             1. git pull
2. Test locally           2. docker compose build (builds from source)
3. git commit/push        3. docker compose up (runs new containers)
```

**Key Point**: Production builds containers FROM SOURCE CODE on the server, not from pre-built images.

## Migration Reset Process

### Part 1: Development (One Time)

```bash
# 1. Run reset script
chmod +x reset_migrations_clean_dev.sh
./reset_migrations_clean_dev.sh

# This creates:
# - backend/alembic/versions/00_baseline_schema.py
# - backend/alembic/baseline_schema.sql

# 2. Commit to git
git add backend/alembic/versions/00_baseline_schema.py
git add backend/alembic/baseline_schema.sql
git commit -m "Reset migrations to clean baseline"
git push
```

### Part 2: Production (One Time)

```bash
# SSH to production server
ssh user@your-server
cd ~/abparts

# Pull code (includes baseline migration)
git pull

# Deploy with baseline
chmod +x deploy_baseline_to_prod.sh
./deploy_baseline_to_prod.sh

# Done! The script handles:
# - Rebuilding API container (baseline migration is now in the image)
# - Clearing old migration history
# - Stamping database at 00_baseline
# - Restarting services
```

## Why This Works

1. **Development**: Creates baseline migration file
2. **Git**: Baseline migration is in repository
3. **Production git pull**: Gets baseline migration file
4. **Production docker build**: Baseline migration is copied into container image
5. **Production alembic stamp**: Database is marked at baseline

The baseline migration is **part of the code**, so it gets deployed like any other code change.

## Future Migrations (After Baseline)

### In Development

```bash
# 1. Edit models
nano backend/app/models.py

# 2. Generate migration
docker compose exec api alembic revision --autogenerate -m "add new field"

# 3. Apply migration
docker compose exec api alembic upgrade head

# 4. Test
docker compose restart api

# 5. Commit
git add backend/app/models.py
git add backend/alembic/versions/<new_migration>.py
git commit -m "Add new field to model"
git push
```

### In Production

```bash
# 1. Pull code
git pull

# 2. Rebuild and restart
docker compose -f docker-compose.prod.yml build api
docker compose -f docker-compose.prod.yml up -d

# 3. Apply migration
docker compose -f docker-compose.prod.yml exec api alembic upgrade head

# 4. Verify
docker compose -f docker-compose.prod.yml exec api alembic current
```

Or use the automated deployment script:

```bash
git pull
./deploy_production_clean.sh
```

## Why You Don't Need Separate Production Script

You asked: "Why do I have to run it also in production?"

**Answer**: You don't run the *reset* script in production. You run a *deployment* script that:
1. Rebuilds containers (which includes the baseline migration from git)
2. Stamps the database

The baseline migration file comes from git, not from running a reset script.

## Alternative: Pre-Built Images (Future)

If you want to build images in development and use them in production:

### Development
```bash
# Build image
docker build -t myregistry.com/abparts-api:v1.0 ./backend

# Push to registry
docker push myregistry.com/abparts-api:v1.0
```

### Production
```yaml
# docker-compose.prod.yml
api:
  image: myregistry.com/abparts-api:v1.0  # Use pre-built image
  # No build section
```

```bash
# Production deployment
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

**Benefits**:
- Faster production deployments
- Guaranteed same image as tested in dev
- No build tools needed on production server

**Your Current Approach is Fine For**:
- Small teams
- Simple deployment process
- When you control the production server

## Summary

**Current Setup** (Build on Server):
```
Dev: Code → Git
Prod: Git → Build → Run
```

**Alternative** (Pre-Built Images):
```
Dev: Code → Build → Registry
Prod: Registry → Run
```

Both work! Your current setup is simpler and perfectly fine for your scale.

## What You Actually Need to Do

1. **Development**: `./reset_migrations_clean_dev.sh` + commit + push
2. **Production**: `git pull` + `./deploy_baseline_to_prod.sh`

That's it! The baseline migration travels through git, gets built into the container, and stamps the database.
