#!/usr/bin/env python3
"""
Docker-aware performance test runner for parts system.
Executes comprehensive performance tests within the Docker environment.
"""

import os
import sys
import subprocess
import time
import json
from typing import Dict, Any, List


class DockerPerformanceTestRunner:
    """Docker-aware performance test runner."""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "environment": "docker",
            "tests": {}
        }
    
    def check_docker_environment(self) -> bool:
        """Check if Docker environment is available."""
        print("🐳 Checking Docker environment...")
        
        try:
            # Check if docker-compose is available
            result = subprocess.run(["docker-compose", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ docker-compose not available")
                return False
            
            print(f"✅ Docker Compose: {result.stdout.strip()}")
            
            # Check if services are running
            result = subprocess.run(["docker-compose", "ps"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Failed to check Docker services")
                return False
            
            print("✅ Docker environment ready")
            return True
            
        except Exception as e:
            print(f"❌ Docker environment check failed: {str(e)}")
            return False
    
    def setup_test_environment(self) -> bool:
        """Set up the test environment."""
        print("\n🔧 Setting up test environment...")
        
        try:
            # Ensure services are up
            print("Starting Docker services...")
            result = subprocess.run(["docker-compose", "up", "-d", "db", "redis", "api"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Failed to start services: {result.stderr}")
                return False
            
            # Wait for services to be ready
            print("Waiting for services to be ready...")
            time.sleep(10)
            
            # Check API health
            result = subprocess.run([
                "docker-compose", "exec", "-T", "api", 
                "python", "-c", "import requests; print('API ready' if requests.get('http://localhost:8000/docs').status_code == 200 else 'API not ready')"
            ], capture_output=True, text=True)
            
            if "API ready" not in result.stdout:
                print("⚠️ API may not be fully ready, continuing anyway...")
            else:
                print("✅ API is ready")
            
            return True
            
        except Exception as e:
            print(f"❌ Environment setup failed: {str(e)}")
            return False
    
    def run_backend_performance_tests(self) -> Dict[str, Any]:
        """Run backend performance tests in Docker."""
        print("\n🚀 Running Backend Performance Tests")
        print("=" * 50)
        
        backend_results = {}
        
        # Test 1: API Performance Tests
        print("\n📋 Running API Performance Tests...")
        try:
            cmd = [
                "docker-compose", "exec", "-T", "api",
                "python", "-m", "pytest",
                "tests/test_parts_api_performance.py",
                "-v", "-s", "--tb=short",
                "--disable-warnings"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            end_time = time.time()
            
            backend_results["api_performance"] = {
                "execution_time": end_time - start_time,
                "exit_code": result.returncode,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            if result.returncode == 0:
                print(f"✅ API performance tests completed in {end_time - start_time:.2f}s")
            else:
                print(f"❌ API performance tests failed")
                print(f"Error output: {result.stderr[:300]}...")
            
        except subprocess.TimeoutExpired:
            print("⏰ API performance tests timed out")
            backend_results["api_performance"] = {
                "execution_time": 600,
                "exit_code": -1,
                "success": False,
                "error": "Timeout"
            }
        except Exception as e:
            print(f"💥 API performance tests failed: {str(e)}")
            backend_results["api_performance"] = {
                "execution_time": 0,
                "exit_code": -1,
                "success": False,
                "error": str(e)
            }
        
        # Test 2: Database Performance Tests
        print("\n🗄️ Running Database Performance Tests...")
        try:
            cmd = [
                "docker-compose", "exec", "-T", "api",
                "python", "-m", "pytest",
                "tests/test_database_query_performance.py",
                "-v", "-s", "--tb=short",
                "--disable-warnings"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
            end_time = time.time()
            
            backend_results["database_performance"] = {
                "execution_time": end_time - start_time,
                "exit_code": result.returncode,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            if result.returncode == 0:
                print(f"✅ Database performance tests completed in {end_time - start_time:.2f}s")
            else:
                print(f"❌ Database performance tests failed")
                print(f"Error output: {result.stderr[:300]}...")
            
        except subprocess.TimeoutExpired:
            print("⏰ Database performance tests timed out")
            backend_results["database_performance"] = {
                "execution_time": 900,
                "exit_code": -1,
                "success": False,
                "error": "Timeout"
            }
        except Exception as e:
            print(f"💥 Database performance tests failed: {str(e)}")
            backend_results["database_performance"] = {
                "execution_time": 0,
                "exit_code": -1,
                "success": False,
                "error": str(e)
            }
        
        return backend_results
    
    def run_frontend_performance_tests(self) -> Dict[str, Any]:
        """Run frontend performance tests."""
        print("\n🎨 Running Frontend Performance Tests")
        print("=" * 50)
        
        frontend_results = {}
        
        try:
            # Check if frontend service is available
            result = subprocess.run(["docker-compose", "ps", "web"], 
                                  capture_output=True, text=True)
            
            if "web" not in result.stdout:
                print("⚠️ Frontend service not running, starting it...")
                subprocess.run(["docker-compose", "up", "-d", "web"], 
                             capture_output=True, text=True)
                time.sleep(5)
            
            # Run Jest tests in frontend container
            cmd = [
                "docker-compose", "exec", "-T", "web",
                "npm", "test", "--",
                "src/tests/parts-performance.test.js",
                "--verbose", "--watchAll=false", "--coverage=false"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            end_time = time.time()
            
            frontend_results["jest_performance"] = {
                "execution_time": end_time - start_time,
                "exit_code": result.returncode,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            if result.returncode == 0:
                print(f"✅ Frontend performance tests completed in {end_time - start_time:.2f}s")
            else:
                print(f"❌ Frontend performance tests failed")
                print(f"Error output: {result.stderr[:300]}...")
            
        except subprocess.TimeoutExpired:
            print("⏰ Frontend performance tests timed out")
            frontend_results["jest_performance"] = {
                "execution_time": 300,
                "exit_code": -1,
                "success": False,
                "error": "Timeout"
            }
        except Exception as e:
            print(f"💥 Frontend performance tests failed: {str(e)}")
            frontend_results["jest_performance"] = {
                "execution_time": 0,
                "exit_code": -1,
                "success": False,
                "error": str(e)
            }
        
        return frontend_results
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration performance tests."""
        print("\n🔗 Running Integration Performance Tests")
        print("=" * 50)
        
        integration_results = {}
        
        try:
            # Run existing performance optimization tests
            cmd = [
                "docker-compose", "exec", "-T", "api",
                "python", "test_performance_optimizations.py"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            end_time = time.time()
            
            integration_results["optimization_tests"] = {
                "execution_time": end_time - start_time,
                "exit_code": result.returncode,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            if result.returncode == 0:
                print(f"✅ Integration tests completed in {end_time - start_time:.2f}s")
            else:
                print(f"❌ Integration tests failed")
                print(f"Error output: {result.stderr[:300]}...")
            
        except subprocess.TimeoutExpired:
            print("⏰ Integration tests timed out")
            integration_results["optimization_tests"] = {
                "execution_time": 300,
                "exit_code": -1,
                "success": False,
                "error": "Timeout"
            }
        except Exception as e:
            print(f"💥 Integration tests failed: {str(e)}")
            integration_results["optimization_tests"] = {
                "execution_time": 0,
                "exit_code": -1,
                "success": False,
                "error": str(e)
            }
        
        return integration_results
    
    def run_database_index_validation(self) -> Dict[str, Any]:
        """Validate database indexes for performance."""
        print("\n📊 Validating Database Indexes")
        print("=" * 50)
        
        index_results = {}
        
        try:
            # Run parts index validation
            cmd = [
                "docker-compose", "exec", "-T", "api",
                "python", "test_parts_indexes.py"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            end_time = time.time()
            
            index_results["parts_indexes"] = {
                "execution_time": end_time - start_time,
                "exit_code": result.returncode,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            if result.returncode == 0:
                print(f"✅ Index validation completed in {end_time - start_time:.2f}s")
            else:
                print(f"❌ Index validation failed")
                print(f"Error output: {result.stderr[:300]}...")
            
        except Exception as e:
            print(f"💥 Index validation failed: {str(e)}")
            index_results["parts_indexes"] = {
                "execution_time": 0,
                "exit_code": -1,
                "success": False,
                "error": str(e)
            }
        
        return index_results
    
    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate summary report of all tests."""
        print("\n📊 Generating Summary Report")
        print("=" * 50)
        
        total_tests = 0
        passed_tests = 0
        total_time = 0
        
        # Count all test results
        for category, tests in self.results["tests"].items():
            for test_name, test_result in tests.items():
                total_tests += 1
                if test_result.get("success", False):
                    passed_tests += 1
                total_time += test_result.get("execution_time", 0)
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_execution_time": total_time
        }
        
        print(f"📈 Performance Test Summary:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {total_tests - passed_tests}")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Total Time: {total_time:.2f}s")
        
        return summary
    
    def save_results(self):
        """Save test results to file."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"parts_performance_results_{timestamp}.json"
        filepath = os.path.join(self.base_dir, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            
            print(f"\n💾 Results saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Failed to save results: {str(e)}")
    
    def run_all_tests(self) -> int:
        """Run all performance tests."""
        print("🚀 Starting Parts Performance Tests")
        print("=" * 60)
        
        start_time = time.time()
        
        # Check Docker environment
        if not self.check_docker_environment():
            print("❌ Docker environment not available")
            return 1
        
        # Setup test environment
        if not self.setup_test_environment():
            print("❌ Failed to setup test environment")
            return 1
        
        try:
            # Run all test categories
            self.results["tests"]["backend"] = self.run_backend_performance_tests()
            self.results["tests"]["frontend"] = self.run_frontend_performance_tests()
            self.results["tests"]["integration"] = self.run_integration_tests()
            self.results["tests"]["database_indexes"] = self.run_database_index_validation()
            
            # Generate summary
            summary = self.generate_summary_report()
            self.results["summary"] = summary
            
            # Save results
            self.save_results()
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"\n🎉 Performance Testing Complete!")
            print(f"Total Execution Time: {total_time:.2f}s")
            
            # Determine overall result
            if summary["success_rate"] >= 75:
                print("✅ Overall Result: PASS (≥75% success rate)")
                return 0
            else:
                print("❌ Overall Result: FAIL (<75% success rate)")
                return 1
                
        except KeyboardInterrupt:
            print("\n⏹️ Performance testing interrupted by user")
            return 1
        except Exception as e:
            print(f"\n💥 Performance testing failed: {str(e)}")
            return 1


def main():
    """Main function."""
    print("ABParts Performance Test Suite")
    print("==============================")
    
    runner = DockerPerformanceTestRunner()
    exit_code = runner.run_all_tests()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()