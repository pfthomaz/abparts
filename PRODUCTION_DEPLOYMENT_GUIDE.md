# Production Deployment Guide - ABParts

## Database Changes Summary (Last 2 Weeks)

### New Columns Added:

1. **`users` table**
   - `profile_photo_url` (VARCHAR(500)) - Stores path to user profile photos

2. **`organizations` table**
   - `logo_url` (VARCHAR(500)) - Stores path to organization logos

3. **`customer_orders` table**
   - `shipped_by_user_id` (UUID, FK to users) - Tracks who marked order as shipped

### No New Tables
All other tables (machines, warehouses, parts, inventory, transactions, etc.) already exist from previous migrations.

---

## Deployment Steps

### Step 1: Backup Production Database

```bash
# Create a backup before making any changes
pg_dump -U your_db_user -d your_db_name > backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup was created
ls -lh backup_*.sql
```

### Step 2: Run Database Migration

```bash
# Connect to production database
psql -U your_db_user -d your_db_name

# Run the migration script
\i PRODUCTION_DATABASE_MIGRATION.sql

# Verify changes
\d users
\d organizations
\d customer_orders
```

**OR** use the SQL file directly:

```bash
psql -U your_db_user -d your_db_name -f PRODUCTION_DATABASE_MIGRATION.sql
```

### Step 3: Create Static Files Directory

```bash
# On your production server
cd /path/to/abparts/backend
mkdir -p static/images
chmod 755 static/images

# Set ownership to your web server user (adjust as needed)
chown -R www-data:www-data static/
# OR for nginx
chown -R nginx:nginx static/
# OR for your app user
chown -R your_app_user:your_app_user static/
```

### Step 4: Update Backend Code

```bash
# Pull latest code
git pull origin main

# Restart backend service
# For Docker:
docker-compose restart api

# For systemd:
sudo systemctl restart abparts-api

# For PM2:
pm2 restart abparts-api
```

### Step 5: Update Frontend Code

```bash
# Build frontend
cd frontend
npm install  # if there are new dependencies
npm run build

# Deploy build files to your web server
# Copy build/ directory to your nginx/apache document root
```

### Step 6: Verify Deployment

1. **Test Profile Photo Upload**
   - Login to the application
   - Go to "My Profile"
   - Upload a profile photo
   - Verify it appears in the header

2. **Test Organization Logo Upload**
   - Go to "Organizations" page
   - Edit an organization (as admin)
   - Upload a logo
   - Verify it appears in the header

3. **Test Part Usage**
   - Go to "Machines" page
   - Click "Use Part" on a machine
   - Select warehouse, part, and quantity
   - Submit and verify transaction appears in Transactions page
   - Verify "TO" column shows machine name (not serial number)

4. **Check API Health**
   ```bash
   curl http://your-domain/api/health
   ```

---

## Configuration Changes

### Environment Variables

Ensure these are set in your production `.env` file:

```bash
# API Base URL
REACT_APP_API_BASE_URL=http://your-domain:8000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/abparts_prod

# Static files path (backend)
STATIC_FILES_PATH=/path/to/backend/static
```

### Nginx Configuration (if using Nginx)

Add static files serving:

```nginx
location /static/ {
    alias /path/to/abparts/backend/static/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

---

## Rollback Procedure

If something goes wrong:

### 1. Restore Database Backup

```bash
# Stop the application
docker-compose stop api  # or your stop command

# Restore database
psql -U your_db_user -d your_db_name < backup_YYYYMMDD_HHMMSS.sql

# Restart application
docker-compose start api
```

### 2. Revert Code Changes

```bash
git log  # find the commit before deployment
git revert <commit-hash>
# OR
git reset --hard <previous-commit-hash>
git push origin main --force  # only if safe to do so
```

---

## Troubleshooting

### Issue: Profile photos not showing

**Check:**
1. Static directory exists and has correct permissions
2. API can write to static/images directory
3. Nginx/Apache is serving /static/ path correctly
4. Browser console for 404 errors

**Fix:**
```bash
chmod 755 backend/static/images
chown www-data:www-data backend/static/images
```

### Issue: Database migration fails

**Check:**
1. Database user has ALTER TABLE permissions
2. No conflicting column names
3. Database connection is working

**Fix:**
```sql
-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_db_user;
```

### Issue: Part usage not recording

**Check:**
1. Inventory has stock > 0
2. User has permission to record part usage
3. Machine belongs to same organization as warehouse

**Fix:**
- Check browser console for errors
- Check API logs: `docker-compose logs api`

---

## Post-Deployment Checklist

- [ ] Database backup created
- [ ] Migration script executed successfully
- [ ] Static files directory created with correct permissions
- [ ] Backend code updated and restarted
- [ ] Frontend code built and deployed
- [ ] Profile photo upload tested
- [ ] Organization logo upload tested
- [ ] Part usage workflow tested
- [ ] Transaction history displays correctly
- [ ] No errors in browser console
- [ ] No errors in API logs
- [ ] All users can login successfully

---

## Support

If you encounter issues:

1. Check API logs: `docker-compose logs api --tail=100`
2. Check database logs: `docker-compose logs db --tail=100`
3. Check browser console (F12)
4. Verify all environment variables are set correctly
5. Ensure all services are running: `docker-compose ps`

---

## Summary of Changes

**Database:** 3 new columns (profile_photo_url, logo_url, shipped_by_user_id)
**Backend:** Image upload endpoints, part usage improvements, transaction display fixes
**Frontend:** Profile photo UI, organization logo UI, part usage recorder, transaction history updates
**Infrastructure:** Static files directory for image storage

**No breaking changes** - All changes are backward compatible. Existing data will not be affected.
