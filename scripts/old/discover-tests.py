#!/usr/bin/env python3
"""
Test discovery script for Kiro IDE
This script discovers tests from the Docker environment and formats them for IDE consumption
"""

import subprocess
import sys
import json
import re
from pathlib import Path

def run_docker_command(cmd):
    """Run a Docker command and return the output"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def check_api_container():
    """Check if API container is running"""
    returncode, stdout, _ = run_docker_command(["docker", "ps"])
    return returncode == 0 and "abparts_api" in stdout

def discover_tests():
    """Discover tests using Docker"""
    if check_api_container():
        cmd = ["docker-compose", "exec", "-T", "api", "python", "-m", "pytest", "--collect-only", "-q"]
    else:
        print("Starting test environment for discovery...", file=sys.stderr)
        # Start test database
        run_docker_command(["docker-compose", "--profile", "testing", "up", "-d", "test_db", "redis"])
        cmd = ["docker-compose", "--profile", "testing", "run", "--rm", "test", "pytest", "--collect-only", "-q"]
    
    returncode, stdout, stderr = run_docker_command(cmd)
    
    if returncode != 0:
        print(f"Error discovering tests: {stderr}", file=sys.stderr)
        return []
    
    # Parse test names from output
    test_names = []
    for line in stdout.split('\n'):
        line = line.strip()
        if '::' in line and not line.startswith('=') and not line.startswith('-'):
            # Convert Docker paths back to local paths
            if line.startswith('tests/'):
                line = 'backend/' + line
            test_names.append(line)
    
    return test_names

def main():
    """Main entry point"""
    tests = discover_tests()
    
    if not tests:
        print("No tests discovered", file=sys.stderr)
        return 1
    
    # Output in a format that IDEs can understand
    for test in tests:
        print(test)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())