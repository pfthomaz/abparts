#!/usr/bin/env python3
"""
Create a test user with known password
"""
import sys
sys.path.insert(0, 'backend')

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Generate hash for "testpass123"
password = "testpass123"
hashed = pwd_context.hash(password)

print(f"Password: {password}")
print(f"Hash: {hashed}")
print("\nSQL to create test user:")
print(f"""
INSERT INTO users (id, organization_id, username, password_hash, email, name, role, user_status)
VALUES (
    gen_random_uuid(),
    (SELECT id FROM organizations WHERE name = 'BossServ LLC' LIMIT 1),
    'testuser',
    '{hashed}',
    'testuser@test.com',
    'Test User',
    'super_admin',
    'active'
);
""")
