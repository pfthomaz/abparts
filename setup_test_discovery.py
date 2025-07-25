#!/usr/bin/env python3
"""
Setup script for test discovery in Kiro IDE
This script prepares the environment for local test discovery
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Set up environment variables for test discovery"""
    # Load local environment variables using existing PostgreSQL test database
    env_vars = {
        'DATABASE_URL': 'postgresql://abparts_user:abparts_pass@localhost:5432/abparts_test',
        'REDIS_URL': 'redis://localhost:6379/1',
        'ENVIRONMENT': 'testing',
        'TESTING': 'true',
        'SECRET_KEY': 'test-secret-key-for-discovery-only',
        'ACCESS_TOKEN_EXPIRE_MINUTES': '30',
        'SMTP_SERVER': 'smtp.example.com',
        'SMTP_PORT': '587',
        'SMTP_USERNAME': 'test@example.com',
        'SMTP_PASSWORD': 'test_password',
        'FROM_EMAIL': 'test@abparts.com',
        'BASE_URL': 'http://localhost:8000',
        'CORS_ALLOWED_ORIGINS': 'http://localhost:3000,http://127.0.0.1:3000',
        'CORS_ALLOW_CREDENTIALS': 'true',
        'PYTHONPATH': str(Path(__file__).parent / 'backend')
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value

def main():
    """Main setup function"""
    setup_environment()
    
    # Add backend to Python path
    backend_path = Path(__file__).parent / 'backend'
    if str(backend_path) not in sys.path:
        sys.path.insert(0, str(backend_path))
    
    print("Environment set up for test discovery")
    return True

if __name__ == "__main__":
    main()