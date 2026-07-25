# Project Cleanup Plan

## Current Situation

Your root directory has accumulated ~100+ files including:
- Old deployment scripts
- Temporary fix scripts
- Historical documentation
- Test scripts
- SQL files

## Proposed Structure

```
abparts/
├── README.md                    # Main project documentation
├── docker-compose.yml           # Docker configuration
├── docker-compose.prod.yml      # Production Docker config
├── .env.development             # Dev environment
├── .env.production.example      # Prod environment template
├── .gitignore
│
├── backend/                     # Backend source code
├── frontend/                    # Frontend source code
├── init_db/                     # Database initialization
├── .kiro/                       # Kiro AI configuration
│
├── docs/                        # All documentation
│   ├── README.md
│   ├── archive/                 # Old/completed docs
│   ├── deployment/              # Deployment guides
│   ├── features/                # Feature specifications
│   └── architecture/            # System design docs
│
└── scripts/                     # All scripts
    ├── README.md
    ├── archive/                 # Old/deprecated scripts
    ├── deployment/              # Production deployment
    ├── maintenance/             # Operations & maintenance
    ├── testing/                 # Test & diagnostic scripts
    └── sql/                     # SQL migration files
```

## What Gets Moved

### Documentation → `docs/`

**To `docs/archive/`** (completed/old):
- SESSION_SUMMARY_*.md
- TOMORROW_*.md
- *_COMPLETE.md
- *_FIXES.md
- FIX_NOW.md
- MANUAL_FIXES.md
- QUICK_START_*.md

**To `docs/deployment/`**:
- DEPLOYMENT_*.md
- PRODUCTION_*.md
- HETZNER_*.md
- HTTPS_*.md
- DOCKER_*.md
- MIGRATION_*.md
- ALEMBIC_*.md

**To `docs/features/`**:
- *_FEATURE_*.md
- *_IMPLEMENTATION*.md
- CUSTOMER_ORDER_*.md
- MACHINE_HOURS_*.md
- STOCK_*.md
- USER_GUIDE_*.md

**To `docs/architecture/`**:
- *_ARCHITECTURE*.md
- *_SYSTEM_*.md
- *_EXPLAINED.md
- *_ANALYSIS.md
- INVENTORY_*.md
- DATABASE_*.md

### Scripts → `scripts/`

**To `scripts/archive/`** (old/deprecated):
- fix_*.sh (old fix scripts)
- setup_*.sh (old setup scripts)
- complete_*.sh
- cleanup_*.sh (except this one!)
- safe_*.sh

**To `scripts/deployment/`**:
- deploy_*.sh
- reset_migrations_*.sh
- pre_*.sh

**To `scripts/maintenance/`**:
- restart_*.sh
- rebuild_*.sh
- verify_*.sh
- check_*.sh

**To `scripts/testing/`**:
- test_*.py
- diagnose_*.py
- migrate_*.py

**To `scripts/sql/`**:
- *.sql

## What Stays in Root

- README.md
- docker-compose.yml
- docker-compose.prod.yml
- .env files
- .gitignore
- nginx-native-setup.conf
- Source directories (backend/, frontend/, etc.)

## Benefits

1. **Cleaner root directory** - Easy to find important files
2. **Better organization** - Logical grouping of related files
3. **Easier navigation** - Know where to look for things
4. **Historical context** - Old files archived, not deleted
5. **Professional structure** - Standard project layout

## How to Execute

```bash
# Make the cleanup script executable
chmod +x cleanup_project.sh

# Run the cleanup
./cleanup_project.sh

# Review the results
ls -la docs/
ls -la scripts/

# Optional: Delete archives if you don't need them
rm -rf docs/archive/
rm -rf scripts/archive/
```

## After Cleanup

You can safely delete the archive directories if you don't need the old files:

```bash
# Review what's in archives first
ls docs/archive/
ls scripts/archive/

# Delete if not needed
rm -rf docs/archive/
rm -rf scripts/archive/
```

## Recommendation

**Yes, definitely clean up!** Your project will be much easier to navigate and maintain. The cleanup script:
- ✓ Preserves all files (moves, doesn't delete)
- ✓ Creates logical organization
- ✓ Adds README files for navigation
- ✓ Can be reversed if needed

Run it now and enjoy a cleaner workspace!
