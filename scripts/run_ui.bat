@echo off
setlocal ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
title Lynx Thermal Cycle - UI Launcher

REM =================================================================
REM Lynx Thermal Cycle Live View Launcher
REM =================================================================

echo.
echo ========================================================
echo  Lynx Thermal Cycle - Live View Launcher
echo ========================================================
echo.

REM Navigate to repository root directory
cd /d "%~dp0\.."
set "REPO_ROOT=%CD%"
echo Repository root: %REPO_ROOT%

REM Check if required directories exist
if not exist "src\ui\" (
    echo [ERROR] UI source directory not found: src\ui\
    echo Please ensure you're running this from the correct location.
    pause
    exit /b 1
)

REM Python interpreter detection with priority order
echo Detecting Python interpreter...
set "PYEXE="
set "PYTHON_TYPE="

REM 1. Check for virtual environment
if exist "%REPO_ROOT%\venv\Scripts\python.exe" (
    set "PYEXE=%REPO_ROOT%\venv\Scripts\python.exe"
    set "PYTHON_TYPE=Virtual Environment"
    goto :python_found
)

REM 2. Check for py launcher with Python 3
where py >nul 2>nul
if !ERRORLEVEL! EQU 0 (
    py -3 --version >nul 2>nul
    if !ERRORLEVEL! EQU 0 (
        set "PYEXE=py -3"
        set "PYTHON_TYPE=Python Launcher"
        goto :python_found
    )
)

REM 3. Check for direct python command
where python >nul 2>nul
if !ERRORLEVEL! EQU 0 (
    python --version >nul 2>nul
    if !ERRORLEVEL! EQU 0 (
        set "PYEXE=python"
        set "PYTHON_TYPE=System Python"
        goto :python_found
    )
)

REM Python not found
echo [ERROR] Python 3.10+ not found in any of the following locations:
echo   - Virtual environment: %REPO_ROOT%\venv\Scripts\python.exe
echo   - Python Launcher: py -3
echo   - System Python: python
echo.
echo Please install Python 3.10+ or create a virtual environment:
echo   1. Download Python: https://www.python.org/downloads/windows/
echo   2. Or create venv: python -m venv venv
echo.
pause
exit /b 1

:python_found
echo Found Python: %PYTHON_TYPE%

REM Verify Python version
echo Checking Python version...
%PYEXE% -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
if !ERRORLEVEL! NEQ 0 (
    echo [WARNING] Python version may be too old. Python 3.10+ recommended.
    %PYEXE% --version
)

REM Check for required Python modules
echo Checking dependencies...
%PYEXE% -c "import PyQt5, pyqtgraph" >nul 2>nul
if !ERRORLEVEL! NEQ 0 (
    echo [WARNING] Missing GUI dependencies. Install with:
    echo   %PYEXE% -m pip install PyQt5 pyqtgraph
    echo.
    echo Attempting to install dependencies...
    %PYEXE% -m pip install PyQt5 pyqtgraph
    if !ERRORLEVEL! NEQ 0 (
        echo [ERROR] Failed to install dependencies automatically.
        echo Please install manually and try again.
        pause
        exit /b 1
    )
)

REM Launch the application
echo.
echo ========================================================
echo  Launching Lynx Thermal Cycle Live View...
echo ========================================================
echo.

%PYEXE% -m src.ui.live_view
set EXITCODE=!ERRORLEVEL!

echo.
echo ========================================================
if !EXITCODE! EQU 0 (
    echo  Application closed successfully
) else (
    echo  Application exited with error code: !EXITCODE!
    echo.
    echo Troubleshooting:
    echo   - Ensure all dependencies are installed
    echo   - Check that hardware is properly connected
    echo   - Verify configuration files are present
    echo.
    echo For help, contact the development team.
)
echo ========================================================
echo.
pause

endlocal
