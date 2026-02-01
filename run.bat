@echo off
setlocal

rem ==================================================================================
rem Audiobooker Launcher
rem ==================================================================================

rem Check for virtual environment
if not exist "%~dp0venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found in %~dp0venv
    echo Please create the virtual environment according to the README:
    echo   python -m venv venv
    echo   venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

rem Set PYTHONPATH to the repo root so imports work
set "PYTHONPATH=%~dp0"

rem Define paths
set "PYTHON_EXE=%~dp0venv\Scripts\python.exe"
set "MAIN_SCRIPT=%~dp0scripts\generate_audiobook.py"

rem Check if arguments were provided
if "%~1"=="" goto :InteractiveMode

:RunMode
rem Check args to see if we should auto-name the output folder
set "HAS_OUT="
set "PDF_NAME="

rem Naive arg parsing to find input PDF and check for --out flag
for %%a in (%*) do (
    if /I "%%~a"=="--out" set HAS_OUT=1
    if /I "%%~xa"==".pdf" set "PDF_NAME=%%~na"
)

rem If --out is not specified and we found a PDF, use the PDF name as the output folder
if not defined HAS_OUT (
    if defined PDF_NAME (
        echo [Run.bat] Auto-setting output directory to: "%PDF_NAME%"
        "%PYTHON_EXE%" "%MAIN_SCRIPT%" %* --out "%PDF_NAME%"
        goto :End
    )
)

rem Otherwise run exactly as provided
"%PYTHON_EXE%" "%MAIN_SCRIPT%" %*
goto :End

:InteractiveMode
echo ==================================================
echo Audiobooker CLI
echo ==================================================
echo.
echo Usage: %~nx0 [pdf_file] [options]
echo.
echo No arguments provided. Showing help options below:
echo --------------------------------------------------
"%PYTHON_EXE%" "%MAIN_SCRIPT%" --help
echo --------------------------------------------------
echo.
echo To use this tool, drag and drop a PDF file onto this script
echo or run it from the command line.
echo.
echo Dropping into a shell with environment configured...
echo You can run commands like: python scripts/generate_audiobook.py ...
echo.
cmd /k
goto :End

:End
endlocal
