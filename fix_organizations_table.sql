-- Add missing country column to organizations table
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS country VARCHAR(3);