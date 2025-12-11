# Production Fixes - Cheat Sheet

## The Three Issues (All Resolved)

| Issue | Status | Solution |
|-------|--------|----------|
| Migration mess | ✅ Fixed | `./reset_migrations_clean.sh` |
| Web container | ✅ Already OK | Use `docker compose up -d` |
| CORS errors | ✅ Already OK | Configure via `.env` |

## Quick Commands

### First Time Setup
```bash
# 1. Make scripts executable
chmod +x *.sh

# 2. Create .env from template
cp .env.production.example .env
nano .env  # Edit with your values

# 3. Reset migrations (one time)
./reset_migrations_clean.sh

# 4. Deploy
./deploy_production_clean.sh
```

### Regular Deployment
```bash
./deploy_production_clean.sh
```

### Verify Setup
```bash
./verify_production_setup.sh
```

### View Logs
```bash
docker compose logs -f api
docker compose logs -f web
```

### Restart Services
```bash
docker compose restart api
docker compose restart web
```

### Check Health
```bash
curl https://abparts.oraseas.com/api/health
docker compose ps
```

## Critical .env Settings

```bash
ENVIRONMENT=production
CORS_ALLOWED_ORIGINS=https://abparts.oraseas.com
CORS_ALLOW_CREDENTIALS=true
REACT_APP_API_BASE_URL=/api
SECRET_KEY=<32+ char random string>
JWT_SECRET_KEY=<32+ char random string>
```

Generate keys:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Troubleshooting

### CORS Error
```bash
grep CORS .env  # Check config
docker compose restart api  # Restart
docker compose logs api | grep CORS  # Verify
```

### Web Not Starting
```bash
docker compose logs web  # Check error
docker compose build --no-cache web  # Rebuild
docker compose up -d web  # Start
```

### Database Error
```bash
docker compose exec db psql -U abparts_user -d abparts_prod -c "SELECT * FROM alembic_version;"
./reset_migrations_clean.sh  # If needed
```

## Files Reference

| File | Purpose |
|------|---------|
| `reset_migrations_clean.sh` | Reset migrations to baseline |
| `deploy_production_clean.sh` | Full deployment automation |
| `verify_production_setup.sh` | Check configuration |
| `.env.production.example` | Environment template |
| `README_PRODUCTION_FIXES.md` | Complete documentation |

## That's It!

Everything is automated. Just run:
```bash
./deploy_production_clean.sh
```
