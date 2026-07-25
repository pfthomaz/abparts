#!/bin/bash

# Script to help migrate components to use translations
# This will show you which files need migration

echo "🌍 Translation Migration Helper"
echo "================================"
echo ""
echo "Searching for hardcoded strings that should be translated..."
echo ""

# Common patterns to look for
patterns=(
  "Save"
  "Cancel"
  "Delete"
  "Edit"
  "Add"
  "Create"
  "Update"
  "Dashboard"
  "Organizations"
  "Users"
  "Parts"
  "Warehouses"
  "Machines"
  "Orders"
)

echo "Files that likely need translation:"
echo "-----------------------------------"

for pattern in "${patterns[@]}"; do
  echo ""
  echo "🔍 Looking for: '$pattern'"
  grep -r "\"$pattern\"" frontend/src/pages/ frontend/src/components/ 2>/dev/null | grep -v "node_modules" | grep -v ".test." | head -5
done

echo ""
echo "================================"
echo "✅ To migrate a component:"
echo "1. Add: import { useTranslation } from '../hooks/useTranslation';"
echo "2. Add: const { t } = useTranslation();"
echo "3. Replace: 'Save' with {t('common.save')}"
echo ""
echo "See HOW_TO_SEE_TRANSLATIONS.md for details"
