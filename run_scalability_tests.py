#!/usr/bin/env python3
"""
Script to run scalability tests in Docker environment.
Ensures services are running and executes comprehensive scalability validation.
"""

import subprocess
import time
import sys
import requests
from typing import List

def run_command(command: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result"""
    print(f"Running: {' '.join(command)}")
    try:
        result = subprocess.run(command, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"Error: {result.stderr}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        raise

def check_service_health(url: str, service_name: str, max_retries: int = 30) -> bool:
    """Check if a service is healthy"""
    print(f"Checking {service_name} health at {url}...")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"✓ {service_name} is healthy")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if attempt < max_retries - 1:
            print(f"Waiting for {service_name}... (attempt {attempt + 1}/{max_retries})")
            time.sleep(2)
    
    print(f"✗ {service_name} failed to become healthy")
    return False

def ensure_services_running():
    """Ensure all required services are running"""
    print("=== Ensuring Docker services are running ===")
    
    # Start services
    run_command(["docker-compose", "up", "-d"])
    
    # Wait for services to be healthy
    services_healthy = True
    
    # Check API service
    if not check_service_health("http://localhost:8000/docs", "Backend API"):
        services_healthy = False
    
    # Check frontend service
    if not check_service_health("http://localhost:3000", "Frontend"):
        services_healthy = False
    
    if not services_healthy:
        print("✗ Some services are not healthy. Check docker-compose logs.")
        sys.exit(1)
    
    print("✓ All services are healthy")

def run_database_migrations():
    """Run database migrations to ensure schema is up to date"""
    print("=== Running database migrations ===")
    
    try:
        run_command([
            "docker-compose", "exec", "-T", "api", 
            "alembic", "upgrade", "head"
        ])
        print("✓ Database migrations completed")
    except subprocess.CalledProcessError:
        print("✗ Database migrations failed")
        sys.exit(1)

def install_test_dependencies():
    """Install required Python packages for testing"""
    print("=== Installing test dependencies ===")
    
    try:
        run_command([
            "docker-compose", "exec", "-T", "api",
            "pip", "install", "requests"
        ])
        print("✓ Test dependencies installed")
    except subprocess.CalledProcessError:
        print("✗ Failed to install test dependencies")
        sys.exit(1)

def copy_test_file_to_container():
    """Copy the scalability test file to the API container"""
    print("=== Copying test file to container ===")
    
    try:
        run_command([
            "docker", "cp", 
            "test_comprehensive_scalability.py",
            "abparts-api-1:/app/test_comprehensive_scalability.py"
        ])
        print("✓ Test file copied to container")
    except subprocess.CalledProcessError:
        print("✗ Failed to copy test file to container")
        sys.exit(1)

def run_scalability_tests():
    """Execute the scalability tests inside the API container"""
    print("=== Running scalability tests ===")
    
    try:
        result = run_command([
            "docker-compose", "exec", "-T", "api",
            "python", "/app/test_comprehensive_scalability.py"
        ], check=False)
        
        if result.returncode == 0:
            print("✓ Scalability tests completed successfully")
            return True
        else:
            print("✗ Scalability tests failed")
            return False
            
    except Exception as e:
        print(f"✗ Error running scalability tests: {e}")
        return False

def show_service_logs():
    """Show recent logs from services for debugging"""
    print("=== Recent service logs ===")
    
    services = ["api", "web", "db"]
    
    for service in services:
        print(f"\n--- {service.upper()} LOGS ---")
        try:
            run_command([
                "docker-compose", "logs", "--tail=20", service
            ], check=False)
        except Exception as e:
            print(f"Could not get logs for {service}: {e}")

def main():
    """Main execution function"""
    print("ABParts Scalability Test Runner")
    print("=" * 50)
    
    try:
        # Step 1: Ensure services are running
        ensure_services_running()
        
        # Step 2: Run database migrations
        run_database_migrations()
        
        # Step 3: Install test dependencies
        install_test_dependencies()
        
        # Step 4: Copy test file to container
        copy_test_file_to_container()
        
        # Step 5: Run scalability tests
        success = run_scalability_tests()
        
        if success:
            print("\n🎉 Scalability validation completed successfully!")
            print("The system can handle large datasets efficiently.")
        else:
            print("\n❌ Scalability validation failed!")
            print("Check the test output above for details.")
            show_service_logs()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        show_service_logs()
        sys.exit(1)

if __name__ == "__main__":
    main()