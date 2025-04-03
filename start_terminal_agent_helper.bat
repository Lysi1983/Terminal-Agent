@echo off

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. > error_log.txt
    echo Please install Python 3.6+ and try again. >> error_log.txt
    exit /b 1
)

:: Check for required packages
python -c "import requests" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    pip install requests >nul 2>&1
)

:: Start the application
start /b "" python gui_launcher.py