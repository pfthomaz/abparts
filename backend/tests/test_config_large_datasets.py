"""
Configuration for large dataset testing.
Provides configurable parameters for test data generation beyond the previous 200-part limit.
"""

import os
from typing import Dict, Any


class LargeDatasetTestConfig:
    """Configuration class for large dataset testing."""
    
    # Default dataset sizes for different test scenarios
    DEFAULT_DATASET_SIZES = {
        "small": 1000,      # 1K parts - basic large dataset testing
        "medium": 5000,     # 5K parts - moderate scale testing  
        "large": 10000,     # 10K parts - high scale testing
        "xlarge": 25000,    # 25K parts - stress testing (optional)
    }
    
    # Performance thresholds (in milliseconds)
    PERFORMANCE_THRESHOLDS = {
        "api_response_1k": 2000.0,   # API response time for 1K parts (2 seconds)
        "api_response_5k": 3000.0,   # API response time for 5K parts (3 seconds)
        "api_response_10k": 5000.0,  # API response time for 10K parts (5 seconds)
        "db_query_1k": 50.0,         # Database query time for 1K parts (50ms)
        "db_query_5k": 100.0,        # Database query time for 5K parts (100ms)
        "db_query_10k": 200.0,       # Database query time for 10K parts (200ms)
        "search_1k": 100.0,          # Search time for 1K parts (100ms)
        "search_5k": 200.0,          # Search time for 5K parts (200ms)
        "search_10k": 400.0,         # Search time for 10K parts (400ms)
    }
    
    # Memory usage thresholds (in MB)
    MEMORY_THRESHOLDS = {
        "dataset_1k": 100,          # Memory increase for 1K parts dataset
        "dataset_5k": 500,          # Memory increase for 5K parts dataset
        "dataset_10k": 1000,        # Memory increase for 10K parts dataset
    }
    
    @classmethod
    def get_dataset_size(cls, size_name: str) -> int:
        """Get dataset size by name."""
        return cls.DEFAULT_DATASET_SIZES.get(size_name, 1000)
    
    @classmethod
    def get_performance_threshold(cls, operation: str) -> float:
        """Get performance threshold for operation."""
        return cls.PERFORMANCE_THRESHOLDS.get(operation, 5.0)
    
    @classmethod
    def get_memory_threshold(cls, dataset: str) -> int:
        """Get memory threshold for dataset."""
        return cls.MEMORY_THRESHOLDS.get(dataset, 500)
    
    @classmethod
    def get_test_config(cls) -> Dict[str, Any]:
        """Get complete test configuration."""
        return {
            "dataset_sizes": cls.DEFAULT_DATASET_SIZES,
            "performance_thresholds": cls.PERFORMANCE_THRESHOLDS,
            "memory_thresholds": cls.MEMORY_THRESHOLDS,
            "enable_stress_tests": os.getenv("ENABLE_STRESS_TESTS", "false").lower() == "true",
            "max_test_duration": int(os.getenv("MAX_TEST_DURATION", "300")),  # 5 minutes default
        }


# Environment-based configuration overrides
def get_environment_config() -> Dict[str, Any]:
    """Get configuration based on environment variables."""
    config = LargeDatasetTestConfig.get_test_config()
    
    # Override dataset sizes from environment
    if os.getenv("TEST_PARTS_COUNT_SMALL"):
        config["dataset_sizes"]["small"] = int(os.getenv("TEST_PARTS_COUNT_SMALL"))
    
    if os.getenv("TEST_PARTS_COUNT_MEDIUM"):
        config["dataset_sizes"]["medium"] = int(os.getenv("TEST_PARTS_COUNT_MEDIUM"))
    
    if os.getenv("TEST_PARTS_COUNT_LARGE"):
        config["dataset_sizes"]["large"] = int(os.getenv("TEST_PARTS_COUNT_LARGE"))
    
    # Override performance thresholds from environment
    if os.getenv("API_RESPONSE_THRESHOLD"):
        threshold = float(os.getenv("API_RESPONSE_THRESHOLD"))
        config["performance_thresholds"]["api_response_1k"] = threshold
        config["performance_thresholds"]["api_response_5k"] = threshold * 1.5
        config["performance_thresholds"]["api_response_10k"] = threshold * 2.5
    
    return config


# Test scenario configurations
TEST_SCENARIOS = {
    "basic_performance": {
        "description": "Basic performance testing with 1K parts",
        "parts_count": 1000,
        "include_inventory": True,
        "include_transactions": False,  # Skip transactions to avoid enum serialization issues
        "performance_threshold": 2.0
    },
    "moderate_scale": {
        "description": "Moderate scale testing with 5K parts",
        "parts_count": 5000,
        "include_inventory": True,
        "include_transactions": False,  # Skip transactions for faster generation
        "performance_threshold": 3.0
    },
    "high_scale": {
        "description": "High scale testing with 10K parts",
        "parts_count": 10000,
        "include_inventory": True,
        "include_transactions": False,
        "performance_threshold": 5.0
    },
    "stress_test": {
        "description": "Stress testing with 25K parts",
        "parts_count": 25000,
        "include_inventory": False,  # Skip inventory for faster generation
        "include_transactions": False,
        "performance_threshold": 10.0,
        "enabled": False  # Disabled by default, enable via environment
    }
}


def get_test_scenario(scenario_name: str) -> Dict[str, Any]:
    """Get test scenario configuration by name."""
    scenario = TEST_SCENARIOS.get(scenario_name, TEST_SCENARIOS["basic_performance"])
    
    # Check if stress tests are enabled
    if scenario_name == "stress_test":
        scenario["enabled"] = os.getenv("ENABLE_STRESS_TESTS", "false").lower() == "true"
    
    return scenario


def should_run_large_dataset_tests() -> bool:
    """Check if large dataset tests should be run based on environment."""
    # Skip large dataset tests in CI unless explicitly enabled
    if os.getenv("CI") and not os.getenv("ENABLE_LARGE_DATASET_TESTS"):
        return False
    
    # Skip if explicitly disabled
    if os.getenv("SKIP_LARGE_DATASET_TESTS", "false").lower() == "true":
        return False
    
    return True


def get_pytest_markers_for_scenario(scenario_name: str) -> list:
    """Get pytest markers for a test scenario."""
    markers = ["large_dataset", "performance"]
    
    scenario = get_test_scenario(scenario_name)
    
    if scenario["parts_count"] >= 10000:
        markers.append("slow")
    
    if scenario_name == "stress_test":
        markers.append("stress")
    
    return markers