@echo off
echo Installing Website Scraper MCP Server...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.9 or later.
    exit /b 1
)

REM Check if uv is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing uv...
    pip install uv
)

REM Install the package in development mode
echo Installing package...
uv pip install -e .

REM Install Playwright browsers
echo Installing Playwright browsers...
python -m playwright install chromium

echo Installation complete!
echo.
echo To run the MCP server:
echo uvx website-scraper-mcp
echo.
echo To use with Kiro, make sure you have configured the MCP server in .kiro/settings/mcp.json