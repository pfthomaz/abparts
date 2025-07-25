# ABParts Testing Guide

## Overview

ABParts uses a Docker-based testing environment with pytest. Tests run inside Docker containers to ensure consistency with the production environment.

## Quick Start

### Running Tests

```bash
# Run all tests in existing API container (fastest for development)
docker-compose exec api python -m pytest

# Run specific test file
docker-compose exec api python -m pytest tests/test_organization_crud_functions.py

# Run specific test
docker-compose exec api python -m pytest tests/test_organization_crud_functions.py::TestGetPotentialParentOrganizations::test_supplier_potential_parents_returns_customer_and_oraseas -v

# Run with coverage
docker-compose exec api python -m pytest --cov=app --cov-report=html

# Run tests in dedicated test environment (isolated)
docker-compose --profile testing run --rm test pytest
```

### Using Test Runner Scripts

```bash
# Windows
python test-runner.py
python test-runner.py tests/test_organization_crud_functions.py
python test-runner.py --cov=app --cov-report=html

# Linux/Mac
./scripts/run-tests.sh
./scripts/run-tests.sh -c  # with coverage
./scripts/run-tests.sh -u  # unit tests only
```

## Test Organization

```
backend/tests/
├── conftest.py                 # Test configuration and fixtures
├── test_business_workflows.py # Business logic integration tests
├── test_integration_workflows.py # Cross-system integration tests
├── test_organization_*.py     # Organization-related tests
├── test_user_*.py            # User management tests
├── test_security.py          # Security and authentication tests
├── test_performance.py       # Performance and load tests
└── test_user_acceptance.py   # User acceptance scenarios
```

## Test Categories

Tests are organized with pytest markers:

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Database integration tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.slow` - Performance/load tests
- `@pytest.mark.security` - Security-related tests
- `@pytest.mark.business` - Business workflow tests

### Running Specific Categories

```bash
# Run only unit tests
docker-compose exec api python -m pytest -m unit

# Run only integration tests
docker-compose exec api python -m pytest -m integration

# Run only API tests
docker-compose exec api python -m pytest -m api

# Skip slow tests
docker-compose exec api python -m pytest -m "not slow"
```

## Test Environment

### Docker Services

- **test_db**: Isolated PostgreSQL database for testing
- **test**: Dedicated container for running tests
- **api**: Development API container (can also run tests)

### Database

Tests use a separate test database (`abparts_test`) with automatic transaction rollback for isolation.

### Configuration

- `backend/pytest.ini` - Pytest configuration
- `backend/tests/conftest.py` - Test fixtures and setup
- `docker-compose.yml` - Test services configuration

## IDE Integration

### Kiro IDE

Due to the Docker-based setup, automatic test discovery may not work perfectly in Kiro IDE. Use these approaches:

1. **Manual Test Execution**: Run tests using the terminal commands above
2. **Test Runner Script**: Use `python test-runner.py` for easier execution
3. **Docker Commands**: Use Docker Compose commands directly

### Disabling Auto-Discovery

If you're seeing "Unittest Discovery Error" in your IDE:

1. Disable automatic test discovery in your IDE settings
2. Use manual test execution via terminal
3. Use the provided test runner scripts

## Coverage Reports

```bash
# Generate HTML coverage report
docker-compose exec api python -m pytest --cov=app --cov-report=html

# View coverage report
# Open backend/htmlcov/index.html in your browser

# Generate XML coverage report (for CI)
docker-compose exec api python -m pytest --cov=app --cov-report=xml
```

## Debugging Tests

### Verbose Output

```bash
docker-compose exec api python -m pytest -v
```

### Debug Specific Test

```bash
docker-compose exec api python -m pytest tests/test_organization_crud_functions.py::TestGetPotentialParentOrganizations::test_supplier_potential_parents_returns_customer_and_oraseas -v -s
```

### Interactive Debugging

```bash
# Add breakpoint in test code with:
import pdb; pdb.set_trace()

# Run test with:
docker-compose exec api python -m pytest tests/your_test.py -s
```

## Common Issues

### "Unittest Discovery Error"

This is expected when using Docker-based testing. The IDE cannot discover tests because they require the Docker environment. Use manual test execution instead.

### Database Connection Errors

Make sure the database service is running:
```bash
docker-compose up -d db
```

### Import Errors

Tests must run inside the Docker container where all dependencies are installed.

### Permission Errors

On Windows, make sure Docker Desktop is running and you have proper permissions.

## Best Practices

1. **Write tests that run in Docker** - Don't rely on local environment
2. **Use fixtures from conftest.py** - Leverage existing test data factories
3. **Test isolation** - Each test should be independent
4. **Clear test names** - Use descriptive test method names
5. **Test categories** - Use appropriate pytest markers
6. **Coverage goals** - Aim for 80%+ code coverage

## Continuous Integration

Tests run automatically in CI/CD pipelines using the same Docker environment:

```yaml
# Example GitHub Actions
- name: Run Tests
  run: docker-compose --profile testing run --rm test pytest --cov=app --cov-report=xml
```

## Troubleshooting

### Container Issues

```bash
# Restart containers
docker-compose down
docker-compose up -d

# Rebuild containers
docker-compose build --no-cache
```

### Database Issues

```bash
# Reset test database
docker-compose --profile testing down
docker-compose --profile testing up -d test_db
```

### Performance Issues

```bash
# Run tests in parallel
docker-compose exec api python -m pytest -n auto
```