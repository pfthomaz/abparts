#!/usr/bin/env python3
"""
Comprehensive performance test runner for parts system.
Executes API, database, and integration performance tests with different dataset sizes.
"""

import os
import sys
import time
import subprocess
import json
from typing import Dict, List, Any
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .test_config_large_datasets import LargeDatasetTestConfig, get_test_scenario


class PerformanceTestRunner:
    """Comprehensive performance test runner."""
    
    def __init__(self):
        self.config = LargeDatasetTestConfig()
        self.results = {
            "test_run_id": f"perf_test_{int(time.time())}",
            "timestamp": datetime.now().isoformat(),
            "api_tests": {},
            "database_tests": {},
            "frontend_tests": {},
            "summary": {}
        }
    
    def run_backend_api_tests(self) -> Dict[str, Any]:
        """Run backend API performance tests."""
        print("\n🚀 Running Backend API Performance Tests")
        print("=" * 50)
        
        api_results = {}
        
        # Test scenarios
        scenarios = ["basic_performance", "moderate_scale", "high_scale"]
        
        for scenario_name in scenarios:
            scenario = get_test_scenario(scenario_name)
            if not scenario.get("enabled", True):
                print(f"⏭️ Skipping {scenario_name} (disabled)")
                continue
            
            print(f"\n📋 Running {scenario_name} scenario ({scenario['parts_count']} parts)...")
            
            try:
                # Run pytest for API performance tests
                cmd = [
                    "python", "-m", "pytest",
                    "backend/tests/test_parts_api_performance.py",
                    f"-k", f"test_parts_api_performance_{scenario['parts_count']//1000}k",
                    "-v", "-s", "--tb=short",
                    "--disable-warnings"
                ]
                
                start_time = time.time()
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                end_time = time.time()
                
                api_results[scenario_name] = {
                    "scenario": scenario_name,
                    "parts_count": scenario["parts_count"],
                    "execution_time": end_time - start_time,
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": result.returncode == 0
                }
                
                if result.returncode == 0:
                    print(f"✅ {scenario_name} completed successfully in {end_time - start_time:.2f}s")
                else:
                    print(f"❌ {scenario_name} failed with exit code {result.returncode}")
                    print(f"Error: {result.stderr[:200]}...")
                
            except subprocess.TimeoutExpired:
                print(f"⏰ {scenario_name} timed out after 300 seconds")
                api_results[scenario_name] = {
                    "scenario": scenario_name,
                    "parts_count": scenario["parts_count"],
                    "execution_time": 300,
                    "exit_code": -1,
                    "success": False,
                    "error": "Test timed out"
                }
            except Exception as e:
                print(f"💥 {scenario_name} failed with exception: {str(e)}")
                api_results[scenario_name] = {
                    "scenario": scenario_name,
                    "parts_count": scenario["parts_count"],
                    "execution_time": 0,
                    "exit_code": -1,
                    "success": False,
                    "error": str(e)
                }
        
        return api_results
    
    def run_database_performance_tests(self) -> Dict[str, Any]:
        """Run database query performance tests."""
        print("\n🗄️ Running Database Performance Tests")
        print("=" * 50)
        
        db_results = {}
        
        # Test scenarios
        scenarios = ["basic_performance", "moderate_scale", "high_scale"]
        
        for scenario_name in scenarios:
            scenario = get_test_scenario(scenario_name)
            if not scenario.get("enabled", True):
                print(f"⏭️ Skipping {scenario_name} (disabled)")
                continue
            
            print(f"\n🔍 Running {scenario_name} database tests ({scenario['parts_count']} parts)...")
            
            try:
                # Run pytest for database performance tests
                cmd = [
                    "python", "-m", "pytest",
                    "backend/tests/test_database_query_performance.py",
                    f"-k", f"test_database_performance_{scenario['parts_count']//1000}k",
                    "-v", "-s", "--tb=short",
                    "--disable-warnings"
                ]
                
                start_time = time.time()
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
                end_time = time.time()
                
                db_results[scenario_name] = {
                    "scenario": scenario_name,
                    "parts_count": scenario["parts_count"],
                    "execution_time": end_time - start_time,
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": result.returncode == 0
                }
                
                if result.returncode == 0:
                    print(f"✅ {scenario_name} database tests completed in {end_time - start_time:.2f}s")
                else:
                    print(f"❌ {scenario_name} database tests failed with exit code {result.returncode}")
                    print(f"Error: {result.stderr[:200]}...")
                
            except subprocess.TimeoutExpired:
                print(f"⏰ {scenario_name} database tests timed out after 600 seconds")
                db_results[scenario_name] = {
                    "scenario": scenario_name,
                    "parts_count": scenario["parts_count"],
                    "execution_time": 600,
                    "exit_code": -1,
                    "success": False,
                    "error": "Test timed out"
                }
            except Exception as e:
                print(f"💥 {scenario_name} database tests failed: {str(e)}")
                db_results[scenario_name] = {
                    "scenario": scenario_name,
                    "parts_count": scenario["parts_count"],
                    "execution_time": 0,
                    "exit_code": -1,
                    "success": False,
                    "error": str(e)
                }
        
        return db_results
    
    def run_frontend_performance_tests(self) -> Dict[str, Any]:
        """Run frontend performance tests."""
        print("\n🎨 Running Frontend Performance Tests")
        print("=" * 50)
        
        frontend_results = {}
        
        try:
            # Check if Node.js and npm are available
            node_check = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if node_check.returncode != 0:
                print("⚠️ Node.js not available, skipping frontend tests")
                return {"error": "Node.js not available"}
            
            # Change to frontend directory
            frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
            
            # Run Jest tests for frontend performance
            cmd = [
                "npm", "test", "--",
                "src/tests/parts-performance.test.js",
                "--verbose", "--no-coverage"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, cwd=frontend_dir, capture_output=True, text=True, timeout=300)
            end_time = time.time()
            
            frontend_results["jest_tests"] = {
                "execution_time": end_time - start_time,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
            if result.returncode == 0:
                print(f"✅ Frontend tests completed successfully in {end_time - start_time:.2f}s")
            else:
                print(f"❌ Frontend tests failed with exit code {result.returncode}")
                print(f"Error: {result.stderr[:200]}...")
            
        except subprocess.TimeoutExpired:
            print("⏰ Frontend tests timed out after 300 seconds")
            frontend_results["jest_tests"] = {
                "execution_time": 300,
                "exit_code": -1,
                "success": False,
                "error": "Test timed out"
            }
        except Exception as e:
            print(f"💥 Frontend tests failed: {str(e)}")
            frontend_results["jest_tests"] = {
                "execution_time": 0,
                "exit_code": -1,
                "success": False,
                "error": str(e)
            }
        
        return frontend_results
    
    def run_integration_performance_tests(self) -> Dict[str, Any]:
        """Run end-to-end integration performance tests."""
        print("\n🔗 Running Integration Performance Tests")
        print("=" * 50)
        
        integration_results = {}
        
        try:
            # Run existing performance optimization tests
            cmd = [
                "python", "-m", "pytest",
                "backend/test_performance_optimizations.py",
                "-v", "-s", "--tb=short",
                "--disable-warnings"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            end_time = time.time()
            
            integration_results["optimization_tests"] = {
                "execution_time": end_time - start_time,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }
            
            if result.returncode == 0:
                print(f"✅ Integration tests completed in {end_time - start_time:.2f}s")
            else:
                print(f"❌ Integration tests failed with exit code {result.returncode}")
                print(f"Error: {result.stderr[:200]}...")
            
        except Exception as e:
            print(f"💥 Integration tests failed: {str(e)}")
            integration_results["optimization_tests"] = {
                "execution_time": 0,
                "exit_code": -1,
                "success": False,
                "error": str(e)
            }
        
        return integration_results
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        print("\n📊 Generating Performance Report")
        print("=" * 50)
        
        # Calculate summary statistics
        total_tests = 0
        passed_tests = 0
        total_execution_time = 0
        
        # API tests summary
        for test_name, test_result in self.results["api_tests"].items():
            total_tests += 1
            if test_result.get("success", False):
                passed_tests += 1
            total_execution_time += test_result.get("execution_time", 0)
        
        # Database tests summary
        for test_name, test_result in self.results["database_tests"].items():
            total_tests += 1
            if test_result.get("success", False):
                passed_tests += 1
            total_execution_time += test_result.get("execution_time", 0)
        
        # Frontend tests summary
        if "jest_tests" in self.results["frontend_tests"]:
            total_tests += 1
            if self.results["frontend_tests"]["jest_tests"].get("success", False):
                passed_tests += 1
            total_execution_time += self.results["frontend_tests"]["jest_tests"].get("execution_time", 0)
        
        # Integration tests summary
        if "optimization_tests" in self.results.get("integration_tests", {}):
            total_tests += 1
            if self.results["integration_tests"]["optimization_tests"].get("success", False):
                passed_tests += 1
            total_execution_time += self.results["integration_tests"]["optimization_tests"].get("execution_time", 0)
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_execution_time": total_execution_time,
            "performance_thresholds": self.config.PERFORMANCE_THRESHOLDS,
            "dataset_sizes": self.config.DEFAULT_DATASET_SIZES
        }
        
        self.results["summary"] = summary
        
        # Print summary
        print(f"📈 Test Results Summary:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {total_tests - passed_tests}")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Total Execution Time: {total_execution_time:.2f}s")
        
        return summary
    
    def save_results(self, filename: str = None):
        """Save test results to JSON file."""
        if filename is None:
            filename = f"performance_test_results_{self.results['test_run_id']}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            print(f"\n💾 Results saved to: {filepath}")
            
        except Exception as e:
            print(f"❌ Failed to save results: {str(e)}")
    
    def run_all_tests(self):
        """Run all performance tests."""
        print("🚀 Starting Comprehensive Performance Tests")
        print("=" * 60)
        print(f"Test Run ID: {self.results['test_run_id']}")
        print(f"Timestamp: {self.results['timestamp']}")
        
        start_time = time.time()
        
        try:
            # Run API performance tests
            self.results["api_tests"] = self.run_backend_api_tests()
            
            # Run database performance tests
            self.results["database_tests"] = self.run_database_performance_tests()
            
            # Run frontend performance tests
            self.results["frontend_tests"] = self.run_frontend_performance_tests()
            
            # Run integration performance tests
            self.results["integration_tests"] = self.run_integration_performance_tests()
            
            # Generate report
            summary = self.generate_performance_report()
            
            # Save results
            self.save_results()
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"\n🎉 Performance Testing Complete!")
            print(f"Total Time: {total_time:.2f}s")
            
            if summary["success_rate"] >= 80:
                print("✅ Overall Result: PASS (≥80% success rate)")
                return 0
            else:
                print("❌ Overall Result: FAIL (<80% success rate)")
                return 1
                
        except Exception as e:
            print(f"\n💥 Performance testing failed: {str(e)}")
            return 1


def main():
    """Main function to run performance tests."""
    runner = PerformanceTestRunner()
    exit_code = runner.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()