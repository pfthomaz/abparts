#!/bin/bash
# resolve_migration_conflict.sh
# Resolve the migration file conflict by removing the old backup file

echo "=== Resolving Migration File Conflict ==="
echo ""

echo "Current git status:"
git status

echo ""
echo "The conflict is about an old migration file that should be deleted."
echo "We want to keep the clean state (no old migration files)."
echo ""

# Remove the conflicting backup file
echo "Removing the old migration backup file..."
rm -f backend/alembic/versions/add_protocol_translations_06.py.backup

echo "✅ Removed conflicting file"

# Add the deletion to git
echo "Staging the file deletion..."
git add backend/alembic/versions/add_protocol_translations_06.py.backup

echo "✅ Staged file deletion"

# Complete the merge
echo "Completing the merge..."
git commit -m "Resolve migration conflict: remove old migration backup file

- Removed add_protocol_translations_06.py.backup as part of migration reset
- This aligns with the new baseline migration approach"

echo "✅ Merge completed successfully!"

echo ""
echo "Final status:"
git status

echo ""
echo "Recent commits:"
git log --oneline -3