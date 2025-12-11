#!/usr/bin/env python3
"""
Kiro IDE pytest wrapper
This script provides pytest-compatible interface for Kiro IDE while using Docker for execution
"""

import sys
import os
import subprocess
import json
from pathlib import Path

def setup_environment():
    """Set up environment for test discovery"""
    os.environ.update({
        'DATABASE_URL': 'sqlite:///./test_discovery.db',
        'REDIS_URL': 'redis://localhost:6379/0',
        'ENVIRONMENT': 'test_discovery',
        'TESTING': 'true',
        'SECRET_KEY': 'test-secret-key-for-discovery-only',
        'SKIP_DB_INIT': 'true'
    })

def is_collect_only():
    """Check if this is a test collection request"""
    return '--collect-only' in sys.argv

def run_test_discovery():
    """Run test discovery using our Python script"""
    try:
        # Use our test-discovery.py script
        result = subprocess.run([
            sys.executable, 'test-discovery.py'
        ] + sys.argv[1:], 
        capture_output=True, 
        text=True, 
        timeout=30
        )
        
        print(result.stdout, end='')
        if result.stderr:
            print(result.stderr, file=sys.stderr, end='')
        
        return result.returncode
    except subprocess.TimeoutExpired:
        print("Test discovery timed out", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error during test discovery: {e}", file=sys.stderr)
        return 1

def run_docker_tests():
    """Run tests in Docker environment"""
    print("Tests should be run in Docker environment.", file=sys.stderr)
    print("Use: python test-runner.py", file=sys.stderr)
    return 1

def main():
    """Main entry point"""
    setup_environment()
    
    if is_collect_only():
        return run_test_discovery()
    else:
        return run_docker_tests()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)