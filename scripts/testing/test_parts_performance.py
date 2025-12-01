#!/usr/bin/env python3
"""
Simple performance test execution script for parts system.
Allows running individual performance test categories or all tests.
"""

import os
import sys
import subprocess
import argparse
import time


def run_api_performance_tests():
    """Run API performance tests."""
    print("🚀 Running API Performance Tests...")
    
    cmd = [
        "docker-compose", "exec", "-T", "api",
        "python", "-m", "pytest",
        "tests/test_parts_api_performance.py",
        "-v", "-s"
    ]
    
    return subprocess.run(cmd)


def run_database_performance_tests():
    """Run database performance tests."""
    print("🗄️ Running Database Performance Tests...")
    
    cmd = [
        "docker-compose", "exec", "-T", "api",
        "python", "-m", "pytest",
        "tests/test_database_query_performance.py",
        "-v", "-s"
    ]
    
    return subprocess.run(cmd)


def run_frontend_performance_tests():
    """Run frontend performance tests."""
    print("🎨 Running Frontend Performance Tests...")
    
    cmd = [
        "docker-compose", "exec", "-T", "web",
        "npm", "test", "--",
        "src/tests/parts-performance.test.js",
        "--verbose", "--watchAll=false"
    ]
    
    return subprocess.run(cmd)


def run_integration_tests():
    """Run integration performance tests."""
    print("🔗 Running Integration Performance Tests...")
    
    cmd = [
        "docker-compose", "exec", "-T", "api",
        "python", "test_performance_optimizations.py"
    ]
    
    return subprocess.run(cmd)


def run_index_validation():
    """Run database index validation."""
    print("📊 Running Database Index Validation...")
    
    cmd = [
        "docker-compose", "exec", "-T", "api",
        "python", "test_parts_indexes.py"
    ]
    
    return subprocess.run(cmd)


def setup_test_data():
    """Setup test data for performance tests."""
    print("🔧 Setting up test data...")
    
    # Create test data using the API
    cmd = [
        "docker-compose", "exec", "-T", "api",
        "python", "-c", """
import sys
sys.path.append('/app')
from tests.test_data_generators import generate_large_parts_dataset
from app.database import SessionLocal

print('Generating test data...')
with SessionLocal() as db:
    dataset = generate_large_parts_dataset(db, parts_count=1000, include_inventory=True, include_transactions=False)
    print(f'Generated {len(dataset["parts"])} parts for testing')
"""
    ]
    
    return subprocess.run(cmd)


def check_environment():
    """Check if the test environment is ready."""
    print("🔍 Checking test environment...")
    
    # Check if services are running
    result = subprocess.run(["docker-compose", "ps"], capture_output=True, text=True)
    
    if "api" not in result.stdout or "db" not in result.stdout:
        print("⚠️ Services not running. Starting them...")
        subprocess.run(["docker-compose", "up", "-d", "db", "redis", "api"])
        print("Waiting for services to start...")
        time.sleep(10)
    
    # Test API connectivity
    cmd = [
        "docker-compose", "exec", "-T", "api",
        "python", "-c", "import requests; print('✅ API ready' if requests.get('http://localhost:8000/docs').status_code == 200 else '❌ API not ready')"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout.strip())
    
    return "✅" in result.stdout


def main():
    """Main function with command line argument parsing."""
    parser = argparse.ArgumentParser(description="Run ABParts performance tests")
    parser.add_argument(
        "test_type",
        nargs="?",
        choices=["api", "database", "frontend", "integration", "indexes", "all", "setup"],
        default="all",
        help="Type of performance test to run"
    )
    parser.add_argument(
        "--setup-data",
        action="store_true",
        help="Setup test data before running tests"
    )
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="Check environment before running tests"
    )
    
    args = parser.parse_args()
    
    print("ABParts Performance Test Runner")
    print("===============================")
    
    # Check environment if requested
    if args.check_env or args.test_type == "all":
        if not check_environment():
            print("❌ Environment check failed")
            return 1
    
    # Setup test data if requested
    if args.setup_data:
        result = setup_test_data()
        if result.returncode != 0:
            print("❌ Test data setup failed")
            return 1
    
    # Run the requested tests
    start_time = time.time()
    
    if args.test_type == "api":
        result = run_api_performance_tests()
    elif args.test_type == "database":
        result = run_database_performance_tests()
    elif args.test_type == "frontend":
        result = run_frontend_performance_tests()
    elif args.test_type == "integration":
        result = run_integration_tests()
    elif args.test_type == "indexes":
        result = run_index_validation()
    elif args.test_type == "setup":
        result = setup_test_data()
    elif args.test_type == "all":
        print("\n🚀 Running All Performance Tests")
        print("=" * 40)
        
        results = []
        
        # Run API tests
        results.append(("API", run_api_performance_tests()))
        
        # Run database tests
        results.append(("Database", run_database_performance_tests()))
        
        # Run frontend tests
        results.append(("Frontend", run_frontend_performance_tests()))
        
        # Run integration tests
        results.append(("Integration", run_integration_tests()))
        
        # Run index validation
        results.append(("Indexes", run_index_validation()))
        
        # Summary
        print("\n📊 Test Results Summary:")
        print("=" * 30)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result.returncode == 0 else "❌ FAIL"
            print(f"{status} {test_name}")
            if result.returncode == 0:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        # Return overall result
        result = type('Result', (), {'returncode': 0 if passed == total else 1})()
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"\n⏱️ Execution time: {execution_time:.2f}s")
    
    if result.returncode == 0:
        print("✅ Performance tests completed successfully!")
    else:
        print("❌ Performance tests failed!")
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())