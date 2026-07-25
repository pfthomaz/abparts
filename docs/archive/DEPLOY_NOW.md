# Deploy AI Assistant to Production - Quick Start

## On Production Server (~/abparts directory)

### Step 1: Deploy
```bash
./deploy_ai_assistant_to_production.sh
```

This will:
- Fix database schema (troubleshooting_steps table)
- Pull latest code (translation fixes + new icon)
- Rebuild frontend
- Restart containers
- Verify services

**Time: ~3-5 minutes**

### Step 2: Verify
```bash
./verify_ai_assistant_production.sh
```

This checks:
- Database tables exist
- Schema is correct
- Containers are running
- Services are healthy

### Step 3: Test Manually

1. Open your ABParts application
2. Login: `dthomaz` / `amFT1999!`
3. Click AI Assistant icon (bottom-right)
4. **Check icon**: Should see AutoBoss machine (not computer)
5. **Check size**: Icon should be larger (24px)
6. Select a machine
7. Type: "Machine won't start"
8. **Check translations**: Should see "Step 1" (not "Step {number}")
9. **Check workflow**: Should see "It worked!" and "Didn't work" buttons
10. Click "It worked!" to complete session

## What's Being Deployed

### Visual Changes
- ✓ Custom AutoBoss machine icon (top-view with deck and arms)
- ✓ Icon 50% larger (more visible)

### Translation Fixes
- ✓ "Step 1" instead of "Step {number}"
- ✓ "5 min" instead of "{minutes} min"
- ✓ "85% success rate" instead of "{rate}% success rate"

### New Features
- ✓ Step-by-step troubleshooting workflow
- ✓ Interactive feedback ("It worked!" / "Didn't work")
- ✓ Learning system (improves over time)
- ✓ Machine-aware guidance

## If Something Goes Wrong

```bash
# Check logs
docker compose logs ai_assistant

# Check database
docker compose exec db psql -U abparts_user -d abparts_prod

# Restart services
docker compose restart web ai_assistant
```

## Files on Production Server

- `fix_troubleshooting_steps_production.sql` - Database fix
- `deploy_ai_assistant_to_production.sh` - Deployment script
- `verify_ai_assistant_production.sh` - Verification script
- `AI_ASSISTANT_PRODUCTION_DEPLOYMENT_READY.md` - Full documentation

## That's It!

The deployment is automated and safe. The script will stop if anything fails.
