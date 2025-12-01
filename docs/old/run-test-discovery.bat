@echo off
REM Test discovery batch file for Kiro IDE
REM This script provides fast test discovery without requiring Docker

REM Change to the correct directory
cd /d "%~dp0"

REM Use our Python-based test discovery script with explicit exit
python test-discovery.py %*
exit /b %ERRORLEVEL%