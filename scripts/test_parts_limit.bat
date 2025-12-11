@echo off
REM Test script to validate the removal of the 200 parts limit
REM This script creates 500+ parts and tests system performance

echo 🚀 Testing Parts Limit Removal
echo ================================

REM Check if Docker containers are running
docker-compose ps | findstr "Up" >nul
if %errorlevel% neq 0 (
    echo ❌ Docker containers are not running. Starting them...
    docker-compose up -d
    echo ⏳ Waiting for containers to be ready...
    timeout /t 10 /nobreak >nul
)

REM Check if the API is responding
echo 🔍 Checking API health...
curl -s http://localhost:8000/health >nul
if %errorlevel% neq 0 (
    echo ❌ API is not responding. Please check the backend container.
    exit /b 1
)

echo ✅ API is responding

REM Run the parts creation test
echo.
echo 🔧 Running parts creation test...
echo ================================

REM Execute the test script inside the backend container
docker-compose exec -T api python test_create_500_parts.py

REM Check the exit code
if %errorlevel% equ 0 (
    echo.
    echo ✅ Parts creation test completed successfully!
    echo.
    echo 🌐 Now testing API endpoints...
    echo ================================
    
    REM Test the API endpoints
    docker-compose exec -T api python test_api_with_500_parts.py
    
    if %errorlevel% equ 0 (
        echo.
        echo 🎉 All tests completed successfully!
        echo.
        echo 📋 Frontend Testing Instructions:
        echo 1. Open the web interface: http://localhost:3000
        echo 2. Login with:
        echo    - Username: superadmin
        echo    - Password: superadmin
        echo 3. Navigate to the Parts page
        echo 4. Verify you can see more than 200 parts
        echo 5. Try creating a new part
        echo 6. Test search and filtering functionality
        echo 7. Check that pagination works correctly
    ) else (
        echo.
        echo ❌ API tests failed!
        echo The parts were created but API access has issues.
        exit /b 1
    )
) else (
    echo.
    echo ❌ Parts creation test failed!
    echo Check the error messages above for details.
    exit /b 1
)

pause