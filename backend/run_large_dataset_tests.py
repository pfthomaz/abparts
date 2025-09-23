#!/usr/bin/env python3
"""
Test runner for large dataset performance tests.
Supports running tests with configurable dataset sizes beyond the previous 200-part limit.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

from tests.test_config_large_datasets import (
    LargeDatasetTestConfig, 
    get_environment_config,
    get_test_scenario,
    should_run_large_dataset_tests
)


def run_large_dataset_tests(
    scenario: str = "basic_performance",
    verbose: bool = False,
    markers: str = None,
    output_file: str = None
):
    """
    Run large dataset performance tests.
    
    Args:
        scenario: Test scenario name (basic_performance, moderate_scale, high_scale, stress_test)
        verbose: Enable verbose output
        markers: Additional pytest markers to include/exclude
        output_file: File to save test results
    """
    
    if not should_run_large_dataset_tests():
        print("Large dataset tests are disabled. Set ENABLE_LARGE_DATASET_TESTS=true to enable.")
        return False
    
    # Get scenario configuration
    scenario_config = get_test_scenario(scenario)
    if not scenario_config.get("enabled", True):
        print(f"Scenario '{scenario}' is disabled. Enable via environment variables.")
        return False
    
    print(f"Running large dataset tests - Scenario: {scenario}")
    print(f"Description: {scenario_config['description']}")
    print(f"Parts count: {scenario_config['parts_count']:,}")
    print(f"Performance threshold: {scenario_config['performance_threshold']}s")
    print("-" * 60)
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test file
    cmd.extend([
        "tests/test_large_dataset_performance.py",
        "tests/test_data_generators.py"
    ])
    
    # Add markers
    test_markers = ["large_dataset", "performance"]
    if markers:
        test_markers.extend(markers.split(","))
    
    if test_markers:
        cmd.extend(["-m", " and ".join(test_markers)])
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add output options
    cmd.extend([
        "--tb=short",
        "--color=yes",
        "--durations=10"  # Show 10 slowest tests
    ])
    
    # Add output file if specified
    if output_file:
        cmd.extend(["--junitxml", output_file])
    
    # Set environment variables for the scenario
    env = os.environ.copy()
    env.update({
        "TEST_SCENARIO": scenario,
        "TEST_PARTS_COUNT": str(scenario_config["parts_count"]),
        "PERFORMANCE_THRESHOLD": str(scenario_config["performance_threshold"]),
        "INCLUDE_INVENTORY": str(scenario_config.get("include_inventory", True)),
        "INCLUDE_TRANSACTIONS": str(scenario_config.get("include_transactions", True))
    })
    
    print(f"Running command: {' '.join(cmd)}")
    print("-" * 60)
    
    # Run tests
    try:
        result = subprocess.run(cmd, env=env, cwd=backend_path)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        return False
    except Exception as e:
        print(f"Error running tests: {e}")
        return False


def run_all_scenarios(verbose: bool = False, output_dir: str = None):
    """Run all test scenarios."""
    scenarios = ["basic_performance", "moderate_scale", "high_scale"]
    
    # Add stress test if enabled
    if os.getenv("ENABLE_STRESS_TESTS", "false").lower() == "true":
        scenarios.append("stress_test")
    
    results = {}
    
    for scenario in scenarios:
        print(f"\n{'='*80}")
        print(f"RUNNING SCENARIO: {scenario.upper()}")
        print(f"{'='*80}")
        
        output_file = None
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f"results_{scenario}.xml")
        
        success = run_large_dataset_tests(
            scenario=scenario,
            verbose=verbose,
            output_file=output_file
        )
        
        results[scenario] = success
        
        if success:
            print(f"✅ Scenario '{scenario}' PASSED")
        else:
            print(f"❌ Scenario '{scenario}' FAILED")
    
    # Print summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    
    for scenario, success in results.items():
        status = "PASSED" if success else "FAILED"
        icon = "✅" if success else "❌"
        print(f"{icon} {scenario}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} scenarios passed")
    
    return all(results.values())


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run large dataset performance tests for ABParts"
    )
    
    parser.add_argument(
        "--scenario",
        choices=["basic_performance", "moderate_scale", "high_scale", "stress_test", "all"],
        default="basic_performance",
        help="Test scenario to run (default: basic_performance)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--markers", "-m",
        help="Additional pytest markers (comma-separated)"
    )
    
    parser.add_argument(
        "--output-file", "-o",
        help="Output file for test results (JUnit XML format)"
    )
    
    parser.add_argument(
        "--output-dir",
        help="Output directory for test results (when running all scenarios)"
    )
    
    parser.add_argument(
        "--config",
        action="store_true",
        help="Show current configuration and exit"
    )
    
    args = parser.parse_args()
    
    if args.config:
        config = get_environment_config()
        print("Current Large Dataset Test Configuration:")
        print("-" * 40)
        
        print("Dataset Sizes:")
        for name, size in config["dataset_sizes"].items():
            print(f"  {name}: {size:,} parts")
        
        print("\nPerformance Thresholds:")
        for name, threshold in config["performance_thresholds"].items():
            print(f"  {name}: {threshold}s")
        
        print(f"\nStress tests enabled: {config['enable_stress_tests']}")
        print(f"Max test duration: {config['max_test_duration']}s")
        
        return
    
    if args.scenario == "all":
        success = run_all_scenarios(
            verbose=args.verbose,
            output_dir=args.output_dir
        )
    else:
        success = run_large_dataset_tests(
            scenario=args.scenario,
            verbose=args.verbose,
            markers=args.markers,
            output_file=args.output_file
        )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()