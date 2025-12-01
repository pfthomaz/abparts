#!/usr/bin/env python3
"""
Preparation script for scalability testing.
Ensures Docker services are running and database is ready.
"""

import subprocess
import time
import sys
import requests

def start_docker_services():
    """Start Docker services if not running."""
    print("🐳 Starting Docker services...")
    
    try:
        # Start services in detached mode
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            check=True,
            capture_output=True,
            text=True
        )
        
        print("✅ Docker services started")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Docker services: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    except FileNotFoundError:
        print("❌ docker-compose not found. Please install Docker and docker-compose")
        return False

def wait_for_database():
    """Wait for database to be ready."""
    print("🗄️  Waiting for database to be ready...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            result = subprocess.run([
                "docker-compose", "exec", "-T", "db", 
                "pg_isready", "-U", "abparts_user", "-d", "abparts_dev"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Database is ready")
                return True
                
        except subprocess.TimeoutExpired:
            pass
        except Exception as e:
            print(f"   Database check attempt {attempt + 1}/{max_attempts} failed: {e}")
        
        time.sleep(2)
    
    print("❌ Database not ready after 60 seconds")
    return False

def wait_for_api():
    """Wait for API to be ready."""
    print("🔧 Waiting for API to be ready...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/docs", timeout=5)
            if response.status_code == 200:
                print("✅ API is ready")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"   API check attempt {attempt + 1}/{max_attempts}")
        time.sleep(2)
    
    print("❌ API not ready after 60 seconds")
    return False

def wait_for_frontend():
    """Wait for frontend to be ready."""
    print("🌐 Waiting for frontend to be ready...")
    
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            if response.status_code in [200, 404]:  # 404 is OK for React dev server
                print("✅ Frontend is ready")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"   Frontend check attempt {attempt + 1}/{max_attempts}")
        time.sleep(2)
    
    print("❌ Frontend not ready after 60 seconds")
    return False

def run_database_migrations():
    """Run database migrations to ensure schema is up to date."""
    print("📊 Running database migrations...")
    
    try:
        result = subprocess.run([
            "docker-compose", "exec", "-T", "api",
            "alembic", "upgrade", "head"
        ], check=True, capture_output=True, text=True)
        
        print("✅ Database migrations completed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Database migrations failed: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def verify_superadmin_user():
    """Verify superadmin user exists."""
    print("👤 Verifying superadmin user...")
    
    try:
        # Try to authenticate with superadmin credentials
        response = requests.post(
            "http://localhost:8000/token",
            data={
                "username": "superadmin",
                "password": "superadmin"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Superadmin user verified")
            return True
        else:
            print(f"❌ Superadmin authentication failed: {response.status_code}")
            print("Response:", response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to verify superadmin user: {e}")
        return False

def check_system_resources():
    """Check system resources for testing."""
    print("💻 Checking system resources...")
    
    try:
        # Check available disk space
        result = subprocess.run(["df", "-h", "."], capture_output=True, text=True)
        print("   Disk space:")
        print("  ", result.stdout.strip().split('\n')[-1])
        
        # Check memory usage
        try:
            result = subprocess.run(["free", "-h"], capture_output=True, text=True)
            print("   Memory usage:")
            for line in result.stdout.strip().split('\n')[1:2]:  # Just the memory line
                print("  ", line)
        except FileNotFoundError:
            print("   Memory check not available on this system")
        
        print("✅ System resources checked")
        return True
        
    except Exception as e:
        print(f"⚠️  System resource check failed: {e}")
        return True  # Non-critical failure

def main():
    """Main preparation function."""
    print("🚀 Preparing ABParts System for Scalability Testing")
    print("="*60)
    
    steps = [
        ("Starting Docker services", start_docker_services),
        ("Waiting for database", wait_for_database),
        ("Running database migrations", run_database_migrations),
        ("Waiting for API", wait_for_api),
        ("Waiting for frontend", wait_for_frontend),
        ("Verifying superadmin user", verify_superadmin_user),
        ("Checking system resources", check_system_resources)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Preparation failed at: {step_name}")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ System preparation completed successfully!")
    print("🚀 Ready to run scalability tests")
    print("="*60)
    print("\nNext steps:")
    print("1. Run: python run_scalability_validation.py")
    print("2. Or run individual tests:")
    print("   - Backend: python test_large_dataset_scalability.py")
    print("   - Frontend: cd frontend && node test_frontend_scalability.js")

if __name__ == "__main__":
    main()