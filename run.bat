@echo off
REM Quick start script for Drowsiness Detection System

echo.
echo ========================================
echo Real-Time Drowsiness Detection System
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

echo Starting application...
echo.
echo Controls:
echo   - Press 'Q' to quit the application
echo   - Keep face in front of camera
echo   - Good lighting is recommended
echo.
echo ========================================
echo.

REM Run the application
"venv\Scripts\python.exe" drowsiness_yawn_nolibdlib.py

pause
