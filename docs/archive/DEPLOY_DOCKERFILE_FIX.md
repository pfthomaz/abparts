# Deploy Dockerfile Fix for localhost:8000 Issue

## The Problem
The frontend build was falling back to `localhost:8000` because the `REACT_APP_API_BASE_URL` environment variable wasn't available during the Docker build process.

## The Fix
Moved the `ARG` and `ENV` declarations in the Dockerfile to **before** the `COPY . .` command, ensuring the environment variable is set before the build runs.

## Deployment Steps

### 1. Copy files to server

```bash
# From your local machine
scp frontend/Dockerfile.frontend diogo@46.62.153.166:/tmp/
scp frontend/.dockerignore diogo@46.62.153.166:/tmp/
```

### 2. SSH into server and deploy

```bash
ssh diogo@46.62.153.166

# Move files to correct location
sudo mv /tmp/Dockerfile.frontend /root/abparts/frontend/
sudo mv /tmp/.dockerignore /root/abparts/frontend/

# Go to project directory
cd /root/abparts

# Stop and remove old container
sudo docker compose -f docker-compose.prod.yml stop web
sudo docker rm abparts_web_prod
sudo docker rmi abparts-web

# Rebuild with --no-cache
# You should see "Building with REACT_APP_API_BASE_URL=/api" in the output
sudo docker compose -f docker-compose.prod.yml build --no-cache web

# Start the container
sudo docker compose -f docker-compose.prod.yml up -d web

# Wait a moment for it to start
sleep 5

# Verify the fix (should return nothing if successful)
sudo docker exec abparts_web_prod grep -r "localhost:8000" /usr/share/nginx/html/static/js/*.js | head -1
```

### 3. If successful, you should see:
- No output from the grep command (meaning no localhost:8000 found)
- The app should now work at https://abparts.oraseas.com

### 4. If still failing, debug with:

```bash
# Check what API_BASE_URL is actually set to in the built files
sudo docker exec abparts_web_prod grep -o 'API_BASE_URL="[^"]*' /usr/share/nginx/html/static/js/main.*.js | head -1

# Check the build logs
sudo docker compose -f docker-compose.prod.yml logs web | tail -50
```

## What Changed

**frontend/Dockerfile.frontend:**
- Moved `ARG REACT_APP_API_BASE_URL=/api` and `ENV REACT_APP_API_BASE_URL=$REACT_APP_API_BASE_URL` to **before** `COPY . .`
- Added debug echo: `RUN echo "Building with REACT_APP_API_BASE_URL=$REACT_APP_API_BASE_URL"`

**frontend/.dockerignore (new file):**
- Prevents local `.env` files from being copied into the Docker build context
- Ensures clean builds without local development configuration

## Why This Works

1. Docker build args must be declared before they're needed
2. The `COPY . .` command copies source code that references `process.env.REACT_APP_API_BASE_URL`
3. When `npm run build` runs, it needs the ENV variable to be already set
4. By setting ARG/ENV before COPY, the variable is available during the entire build process
5. React's build process bakes the environment variable value into the JavaScript bundle
