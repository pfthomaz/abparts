"""
Pytest plugin for Docker-based test execution
This plugin allows pytest to discover tests locally but run them in Docker
"""

import os
import subprocess
import sys
from pathlib import Path

def pytest_configure(config):
    """Configure pytest for Docker execution"""
    # Set up environment for test discovery
    os.environ.update({
        'DATABASE_URL': 'sqlite:///./test_discovery.db',
        'REDIS_URL': 'redis://localhost:6379/0',
        'ENVIRONMENT': 'test_discovery',
        'TESTING': 'true',
        'SECRET_KEY': 'test-secret-key-for-discovery-only',
        'SKIP_DB_INIT': 'true'
    })

def pytest_collection_modifyitems(config, items):
    """Modify test items to indicate they should run in Docker"""
    if not config.getoption("--collect-only"):
        # Add a marker to indicate these tests should run in Docker
        import pytest
        docker_marker = pytest.mark.skip(reason="Use 'python test-runner.py' to run tests in Docker")
        for item in items:
            item.add_marker(docker_marker)

def pytest_runtest_setup(item):
    """Setup for running individual tests"""
    # This will be called for each test, but we'll skip them with the marker above
    pass