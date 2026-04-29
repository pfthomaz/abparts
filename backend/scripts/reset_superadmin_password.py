#!/usr/bin/env python3
"""
Reset a super admin (or any user) password in the local database.

Usage:
  python backend/scripts/reset_superadmin_password.py --username superadmin
  python backend/scripts/reset_superadmin_password.py --email user@example.com
  DATABASE_URL=postgresql://... python backend/scripts/reset_superadmin_password.py --username superadmin

If --password is omitted, you will be prompted securely.
"""

import argparse
import os
from getpass import getpass

from passlib.context import CryptContext
from sqlalchemy import create_engine, text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reset a local user password.")
    parser.add_argument("--username", help="Username to reset (default: superadmin)")
    parser.add_argument("--email", help="Email to reset")
    parser.add_argument("--password", help="New password (if omitted, prompted securely)")
    parser.add_argument("--database-url", help="Database URL (overrides DATABASE_URL env)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    identifier_username = args.username or "superadmin"
    identifier_email = args.email

    if not identifier_username and not identifier_email:
        print("❌ Provide --username or --email")
        return 1

    database_url = args.database_url or os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL is not set. Provide --database-url or set DATABASE_URL.")
        return 1

    new_password = args.password or getpass("New password: ")
    if not new_password:
        print("❌ Password cannot be empty")
        return 1

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    password_hash = pwd_context.hash(new_password)

    engine = create_engine(database_url, pool_pre_ping=True)
    query = """
        UPDATE users
        SET
            password_hash = :password_hash,
            password_reset_token = NULL,
            password_reset_expires_at = NULL,
            failed_login_attempts = 0,
            locked_until = NULL,
            is_active = true,
            updated_at = CURRENT_TIMESTAMP
        WHERE
            {filter_clause}
        RETURNING id, username, email
    """

    if identifier_email:
        filter_clause = "email = :identifier_email"
    else:
        filter_clause = "username = :identifier_username"

    try:
        with engine.begin() as conn:
            result = conn.execute(
                text(query.format(filter_clause=filter_clause)),
                {
                    "password_hash": password_hash,
                    "identifier_email": identifier_email,
                    "identifier_username": identifier_username,
                },
            ).fetchone()

        if not result:
            who = identifier_email or identifier_username
            print(f"❌ User not found for {who}")
            return 1

        label = result.email or result.username
        print(f"✅ Password reset for {label}")
        return 0
    except Exception as exc:
        print(f"❌ Failed to reset password: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
