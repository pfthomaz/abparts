# ABParts Tests

## Directory Structure

- **integration/** - Integration and API tests
- **unit/** - Unit tests (if any)
- **performance/** - Performance and scalability tests
- **fixtures/** - Test data and fixtures

## Running Tests

### Integration Tests
```bash
python tests/integration/test_name.py
```

### Performance Tests
```bash
python tests/performance/run_scalability_tests.py
```

## Test Files

- `test_*.py` - Test scripts
- `check_*.py` - Verification scripts
- `validate_*.py` - Validation scripts
- `debug_*.py` - Debugging utilities
- `diagnose_*.py` - Diagnostic tools

## Configuration

- `pytest.ini` - Pytest configuration
- `conftest.py` - Pytest fixtures and configuration
