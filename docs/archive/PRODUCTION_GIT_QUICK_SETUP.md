# Quick Git Setup for Production Server

## Your Situation
- You're on Ubuntu server: `diogo@ubuntu-8gb-hel1-2`
- Your project directory: `~/abparts`
- Directory exists but is NOT a Git repository yet
- You already have SSH keys set up (working with another repo)

## Step 1: Backup Your Current Files

Before initializing Git, backup your current production files:

```bash
# Create backup directory
mkdir -p ~/backups/pre-git-$(date +%Y%m%d_%H%M%S)

# Backup important files
cp ~/abparts/.env ~/backups/pre-git-$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
cp ~/abparts/.env.production ~/backups/pre-git-$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
cp ~/abparts/docker-compose.prod.yml ~/backups/pre-git-$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true

echo "✅ Backup complete"
```

## Step 2: Initialize Git Repository

```bash
# Navigate to your project directory
cd ~/abparts

# Initialize Git
git init

# Verify Git is initialized
ls -la .git
```

## Step 3: Add Your GitHub Repository as Remote

**Important:** Replace `yourusername/abparts` with your actual GitHub repository path!

```bash
# Add remote repository (use SSH since you already have keys)
git remote add origin git@github.com:yourusername/abparts.git

# Verify remote was added
git remote -v
```

## Step 4: Fetch Repository Content

```bash
# Fetch all branches and commits from remote
git fetch origin

# List available branches
git branch -r
```

## Step 5: Checkout Main Branch

**Note:** Your repository might use `main` or `master` as the default branch. Try `main` first:

```bash
# Try main branch first
git checkout -b main origin/main
```

If that fails with "origin/main not found", try master:

```bash
# If main doesn't exist, try master
git checkout -b master origin/master
```

## Step 6: Handle Existing Files

If Git complains about existing files that would be overwritten:

### Option A: Keep Remote Version (Recommended for first setup)

```bash
# Stash your local files
git stash

# Pull from remote
git pull origin main  # or master

# Your local changes are saved in stash
# You can restore specific files later if needed
```

### Option B: Keep Local Files and Merge

```bash
# Add all local files
git add .

# Commit local state
git commit -m "Production state before Git setup"

# Pull and merge
git pull origin main --allow-unrelated-histories
```

## Step 7: Verify Setup

```bash
# Check current branch
git branch

# Check status
git status

# View recent commits
git log --oneline -5

# Verify remote connection
git remote -v
```

## Step 8: Test Git Pull

```bash
# Try pulling latest changes
git pull origin main  # or master

# Should see "Already up to date" if everything is synced
```

## Common Issues and Solutions

### Issue: "Permission denied (publickey)"

Your SSH key might not be added to GitHub yet.

```bash
# Test SSH connection to GitHub
ssh -T git@github.com

# Should see: "Hi username! You've successfully authenticated..."
```

If it fails, add your SSH key to GitHub:

```bash
# Display your public key
cat ~/.ssh/id_ed25519.pub
# or
cat ~/.ssh/id_rsa.pub

# Copy the output and add it to GitHub:
# GitHub.com → Settings → SSH and GPG keys → New SSH key
```

### Issue: "fatal: refusing to merge unrelated histories"

This happens when local and remote have different histories:

```bash
# Force merge with unrelated histories
git pull origin main --allow-unrelated-histories
```

### Issue: Files would be overwritten

```bash
# See which files conflict
git status

# Option 1: Stash local changes
git stash

# Option 2: Force overwrite with remote
git reset --hard origin/main
```

## Quick Reference for Daily Use

```bash
# Pull latest changes
cd ~/abparts
git pull origin main

# Check what changed
git log --oneline -10

# See current status
git status

# Discard all local changes (careful!)
git reset --hard origin/main
```

## Next Steps After Setup

1. **Create a deployment script** (see PRODUCTION_GIT_SETUP_GUIDE.md)
2. **Set up automatic backups** before each pull
3. **Test the workflow** with a small change
4. **Document your specific deployment process**

## Need Help?

- Full detailed guide: See `PRODUCTION_GIT_SETUP_GUIDE.md`
- Git basics: `git --help`
- GitHub SSH setup: https://docs.github.com/en/authentication/connecting-to-github-with-ssh

---

**Remember:** Always backup your `.env` and production config files before pulling changes!
