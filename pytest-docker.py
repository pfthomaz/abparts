#!/usr/bin/env python3
"""
Docker-based pytest wrapper for Kiro IDE
This script allows Kiro IDE to run pytest tests in Docker containers
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def check_docker():
    """Check if Docker is running"""
    try:
        result = subprocess.run(
            ["docker", "info"], 
            capture_output=True, 
            text=True, 
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_api_container():
    """Check if API container is running"""
    try:
        result = subprocess.run(
            ["docker", "ps"], 
            capture_output=True, 
            text=True, 
            check=False
        )
        return "abparts_api" in result.stdout
    except FileNotFoundError:
        return False

def run_pytest_in_docker(args):
    """Run pytest in Docker container"""
    if not check_docker():
        print("Error: Docker is not running", file=sys.stderr)
        return 1
    
    # Convert local paths to container paths
    docker_args = []
    for arg in args:
        if arg.startswith("backend/tests/") or arg.startswith("backend\\tests\\"):
            # Convert Windows paths to Linux paths for Docker
            docker_arg = arg.replace("backend/", "").replace("backend\\", "").replace("\\", "/")
            docker_args.append(docker_arg)
        elif arg.startswith("tests/") or arg.startswith("tests\\"):
            # Already in correct format
            docker_arg = arg.replace("\\", "/")
            docker_args.append(docker_arg)
        else:
            docker_args.append(arg)
    
    # Choose Docker command based on container availability
    if check_api_container():
        cmd = ["docker-compose", "exec", "-T", "api", "python", "-m", "pytest"] + docker_args
    else:
        # Start test environment
        subprocess.run(
            ["docker-compose", "--profile", "testing", "up", "-d", "test_db", "redis"],
            capture_output=True
        )
        cmd = ["docker-compose", "--profile", "testing", "run", "--rm", "test", "pytest"] + docker_args
    
    # Run the command
    try:
        result = subprocess.run(cmd, cwd=os.getcwd())
        return result.returncode
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        print(f"Error running pytest: {e}", file=sys.stderr)
        return 1

def main():
    """Main entry point"""
    # Remove the script name from args
    pytest_args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    # If no args provided, run test discovery
    if not pytest_args:
        pytest_args = ["--collect-only", "-q"]
    
    return run_pytest_in_docker(pytest_args)

if __name__ == "__main__":
    sys.exit(main())