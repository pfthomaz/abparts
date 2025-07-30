@echo off
REM ABParts Windows Firewall Fix
REM Run this batch file as Administrator to allow mobile access

echo.
echo === ABParts Windows Firewall Configuration ===
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [INFO] Running as Administrator - proceeding with firewall configuration...
) else (
    echo [ERROR] This script must be run as Administrator!
    echo [INFO] Right-click this file and select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo.
echo [INFO] Adding firewall rules for ABParts mobile access...
echo.

REM Add firewall rules for ABParts ports
netsh advfirewall firewall add rule name="ABParts Frontend" dir=in action=allow protocol=TCP localport=3000
if %errorLevel% == 0 (
    echo [SUCCESS] Added rule for Frontend (port 3000)
) else (
    echo [ERROR] Failed to add rule for Frontend
)

netsh advfirewall firewall add rule name="ABParts API" dir=in action=allow protocol=TCP localport=8000
if %errorLevel% == 0 (
    echo [SUCCESS] Added rule for API (port 8000)
) else (
    echo [ERROR] Failed to add rule for API
)

netsh advfirewall firewall add rule name="ABParts Admin" dir=in action=allow protocol=TCP localport=8080
if %errorLevel% == 0 (
    echo [SUCCESS] Added rule for Admin (port 8080)
) else (
    echo [ERROR] Failed to add rule for Admin
)

echo.
echo [SUCCESS] Firewall configuration complete!
echo.
echo [INFO] Your mobile devices should now be able to access ABParts at:

REM Try to read HOST_IP from .env.local
if exist ".env.local" (
    for /f "tokens=2 delims==" %%a in ('findstr "HOST_IP=" .env.local') do set HOST_IP=%%a
    if defined HOST_IP (
        echo   Frontend: http://%HOST_IP%:3000
        echo   API: http://%HOST_IP%:8000
        echo   API Docs: http://%HOST_IP%:8000/docs
        echo   Admin: http://%HOST_IP%:8080
    ) else (
        echo   Frontend: http://YOUR_IP:3000
        echo   API: http://YOUR_IP:8000
        echo   Admin: http://YOUR_IP:8080
    )
) else (
    echo   Frontend: http://YOUR_IP:3000
    echo   API: http://YOUR_IP:8000
    echo   Admin: http://YOUR_IP:8080
)

echo.
echo [INFO] Make sure your mobile device is on the same WiFi network.
echo [INFO] Test the API docs first: http://YOUR_IP:8000/docs
echo.
pause