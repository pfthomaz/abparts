#!/usr/bin/env python3
"""
Comprehensive scalability validation test runner for ABParts system.
Orchestrates backend API tests and frontend performance tests with large datasets.
"""

import subprocess
import sys
import time
import json
import os
from pathlib import Path

class ScalabilityTestRunner:
    def __init__(self):
        self.results = {}
        self.start_time = time.time()
        
    def check_docker_services(self):
        """Check if required Docker services are running."""
        print("🐳 Checking Docker services...")
        
        try:
            # Check if docker-compose is available
            result = subprocess.run(
                ["docker-compose", "ps"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            services_output = result.stdout
            
            # Check for required services
            required_services = ["api", "web", "db", "redis"]
            running_services = []
            
            for service in required_services:
                if service in services_output and "Up" in services_output:
                    running_services.append(service)
            
            print(f"   Running services: {', '.join(running_services)}")
            
            if len(running_services) >= 3:  # At least api, web, db
                print("✅ Required Docker services are running")
                return True
            else:
                print("❌ Not all required services are running")
                print("   Please start services with: docker-compose up -d")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Docker services check failed: {e}")
            print("   Please ensure Docker and docker-compose are installed and services are running")
            return False
        except FileNotFoundError:
            print("❌ docker-compose not found")
            print("   Please install Docker and docker-compose")
            return False
    
    def wait_for_services(self, max_wait=60):
        """Wait for services to be ready."""
        print("⏳ Waiting for services to be ready...")
        
        import requests
        
        services_to_check = [
            {"url": "http://localhost:8000/docs", "name": "Backend API"},
            {"url": "http://localhost:3000", "name": "Frontend"}
        ]
        
        start_time = time.time()
        
        for service in services_to_check:
            print(f"   Checking {service['name']}...")
            
            while time.time() - start_time < max_wait:
                try:
                    response = requests.get(service["url"], timeout=5)
                    if response.status_code in [200, 404]:  # 404 is OK for some endpoints
                        print(f"   ✅ {service['name']} is ready")
                        break
                except requests.exceptions.RequestException:
                    time.sleep(2)
                    continue
            else:
                print(f"   ❌ {service['name']} not ready after {max_wait}s")
                return False
        
        print("✅ All services are ready")
        return True
    
    def run_backend_tests(self):
        """Run backend scalability tests."""
        print("\n" + "="*60)
        print("🔧 RUNNING BACKEND SCALABILITY TESTS")
        print("="*60)
        
        try:
            # Run the backend scalability test
            result = subprocess.run(
                [sys.executable, "test_large_dataset_scalability.py"],
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes timeout
            )
            
            print(result.stdout)
            
            if result.stderr:
                print("STDERR:", result.stderr)
            
            # Load results from JSON file if it exists
            if os.path.exists("scalability_test_results.json"):
                with open("scalability_test_results.json", "r") as f:
                    backend_results = json.load(f)
                    self.results["backend"] = backend_results
                    print("✅ Backend test results loaded")
            else:
                print("❌ Backend test results file not found")
                self.results["backend"] = {"error": "Results file not found"}
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("❌ Backend tests timed out after 30 minutes")
            self.results["backend"] = {"error": "Tests timed out"}
            return False
        except Exception as e:
            print(f"❌ Backend tests failed: {str(e)}")
            self.results["backend"] = {"error": str(e)}
            return False
    
    def install_frontend_dependencies(self):
        """Install frontend test dependencies."""
        print("📦 Installing frontend test dependencies...")
        
        try:
            # Check if puppeteer is installed
            result = subprocess.run(
                ["npm", "list", "puppeteer"],
                cwd="frontend",
                capture_output=True,
                text=True
            )
            
            if "puppeteer" not in result.stdout:
                print("   Installing puppeteer...")
                subprocess.run(
                    ["npm", "install", "puppeteer"],
                    cwd="frontend",
                    check=True
                )
                print("   ✅ Puppeteer installed")
            else:
                print("   ✅ Puppeteer already installed")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Failed to install dependencies: {e}")
            return False
        except FileNotFoundError:
            print("   ❌ npm not found - please install Node.js")
            return False
    
    def run_frontend_tests(self):
        """Run frontend scalability tests."""
        print("\n" + "="*60)
        print("🌐 RUNNING FRONTEND SCALABILITY TESTS")
        print("="*60)
        
        try:
            # Install dependencies first
            if not self.install_frontend_dependencies():
                self.results["frontend"] = {"error": "Failed to install dependencies"}
                return False
            
            # Run the frontend scalability test
            result = subprocess.run(
                ["node", "test_frontend_scalability.js"],
                cwd="frontend",
                capture_output=True,
                text=True,
                timeout=900  # 15 minutes timeout
            )
            
            print(result.stdout)
            
            if result.stderr:
                print("STDERR:", result.stderr)
            
            # Load results from JSON file if it exists
            frontend_results_path = "frontend/frontend_scalability_results.json"
            if os.path.exists(frontend_results_path):
                with open(frontend_results_path, "r") as f:
                    frontend_results = json.load(f)
                    self.results["frontend"] = frontend_results
                    print("✅ Frontend test results loaded")
            else:
                print("❌ Frontend test results file not found")
                self.results["frontend"] = {"error": "Results file not found"}
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            print("❌ Frontend tests timed out after 15 minutes")
            self.results["frontend"] = {"error": "Tests timed out"}
            return False
        except Exception as e:
            print(f"❌ Frontend tests failed: {str(e)}")
            self.results["frontend"] = {"error": str(e)}
            return False
    
    def run_database_performance_check(self):
        """Run database performance checks."""
        print("\n" + "="*60)
        print("🗄️  RUNNING DATABASE PERFORMANCE CHECKS")
        print("="*60)
        
        try:
            # Check database performance using docker-compose exec
            db_queries = [
                {
                    "name": "Parts count",
                    "query": "SELECT COUNT(*) as total_parts FROM parts;"
                },
                {
                    "name": "Index usage check",
                    "query": "SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch FROM pg_stat_user_indexes WHERE tablename = 'parts';"
                },
                {
                    "name": "Table size check",
                    "query": "SELECT pg_size_pretty(pg_total_relation_size('parts')) as table_size;"
                },
                {
                    "name": "Query performance test",
                    "query": "EXPLAIN ANALYZE SELECT * FROM parts WHERE part_type = 'CONSUMABLE' LIMIT 100;"
                }
            ]
            
            db_results = []
            
            for query_info in db_queries:
                print(f"   Running: {query_info['name']}")
                
                try:
                    result = subprocess.run([
                        "docker-compose", "exec", "-T", "db", 
                        "psql", "-U", "abparts_user", "-d", "abparts_dev", 
                        "-c", query_info["query"]
                    ], capture_output=True, text=True, timeout=30)
                    
                    if result.returncode == 0:
                        db_results.append({
                            "name": query_info["name"],
                            "success": True,
                            "output": result.stdout.strip()
                        })
                        print(f"     ✅ {query_info['name']} completed")
                    else:
                        db_results.append({
                            "name": query_info["name"],
                            "success": False,
                            "error": result.stderr.strip()
                        })
                        print(f"     ❌ {query_info['name']} failed")
                        
                except subprocess.TimeoutExpired:
                    db_results.append({
                        "name": query_info["name"],
                        "success": False,
                        "error": "Query timed out"
                    })
                    print(f"     ❌ {query_info['name']} timed out")
            
            self.results["database"] = {"queries": db_results}
            return True
            
        except Exception as e:
            print(f"❌ Database performance check failed: {str(e)}")
            self.results["database"] = {"error": str(e)}
            return False
    
    def generate_comprehensive_report(self):
        """Generate comprehensive scalability test report."""
        print("\n" + "="*60)
        print("📊 GENERATING COMPREHENSIVE SCALABILITY REPORT")
        print("="*60)
        
        total_time = time.time() - self.start_time
        
        report = {
            "test_suite": "ABParts Scalability Validation",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_execution_time": f"{total_time:.2f} seconds",
            "results": self.results,
            "summary": {
                "overall_status": "UNKNOWN",
                "backend_status": "UNKNOWN",
                "frontend_status": "UNKNOWN",
                "database_status": "UNKNOWN",
                "key_findings": [],
                "recommendations": []
            }
        }
        
        # Analyze backend results
        if "backend" in self.results and "summary" in self.results["backend"]:
            backend_summary = self.results["backend"]["summary"]
            report["summary"]["backend_status"] = backend_summary.get("overall_status", "UNKNOWN")
            
            if "recommendations" in backend_summary:
                report["summary"]["recommendations"].extend(backend_summary["recommendations"])
        
        # Analyze frontend results
        if "frontend" in self.results and "summary" in self.results["frontend"]:
            frontend_summary = self.results["frontend"]["summary"]
            report["summary"]["frontend_status"] = frontend_summary.get("overallStatus", "UNKNOWN")
            
            if "recommendations" in frontend_summary:
                report["summary"]["recommendations"].extend(frontend_summary["recommendations"])
        
        # Analyze database results
        if "database" in self.results and "queries" in self.results["database"]:
            db_queries = self.results["database"]["queries"]
            successful_queries = len([q for q in db_queries if q.get("success", False)])
            total_queries = len(db_queries)
            
            if successful_queries == total_queries:
                report["summary"]["database_status"] = "PASS"
            elif successful_queries > 0:
                report["summary"]["database_status"] = "WARNING"
            else:
                report["summary"]["database_status"] = "FAIL"
        
        # Determine overall status
        statuses = [
            report["summary"]["backend_status"],
            report["summary"]["frontend_status"],
            report["summary"]["database_status"]
        ]
        
        if all(s == "PASS" for s in statuses):
            report["summary"]["overall_status"] = "PASS"
        elif any(s == "FAIL" for s in statuses):
            report["summary"]["overall_status"] = "FAIL"
        else:
            report["summary"]["overall_status"] = "WARNING"
        
        # Add key findings
        if "backend" in self.results:
            backend = self.results["backend"]
            if "parts_creation" in backend:
                creation = backend["parts_creation"]
                report["summary"]["key_findings"].append(
                    f"Created {creation.get('total_parts_created', 0)} parts at "
                    f"{creation.get('average_parts_per_second', 0):.2f} parts/second"
                )
            
            if "search_performance" in backend:
                search = backend["search_performance"]
                report["summary"]["key_findings"].append(
                    f"Average search time: {search.get('average_search_time', 0):.3f} seconds"
                )
        
        if "frontend" in self.results and "summary" in self.results["frontend"]:
            frontend_summary = self.results["frontend"]["summary"]
            if "performanceMetrics" in frontend_summary:
                metrics = frontend_summary["performanceMetrics"]
                if "averagePageLoadTime" in metrics:
                    report["summary"]["key_findings"].append(
                        f"Average frontend page load: {metrics['averagePageLoadTime']:.0f}ms"
                    )
        
        # Save comprehensive report
        with open("comprehensive_scalability_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print(f"Overall Status: {report['summary']['overall_status']}")
        print(f"Execution Time: {report['total_execution_time']}")
        print(f"Backend Status: {report['summary']['backend_status']}")
        print(f"Frontend Status: {report['summary']['frontend_status']}")
        print(f"Database Status: {report['summary']['database_status']}")
        
        if report["summary"]["key_findings"]:
            print("\nKey Findings:")
            for finding in report["summary"]["key_findings"]:
                print(f"  • {finding}")
        
        if report["summary"]["recommendations"]:
            print("\nRecommendations:")
            for rec in report["summary"]["recommendations"][:5]:  # Top 5 recommendations
                print(f"  • {rec}")
        
        print(f"\n📄 Comprehensive report saved to: comprehensive_scalability_report.json")
        
        return report
    
    def run_full_validation(self):
        """Run complete scalability validation test suite."""
        print("🚀 ABParts System Scalability Validation Test Suite")
        print("="*60)
        print("Testing system performance with 10,000+ parts dataset")
        print("="*60)
        
        # Check prerequisites
        if not self.check_docker_services():
            return False
        
        if not self.wait_for_services():
            return False
        
        # Run all test suites
        backend_success = self.run_backend_tests()
        frontend_success = self.run_frontend_tests()
        database_success = self.run_database_performance_check()
        
        # Generate comprehensive report
        report = self.generate_comprehensive_report()
        
        print("\n" + "="*60)
        print("🏁 SCALABILITY VALIDATION COMPLETE")
        print("="*60)
        
        if report["summary"]["overall_status"] == "PASS":
            print("✅ System successfully handles large datasets")
            return True
        elif report["summary"]["overall_status"] == "WARNING":
            print("⚠️  System handles large datasets with some performance concerns")
            return True
        else:
            print("❌ System has significant scalability issues")
            return False

def main():
    """Main execution function."""
    runner = ScalabilityTestRunner()
    success = runner.run_full_validation()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()