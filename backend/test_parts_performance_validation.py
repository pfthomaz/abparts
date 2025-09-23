#!/usr/bin/env python3
"""
Performance validation script for parts system.
This script tests the parts API and CRUD operations with large datasets
to validate performance benchmarks and monitoring.
"""

import asyncio
import time
import statistics
import requests
import json
from typing import List, Dict, Any
from datetime import datetime
import argparse
import sys
import os

# Add the app directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.performance_monitoring import PerformanceBenchmark


class PerformanceValidator:
    """Performance validation utility for parts system"""
    
    def __init__(self, base_url: str = "http://localhost:8000", auth_token: str = None):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.session = requests.Session()
        
        if auth_token:
            self.session.headers.update({"Authorization": f"Bearer {auth_token}"})
    
    def authenticate(self, username: str = "superadmin", password: str = "superadmin") -> str:
        """Authenticate and get access token"""
        auth_data = {
            "username": username,
            "password": password
        }
        
        response = self.session.post(
            f"{self.base_url}/token",
            data=auth_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            self.auth_token = token_data["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
            print(f"✓ Authentication successful")
            return self.auth_token
        else:
            print(f"✗ Authentication failed: {response.status_code} - {response.text}")
            return None
    
    def test_endpoint_performance(self, endpoint: str, method: str = "GET", 
                                 data: Dict = None, iterations: int = 10) -> Dict[str, Any]:
        """Test endpoint performance with multiple iterations"""
        url = f"{self.base_url}{endpoint}"
        execution_times = []
        errors = []
        
        print(f"Testing {method} {endpoint} ({iterations} iterations)...")
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                if method.upper() == "GET":
                    response = self.session.get(url)
                elif method.upper() == "POST":
                    response = self.session.post(url, json=data)
                elif method.upper() == "PUT":
                    response = self.session.put(url, json=data)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                execution_time = time.time() - start_time
                execution_times.append(execution_time)
                
                if response.status_code not in [200, 201]:
                    errors.append(f"HTTP {response.status_code}: {response.text[:100]}")
                
            except Exception as e:
                execution_time = time.time() - start_time
                execution_times.append(execution_time)
                errors.append(str(e))
        
        # Calculate statistics
        if execution_times:
            avg_time = statistics.mean(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            p95_time = statistics.quantiles(execution_times, n=20)[18] if len(execution_times) >= 20 else max_time
            p99_time = statistics.quantiles(execution_times, n=100)[98] if len(execution_times) >= 100 else max_time
        else:
            avg_time = min_time = max_time = p95_time = p99_time = 0
        
        return {
            "endpoint": endpoint,
            "method": method,
            "iterations": iterations,
            "avg_time": avg_time,
            "min_time": min_time,
            "max_time": max_time,
            "p95_time": p95_time,
            "p99_time": p99_time,
            "success_rate": (iterations - len(errors)) / iterations * 100,
            "errors": errors[:5]  # Keep only first 5 errors
        }
    
    def validate_against_benchmarks(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate performance results against benchmarks"""
        benchmarks = PerformanceBenchmark.create_benchmark_thresholds()
        validation_results = []
        
        # Map endpoint patterns to benchmark operations
        endpoint_mapping = {
            "/parts/": "api.get_parts",
            "/parts/search": "api.search_parts",
            "/parts/with-inventory": "api.get_parts_with_inventory",
            "/parts/search-with-inventory": "api.search_parts_with_inventory"
        }
        
        for result in results:
            endpoint = result["endpoint"]
            
            # Find matching benchmark
            benchmark_op = None
            for pattern, op in endpoint_mapping.items():
                if pattern in endpoint:
                    benchmark_op = op
                    break
            
            if benchmark_op:
                # Find benchmark threshold
                threshold = None
                for category, ops in benchmarks.items():
                    if benchmark_op in ops:
                        threshold = ops[benchmark_op]
                        break
                
                if threshold:
                    validation = PerformanceBenchmark.validate_performance(
                        benchmark_op, result["avg_time"], benchmarks
                    )
                    validation.update({
                        "endpoint": endpoint,
                        "test_result": result
                    })
                    validation_results.append(validation)
        
        return validation_results
    
    def run_parts_performance_tests(self) -> Dict[str, Any]:
        """Run comprehensive parts performance tests"""
        print("=" * 60)
        print("PARTS SYSTEM PERFORMANCE VALIDATION")
        print("=" * 60)
        
        # Test endpoints with different scenarios
        test_scenarios = [
            # Basic parts listing
            {
                "endpoint": "/parts/",
                "method": "GET",
                "iterations": 20,
                "description": "Basic parts listing"
            },
            {
                "endpoint": "/parts/?limit=100",
                "method": "GET", 
                "iterations": 15,
                "description": "Parts listing with pagination"
            },
            {
                "endpoint": "/parts/?part_type=consumable",
                "method": "GET",
                "iterations": 15,
                "description": "Parts filtering by type"
            },
            {
                "endpoint": "/parts/?is_proprietary=true",
                "method": "GET",
                "iterations": 15,
                "description": "Parts filtering by proprietary status"
            },
            {
                "endpoint": "/parts/?include_count=true",
                "method": "GET",
                "iterations": 10,
                "description": "Parts listing with count (expensive operation)"
            },
            
            # Search operations
            {
                "endpoint": "/parts/search?q=test",
                "method": "GET",
                "iterations": 15,
                "description": "Basic parts search"
            },
            {
                "endpoint": "/parts/search?q=part&part_type=consumable",
                "method": "GET",
                "iterations": 15,
                "description": "Parts search with filtering"
            },
            {
                "endpoint": "/parts/search?q=test&include_count=true",
                "method": "GET",
                "iterations": 10,
                "description": "Parts search with count"
            },
            
            # Inventory operations
            {
                "endpoint": "/parts/with-inventory",
                "method": "GET",
                "iterations": 10,
                "description": "Parts with inventory data"
            },
            {
                "endpoint": "/parts/with-inventory?limit=50",
                "method": "GET",
                "iterations": 10,
                "description": "Parts with inventory (paginated)"
            },
            {
                "endpoint": "/parts/search-with-inventory?q=test",
                "method": "GET",
                "iterations": 10,
                "description": "Search parts with inventory"
            },
            
            # Individual part operations
            {
                "endpoint": "/parts/types",
                "method": "GET",
                "iterations": 20,
                "description": "Get part types (should be very fast)"
            }
        ]
        
        results = []
        
        for scenario in test_scenarios:
            print(f"\n📊 {scenario['description']}")
            result = self.test_endpoint_performance(
                scenario["endpoint"],
                scenario["method"],
                iterations=scenario["iterations"]
            )
            results.append(result)
            
            # Print immediate results
            status = "✓" if result["success_rate"] >= 95 else "⚠" if result["success_rate"] >= 80 else "✗"
            print(f"   {status} Avg: {result['avg_time']:.3f}s, "
                  f"P95: {result['p95_time']:.3f}s, "
                  f"Success: {result['success_rate']:.1f}%")
            
            if result["errors"]:
                print(f"   Errors: {len(result['errors'])}")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "test_results": results,
            "summary": self._generate_summary(results)
        }
    
    def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate performance test summary"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r["success_rate"] >= 95)
        warning_tests = sum(1 for r in results if 80 <= r["success_rate"] < 95)
        failed_tests = sum(1 for r in results if r["success_rate"] < 80)
        
        avg_times = [r["avg_time"] for r in results]
        overall_avg = statistics.mean(avg_times) if avg_times else 0
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "warning_tests": warning_tests,
            "failed_tests": failed_tests,
            "overall_avg_time": overall_avg,
            "overall_success_rate": (passed_tests + warning_tests) / total_tests * 100 if total_tests > 0 else 0
        }
    
    def test_performance_monitoring_api(self) -> Dict[str, Any]:
        """Test the performance monitoring API endpoints"""
        print("\n" + "=" * 60)
        print("PERFORMANCE MONITORING API TESTS")
        print("=" * 60)
        
        monitoring_tests = [
            "/performance/metrics/operations",
            "/performance/benchmarks",
            "/performance/health",
            "/performance/metrics/slow-operations"
        ]
        
        results = []
        
        for endpoint in monitoring_tests:
            print(f"\n📊 Testing {endpoint}")
            result = self.test_endpoint_performance(endpoint, iterations=5)
            results.append(result)
            
            status = "✓" if result["success_rate"] >= 80 else "✗"
            print(f"   {status} Avg: {result['avg_time']:.3f}s, Success: {result['success_rate']:.1f}%")
        
        return results
    
    def generate_report(self, parts_results: Dict[str, Any], 
                       monitoring_results: List[Dict[str, Any]]) -> str:
        """Generate a comprehensive performance report"""
        report = []
        report.append("ABPARTS PERFORMANCE VALIDATION REPORT")
        report.append("=" * 50)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Parts system summary
        summary = parts_results["summary"]
        report.append("PARTS SYSTEM PERFORMANCE SUMMARY")
        report.append("-" * 35)
        report.append(f"Total Tests: {summary['total_tests']}")
        report.append(f"Passed: {summary['passed_tests']} (≥95% success rate)")
        report.append(f"Warning: {summary['warning_tests']} (80-94% success rate)")
        report.append(f"Failed: {summary['failed_tests']} (<80% success rate)")
        report.append(f"Overall Success Rate: {summary['overall_success_rate']:.1f}%")
        report.append(f"Overall Average Time: {summary['overall_avg_time']:.3f}s")
        report.append("")
        
        # Detailed results
        report.append("DETAILED PERFORMANCE RESULTS")
        report.append("-" * 30)
        
        for result in parts_results["test_results"]:
            status = "PASS" if result["success_rate"] >= 95 else "WARN" if result["success_rate"] >= 80 else "FAIL"
            report.append(f"{status:4} {result['endpoint']:40} "
                         f"Avg: {result['avg_time']:.3f}s "
                         f"P95: {result['p95_time']:.3f}s "
                         f"Success: {result['success_rate']:.1f}%")
        
        report.append("")
        
        # Benchmark validation
        validation_results = self.validate_against_benchmarks(parts_results["test_results"])
        if validation_results:
            report.append("BENCHMARK VALIDATION")
            report.append("-" * 20)
            
            for validation in validation_results:
                status = "PASS" if validation["meets_benchmark"] else "FAIL"
                report.append(f"{status:4} {validation['operation']:30} "
                             f"Actual: {validation['execution_time']:.3f}s "
                             f"Benchmark: {validation['benchmark_threshold']:.3f}s "
                             f"Ratio: {validation['performance_ratio']:.2f}x")
            
            report.append("")
        
        # Monitoring API results
        if monitoring_results:
            report.append("PERFORMANCE MONITORING API")
            report.append("-" * 25)
            
            for result in monitoring_results:
                status = "PASS" if result["success_rate"] >= 80 else "FAIL"
                report.append(f"{status:4} {result['endpoint']:40} "
                             f"Avg: {result['avg_time']:.3f}s "
                             f"Success: {result['success_rate']:.1f}%")
        
        return "\n".join(report)


def main():
    """Main function to run performance validation"""
    parser = argparse.ArgumentParser(description="ABParts Performance Validation")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Base URL for the API (default: http://localhost:8000)")
    parser.add_argument("--username", default="superadmin", 
                       help="Username for authentication (default: superadmin)")
    parser.add_argument("--password", default="superadmin", 
                       help="Password for authentication (default: superadmin)")
    parser.add_argument("--output", help="Output file for the report")
    parser.add_argument("--skip-auth", action="store_true", 
                       help="Skip authentication (use if already authenticated)")
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = PerformanceValidator(base_url=args.url)
    
    # Authenticate if not skipped
    if not args.skip_auth:
        token = validator.authenticate(args.username, args.password)
        if not token:
            print("❌ Authentication failed. Exiting.")
            sys.exit(1)
    
    try:
        # Run parts performance tests
        parts_results = validator.run_parts_performance_tests()
        
        # Run monitoring API tests
        monitoring_results = validator.test_performance_monitoring_api()
        
        # Generate report
        report = validator.generate_report(parts_results, monitoring_results)
        
        # Output report
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"\n📄 Report saved to: {args.output}")
        else:
            print("\n" + "=" * 60)
            print(report)
        
        # Exit with appropriate code
        summary = parts_results["summary"]
        if summary["failed_tests"] > 0:
            print("\n❌ Some tests failed. Check the results above.")
            sys.exit(1)
        elif summary["warning_tests"] > 0:
            print("\n⚠️  Some tests had warnings. Performance may need attention.")
            sys.exit(0)
        else:
            print("\n✅ All performance tests passed!")
            sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n⏹️  Performance validation interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Performance validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()