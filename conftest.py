"""
Local pytest configuration for test discovery in Kiro IDE
This file provides minimal fixtures for test discovery without requiring Docker
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock
from typing import Generator, Dict, Any

# Set up environment for test discovery
def setup_test_discovery_env():
    """Set up environment variables for test discovery"""
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
        'CORS_ALLOW_CREDENTIALS': 'true'
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value

# Set up environment before importing anything else
setup_test_discovery_env()

# Add backend to Python path
backend_path = Path(__file__).parent / 'backend'
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

# Mock fixtures for test discovery - these won't actually run tests
@pytest.fixture(scope="function")
def db_session():
    """Mock database session for test discovery"""
    return MagicMock()

@pytest.fixture(scope="function") 
def client():
    """Mock test client for test discovery"""
    return MagicMock()

@pytest.fixture(scope="function")
def test_organizations():
    """Mock test organizations for test discovery"""
    return {}

@pytest.fixture(scope="function")
def test_users():
    """Mock test users for test discovery"""
    return {}

@pytest.fixture(scope="function")
def test_warehouses():
    """Mock test warehouses for test discovery"""
    return {}

@pytest.fixture(scope="function")
def test_parts():
    """Mock test parts for test discovery"""
    return {}

@pytest.fixture(scope="function")
def test_machines():
    """Mock test machines for test discovery"""
    return {}

@pytest.fixture(scope="function")
def test_inventory():
    """Mock test inventory for test discovery"""
    return {}

@pytest.fixture(scope="function")
def auth_headers():
    """Mock auth headers for test discovery"""
    return {}

@pytest.fixture(scope="function")
def performance_test_data():
    """Mock performance test data for test discovery"""
    return {}

# Configure pytest to skip actual test execution when running locally
def pytest_configure(config):
    """Configure pytest for local test discovery"""
    if not config.getoption("--collect-only"):
        # Add a marker to skip tests when not in Docker
        config.addinivalue_line(
            "markers", "docker_only: mark test to run only in Docker environment"
        )

def pytest_collection_modifyitems(config, items):
    """Modify test items during collection"""
    if not config.getoption("--collect-only"):
        # Mark all tests to be skipped when running locally (not in Docker)
        skip_local = pytest.mark.skip(reason="Test should run in Docker environment - use 'python test-runner.py' to execute")
        for item in items:
            item.add_marker(skip_local)