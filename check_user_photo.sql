-- Check if the profile photo was saved to the database
SELECT 
    id,
    username,
    name,
    email,
    profile_photo_url,
    updated_at
FROM users
WHERE username = 'jamie';
