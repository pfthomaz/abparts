# 🚀 Start Here - Hybrid Storage Deployment

## Quick Overview

We've implemented a solution to permanently fix your recurring image sync issues by storing images in the PostgreSQL database.

## What You Need to Know

1. **Images → Database**: All images (profile photos, logos, part images) will be stored in PostgreSQL
2. **Automatic Compression**: Images automatically compressed to WebP format (max 500KB)
3. **No More Sync Issues**: Images travel with database backups
4. **Ready to Deploy**: All code is ready and tested

## Choose Your Deployment Method

### Option 1: Automated (Recommended)
```bash
./deploy_hybrid_storage.sh
```
- Fully automated
- Takes ~5 minutes
- Handles everything automatically

### Option 2: Step-by-Step Interactive
```bash
./deploy_dev_step_by_step.sh
```
- Pauses at each step
- Shows what's happening
- Good for learning/debugging

### Option 3: Manual (Most Control)
Follow the guide: `DEPLOY_MANUAL_STEPS.md`
- Run each command yourself
- See exactly what happens
- Best for troubleshooting

## Before You Start

1. **Make sure Docker is running**
   ```bash
   docker ps
   ```

2. **You're in the project root**
   ```bash
   pwd  # Should show .../abparts
   ```

3. **Development environment is up** (or will be started by script)
   ```bash
   docker compose ps
   ```

## Recommended: Start with Automated

```bash
# Run the automated deployment
./deploy_hybrid_storage.sh
```

This will:
1. ✅ Backup your database
2. ✅ Install dependencies (Pillow)
3. ✅ Run database migration
4. ✅ Migrate existing images to database
5. ✅ Start all services
6. ✅ Verify everything works

**Time**: ~5 minutes

## After Deployment

### Test Everything
1. Open http://localhost:3000
2. Login
3. Upload a profile photo
4. Upload an organization logo
5. Verify images display correctly

### Verify Database
```bash
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
  (SELECT COUNT(*) FROM users WHERE profile_photo_data IS NOT NULL) as users_with_photos,
  (SELECT COUNT(*) FROM organizations WHERE logo_data IS NOT NULL) as orgs_with_logos,
  (SELECT COUNT(*) FROM parts WHERE image_data IS NOT NULL) as parts_with_images;
"
```

## If Something Goes Wrong

### Check Logs
```bash
docker compose logs -f api
```

### Check Services
```bash
docker compose ps
```

### Rollback
```bash
# Restore from backup
docker compose down
gunzip < ./backups/abparts_dev_backup_*.sql.gz | docker compose exec -T db psql -U abparts_user abparts_dev
docker compose up -d
```

## Documentation

- **Quick Start**: `QUICK_START_HYBRID_STORAGE.md`
- **Manual Steps**: `DEPLOY_MANUAL_STEPS.md`
- **Full Plan**: `HYBRID_STORAGE_DEPLOYMENT_PLAN.md`
- **Technical Details**: `IMAGE_STORAGE_PERMANENT_SOLUTION.md`
- **Checklist**: `DEPLOYMENT_CHECKLIST.md`

## Production Deployment

After testing in development:
```bash
./deploy_to_production.sh
```

This will deploy to production with full backup and migration.

## Need Help?

1. Check `DEPLOY_MANUAL_STEPS.md` for troubleshooting
2. Review logs: `docker compose logs -f api`
3. Check database: `docker compose exec db psql -U abparts_user -d abparts_dev`

## What's Different After Deployment?

### Before (File-Based)
- Images in `/app/static/images/`
- Manual rsync to sync dev/prod
- Images not in database backups
- Recurring sync issues

### After (Database-Based)
- Images in PostgreSQL database
- Automatic sync with database
- Images in database backups
- No more sync issues

## Ready?

Run this command to start:
```bash
./deploy_hybrid_storage.sh
```

Or for step-by-step:
```bash
./deploy_dev_step_by_step.sh
```

Or follow manual steps:
```bash
cat DEPLOY_MANUAL_STEPS.md
```

---

**Note**: The automated script had an SSH issue (trying to backup production). This has been fixed. The script now correctly backs up the development database locally.
