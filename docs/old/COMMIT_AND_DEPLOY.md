# Commit and Deploy Production Fix

## Step 1: Commit Changes (Local Machine)

```bash
# Check what files changed
git status

# Add the changed files
git add frontend/Dockerfile.frontend
git add docker-compose.prod.yml
git add frontend/nginx.conf

# Commit
git commit -m "Fix production CORS: use nginx proxy for API calls

- Updated Dockerfile to accept REACT_APP_API_BASE_URL build arg
- Modified docker-compose.prod.yml to pass build arg
- Nginx already configured to proxy /api/ to backend
- This fixes CORS by serving frontend and API from same origin"

# Push to repository
git push
```

## Step 2: Deploy on Server

```bash
# SSH to server
ssh diogo@46.62.153.166

# Navigate to project
cd ~/abparts

# Pull changes
git pull

# Update .env file
nano .env
# Add this line: REACT_APP_API_BASE_URL=/api
# Save and exit (Ctrl+X, Y, Enter)

# Rebuild and restart
sudo docker compose -f docker-compose.prod.yml down
sudo docker compose -f docker-compose.prod.yml build web --no-cache
sudo docker compose -f docker-compose.prod.yml up -d

# Verify
sudo docker ps
curl http://localhost/api/
```

## Step 3: Test

Open browser: http://46.62.153.166/

Try to login. Check browser console (F12) - you should see:
- ✓ Requests to `/api/token` (not `:8000/token`)
- ✓ No CORS errors
- ✓ Successful login
