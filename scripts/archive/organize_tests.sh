#!/bin/bash

echo "========================================="
echo "Organize Test Files"
echo "========================================="
echo ""
echo "This will move all test files to a tests/ directory."
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Cancelled."
    exit 1
fi

# Create test directory structure
mkdir -p tests/integration
mkdir -p tests/unit
mkdir -p tests/performance
mkdir -p tests/fixtures

echo ""
echo "Moving test files..."

# Move test Python files
MOVED_TESTS=0
for file in test_*.py check_*.py validate_*.py debug_*.py diagnose_*.py verify_*.py; do
    if [ -f "$file" ]; then
        mv "$file" tests/integration/
        ((MOVED_TESTS++))
    fi
done

# Move test shell scripts
for file in test_*.sh check_*.sh debug_*.sh diagnose_*.sh verify_*.sh; do
    if [ -f "$file" ]; then
        mv "$file" tests/integration/
        ((MOVED_TESTS++))
    fi
done

# Move test configuration files
for file in pytest.ini conftest.py pytest*.py; do
    if [ -f "$file" ]; then
        mv "$file" tests/
        ((MOVED_TESTS++))
    fi
done

# Move test data files
for file in test_*.json test_*.html test_*.md; do
    if [ -f "$file" ]; then
        mv "$file" tests/fixtures/
        ((MOVED_TESTS++))
    fi
done

# Move performance/scalability test files
for file in *scalability*.py *performance*.py run_*_tests.py; do
    if [ -f "$file" ]; then
        mv "$file" tests/performance/
        ((MOVED_TESTS++))
    fi
done

# Create README for tests directory
cat > tests/README.md << 'EOF'
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
EOF

echo ""
echo "========================================="
echo "✓ Test Organization Complete!"
echo "========================================="
echo ""
echo "Moved $MOVED_TESTS test files to tests/"
echo ""
echo "Test directory structure:"
echo "  tests/"
echo "    ├── integration/    (test scripts)"
echo "    ├── performance/    (performance tests)"
echo "    ├── fixtures/       (test data)"
echo "    └── README.md"
echo ""
echo "To see what was moved:"
echo "  ls tests/integration/"
echo "  ls tests/performance/"
echo ""
