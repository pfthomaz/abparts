# ABParts Testing Framework

This directory contains comprehensive testing for the ABParts system, including integration tests, performance tests, security tests, and user acceptance tests.

## Test Structure

- `conftest.py` - Pytest fixtures and configuration
- `test_business_workflows.py` - Integration tests for business workflows
- `test_security.py` - Security testing for role-based access control
- `test_performance.py` - Performance testing for data model and relationships
- `test_user_acceptance.py` - User acceptance testing scenarios
- `locustfile.py` - Load testing script using Locust

## Running Tests

### Running All Tests

To run all tests, use the `run_tests.py` script:

```bash
python run_tests.py
```

Options:
- `-v, --verbose` - Verbose output
- `-p, --pattern PATTERN` - Test pattern to match
- `--pytest-only` - Run only pytest tests
- `--unittest-only` - Run only unittest tests

### Running Specific Test Modules

To run a specific test module:

```bash
pytest tests/test_business_workflows.py -v
```

### Running Load Tests

To run load tests with Locust:

```bash
cd tests
locust -f locustfile.py
```

Then open http://localhost:8089 in your browser to start the load test.

## Test Categories

### Integration Tests

Integration tests verify that different components of the system work together correctly. These tests focus on business workflows and data flow between components.

### Security Tests

Security tests verify that the role-based access control system works correctly and that users can only access resources they are authorized to access.

### Performance Tests

Performance tests verify that the system performs well under various load conditions and that the data model and relationships are optimized for performance.

### User Acceptance Tests

User acceptance tests verify that the system meets the requirements from an end-user perspective. These tests focus on user workflows and scenarios.

## Monitoring and Alerting

The system includes a monitoring and alerting system that tracks system health, performance metrics, and generates alerts when issues are detected.

### Monitoring Endpoints

- `/monitoring/health` - System health status
- `/monitoring/metrics` - System metrics (admin only)
- `/monitoring/alerts` - Active alerts (admin only)
- `/monitoring/alert-history` - Alert history (admin only)

### Metrics Collected

- System metrics: CPU, memory, disk usage
- Application metrics: Request rate, error rate, response time
- Database metrics: Connection pool usage, query time
- Redis metrics: Memory usage, connected clients

### Alerts

The system generates alerts for various conditions:
- High CPU/memory/disk usage
- High API error rate or latency
- High database latency or connection pool usage
- System health degradation or failure