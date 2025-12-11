@echo off
REM Simple pytest wrapper for Kiro IDE test discovery

REM Set minimal environment
set DATABASE_URL=sqlite:///./test_discovery.db
set ENVIRONMENT=test_discovery
set TESTING=true
set PYTHONPATH=%~dp0backend

REM Check if this is test discovery
if "%1"=="--collect-only" (
    if "%2"=="-q" (
        REM Use our Python script for fast discovery
        python "%~dp0test-discovery.py" %*
    ) else (
        REM Regular pytest collect
        python -m pytest %*
    )
) else (
    REM For actual test runs, redirect to Docker
    echo Tests should be run in Docker environment.
    echo Use: python test-runner.py %*
    exit /b 1
)