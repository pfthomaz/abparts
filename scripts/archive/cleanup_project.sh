#!/bin/bash

echo "========================================="
echo "ABParts Project Cleanup"
echo "========================================="
echo ""
echo "This will organize your project by:"
echo "1. Moving old documentation to docs/archive/"
echo "2. Moving old scripts to scripts/archive/"
echo "3. Keeping only current, useful files in root"
echo "4. Creating a clean project structure"
echo ""

read -p "Continue with cleanup? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Cancelled."
    exit 1
fi

# Create directory structure
echo ""
echo "Creating directory structure..."
mkdir -p docs/archive
mkdir -p docs/deployment
mkdir -p docs/features
mkdir -p docs/architecture
mkdir -p scripts/archive
mkdir -p scripts/deployment
mkdir -p scripts/maintenance
mkdir -p scripts/testing

echo "✓ Directories created"

# Move documentation files
echo ""
echo "Organizing documentation..."

# Archive old/completed docs
mv SESSION_SUMMARY_NOV26.md docs/archive/ 2>/dev/null || true
mv TOMORROW_*.md docs/archive/ 2>/dev/null || true
mv *_COMPLETE.md docs/archive/ 2>/dev/null || true
mv *_FIXES.md docs/archive/ 2>/dev/null || true
mv *_FIX.md docs/archive/ 2>/dev/null || true
mv QUICK_START_*.md docs/archive/ 2>/dev/null || true
mv FIX_NOW.md docs/archive/ 2>/dev/null || true
mv MANUAL_FIXES.md docs/archive/ 2>/dev/null || true
mv CORRECT_WORKFLOW.md docs/archive/ 2>/dev/null || true

# Move deployment docs to proper location
mv DEPLOYMENT_*.md docs/deployment/ 2>/dev/null || true
mv DEPLOY_*.md docs/deployment/ 2>/dev/null || true
mv PRODUCTION_*.md docs/deployment/ 2>/dev/null || true
mv HETZNER_*.md docs/deployment/ 2>/dev/null || true
mv HTTPS_*.md docs/deployment/ 2>/dev/null || true
mv DOCKER_*.md docs/deployment/ 2>/dev/null || true
mv MIGRATION_*.md docs/deployment/ 2>/dev/null || true
mv ALEMBIC_*.md docs/deployment/ 2>/dev/null || true
mv RESET_*.md docs/deployment/ 2>/dev/null || true

# Move feature docs
mv *_FEATURE_*.md docs/features/ 2>/dev/null || true
mv *_IMPLEMENTATION*.md docs/features/ 2>/dev/null || true
mv *_WORKFLOW*.md docs/features/ 2>/dev/null || true
mv CUSTOMER_ORDER_*.md docs/features/ 2>/dev/null || true
mv SHIPPED_BY_USER_*.md docs/features/ 2>/dev/null || true
mv MACHINE_HOURS_*.md docs/features/ 2>/dev/null || true
mv STOCK_*.md docs/features/ 2>/dev/null || true
mv USER_GUIDE_*.md docs/features/ 2>/dev/null || true
mv PROFILE_PHOTOS_*.md docs/features/ 2>/dev/null || true

# Move architecture docs
mv *_ARCHITECTURE*.md docs/architecture/ 2>/dev/null || true
mv *_SYSTEM_*.md docs/architecture/ 2>/dev/null || true
mv *_EXPLAINED.md docs/architecture/ 2>/dev/null || true
mv *_ANALYSIS.md docs/architecture/ 2>/dev/null || true
mv PARTS_WAREHOUSES_*.md docs/architecture/ 2>/dev/null || true
mv INVENTORY_*.md docs/architecture/ 2>/dev/null || true
mv DATABASE_*.md docs/architecture/ 2>/dev/null || true

# Keep important docs in root
# README.md stays
# .env files stay

echo "✓ Documentation organized"

# Move script files
echo ""
echo "Organizing scripts..."

