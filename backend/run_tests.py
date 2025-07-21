#!/usr/bin/env python3
"""
Test runner for ABParts integration tests.
Runs all test suites and generates a report.
"""

import os
import sys
import time
import argparse
import unittest
import pytest
from datetime import datetime


def run_pytest_tests(verbose=False, pattern=None):
    """Run pytest-based tests."""
    print("\n" + "=" * 80)
    print("Running pytest tests...")
    print("=" * 80)
    
    args = ["-v"] if verbose else []
    
    if pattern:
        args.append(f"-k {pattern}")
    
    # Add test directory
    args.append("tests/")
    
    # Run pytest
    result = pytest.main(args)
    
    return result == 0


def run_unittest_tests(verbose=False, pattern=None):
    """Run unittest-based tests."""
    print("\n" + "=" * 80)
    print("Running unittest tests...")
    print("=" * 80)
    
    # Discover and run tests
    test_loader = unittest.TestLoader()
    if pattern:
        test_loader.testNamePattern = pattern
    
    test_suite = test_loader.discover(".", pattern="test_*.py")
    test_runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = test_runner.run(test_suite)
    
    return result.wasSuccessful()


def generate_report(pytest_success, unittest_success, start_time, end_time):
    """Generate test report."""
    duration = end_time - start_time
    
    print("\n" + "=" * 80)
    print("TEST REPORT")
    print("=" * 80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Pytest tests: {'PASSED' if pytest_success else 'FAILED'}")
    print(f"Unittest tests: {'PASSED' if unittest_success else 'FAILED'}")
    print(f"Overall status: {'PASSED' if pytest_success and unittest_success else 'FAILED'}")
    print("=" * 80)
    
    # Write report to file
    report_dir = "test_reports"
    os.makedirs(report_dir, exist_ok=True)
    
    report_file = os.path.join(report_dir, f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(report_file, "w") as f:
        f.write("ABParts Test Report\n")
        f.write("=" * 80 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Duration: {duration:.2f} seconds\n")
        f.write(f"Pytest tests: {'PASSED' if pytest_success else 'FAILED'}\n")
        f.write(f"Unittest tests: {'PASSED' if unittest_success else 'FAILED'}\n")
        f.write(f"Overall status: {'PASSED' if pytest_success and unittest_success else 'FAILED'}\n")
        f.write("=" * 80 + "\n")
    
    print(f"Report saved to {report_file}")
    
    return pytest_success and unittest_success


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run ABParts tests")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-p", "--pattern", help="Test pattern to match")
    parser.add_argument("--pytest-only", action="store_true", help="Run only pytest tests")
    parser.add_argument("--unittest-only", action="store_true", help="Run only unittest tests")
    args = parser.parse_args()
    
    start_time = time.time()
    
    pytest_success = True
    unittest_success = True
    
    # Run pytest tests
    if not args.unittest_only:
        pytest_success = run_pytest_tests(args.verbose, args.pattern)
    
    # Run unittest tests
    if not args.pytest_only:
        unittest_success = run_unittest_tests(args.verbose, args.pattern)
    
    end_time = time.time()
    
    # Generate report
    success = generate_report(pytest_success, unittest_success, start_time, end_time)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())