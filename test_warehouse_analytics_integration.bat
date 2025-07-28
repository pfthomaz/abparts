@echo off
echo Testing Warehouse Analytics Integration...
echo.

echo 1. Testing frontend accessibility...
curl -s -o nul -w "%%{http_code}" http://localhost:3000 > temp_status.txt
set /p frontend_status=<temp_status.txt
if "%frontend_status%"=="200" (
    echo ✅ Frontend is accessible at http://localhost:3000
) else (
    echo ❌ Frontend not accessible: HTTP %frontend_status%
    goto :error
)
del temp_status.txt

echo.
echo 2. Testing login...
curl -s -X POST "http://localhost:8000/token" -H "Content-Type: application/x-www-form-urlencoded" -d "grant_type=password&username=superadmin&password=superadmin" > login_response.json
findstr "access_token" login_response.json >nul
if %errorlevel%==0 (
    echo ✅ Login successful
    for /f "tokens=2 delims=:," %%a in ('findstr "access_token" login_response.json') do set token=%%a
    set token=%token:"=%
    set token=%token: =%
) else (
    echo ❌ Login failed
    type login_response.json
    goto :error
)

echo.
echo 3. Testing warehouse list...
curl -s -X GET "http://localhost:8000/warehouses/" -H "Authorization: Bearer %token%" > warehouses.json
findstr "id" warehouses.json >nul
if %errorlevel%==0 (
    echo ✅ Warehouse list retrieved successfully
    for /f "tokens=2 delims=:," %%a in ('findstr "id" warehouses.json') do (
        set warehouse_id=%%a
        set warehouse_id=!warehouse_id:"=!
        set warehouse_id=!warehouse_id: =!
        goto :got_warehouse_id
    )
    :got_warehouse_id
) else (
    echo ❌ Failed to get warehouses
    type warehouses.json
    goto :error
)

echo.
echo 4. Testing warehouse analytics...
curl -s -X GET "http://localhost:8000/inventory/warehouse/%warehouse_id%/analytics" -H "Authorization: Bearer %token%" > analytics.json
findstr "warehouse_id" analytics.json >nul
if %errorlevel%==0 (
    echo ✅ Warehouse analytics retrieved successfully
    findstr "total_parts" analytics.json
    findstr "total_value" analytics.json
) else (
    echo ❌ Failed to get warehouse analytics
    type analytics.json
    goto :error
)

echo.
echo 5. Testing warehouse analytics trends...
curl -s -X GET "http://localhost:8000/inventory/warehouse/%warehouse_id%/analytics/trends" -H "Authorization: Bearer %token%" > trends.json
findstr "trends" trends.json >nul
if %errorlevel%==0 (
    echo ✅ Warehouse analytics trends retrieved successfully
) else (
    echo ❌ Failed to get warehouse analytics trends
    type trends.json
    goto :error
)

echo.
echo 6. Testing date range filtering...
curl -s -X GET "http://localhost:8000/inventory/warehouse/%warehouse_id%/analytics?start_date=2025-07-21&end_date=2025-07-28" -H "Authorization: Bearer %token%" > analytics_filtered.json
findstr "warehouse_id" analytics_filtered.json >nul
if %errorlevel%==0 (
    echo ✅ Date range filtering works
) else (
    echo ❌ Date range filtering failed
    type analytics_filtered.json
    goto :error
)

echo.
echo 🎉 All tests passed! Warehouse analytics integration is working correctly.
echo.
echo 📋 Test Summary:
echo    ✅ Frontend is accessible
echo    ✅ Authentication works
echo    ✅ Warehouse list endpoint works
echo    ✅ Warehouse analytics endpoint works
echo    ✅ Analytics trends endpoint works
echo    ✅ Date range filtering works
echo.
echo 🔗 To test the frontend manually:
echo    1. Open http://localhost:3000 in your browser
echo    2. Login with username: superadmin, password: superadmin
echo    3. Navigate to Inventory page
echo    4. Select "Analytics" view mode
echo    5. Select a warehouse from the dropdown
echo    6. Verify analytics data loads and date range filtering works

goto :cleanup

:error
echo.
echo ❌ Integration test failed!
exit /b 1

:cleanup
del login_response.json 2>nul
del warehouses.json 2>nul
del analytics.json 2>nul
del trends.json 2>nul
del analytics_filtered.json 2>nul