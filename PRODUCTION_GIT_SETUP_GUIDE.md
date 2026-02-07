# Production Server Git Setup Guide

This guide will help you set up Git on your Ubuntu production server and link it to your repository for easy deployments.

## Prerequisites
- SSH access to your Ubuntu production server
- Your Git repository URL (GitHub, GitLab, Bitbucket, etc.)
- Server user with appropriate permissions

## Step 1: Install Git on Production Server

SSH into your production server and install Git:

```bash
# Update package list
sudo apt update

# Install Git
sudo apt install git -y

# Verify installation
git --version
```

## Step 2: Configure Git User

Set up your Git identity on the server:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Step 3: Set Up SSH Key for Git (Recommended)

### Generate SSH Key on Server

```bash
# Generate SSH key (press Enter to accept defaults)
ssh-keygen -t ed25519 -C "your.email@example.com"

# Start SSH agent
eval "$(ssh-agent -s)"

# Add SSH key to agent
ssh-add ~/.ssh/id_ed25519

# Display public key (copy this)
cat ~/.ssh/id_ed25519.pub
```

### Add SSH Key to Your Git Provider

**For GitHub:**
1. Go to GitHub.com → Settings → SSH and GPG keys
2. Click "New SSH key"
3. Paste the public key from above
4. Click "Add SSH key"

**For GitLab:**
1. Go to GitLab.com → Preferences → SSH Keys
2. Paste the public key
3. Click "Add key"

**For Bitbucket:**
1. Go to Bitbucket.org → Personal settings → SSH keys
2. Click "Add key"
3. Paste the public key

## Step 4: Clone or Initialize Repository on Server

### Option A: Clone Existing Repository (Fresh Setup)

```bash
# Navigate to where you want the code
cd /opt  # or wherever you want to deploy

# Clone repository (use SSH URL)
git clone git@github.com:yourusername/abparts.git

# Enter the directory
cd abparts
```

### Option B: Link Existing Directory to Repository

If you already have code on the server:

```bash
# Navigate to your existing project directory
cd /path/to/your/abparts

# Initialize git if not already initialized
git init

# Add remote repository
git remote add origin git@github.com:yourusername/abparts.git

# Fetch from remote
git fetch origin

# Set up tracking (if main branch)
git branch --set-upstream-to=origin/main main

# Or if using master branch
git branch --set-upstream-to=origin/master master
```

## Step 5: Create Deployment Script

Create a script to safely deploy updates:

```bash
# Create deployment script
nano ~/deploy.sh
```

Add this content:

```bash
#!/bin/bash

# ABParts Production Deployment Script

set -e  # Exit on error

echo "🚀 Starting deployment..."

# Navigate to project directory
cd /path/to/your/abparts

# Stash any local changes (like .env files)
echo "📦 Stashing local changes..."
git stash

# Pull latest changes
echo "⬇️  Pulling latest changes..."
git pull origin main  # or 'master' if that's your branch

# Restore local changes
echo "📤 Restoring local changes..."
git stash pop || echo "No stash to restore"

# Backend: Install dependencies if requirements changed
if git diff HEAD@{1} --name-only | grep -q "backend/requirements.txt"; then
    echo "📚 Installing backend dependencies..."
    docker-compose exec api pip install -r backend/requirements.txt
fi

# Backend: Run migrations if needed
if git diff HEAD@{1} --name-only | grep -q "backend/alembic/versions/"; then
    echo "🗄️  Running database migrations..."
    docker-compose exec api alembic upgrade head
fi

# Frontend: Rebuild if frontend changed
if git diff HEAD@{1} --name-only | grep -q "frontend/"; then
    echo "🏗️  Rebuilding frontend..."
    docker-compose build web
fi

# Restart services
echo "🔄 Restarting services..."
docker-compose restart

echo "✅ Deployment complete!"
echo ""
echo "📊 Current status:"
docker-compose ps
```

Make it executable:

```bash
chmod +x ~/deploy.sh
```

## Step 6: Set Up .gitignore for Production

Ensure sensitive files are not tracked:

```bash
# Check if .gitignore exists
cat .gitignore

# Make sure these are in .gitignore:
# .env
# .env.production
# *.log
# __pycache__/
# node_modules/
# build/
# *.pyc
```

