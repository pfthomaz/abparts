#!/usr/bin/env python3
"""
Simple test runner for ABParts application
This script helps run tests in the Docker environment from your IDE
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True,
            check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def check_docker():
    """Check if Docker is running"""
    returncode, _, _ = run_command("docker info")
    return returncode == 0

def check_api_container():
    """Check if API container is running"""
    returncode, stdout, _ = run_command("docker ps")
    return "abparts_api" in stdout

def main():
    """Main test runner function"""
    if not check_docker():
        print("❌ Docker is not running. Please start Docker and try again.")
        sys.exit(1)
    
    # Default to running in API container if it's available
    if check_api_container():
        print("🐳 Running tests in existing API container...")
        test_cmd = "docker-compose exec api python -m pytest"
    else:
        print("🐳 Starting test environment...")
        # Start test database first
        run_command("docker-compose --profile testing up -d test_db redis")
        test_cmd = "docker-compose --profile testing run --rm test pytest"
    
    # Add any command line arguments passed to this script
    if len(sys.argv) > 1:
        test_args = " ".join(sys.argv[1:])
        test_cmd += f" {test_args}"
    else:
        # Default: run all tests with verbose output
        test_cmd += " -v"
    
    print(f"🧪 Running: {test_cmd}")
    
    # Run the tests
    returncode, stdout, stderr = run_command(test_cmd)
    
    # Print output
    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)
    
    # Cleanup if we started test environment
    if not check_api_container():
        print("🧹 Cleaning up test environment...")
        run_command("docker-compose --profile testing down")
    
    sys.exit(returncode)

if __name__ == "__main__":
    main()