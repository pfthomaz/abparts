# Large Dataset Testing Guide

This guide explains how to use the enhanced test data generation capabilities that support datasets beyond the previous 200-part limit.

## Overview

The ABParts system now supports unlimited parts management with enhanced test data generation for performance validation. The new test data generators can create datasets with 1,000, 5,000, 10,000+ parts for comprehensive testing.

## New Test Data Generators

### Files Added/Modified

1. **`test_data_generators.py`** - Enhanced test data generation functions
2. **`test_large_dataset_performance.py`** - Performance tests for large datasets
3. **`test_config_large_datasets.py`** - Configuration for large dataset testing
4. **`test_data_generators_validation.py`** - Validation tests for generators
5. **`run_large_dataset_tests.py`** - Test runner for large dataset scenarios
6. **`conftest.py`** - Updated with new fixtures for large datasets

### Key Features

- **Configurable Dataset Sizes**: Generate 1K, 5K, 10K, or custom number of parts
- **Realistic Test Data**: Parts with varied types, manufacturers, and characteristics
- **Performance Monitoring**: Built-in timing and memory usage tracking
- **Scalable Architecture**: Efficient generation and cleanup for large datasets

## Usage Examples

### Basic Usage

```python
from tests.test_data_generators import generate_large_parts_dataset

# Generate 1,000 parts with inventory and transactions
data = generate_large_parts_dataset(
    db_session, 
    parts_count=1000,
    include_inventory=True,
    include_transactions=True
)

print(f"Generated {len(data['parts'])} parts")
print(f"Generated {len(data['inventory'])} inventory records")
print(f"Generated {len(data['transactions'])} transactions")
```

### Using the Generator Class

```python
from tests.test_data_generators import LargeDatasetGenerator

generator = LargeDatasetGenerator(db_session)
data = generator.generate_parts_dataset(
    parts_count=5000,
    include_inventory=True,
    include_transactions=False
)
```

### Performance Test Scenarios

```python
from tests.test_data_generators import generate_performance_test_scenarios

scenarios = generate_performance_test_scenarios(db_session)
# Creates scenarios with 1K, 5K, and 10K parts
```

## Running Large Dataset Tests

### Using the Test Runner

```bash
# Run basic performance tests (1K parts)
python backend/run_large_dataset_tests.py --scenario basic_performance

# Run moderate scale tests (5K parts)
python backend/run_large_dataset_tests.py --scenario moderate_scale

# Run high scale tests (10K parts)
python backend/run_large_dataset_tests.py --scenario high_scale

# Run all scenarios
python backend/run_large_dataset_tests.py --scenario all

# Show current configuration
python backend/run_large_dataset_tests.py --config
```

### Using pytest Directly

```bash
# Run all large dataset tests
pytest backend/tests/test_large_dataset_performance.py -m "large_dataset"

# Run specific test with verbose output
pytest backend/tests/test_large_dataset_performance.py::TestLargeDatasetPerformance::test_parts_api_performance_1k_parts -v

# Run validation tests
pytest backend/tests/test_data_generators_validation.py -v
```

## Test Fixtures

### New Fixtures Available

- `large_parts_dataset_1k` - Dataset with 1,000 parts
- `large_parts_dataset_5k` - Dataset with 5,000 parts  
- `large_parts_dataset_10k` - Dataset with 10,000+ parts

### Using Fixtures in Tests

```python
def test_my_feature(self, large_parts_dataset_1k):
    """Test feature with 1K parts dataset."""
    data = large_parts_dataset_1k
    parts = data["parts"]
    
    # Your test logic here
    assert len(parts) == 1000
```

## Configuration

### Environment Variables

- `ENABLE_LARGE_DATASET_TESTS` - Enable/disable large dataset tests
- `SKIP_LARGE_DATASET_TESTS` - Skip large dataset tests
- `ENABLE_STRESS_TESTS` - Enable stress tests with 25K+ parts
- `TEST_PARTS_COUNT_SMALL` - Override small dataset size (default: 1000)
- `TEST_PARTS_COUNT_MEDIUM` - Override medium dataset size (default: 5000)
- `TEST_PARTS_COUNT_LARGE` - Override large dataset size (default: 10000)
- `API_RESPONSE_THRESHOLD` - Override API response time threshold
- `MAX_TEST_DURATION` - Maximum test duration in seconds (default: 300)

### Test Scenarios

1. **basic_performance** - 1K parts with full data
2. **moderate_scale** - 5K parts with inventory only
3. **high_scale** - 10K parts with inventory only
4. **stress_test** - 25K parts (disabled by default)

## Performance Thresholds

### Default Thresholds

- **API Response Times**:
  - 1K parts: 2.0 seconds
  - 5K parts: 3.0 seconds
  - 10K parts: 5.0 seconds

- **Database Query Times**:
  - 1K parts: 1.0 second
  - 5K parts: 2.0 seconds
  - 10K parts: 3.0 seconds

- **Memory Usage**:
  - 1K parts: 100 MB increase
  - 5K parts: 500 MB increase
  - 10K parts: 1000 MB increase

## Test Markers

Use pytest markers to run specific test categories:

- `@pytest.mark.large_dataset` - Tests with large datasets
- `@pytest.mark.performance` - Performance tests with timing assertions
- `@pytest.mark.slow` - Slow tests (may take several minutes)

## Best Practices

### For Test Development

1. **Use Appropriate Dataset Size**: Choose the smallest dataset that validates your feature
2. **Clean Up Resources**: Use fixtures that automatically clean up after tests
3. **Monitor Performance**: Include timing assertions in performance-critical tests
4. **Use Realistic Data**: Generated parts have realistic names, types, and characteristics

### For CI/CD

1. **Conditional Execution**: Large dataset tests are disabled by default in CI
2. **Timeout Configuration**: Set appropriate timeouts for long-running tests
3. **Resource Monitoring**: Monitor memory and CPU usage during test execution
4. **Parallel Execution**: Consider running large dataset tests in parallel when possible

## Troubleshooting

### Common Issues

1. **Memory Issues**: Reduce dataset size or disable inventory/transactions generation
2. **Timeout Issues**: Increase `MAX_TEST_DURATION` environment variable
3. **Database Issues**: Ensure test database has sufficient resources
4. **Import Errors**: Ensure all dependencies are installed and database is configured

### Performance Optimization

1. **Batch Operations**: Generators use batch operations for efficiency
2. **Selective Generation**: Skip inventory/transactions when not needed
3. **Database Indexing**: Ensure proper indexes are in place for test queries
4. **Connection Pooling**: Use appropriate database connection settings

## Migration from Previous Tests

### Changes Made

1. **Removed 200-part limit** from test configurations
2. **Updated performance test fixtures** to support larger datasets
3. **Added configurable dataset sizes** via environment variables
4. **Enhanced test data realism** with varied part characteristics

### Backward Compatibility

- Existing tests continue to work unchanged
- Default dataset sizes maintain reasonable performance
- New fixtures are optional and don't affect existing tests
- Configuration is backward compatible with previous settings