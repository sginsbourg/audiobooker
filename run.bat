@echo off
setlocal enabledelayedexpansion

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
set "OUT_DIR=out"
set "PDF_PATH="
set "HAS_OUT="

rem Parse arguments to find input PDF and check for --out flag
set "ARGS="
:ParseArgs
if "%~1"=="" goto :AfterParse
set "CURR_ARG=%~1"
set "ARGS=!ARGS! "%CURR_ARG%""

rem Identify PDF and explicit --out
if /I "!CURR_ARG:~-4!"==".pdf" (
    set "PDF_PATH=%~f1"
    set "PDF_NAME=%~n1"
)
if /I "!CURR_ARG!"=="--out" (
    set "HAS_OUT=1"
    shift
    set "OUT_DIR=%~1"
    set "ARGS=!ARGS! "%~1""
)
shift
goto :ParseArgs

:AfterParse
rem If --out is not specified and we found a PDF, use the PDF name as the output folder
if not defined HAS_OUT (
    if defined PDF_NAME (
        set "OUT_DIR=%PDF_NAME%"
        set "ARGS=!ARGS! --out "!OUT_DIR!""
        echo [Run.bat] Auto-setting output directory to: "!OUT_DIR!"
    )
)

rem Run the generator
echo [Run.bat] Starting conversion...
"%PYTHON_EXE%" "%MAIN_SCRIPT%" !ARGS!
set "EXIT_CODE=%ERRORLEVEL%"

if %EXIT_CODE% equ 0 (
    if defined PDF_PATH (
        if exist "%PDF_PATH%" (
            echo [Run.bat] Moving original PDF to "!OUT_DIR!"...
            if not exist "!OUT_DIR!" mkdir "!OUT_DIR!"
            move /Y "%PDF_PATH%" "!OUT_DIR!\" >nul
        )
    )
    echo.
    echo ==================================================
    echo SUCCESS: Audiobook generation complete!
    echo Files are located in: "!OUT_DIR!"
    echo ==================================================
    pause
) else (
    echo.
    echo [ERROR] Audiobook generation failed with exit code %EXIT_CODE%.
    pause
)
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
