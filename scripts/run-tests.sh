#!/bin/bash

# ABParts Test Execution Script
# This script provides different ways to run tests in the Docker environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

# Function to run tests in Docker
run_tests_docker() {
    local test_args="$1"
    print_status "Starting test database and dependencies..."
    
    # Start test database and dependencies
    docker-compose --profile testing up -d test_db redis
    
    # Wait for services to be healthy
    print_status "Waiting for test database to be ready..."
    docker-compose --profile testing exec test_db pg_isready -U abparts_test_user -d abparts_test
    
    # Run tests
    print_status "Running tests with args: $test_args"
    docker-compose --profile testing run --rm test pytest $test_args
    
    # Cleanup
    print_status "Cleaning up test environment..."
    docker-compose --profile testing down
}

# Function to run tests in existing API container
run_tests_api_container() {
    local test_args="$1"
    print_status "Running tests in existing API container..."
    
    # Check if API container is running
    if ! docker ps | grep -q abparts_api; then
        print_error "API container is not running. Please start it with: docker-compose up api"
        exit 1
    fi
    
    # Run tests in API container
    docker-compose exec api pytest $test_args
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] [PYTEST_ARGS]"
    echo ""
    echo "Options:"
    echo "  -h, --help          Show this help message"
    echo "  -d, --docker        Run tests in dedicated Docker test environment (default)"
    echo "  -a, --api           Run tests in existing API container"
    echo "  -u, --unit          Run only unit tests"
    echo "  -i, --integration   Run only integration tests"
    echo "  -e, --api-tests     Run only API endpoint tests"
    echo "  -c, --coverage      Run tests with coverage report"
    echo "  -f, --fast          Run tests in parallel (faster execution)"
    echo "  -v, --verbose       Run tests with verbose output"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Run all tests in Docker"
    echo "  $0 -u                                # Run only unit tests"
    echo "  $0 -c                                # Run tests with coverage"
    echo "  $0 -f                                # Run tests in parallel"
    echo "  $0 -a tests/test_organizations.py    # Run specific test file in API container"
    echo "  $0 -v -c                             # Verbose output with coverage"
}

# Parse command line arguments
DOCKER_MODE=true
TEST_ARGS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -d|--docker)
            DOCKER_MODE=true
            shift
            ;;
        -a|--api)
            DOCKER_MODE=false
            shift
            ;;
        -u|--unit)
            TEST_ARGS="$TEST_ARGS -m unit"
            shift
            ;;
        -i|--integration)
            TEST_ARGS="$TEST_ARGS -m integration"
            shift
            ;;
        -e|--api-tests)
            TEST_ARGS="$TEST_ARGS -m api"
            shift
            ;;
        -c|--coverage)
            TEST_ARGS="$TEST_ARGS --cov=app --cov-report=html --cov-report=term"
            shift
            ;;
        -f|--fast)
            TEST_ARGS="$TEST_ARGS -n auto"
            shift
            ;;
        -v|--verbose)
            TEST_ARGS="$TEST_ARGS -v"
            shift
            ;;
        *)
            # Pass remaining arguments to pytest
            TEST_ARGS="$TEST_ARGS $1"
            shift
            ;;
    esac
done

# Main execution
print_status "ABParts Test Runner"
print_status "==================="

check_docker

if [ "$DOCKER_MODE" = true ]; then
    run_tests_docker "$TEST_ARGS"
else
    run_tests_api_container "$TEST_ARGS"
fi

print_status "Tests completed!"