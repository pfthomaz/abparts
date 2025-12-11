# Fix Git Conflicts on Production Server

## Quick Fix (Recommended)

Run these commands on the production server:

```bash
# Remove the conflicting untracked file
rm rebuild_frontend.sh

# Stash local changes to nginx.conf
git stash

# Pull latest changes
git pull origin main

# Deploy
chmod +x deploy_images_to_production.sh
./deploy_images_to_production.sh
```

## What This Does

1. **Removes `rebuild_frontend.sh`** - This is a temporary script that was created on production
2. **Stashes `frontend/nginx.conf`** - Saves your local nginx changes (if any)
3. **Pulls latest code** - Gets all the new image storage code
4. **Deploys** - Runs the deployment script

## If You Need Your Local nginx.conf Changes

After pulling, check what was stashed:

```bash
# See what was stashed
git stash show -p

# If you need those changes back
git stash pop
```

But most likely, the new `nginx.conf` from git already has everything you need (including the `/images/` proxy).

## Alternative: Force Pull (Nuclear Option)

If you want to completely overwrite local changes:

```bash
# Backup first (optional)
cp frontend/nginx.conf frontend/nginx.conf.backup

# Force pull
git fetch origin main
git reset --hard origin/main
git pull origin main

# Deploy
chmod +x deploy_images_to_production.sh
./deploy_images_to_production.sh
```

## Verify After Pull

Check that nginx.conf has the image proxy:

```bash
grep -A 5 "location ^~ /images/" frontend/nginx.conf
```

Should see:
```nginx
location ^~ /images/ {
    proxy_pass http://api:8000/images/;
    ...
}
```

If it's there, you're good to deploy!
