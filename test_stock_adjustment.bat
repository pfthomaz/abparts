@echo off
echo Testing Stock Adjustment Fix
echo ============================
echo.
echo Make sure your backend is running on http://localhost:8000
echo and you have admin credentials set up.
echo.
pause
echo.
python test_stock_adjustment_fix.py
echo.
pause