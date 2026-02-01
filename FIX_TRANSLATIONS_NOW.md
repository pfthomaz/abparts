# Fix Translation Keys Issue - Quick Start

## Problem
Seeing `aiAssistant.messages.machineSelected` instead of "Selected machine: [name] ([model])"

## Solution
Frontend needs to be rebuilt with latest translation files.

## On Production Server

```bash
cd ~/abparts
./fix_production_translations.sh
```

**Time: 3-5 minutes**

## What It Does
1. ✓ Verifies translation files exist
2. ✓ Checks machineSelected key is present  
3. ✓ Rebuilds frontend (includes all translations)
4. ✓ Restarts web container
5. ✓ Verifies container is running

## After Running

### Test It
1. Open AI Assistant chat
2. Select a machine
3. Should see: **"Selected machine: AutoBoss 1 (V3.1B)"**
4. NOT: ~~"aiAssistant.messages.machineSelected"~~

### If Still Showing Keys
Hard refresh your browser:
- **Windows/Linux**: `Ctrl + Shift + R`
- **Mac**: `Cmd + Shift + R`

This clears the browser cache.

## Manual Alternative

If script doesn't work:

```bash
# Rebuild frontend
docker compose exec web npm run build

# Restart container
docker compose restart web

# Wait 5 seconds
sleep 5

# Check status
docker compose ps web
```

## Diagnostic Tool

Want to investigate first?

```bash
./diagnose_translation_issue.sh
```

Shows:
- Translation files status
- Build directory info
- Container logs
- Key presence in files

## Why This Happened

Translation files were updated with correct `{{param}}` syntax, but production frontend wasn't rebuilt. React bundles translations into JavaScript, so JSON changes need a rebuild.

## Files Created

- `fix_production_translations.sh` - Automated fix (executable)
- `diagnose_translation_issue.sh` - Diagnostic tool (executable)
- `TRANSLATION_KEYS_SHOWING_FIX.md` - Complete documentation

## That's It!

Run the script, wait 3-5 minutes, hard refresh your browser, and the translations will work.
