-- Add missing columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS invited_by_user_id UUID;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_expires_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS pending_email VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS preferred_language VARCHAR(5) DEFAULT 'en';
ALTER TABLE users ADD COLUMN IF NOT EXISTS preferred_country VARCHAR(3);
ALTER TABLE users ADD COLUMN IF NOT EXISTS localization_preferences TEXT;

-- Add foreign key constraint for invited_by_user_id
ALTER TABLE users ADD CONSTRAINT fk_users_invited_by_user_id 
FOREIGN KEY (invited_by_user_id) REFERENCES users(id);