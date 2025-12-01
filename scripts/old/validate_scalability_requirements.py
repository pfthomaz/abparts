#!/usr/bin/env python3
"""
Validation script to check scalability test results against requirements.
Validates that the system meets the performance criteria defined in the requirements.
"""

import json
import sys
from pathlib import Path

class RequirementsValidator:
    def __init__(self):
        self.requirements = {
            "2.1": {
                "description": "Parts API maintains acceptable response times with large datasets",
                "criteria": "API response time < 2 seconds for standard operations"
            },
            "2.2": {
                "description": "Pagination efficiently handles large parts catalogs",
                "criteria": "Pagination response time < 1 second"
            },
            "2.3": {
                "description": "Search functionality performs well with thousands of parts",
                "criteria": "Search response time < 2 seconds"
            },
            "2.4": {
                "description": "Filtering remains responsive with large datasets",
                "criteria": "Filter response time < 2 seconds"
            },
            "4.1": {
                "description": "Parts page loads efficiently regardless of total parts count",
                "criteria": "Page load time < 3 seconds"
            },
            "4.2": {
                "description": "Search provides fast results even with large catalogs",
                "criteria": "Frontend search response < 2 seconds"
            },
            "4.3": {
                "description": "Filters respond quickly with large datasets",
                "criteria": "Frontend filter response < 2 seconds"
            },
            "4.4": {
                "description": "Pagination works smoothly with large catalogs",
                "criteria": "Frontend pagination response < 1 second"
            }
        }
        
        self.validation_results = {}
    
    def load_test_results(self):
        """Load test results from JSON files."""
        results = {}
        
        # Load backend results
        backend_file = Path("scalability_test_results.json")
        if backend_file.exists():
            with open(backend_file, 'r') as f:
                results["backend"] = json.load(f)
            print("✅ Backend test results loaded")
        else:
            print("❌ Backend test results not found")
            results["backend"] = None
        
        # Load frontend results
        frontend_file = Path("frontend/frontend_scalability_results.json")
        if frontend_file.exists():
            with open(frontend_file, 'r') as f:
                results["frontend"] = json.load(f)
            print("✅ Frontend test results loaded")
        else:
            print("❌ Frontend test results not found")
            results["frontend"] = None
        
        # Load comprehensive report
        report_file = Path("comprehensive_scalability_report.json")
        if report_file.exists():
            with open(report_file, 'r') as f:
                results["comprehensive"] = json.load(f)
            print("✅ Comprehensive report loaded")
        else:
            print("❌ Comprehensive report not found")
            results["comprehensive"] = None
        
        return results
    
    def validate_requirement_2_1(self, results):
        """Validate requirement 2.1: Parts API response times."""
        if not results.get("backend"):
            return {"status": "SKIP", "reason": "No backend results available"}
        
        backend = results["backend"]
        
        # Check search performance
        search_perf = backend.get("search_performance", {})
        avg_search_time = search_perf.get("average_search_time", float('inf'))
        
        # Check pagination performance
        pagination_perf = backend.get("pagination_performance", {})
        avg_page_time = pagination_perf.get("overall_average_page_time", float('inf'))
        
        # Check concurrent access
        concurrent = backend.get("concurrent_access", {})
        avg_concurrent_time = concurrent.get("average_response_time", float('inf'))
        
        max_time = max(avg_search_time, avg_page_time, avg_concurrent_time)
        
        if max_time < 2.0:
            return {
                "status": "PASS",
                "details": f"Max API response time: {max_time:.3f}s",
                "metrics": {
                    "search_time": avg_search_time,
                    "pagination_time": avg_page_time,
                    "concurrent_time": avg_concurrent_time
                }
            }
        else:
            return {
                "status": "FAIL",
                "details": f"API response time {max_time:.3f}s exceeds 2s limit",
                "metrics": {
                    "search_time": avg_search_time,
                    "pagination_time": avg_page_time,
                    "concurrent_time": avg_concurrent_time
                }
            }
    
    def validate_requirement_2_2(self, results):
        """Validate requirement 2.2: Pagination performance."""
        if not results.get("backend"):
            return {"status": "SKIP", "reason": "No backend results available"}
        
        backend = results["backend"]
        pagination_perf = backend.get("pagination_performance", {})
        avg_page_time = pagination_perf.get("overall_average_page_time", float('inf'))
        
        if avg_page_time < 1.0:
            return {
                "status": "PASS",
                "details": f"Pagination response time: {avg_page_time:.3f}s",
                "metrics": {"pagination_time": avg_page_time}
            }
        else:
            return {
                "status": "FAIL",
                "details": f"Pagination time {avg_page_time:.3f}s exceeds 1s limit",
                "metrics": {"pagination_time": avg_page_time}
            }
    
    def validate_requirement_2_3(self, results):
        """Validate requirement 2.3: Search performance."""
        if not results.get("backend"):
            return {"status": "SKIP", "reason": "No backend results available"}
        
        backend = results["backend"]
        search_perf = backend.get("search_performance", {})
        avg_search_time = search_perf.get("average_search_time", float('inf'))
        
        if avg_search_time < 2.0:
            return {
                "status": "PASS",
                "details": f"Search response time: {avg_search_time:.3f}s",
                "metrics": {"search_time": avg_search_time}
            }
        else:
            return {
                "status": "FAIL",
                "details": f"Search time {avg_search_time:.3f}s exceeds 2s limit",
                "metrics": {"search_time": avg_search_time}
            }
    
    def validate_requirement_2_4(self, results):
        """Validate requirement 2.4: Filtering performance."""
        if not results.get("backend"):
            return {"status": "SKIP", "reason": "No backend results available"}
        
        backend = results["backend"]
        filter_perf = backend.get("filtering_performance", {})
        avg_filter_time = filter_perf.get("average_filter_time", float('inf'))
        
        if avg_filter_time < 2.0:
            return {
                "status": "PASS",
                "details": f"Filter response time: {avg_filter_time:.3f}s",
                "metrics": {"filter_time": avg_filter_time}
            }
        else:
            return {
                "status": "FAIL",
                "details": f"Filter time {avg_filter_time:.3f}s exceeds 2s limit",
                "metrics": {"filter_time": avg_filter_time}
            }
    
    def validate_requirement_4_1(self, results):
        """Validate requirement 4.1: Frontend page load performance."""
        if not results.get("frontend"):
            return {"status": "SKIP", "reason": "No frontend results available"}
        
        frontend = results["frontend"]
        
        # Check if we have performance metrics in summary
        summary = frontend.get("summary", {})
        metrics = summary.get("performanceMetrics", {})
        avg_load_time = metrics.get("averagePageLoadTime", float('inf'))
        
        # Convert from milliseconds to seconds if needed
        if avg_load_time > 100:  # Assume it's in milliseconds
            avg_load_time = avg_load_time / 1000
        
        if avg_load_time < 3.0:
            return {
                "status": "PASS",
                "details": f"Page load time: {avg_load_time:.3f}s",
                "metrics": {"page_load_time": avg_load_time}
            }
        else:
            return {
                "status": "FAIL",
                "details": f"Page load time {avg_load_time:.3f}s exceeds 3s limit",
                "metrics": {"page_load_time": avg_load_time}
            }
    
    def validate_requirement_4_2(self, results):
        """Validate requirement 4.2: Frontend search performance."""
        if not results.get("frontend"):
            return {"status": "SKIP", "reason": "No frontend results available"}
        
        frontend = results["frontend"]
        summary = frontend.get("summary", {})
        metrics = summary.get("performanceMetrics", {})
        avg_search_time = metrics.get("averageSearchTime", float('inf'))
        
        # Convert from milliseconds to seconds if needed
        if avg_search_time > 100:  # Assume it's in milliseconds
            avg_search_time = avg_search_time / 1000
        
        if avg_search_time < 2.0:
            return {
                "status": "PASS",
                "details": f"Frontend search time: {avg_search_time:.3f}s",
                "metrics": {"search_time": avg_search_time}
            }
        else:
            return {
                "status": "FAIL",
                "details": f"Frontend search time {avg_search_time:.3f}s exceeds 2s limit",
                "metrics": {"search_time": avg_search_time}
            }
    
    def validate_requirement_4_3(self, results):
        """Validate requirement 4.3: Frontend filter performance."""
        if not results.get("frontend"):
            return {"status": "SKIP", "reason": "No frontend results available"}
        
        frontend = results["frontend"]
        
        # Check filtering performance from detailed results
        filter_perf = frontend.get("filteringPerformance", {})
        filter_results = filter_perf.get("results", [])
        
        if filter_results:
            successful_filters = [r for r in filter_results if r.get("success", False)]
            if successful_filters:
                avg_filter_time = sum(r.get("filterTime", 0) for r in successful_filters) / len(successful_filters)
                
                # Convert from milliseconds to seconds if needed
                if avg_filter_time > 100:
                    avg_filter_time = avg_filter_time / 1000
                
                if avg_filter_time < 2.0:
                    return {
                        "status": "PASS",
                        "details": f"Frontend filter time: {avg_filter_time:.3f}s",
                        "metrics": {"filter_time": avg_filter_time}
                    }
                else:
                    return {
                        "status": "FAIL",
                        "details": f"Frontend filter time {avg_filter_time:.3f}s exceeds 2s limit",
                        "metrics": {"filter_time": avg_filter_time}
                    }
        
        return {"status": "SKIP", "reason": "No frontend filter performance data available"}
    
    def validate_requirement_4_4(self, results):
        """Validate requirement 4.4: Frontend pagination performance."""
        if not results.get("frontend"):
            return {"status": "SKIP", "reason": "No frontend results available"}
        
        frontend = results["frontend"]
        
        # Check parts page performance for pagination data
        parts_perf = frontend.get("partsPagePerformance", {})
        parts_results = parts_perf.get("results", [])
        
        pagination_times = [r.get("paginationTime", 0) for r in parts_results if r.get("paginationTime")]
        
        if pagination_times:
            avg_pagination_time = sum(pagination_times) / len(pagination_times)
            
            # Convert from milliseconds to seconds if needed
            if avg_pagination_time > 100:
                avg_pagination_time = avg_pagination_time / 1000
            
            if avg_pagination_time < 1.0:
                return {
                    "status": "PASS",
                    "details": f"Frontend pagination time: {avg_pagination_time:.3f}s",
                    "metrics": {"pagination_time": avg_pagination_time}
                }
            else:
                return {
                    "status": "FAIL",
                    "details": f"Frontend pagination time {avg_pagination_time:.3f}s exceeds 1s limit",
                    "metrics": {"pagination_time": avg_pagination_time}
                }
        
        return {"status": "SKIP", "reason": "No frontend pagination performance data available"}
    
    def validate_all_requirements(self, results):
        """Validate all requirements against test results."""
        validation_methods = {
            "2.1": self.validate_requirement_2_1,
            "2.2": self.validate_requirement_2_2,
            "2.3": self.validate_requirement_2_3,
            "2.4": self.validate_requirement_2_4,
            "4.1": self.validate_requirement_4_1,
            "4.2": self.validate_requirement_4_2,
            "4.3": self.validate_requirement_4_3,
            "4.4": self.validate_requirement_4_4
        }
        
        validation_results = {}
        
        for req_id, method in validation_methods.items():
            print(f"Validating requirement {req_id}...")
            validation_results[req_id] = method(results)
            
            result = validation_results[req_id]
            status_icon = {"PASS": "✅", "FAIL": "❌", "SKIP": "⏭️"}[result["status"]]
            print(f"  {status_icon} {req_id}: {result.get('details', result.get('reason', 'No details'))}")
        
        return validation_results
    
    def generate_validation_report(self, validation_results):
        """Generate comprehensive validation report."""
        report = {
            "validation_timestamp": __import__('time').strftime("%Y-%m-%d %H:%M:%S"),
            "requirements_tested": len(validation_results),
            "requirements_passed": len([r for r in validation_results.values() if r["status"] == "PASS"]),
            "requirements_failed": len([r for r in validation_results.values() if r["status"] == "FAIL"]),
            "requirements_skipped": len([r for r in validation_results.values() if r["status"] == "SKIP"]),
            "detailed_results": {}
        }
        
        for req_id, result in validation_results.items():
            report["detailed_results"][req_id] = {
                "requirement": self.requirements[req_id]["description"],
                "criteria": self.requirements[req_id]["criteria"],
                "status": result["status"],
                "details": result.get("details", result.get("reason", "")),
                "metrics": result.get("metrics", {})
            }
        
        # Determine overall validation status
        if report["requirements_failed"] == 0:
            if report["requirements_skipped"] == 0:
                report["overall_status"] = "PASS"
            else:
                report["overall_status"] = "PARTIAL"
        else:
            report["overall_status"] = "FAIL"
        
        return report
    
    def run_validation(self):
        """Run complete requirements validation."""
        print("🔍 ABParts Scalability Requirements Validation")
        print("="*60)
        
        # Load test results
        results = self.load_test_results()
        
        # Validate all requirements
        print("\nValidating requirements against test results...")
        validation_results = self.validate_all_requirements(results)
        
        # Generate report
        report = self.generate_validation_report(validation_results)
        
        # Save report
        with open("requirements_validation_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("📊 REQUIREMENTS VALIDATION SUMMARY")
        print("="*60)
        print(f"Overall Status: {report['overall_status']}")
        print(f"Requirements Tested: {report['requirements_tested']}")
        print(f"✅ Passed: {report['requirements_passed']}")
        print(f"❌ Failed: {report['requirements_failed']}")
        print(f"⏭️  Skipped: {report['requirements_skipped']}")
        
        if report["requirements_failed"] > 0:
            print("\nFailed Requirements:")
            for req_id, details in report["detailed_results"].items():
                if details["status"] == "FAIL":
                    print(f"  ❌ {req_id}: {details['details']}")
        
        print(f"\n📄 Detailed validation report saved to: requirements_validation_report.json")
        
        return report["overall_status"] in ["PASS", "PARTIAL"]

def main():
    """Main validation function."""
    validator = RequirementsValidator()
    success = validator.run_validation()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()