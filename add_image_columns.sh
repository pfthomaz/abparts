#!/bin/bash

echo "Running migration to add image columns..."

docker-compose exec -T db psql -U abparts_user -d abparts_dev << 'EOF'
-- Add logo_url to organizations table
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS logo_url VARCHAR(500);

-- Add profile_photo_url to users table  
ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_photo_url VARCHAR(500);

-- Verify columns were added
\d organizations
\d users
EOF

echo "Migration complete!"
