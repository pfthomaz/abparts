# Net Cleaning Production Migration Guide

## Issue Fixed
The migration file `create_net_cleaning_tables.py` was not following Alembic's naming convention. It has been renamed to `net_cleaning_001_add_net_cleaning_tables.py`.

Additionally, the frontend was showing "In Progress" status incorrectly because it was checking both `status === 'in_progress'` OR `!end_time`. Now it only checks the `status` field which is automatically managed by the backend.

## Migration Chain
1. **net_cleaning_001** - Creates farm_sites, nets, and net_cleaning_records tables
2. **7b3899138d40** - Adds status column and makes end_time nullable

## Production Deployment Steps

### Step 1: Commit and Push Changes
```bash
git add backend/alembic/versions/
git commit -m "Fix: Rename net cleaning migration to follow Alembic convention"
git push origin main
```

### Step 2: Pull Changes on Production Server
```bash
cd ~/abparts
git pull origin main
```

### Step 3: Check Current Migration Status
```bash
docker compose exec api alembic current
```
Expected output: `ab2c1f16b0b3 (head)`

### Step 4: Check Available Migrations
```bash
docker compose exec api alembic heads
```
This should now show the new migrations are available.

### Step 5: Run Migrations
```bash
docker compose exec api alembic upgrade head
```

This will apply both migrations:
- Creates farm_sites, nets, and net_cleaning_records tables
- Adds status column and makes end_time nullable

### Step 6: Verify Tables Created
```bash
docker compose exec db psql -U abparts_user -d abparts_prod -c "\d farm_sites"
docker compose exec db psql -U abparts_user -d abparts_prod -c "\d nets"
docker compose exec db psql -U abparts_user -d abparts_prod -c "\d net_cleaning_records"
```

### Step 7: Fix Existing Data Status
If you have existing records, run this script to ensure status values are correct:
```bash
docker compose exec api python /app/fix_net_cleaning_status.py
```

### Step 8: Verify Migration Status
```bash
docker compose exec api alembic current
```
Expected output: `7b3899138d40 (head)`

### Step 9: Rebuild Frontend
```bash
docker compose build --no-cache web
```

### Step 10: Restart Services
```bash
docker compose restart
```

## Verification
After deployment, verify the feature works:
1. Log in as dthomaz/amFT1999!
2. Navigate to Farm Sites and create a test farm site
3. Navigate to Nets and create a test net
4. Navigate to Net Cleaning Records and create a test cleaning record
5. Verify you can save a record without end_time (In Progress status)
6. Verify you can edit and complete the record

## Troubleshooting

### If migrations still don't appear:
```bash
# Check Alembic can see the migrations
docker compose exec api alembic history

# Check for any migration conflicts
docker compose exec api alembic branches
```

### If tables already exist (from manual creation):
You may need to stamp the database to the correct revision:
```bash
docker compose exec api alembic stamp 7b3899138d40
```

### Check API logs for errors:
```bash
docker compose logs api --tail=100
```
