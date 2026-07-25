# Project Maintenance Reminders

## Weekly Cleanup (Every 2-3 Days)

Run this to keep your project organized:

```bash
./weekly_cleanup.sh
```

This will:
- Move old files (>2 days) to archive folders
- Organize test files
- Delete very old archives (>30 days)
- Keep only recent work visible in root

## What Gets Cleaned

- **Documentation** (.md files) → `docs/archive/`
- **Scripts** (.sh files) → `scripts/archive/`
- **Python scripts** (.py files) → `scripts/archive/` or `tests/`
- **SQL files** (.sql files) → `scripts/archive/`

## Automatic Cleanup (Optional)

### Option 1: Manual Reminder
Add to your calendar: "Run project cleanup" every 3 days

### Option 2: Git Hook
Create `.git/hooks/post-commit`:
```bash
#!/bin/bash
# Check if cleanup is needed (every 3 days)
if [ -f .last_cleanup ]; then
    DAYS_SINCE=$(( ($(date +%s) - $(date -r .last_cleanup +%s)) / 86400 ))
    if [ $DAYS_SINCE -gt 3 ]; then
        echo ""
        echo "⚠️  It's been $DAYS_SINCE days since last cleanup"
        echo "   Run: ./weekly_cleanup.sh"
        echo ""
    fi
fi
```

### Option 3: Cron Job (macOS/Linux)
```bash
# Edit crontab
crontab -e

# Add this line (runs every 3 days at 9 AM)
0 9 */3 * * cd /path/to/abparts && ./weekly_cleanup.sh --auto
```

## Quick Check

See if cleanup is needed:
```bash
# Count files in root
ls -1 *.md *.sh *.py *.sql 2>/dev/null | wc -l

# If more than 10 files, time to clean up!
```

## Archive Management

Archives are automatically cleaned after 30 days, but you can manually review:

```bash
# See what's in archives
ls -lt docs/archive/ | head -20
ls -lt scripts/archive/ | head -20

# Delete all archives if you don't need them
rm -rf docs/archive/*
rm -rf scripts/archive/*
```

## Best Practices

1. **Run cleanup every 2-3 days** during active development
2. **Keep only current work** in root directory
3. **Review archives monthly** and delete what you don't need
4. **Commit organized structure** to git regularly

## Last Cleanup

Check when you last ran cleanup:
```bash
cat .last_cleanup
```

If it's been more than 3 days, run:
```bash
./weekly_cleanup.sh
```
