# Parts Performance Testing Guide

This document describes the comprehensive performance testing suite for the ABParts system, specifically designed to validate system performance with large parts catalogs (1K, 5K, and 10K+ parts).

## Overview

The performance testing suite includes:

1. **API Performance Tests** - Test REST API endpoints with large datasets
2. **Database Query Performance Tests** - Validate database query execution times and index usage
3. **Frontend Performance Tests** - Test React component rendering and user interaction performance
4. **Integration Performance Tests** - End-to-end performance validation

## Test Structure

### Backend Tests

#### API Performance Tests (`backend/tests/test_parts_api_performance.py`)
- Tests parts list endpoint with different pagination sizes
- Validates search performance with multilingual support
- Tests filtering performance with various combinations
- Measures parts with inventory endpoint performance
- Includes performance threshold validation

#### Database Query Performance Tests (`backend/tests/test_database_query_performance.py`)
- Tests basic SQL query performance
- Validates search query optimization
- Tests database index usage and effectiveness
- Measures JOIN query performance
- Includes EXPLAIN ANALYZE for query plan validation

### Frontend Tests

#### Parts Management Performance Tests (`frontend/src/tests/parts-performance.test.js`)
- Tests component rendering performance with large datasets
- Validates search debouncing functionality
- Tests pagination performance
- Measures filtering performance
- Includes memory leak detection

### Configuration

#### Test Configuration (`backend/tests/test_config_large_datasets.py`)
- Configurable dataset sizes (1K, 5K, 10K+ parts)
- Performance thresholds for different operations
- Memory usage thresholds
- Test scenario definitions

#### Test Data Generators (`backend/tests/test_data_generators.py`)
- Generates realistic test data at scale
- Supports configurable parts counts
- Includes inventory and transaction data generation
- Optimized for large dataset creation

## Running Performance Tests

### Quick Start

```bash
# Run all performance tests
python test_parts_performance.py all

# Run specific test category
python test_parts_performance.py api
python test_parts_performance.py database
python test_parts_performance.py frontend

# Setup test data first
python test_parts_performance.py setup
```

### Comprehensive Testing

```bash
# Run comprehensive performance test suite
python run_parts_performance_tests.py
```

### Docker Commands

```bash
# Run API performance tests in Docker
docker-compose exec -T api python -m pytest tests/test_parts_api_performance.py -v

# Run database performance tests in Docker
docker-compose exec -T api python -m pytest tests/test_database_query_performance.py -v

# Run frontend performance tests in Docker
docker-compose exec -T web npm test -- src/tests/parts-performance.test.js --watchAll=false
```

## Performance Thresholds

### API Response Times
- **1K parts**: < 2.0 seconds
- **5K parts**: < 3.0 seconds  
- **10K parts**: < 5.0 seconds

### Database Query Times
- **1K parts**: < 1.0 second
- **5K parts**: < 2.0 seconds
- **10K parts**: < 3.0 seconds

### Frontend Rendering
- **100 parts**: < 500ms
- **500 parts**: < 1000ms
- **1000+ parts**: < 2000ms

## Test Scenarios

### Basic Performance (1,000 parts)
- Full test coverage including inventory and transactions
- Validates all API endpoints and database operations
- Tests frontend component performance
- Performance threshold: 2.0s for API, 1.0s for database

### Moderate Scale (5,000 parts)
- Focused on core operations
- Reduced transaction generation for faster setup
- Performance threshold: 3.0s for API, 2.0s for database

### High Scale (10,000+ parts)
- Minimal test scope for large datasets
- Basic operations only
- Performance threshold: 5.0s for API, 3.0s for database

## Environment Variables

```bash
# Enable large dataset tests
export ENABLE_LARGE_DATASET_TESTS=true

# Enable stress tests (25K+ parts)
export ENABLE_STRESS_TESTS=true

# Skip large dataset tests
export SKIP_LARGE_DATASET_TESTS=true

# Custom dataset sizes
export TEST_PARTS_COUNT_SMALL=1000
export TEST_PARTS_COUNT_MEDIUM=5000
export TEST_PARTS_COUNT_LARGE=10000

# Custom performance thresholds
export API_RESPONSE_THRESHOLD=2.0
```

## Database Indexes

The performance tests validate the following database indexes:

1. **Unique Index**: `part_number` (already exists)
2. **Composite Index**: `(part_type, is_proprietary)` for filtering
3. **Manufacturer Index**: `manufacturer` for manufacturer-based queries
4. **Full-text Index**: `name` for multilingual search (if supported)

## Troubleshooting

### Common Issues

1. **Tests timeout**: Increase timeout values in test configuration
2. **Memory issues**: Reduce dataset sizes or run tests individually
3. **Docker connectivity**: Ensure all services are running with `docker-compose ps`
4. **Database connection**: Check database service health

### Performance Debugging

1. **Slow API responses**: Check database query performance
2. **Slow database queries**: Validate index usage with EXPLAIN ANALYZE
3. **Frontend lag**: Check component re-rendering and memory usage
4. **Memory leaks**: Monitor memory usage during test execution

### Test Data Issues

1. **Generation fails**: Check database connectivity and permissions
2. **Large datasets**: Ensure sufficient disk space and memory
3. **Cleanup**: Tests use transactions that rollback automatically

## Continuous Integration

### GitHub Actions / CI Integration

```yaml
# Example CI configuration
- name: Run Performance Tests
  run: |
    docker-compose up -d db redis api
    sleep 10
    python test_parts_performance.py all
  env:
    ENABLE_LARGE_DATASET_TESTS: true
    MAX_TEST_DURATION: 300
```

### Performance Monitoring

The test suite generates detailed performance reports including:
- Response time metrics
- Database query execution times
- Memory usage statistics
- Success/failure rates
- Performance threshold compliance

Results are saved to JSON files for historical tracking and analysis.

## Best Practices

1. **Run tests in isolation**: Avoid running other heavy processes during testing
2. **Monitor resources**: Watch CPU, memory, and disk usage during tests
3. **Regular execution**: Run performance tests regularly to catch regressions
4. **Baseline establishment**: Establish performance baselines for comparison
5. **Environment consistency**: Use consistent test environments for reliable results

## Support

For issues with performance tests:
1. Check Docker service status: `docker-compose ps`
2. Review test logs for specific error messages
3. Validate database connectivity and permissions
4. Ensure sufficient system resources (CPU, memory, disk)
5. Check environment variable configuration