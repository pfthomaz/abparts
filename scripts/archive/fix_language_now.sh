#!/bin/bash

echo "🔧 Fixing Language Issue"
echo "========================"
echo ""

# Get the username
read -p "Enter your username: " USERNAME

if [ -z "$USERNAME" ]; then
    echo "❌ Username cannot be empty"
    exit 1
fi

echo ""
echo "Setting language to Greek (el) for user: $USERNAME"
echo ""

# Run SQL directly in the database
docker-compose exec -T db psql -U abparts_user -d abparts_dev << EOF
-- Check current value
SELECT username, email, preferred_language FROM users WHERE username = '$USERNAME';

-- Update to Greek
UPDATE users SET preferred_language = 'el' WHERE username = '$USERNAME';

-- Verify
SELECT username, email, preferred_language FROM users WHERE username = '$USERNAME';
EOF

echo ""
echo "✅ Done! Now:"
echo "1. Logout from the app"
echo "2. Login again"
echo "3. The UI should be in Greek!"
echo ""
echo "If still not working, check browser console (F12) for debug messages"
