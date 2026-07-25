# Fix Translation Keys - Quick Command

## On Production Server

```bash
cd ~/abparts
./rebuild_frontend_production.sh
```

**Time: 3-5 minutes**

## After It Completes

**Hard refresh your browser:**
- Windows/Linux: `Ctrl + Shift + R`  
- Mac: `Cmd + Shift + R`

## Test

1. Open AI Assistant
2. Select a machine
3. Should see: "Selected machine: [name] ([model])"

## Why This Works

Production serves pre-built static files. The container rebuild includes the latest translation files in the build.

## Files

- `rebuild_frontend_production.sh` - Rebuild script (ready to run)
- `TRANSLATION_FIX_PRODUCTION_SIMPLE.md` - Full documentation
