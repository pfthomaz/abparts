#!/bin/bash

# Script to run the preferred_language migration

echo "🌍 Running preferred_language migration..."
echo "=========================================="

# Run the migration
docker-compose exec api alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migration completed successfully!"
    echo ""
    echo "The preferred_language field has been added to the users table."
    echo "Users can now set their preferred language in the user form."
    echo ""
    echo "Supported languages:"
    echo "  - en (English)"
    echo "  - el (Greek - Ελληνικά)"
    echo "  - ar (Arabic - العربية)"
    echo "  - es (Spanish - Español)"
    echo ""
    echo "See docs/LOCALIZATION_GUIDE.md for more information."
else
    echo "❌ Migration failed!"
    echo "Please check the error messages above."
    exit 1
fi
