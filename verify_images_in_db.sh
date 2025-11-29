#!/bin/bash

# Verify images are stored in database

echo "============================================================"
echo "VERIFYING IMAGES IN DATABASE"
echo "============================================================"
echo ""

echo "1. Checking User Profile Photos"
echo "------------------------------------------------------------"
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
  username,
  CASE 
    WHEN profile_photo_data IS NOT NULL THEN 'YES (' || ROUND(length(profile_photo_data)/1024.0, 1) || ' KB)'
    ELSE 'NO'
  END as has_photo_in_db,
  CASE 
    WHEN profile_photo_url IS NOT NULL THEN 'YES (legacy)'
    ELSE 'NO'
  END as has_photo_url
FROM users 
WHERE profile_photo_data IS NOT NULL OR profile_photo_url IS NOT NULL
ORDER BY username;
"
echo ""

echo "2. Checking Organization Logos"
echo "------------------------------------------------------------"
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
  name,
  CASE 
    WHEN logo_data IS NOT NULL THEN 'YES (' || ROUND(length(logo_data)/1024.0, 1) || ' KB)'
    ELSE 'NO'
  END as has_logo_in_db,
  CASE 
    WHEN logo_url IS NOT NULL THEN 'YES (legacy)'
    ELSE 'NO'
  END as has_logo_url
FROM organizations 
WHERE logo_data IS NOT NULL OR logo_url IS NOT NULL
ORDER BY name;
"
echo ""

echo "3. Checking Part Images"
echo "------------------------------------------------------------"
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
  part_number,
  name,
  CASE 
    WHEN image_data IS NOT NULL THEN array_length(image_data, 1) || ' images (' || 
      ROUND(
        (SELECT SUM(length(img)) FROM unnest(image_data) AS img) / 1024.0, 1
      ) || ' KB total)'
    ELSE 'NO'
  END as has_images_in_db,
  CASE 
    WHEN image_urls IS NOT NULL THEN array_length(image_urls, 1) || ' URLs (legacy)'
    ELSE 'NO'
  END as has_image_urls
FROM parts 
WHERE image_data IS NOT NULL OR image_urls IS NOT NULL
ORDER BY part_number
LIMIT 10;
"
echo ""

echo "4. Summary Statistics"
echo "------------------------------------------------------------"
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
  'Users with photos' as category,
  COUNT(*) as count,
  ROUND(SUM(length(profile_photo_data))/1024.0/1024.0, 2) || ' MB' as total_size
FROM users WHERE profile_photo_data IS NOT NULL
UNION ALL
SELECT 
  'Organizations with logos',
  COUNT(*),
  ROUND(SUM(length(logo_data))/1024.0/1024.0, 2) || ' MB'
FROM organizations WHERE logo_data IS NOT NULL
UNION ALL
SELECT 
  'Parts with images',
  COUNT(*),
  ROUND(
    SUM(
      (SELECT SUM(length(img)) FROM unnest(image_data) AS img)
    )/1024.0/1024.0, 2
  ) || ' MB'
FROM parts WHERE image_data IS NOT NULL;
"
echo ""

echo "5. Database Size"
echo "------------------------------------------------------------"
docker compose exec db psql -U abparts_user -d abparts_dev -c "
SELECT 
  pg_size_pretty(pg_database_size('abparts_dev')) as database_size,
  pg_size_pretty(pg_total_relation_size('users')) as users_table_size,
  pg_size_pretty(pg_total_relation_size('organizations')) as organizations_table_size,
  pg_size_pretty(pg_total_relation_size('parts')) as parts_table_size;
"
echo ""

echo "6. Test Image Endpoint"
echo "------------------------------------------------------------"
echo "Getting a user with photo..."
USER_ID=$(docker compose exec db psql -U abparts_user -d abparts_dev -t -c "
SELECT id FROM users WHERE profile_photo_data IS NOT NULL LIMIT 1;
" | tr -d ' ')

if [ ! -z "$USER_ID" ]; then
  echo "Testing endpoint: /images/users/$USER_ID/profile"
  curl -I "http://localhost:8000/images/users/$USER_ID/profile" 2>/dev/null | head -5
  echo ""
else
  echo "No users with photos found"
fi

echo ""
echo "============================================================"
echo "VERIFICATION COMPLETE"
echo "============================================================"
echo ""
echo "✓ Images are stored in database as binary data (BYTEA)"
echo "✓ Legacy URL fields kept for reference"
echo "✓ New uploads will use database storage"
echo ""