# Archive old deployment scripts
mv fix_*.sh scripts/archive/ 2>/dev/null || true
mv setup_*.sh scripts/archive/ 2>/dev/null || true
mv complete_*.sh scripts/archive/ 2>/dev/null || true
mv cleanup_*.sh scripts/archive/ 2>/dev/null || true
mv safe_*.sh scripts/archive/ 2>/dev/null || true
mv switch_*.sh scripts/archive/ 2>/dev/null || true
mv production_cleanup.sh scripts/archive/ 2>/dev/null || true

# Move deployment scripts to proper location
mv deploy_*.sh scripts/deployment/ 2>/dev/null || true
mv reset_migrations_*.sh scripts/deployment/ 2>/dev/null || true
mv pre_*.sh scripts/deployment/ 2>/dev/null || true
mv run_migration_*.sh scripts/deployment/ 2>/dev/null || true

# Move maintenance scripts
mv restart_*.sh scripts/maintenance/ 2>/dev/null || true
mv rebuild_*.sh scripts/maintenance/ 2>/dev/null || true
mv verify_*.sh scripts/maintenance/ 2>/dev/null || true
mv check_*.sh scripts/maintenance/ 2>/dev/null || true

# Move test scripts
mv test_*.py scripts/testing/ 2>/dev/null || true
mv diagnose_*.py scripts/testing/ 2>/dev/null || true
mv migrate_*.py scripts/testing/ 2>/dev/null || true
mv find_*.py scripts/testing/ 2>/dev/null || true

# Move SQL files
mkdir -p scripts/sql
mv *.sql scripts/sql/ 2>/dev/null || true

echo "✓ Scripts organized"

# Create a README for the new structure
cat > docs/README.md << 'EOF'
# ABParts Documentation

## Directory Structure

- **archive/** - Old documentation and completed work
- **deployment/** - Deployment guides and procedures
- **features/** - Feature specifications and implementations
- **architecture/** - System architecture and design docs

## Current Documentation

See the main README.md in the project root for:
- Project overview
- Setup instructions
- Development workflow

## Finding Documentation

- Deployment procedures → `deployment/`
- Feature specs → `features/`
- System design → `architecture/`
- Historical context → `archive/`
EOF

cat > scripts/README.md << 'EOF'
# ABParts Scripts

## Directory Structure

- **archive/** - Old/deprecated scripts (kept for reference)
- **deployment/** - Production deployment scripts
- **maintenance/** - System maintenance and operations
- **testing/** - Test and diagnostic scripts
- **sql/** - SQL migration and fix scripts

## Active Scripts

### Deployment
- `deployment/deploy_with_alembic_production.sh` - Deploy with Alembic migrations
- `deployment/deploy_part_usage_fix_production.sh` - Deploy part usage fix

### Maintenance
- `maintenance/restart_api.sh` - Restart API service
- `maintenance/rebuild_frontend.sh` - Rebuild frontend

### Testing
- `testing/test_*.py` - Various test scripts
- `testing/diagnose_*.py` - Diagnostic tools

## Usage

Always run scripts from the project root directory:
```bash
./scripts/deployment/script_name.sh
```
EOF

echo "✓ README files created"

# Summary
echo ""
echo "========================================="
echo "✓ Cleanup Complete!"
echo "========================================="
echo ""
echo "New structure:"
echo "  docs/"
echo "    ├── archive/          (old docs)"
echo "    ├── deployment/       (deployment guides)"
echo "    ├── features/         (feature specs)"
echo "    ├── architecture/     (system design)"
echo "    └── README.md"
echo ""
echo "  scripts/"
echo "    ├── archive/          (old scripts)"
echo "    ├── deployment/       (deploy scripts)"
echo "    ├── maintenance/      (ops scripts)"
echo "    ├── testing/          (test scripts)"
echo "    ├── sql/              (SQL files)"
echo "    └── README.md"
echo ""
echo "Root directory now contains only:"
echo "  - Core config files (.env, docker-compose.yml, etc.)"
echo "  - README.md"
echo "  - Source code directories (backend/, frontend/, etc.)"
echo ""
echo "Next steps:"
echo "  1. Review the organized files"
echo "  2. Delete scripts/archive/ if you don't need old scripts"
echo "  3. Delete docs/archive/ if you don't need old docs"
echo "  4. Update .gitignore if needed"
echo ""
