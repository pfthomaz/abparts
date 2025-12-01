# Database Reset Instructions

## The Problem
The database is in a partially migrated state with:
- Some enum types already created
- Missing tables (like `machine_hours`)
- Lost custom data (organizations, machines, users you added)

## Solution: Complete Database Reset

### Step 1: Stop all containers
```bash
docker-compose down
```

### Step 2: Remove the database volume (THIS WILL DELETE ALL DATA)
```bash
docker volume rm abparts_db_data
# Or if that doesn't work:
docker volume ls | grep abparts
docker volume rm <volume_name>
```

### Step 3: Start containers fresh
```bash
docker-compose up -d
```

### Step 4: Wait for containers to be healthy (30 seconds)
```bash
sleep 30
```

### Step 5: Run all migrations
```bash
docker-compose exec api alembic upgrade head
```

### Step 6: Initialize with seed data
```bash
docker-compose exec api python3 -c "from app.init_db import init_db; from app.database import SessionLocal; db = SessionLocal(); init_db(db); db.close()"
```

## Alternative: Quick Reset Script

I can create a script that does all of this automatically. Would you like me to create it?

## What You'll Need to Recreate

After the reset, you'll need to recreate:
1. ✅ Base organizations (will be seeded automatically)
2. ✅ Base users (will be seeded automatically)
3. ❌ Custom organizations you added
4. ❌ Custom machines you added
5. ❌ Machine hours records
6. ❌ Any custom data

## Recommendation

Since you've lost data anyway, a clean reset is the best approach. This will:
- ✅ Apply all migrations correctly
- ✅ Create all tables including `machine_hours`
- ✅ Set up the database schema properly
- ✅ Include the new `shipped_date` column
- ✅ Seed initial data

Then you can:
1. Test the customer order workflow with fresh data
2. Recreate any custom organizations/machines you need
3. Have a clean, working system

Would you like me to create an automated reset script?
