#!/bin/bash

# Script to run the protocol translation migration

echo "🚀 Starting Protocol Translation Migration..."
echo "============================================="

# Navigate to backend directory
cd backend

# Check if alembic is available
if ! command -v alembic &> /dev/null; then
    echo "❌ Alembic not found. Please install it first:"
    echo "   pip install alembic"
    exit 1
fi

# Show current migration status
echo "📋 Current migration status:"
alembic current

echo ""
echo "📦 Available migrations:"
alembic history

echo ""
echo "🔄 Running migration to add protocol translations..."

# Run the migration
alembic upgrade head

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration completed successfully!"
    echo ""
    echo "📊 New migration status:"
    alembic current
    echo ""
    echo "🎉 Protocol translation system is now ready!"
    echo ""
    echo "Next steps:"
    echo "1. Restart your FastAPI server"
    echo "2. Test the new translation endpoints"
    echo "3. Start creating translations for your protocols"
else
    echo ""
    echo "❌ Migration failed!"
    echo "Please check the error messages above and fix any issues."
    exit 1
fi