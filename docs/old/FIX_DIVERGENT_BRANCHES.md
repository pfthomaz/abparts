# Fix Divergent Branches on Production

## Problem

Git is reporting divergent branches - production has local changes that conflict with your pushed changes.

## Solution

### Option 1: Stash Local Changes (Recommended)

This preserves any local changes on production while pulling your new code.

```bash
# On production server (as abparts user or root)
cd ~/abparts  # or /root/abparts if root

# See what changed locally
git status
git diff --stat

# Stash local changes
git stash save "local_changes_$(date +%Y%m%d_%H%M%S)"

# Pull with rebase
git pull --rebase origin main

# Check status
git status
```

### Option 2: Force Pull (If Local Changes Don't Matter)

⚠️ **Warning**: This discards any local changes on production!

```bash
# On production server
cd ~/abparts  # or /root/abparts

# Backup current state (just in case)
git diff > /tmp/local_changes_backup.patch

# Reset to remote
git fetch origin
git reset --hard origin/main

# Verify
git status
```

### Option 3: Merge (Keep Both Changes)

```bash
# On production server
cd ~/abparts

# Configure merge strategy
git config pull.rebase false

# Pull and merge
git pull origin main

# If conflicts, resolve them
git status
# Edit conflicting files
git add .
git commit -m "Merge remote changes"
```

## Step-by-Step for Your Situation

Since you're on production as `abparts` user:

```bash
# 1. Check what changed locally
git status
git log --oneline -5

# 2. Stash local changes (safest option)
git stash save "before_hybrid_storage_$(date +%Y%m%d_%H%M%S)"

# 3. Pull with rebase
git pull --rebase origin main

# 4. Verify
git status
git log --oneline -5

# 5. Check stashed changes (optional)
git stash list
git stash show -p stash@{0}
```

## After Fixing Git

Continue with deployment:

```bash
# Switch to root
sudo su -

# Navigate to project
cd /root/abparts

# If you're in /home/abparts/abparts, the changes are there
# If root needs them, pull again as root:
git pull origin main

# Continue with deployment steps...
```

## Common Causes

1. **Direct edits on production** - Files edited directly on server
2. **Previous deployments** - Old deployment scripts made commits
3. **Config changes** - Environment files or configs changed locally

## Prevention

- Never edit files directly on production
- Always deploy via git push/pull
- Use environment variables for config differences
- Keep production as clean git checkout

## Quick Commands Reference

```bash
# See what changed
git status
git diff

# Stash changes
git stash

# Pull latest
git pull origin main

# See stashed changes
git stash list
git stash show -p

# Apply stashed changes (if needed)
git stash pop

# Discard stash
git stash drop

# Reset to remote (nuclear option)
git reset --hard origin/main
```

## For Your Current Situation

Run these commands on production:

```bash
cd ~/abparts
git stash
git pull --rebase origin main
```

Then continue with deployment as root:

```bash
sudo su -
cd /root/abparts
git pull origin main
# Continue with deployment...
```
