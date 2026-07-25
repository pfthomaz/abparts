#!/bin/bash

echo "🔧 Setting Language Directly in Database"
echo "========================================"
echo ""

# Show all users
echo "Current users:"
docker-compose exec -T db psql -U abparts_user -d abparts_dev -c "SELECT id, username, email, preferred_language FROM users ORDER BY username;"

echo ""
read -p "Enter the username to update: " USERNAME

if [ -z "$USERNAME" ]; then
    echo "❌ Username cannot be empty"
    exit 1
fi

echo ""
echo "Setting preferred_language to 'el' (Greek) for user: $USERNAME"
echo ""

# Update the language
docker-compose exec -T db psql -U abparts_user -d abparts_dev << EOF
UPDATE users SET preferred_language = 'el' WHERE username = '$USERNAME';
SELECT username, email, preferred_language FROM users WHERE username = '$USERNAME';
EOF

echo ""
echo "✅ Done!"
echo ""
echo "Now:"
echo "1. Logout from the app"
echo "2. Login again as '$USERNAME'"
echo "3. Open browser console (F12)"
echo "4. Look for: 🌍 Localization: User preferred_language: el"
echo "5. The UI should be in Greek!"
