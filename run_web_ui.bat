@echo off
setlocal

rem Check for virtual environment
if not exist "%~dp0venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found in %~dp0venv
    pause
    exit /b 1
)

rem Set PYTHONPATH
set "PYTHONPATH=%~dp0"

echo ==================================================
echo Audiobooker Web UI
echo ==================================================
echo Launching web browser...
start "" "http://localhost:8000"
echo Starting server at http://localhost:8000
echo.

"%~dp0venv\Scripts\python.exe" "%~dp0ui\app.py"

endlocal
