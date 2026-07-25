#!/bin/bash

# Diagnose Translation Issue in Production
# This script checks various aspects of the translation system

echo "========================================="
echo "Translation System Diagnostics"
echo "========================================="
echo ""

# Check 1: Translation files exist
echo "Check 1: Translation files in container..."
docker compose exec web ls -lh /app/src/locales/

echo ""

# Check 2: Check en.json content for AI Assistant keys
echo "Check 2: AI Assistant translation keys in en.json..."
docker compose exec web grep -A 2 '"aiAssistant"' /app/src/locales/en.json | head -20

echo ""

# Check 3: Check machineSelected key specifically
echo "Check 3: machineSelected key..."
docker compose exec web grep "machineSelected" /app/src/locales/en.json

echo ""

# Check 4: Check if build directory exists
echo "Check 4: Frontend build directory..."
docker compose exec web ls -lh /app/build/ | head -10

echo ""

# Check 5: Check build timestamp
echo "Check 5: Build timestamp..."
docker compose exec web stat /app/build/index.html | grep Modify

echo ""

# Check 6: Check if locales are in build
echo "Check 6: Checking if locales are bundled in build..."
docker compose exec web find /app/build -name "*.js" -exec grep -l "machineSelected" {} \; | head -5

echo ""

# Check 7: Check useTranslation hook
echo "Check 7: useTranslation hook exists..."
docker compose exec web ls -lh /app/src/hooks/useTranslation.js

echo ""

# Check 8: Check LocalizationContext
echo "Check 8: LocalizationContext exists..."
docker compose exec web ls -lh /app/src/contexts/LocalizationContext.js

echo ""

# Check 9: Container status
echo "Check 9: Container status..."
docker compose ps web

echo ""

# Check 10: Recent web container logs
echo "Check 10: Recent web container logs..."
docker compose logs web --tail=30

echo ""
echo "========================================="
echo "Diagnostics Complete"
echo "========================================="
