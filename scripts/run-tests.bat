@echo off
REM ABParts Test Execution Script for Windows
REM This script provides different ways to run tests in the Docker environment

setlocal enabledelayedexpansion

REM Default values
set DOCKER_MODE=true
set TEST_ARGS=

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :run_tests
if "%~1"=="-h" goto :show_usage
if "%~1"=="--help" goto :show_usage
if "%~1"=="-a" set DOCKER_MODE=false & shift & goto :parse_args
if "%~1"=="--api" set DOCKER_MODE=false & shift & goto :parse_args
if "%~1"=="-u" set TEST_ARGS=%TEST_ARGS% -m unit & shift & goto :parse_args
if "%~1"=="--unit" set TEST_ARGS=%TEST_ARGS% -m unit & shift & goto :parse_args
if "%~1"=="-i" set TEST_ARGS=%TEST_ARGS% -m integration & shift & goto :parse_args
if "%~1"=="--integration" set TEST_ARGS=%TEST_ARGS% -m integration & shift & goto :parse_args
if "%~1"=="-e" set TEST_ARGS=%TEST_ARGS% -m api & shift & goto :parse_args
if "%~1"=="--api-tests" set TEST_ARGS=%TEST_ARGS% -m api & shift & goto :parse_args
if "%~1"=="-c" set TEST_ARGS=%TEST_ARGS% --cov=app --cov-report=html --cov-report=term & shift & goto :parse_args
if "%~1"=="--coverage" set TEST_ARGS=%TEST_ARGS% --cov=app --cov-report=html --cov-report=term & shift & goto :parse_args
if "%~1"=="-f" set TEST_ARGS=%TEST_ARGS% -n auto & shift & goto :parse_args
if "%~1"=="--fast" set TEST_ARGS=%TEST_ARGS% -n auto & shift & goto :parse_args
if "%~1"=="-v" set TEST_ARGS=%TEST_ARGS% -v & shift & goto :parse_args
if "%~1"=="--verbose" set TEST_ARGS=%TEST_ARGS% -v & shift & goto :parse_args
set TEST_ARGS=%TEST_ARGS% %~1
shift
goto :parse_args

:show_usage
echo Usage: %0 [OPTIONS] [PYTEST_ARGS]
echo.
echo Options:
echo   -h, --help          Show this help message
echo   -a, --api           Run tests in existing API container
echo   -u, --unit          Run only unit tests
echo   -i, --integration   Run only integration tests
echo   -e, --api-tests     Run only API endpoint tests
echo   -c, --coverage      Run tests with coverage report
echo   -f, --fast          Run tests in parallel (faster execution)
echo   -v, --verbose       Run tests with verbose output
echo.
echo Examples:
echo   %0                                    # Run all tests in Docker
echo   %0 -u                                # Run only unit tests
echo   %0 -c                                # Run tests with coverage
echo   %0 -a tests/test_organizations.py    # Run specific test file in API container
goto :eof

:run_tests
echo [INFO] ABParts Test Runner
echo [INFO] ===================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker and try again.
    exit /b 1
)

if "%DOCKER_MODE%"=="true" (
    echo [INFO] Starting test database and dependencies...
    docker-compose --profile testing up -d test_db redis
    
    echo [INFO] Waiting for test database to be ready...
    timeout /t 5 /nobreak >nul
    
    echo [INFO] Running tests with args: %TEST_ARGS%
    docker-compose --profile testing run --rm test pytest %TEST_ARGS%
    
    echo [INFO] Cleaning up test environment...
    docker-compose --profile testing down
) else (
    echo [INFO] Running tests in existing API container...
    docker-compose exec api pytest %TEST_ARGS%
)

echo [INFO] Tests completed!
goto :eof