## Step 7: Protect Production Files

Create a script to backup important files before pulling:

```bash
nano ~/backup-env.sh
```

Add:

```bash
#!/bin/bash

# Backup production environment files
BACKUP_DIR=~/backups/$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

cd /path/to/your/abparts

# Backup important files
cp .env $BACKUP_DIR/ 2>/dev/null || true
cp .env.production $BACKUP_DIR/ 2>/dev/null || true
cp docker-compose.prod.yml $BACKUP_DIR/ 2>/dev/null || true

echo "✅ Backup created at: $BACKUP_DIR"
```

Make it executable:

```bash
chmod +x ~/backup-env.sh
```

## Step 8: Deployment Workflow

### Regular Deployment

```bash
# 1. Backup environment files
~/backup-env.sh

# 2. Run deployment
~/deploy.sh
```

### Manual Deployment Steps

If you prefer manual control:

```bash
cd /path/to/your/abparts

# Check current status
git status

# See what will be pulled
git fetch origin
git log HEAD..origin/main --oneline

# Pull changes
git pull origin main

# Rebuild and restart
docker-compose build
docker-compose up -d

# Check logs
docker-compose logs -f --tail=100
```

## Step 9: Handle Merge Conflicts

If you have local changes that conflict:

```bash
# See what's different
git status
git diff

# Option 1: Keep remote changes (discard local)
git reset --hard origin/main

# Option 2: Keep local changes (stash, pull, apply)
git stash
git pull origin main
git stash pop
# Resolve conflicts manually if any

# Option 3: Commit local changes first
git add .
git commit -m "Production-specific changes"
git pull origin main --rebase
```

## Step 10: Set Up Automatic Deployments (Optional)

### Using Webhooks

Create a webhook endpoint that triggers deployment:

```bash
# Install webhook tool
sudo apt install webhook -y

# Create webhook configuration
sudo nano /etc/webhook.conf
```

Add:

```json
[
  {
    "id": "deploy-abparts",
    "execute-command": "/home/youruser/deploy.sh",
    "command-working-directory": "/path/to/your/abparts",
    "response-message": "Deployment triggered",
    "trigger-rule": {
      "match": {
        "type": "payload-hash-sha1",
        "secret": "your-webhook-secret",
        "parameter": {
          "source": "header",
          "name": "X-Hub-Signature"
        }
      }
    }
  }
]
```

Start webhook service:

```bash
webhook -hooks /etc/webhook.conf -verbose
```

## Troubleshooting

### Permission Denied

```bash
# Fix file permissions
sudo chown -R $USER:$USER /path/to/your/abparts

# Fix SSH permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

### Authentication Failed

```bash
# Test SSH connection
ssh -T git@github.com

# If using HTTPS, switch to SSH
git remote set-url origin git@github.com:yourusername/abparts.git
```

### Detached HEAD State

```bash
# Return to main branch
git checkout main
git pull origin main
```

### Local Changes Blocking Pull

```bash
# See what's changed
git status

# Stash changes
git stash

# Pull updates
git pull

# Reapply changes
git stash pop
```

## Security Best Practices

1. **Never commit sensitive data**
   - Keep `.env` files out of Git
   - Use `.gitignore` properly

2. **Use SSH keys instead of passwords**
   - More secure
   - No password prompts

3. **Limit server access**
   - Use deploy keys (read-only) if possible
   - Restrict SSH access

4. **Regular backups**
   - Backup database before deployments
   - Keep environment file backups

5. **Test before deploying**
   - Always test changes in development first
   - Use staging environment if possible

## Quick Reference

```bash
# Check status
git status

# Pull latest changes
git pull origin main

# View recent commits
git log --oneline -10

# Discard local changes
git reset --hard origin/main

# Create backup
~/backup-env.sh

# Deploy
~/deploy.sh

# View deployment logs
docker-compose logs -f
```

## Next Steps

1. Set up your SSH key on the server
2. Add the public key to your Git provider
3. Clone or link your repository
4. Create the deployment script
5. Test with a small change
6. Document your specific deployment process

---

**Note:** Replace `/path/to/your/abparts` with your actual project path and adjust branch names (`main` vs `master`) as needed.
