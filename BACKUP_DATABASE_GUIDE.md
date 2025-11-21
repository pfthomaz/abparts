# Production Database Backup Guide

## Step 1: Create Backup on Production Server

SSH to the production server:
```bash
ssh diogo@46.62.153.166
```

Then run these commands:
```bash
# Switch to abparts user
su abparts
# Enter password when prompted

# Navigate to project directory
cd ~/abparts

# Create database backup
sudo docker exec abparts_db_prod pg_dump -U abparts_user -d abparts_prod > /tmp/abparts_backup_$(date +%Y%m%d_%H%M%S).sql

# Create images backup
cd /var/lib/abparts
sudo tar -czf /tmp/abparts_images_$(date +%Y%m%d_%H%M%S).tar.gz images/

# List the backups
ls -lh /tmp/abparts_*

# Note the filenames for the next step
```

## Step 2: Download Backups to Local Machine

On your **local machine**, run:
```bash
# Download database backup (replace with actual filename)
scp abparts@46.62.153.166:/tmp/abparts_backup_YYYYMMDD_HHMMSS.sql ~/Downloads/

# Download images backup (replace with actual filename)
scp abparts@46.62.153.166:/tmp/abparts_images_YYYYMMDD_HHMMSS.tar.gz ~/Downloads/
```

## Step 3: Restore to Local Development

On your **local machine**, in the project directory:

```bash
# Stop local containers
docker-compose down

# Start only the database
docker-compose up -d db
sleep 5

# Drop and recreate database
docker-compose exec db psql -U abparts_user -d postgres -c "DROP DATABASE IF EXISTS abparts_dev;"
docker-compose exec db psql -U abparts_user -d postgres -c "CREATE DATABASE abparts_dev;"

# Restore the backup (replace with your downloaded file)
cat ~/Downloads/abparts_backup_YYYYMMDD_HHMMSS.sql | docker-compose exec -T db psql -U abparts_user -d abparts_dev

# Extract images
mkdir -p backend/static
tar -xzf ~/Downloads/abparts_images_YYYYMMDD_HHMMSS.tar.gz -C backend/static/

# Start all containers
docker-compose up -d

# Check logs
docker-compose logs api
```

## Step 4: Clean Up (Optional)

On the **production server**:
```bash
# Remove temporary backups
rm /tmp/abparts_backup_*.sql
rm /tmp/abparts_images_*.tar.gz
```

## Quick Reference

### Production Server Commands
```bash
# As abparts user
cd ~/abparts
sudo docker exec abparts_db_prod pg_dump -U abparts_user -d abparts_prod > /tmp/backup.sql
sudo tar -czf /tmp/images.tar.gz -C /var/lib/abparts images/
```

### Local Machine Commands
```bash
# Download
scp abparts@46.62.153.166:/tmp/backup.sql .
scp abparts@46.62.153.166:/tmp/images.tar.gz .

# Restore
docker-compose down
docker-compose up -d db
sleep 5
docker-compose exec db psql -U abparts_user -d postgres -c "DROP DATABASE IF EXISTS abparts_dev; CREATE DATABASE abparts_dev;"
cat backup.sql | docker-compose exec -T db psql -U abparts_user -d abparts_dev
tar -xzf images.tar.gz -C backend/static/
docker-compose up -d
```

## Troubleshooting

### "Permission denied" when creating backup
- Make sure you're logged in as the `abparts` user
- Or use `sudo` before the docker commands

### "Database does not exist" error
- The database name in production is `abparts_prod`
- The database name in development is `abparts_dev`
- Make sure you're using the correct names

### Images not showing after restore
- Check that images were extracted to `backend/static/images/`
- Verify the volume mount in docker-compose.yml
- Check file permissions: `ls -la backend/static/images/`

### Connection refused after restore
- Wait a few seconds for containers to start
- Check logs: `docker-compose logs api`
- Verify .env.development has correct credentials
