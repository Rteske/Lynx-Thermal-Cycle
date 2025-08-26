@echo off
setlocal ENABLEDELAYEDEXPANSION ENABLEEXTENSIONS
title Lynx Thermal Cycle - Test Runner

echo.
echo ========================================================
echo  Lynx Thermal Cycle - Test Runner
echo ========================================================
echo.

REM Navigate to repository root directory
cd /d "%~dp0\.."
set "REPO_ROOT=%CD%"

REM Check for virtual environment
if not exist "%REPO_ROOT%\venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at: %REPO_ROOT%\venv\Scripts\python.exe
    echo Please run the setup script first.
    pause
    exit /b 1
)

set "PYEXE=%REPO_ROOT%\venv\Scripts\python.exe"

echo Available test options:
echo   1. Basic DAQ test only
echo   2. Temperature monitoring test
echo   3. Thermal cycle simulation test 
echo   4. All tests (recommended)
echo   5. Exit
echo.

:menu
set /p choice="Please select an option (1-5): "

if "%choice%"=="1" (
    echo.
    echo Running basic DAQ test...
    %PYEXE% scripts/run_thermal_cycle_test.py --test basic
    goto :end
)

if "%choice%"=="2" (
    echo.
    echo Running temperature monitoring test...
    %PYEXE% scripts/run_thermal_cycle_test.py --test temp
    goto :end
)

if "%choice%"=="3" (
    echo.
    echo Running thermal cycle simulation test...
    %PYEXE% scripts/run_thermal_cycle_test.py --test thermal
    goto :end
)

if "%choice%"=="4" (
    echo.
    echo Running all tests...
    %PYEXE% scripts/run_thermal_cycle_test.py --test all
    goto :end
)

if "%choice%"=="5" (
    echo Exiting...
    goto :end
)

echo Invalid choice. Please select 1-5.
goto :menu

:end
echo.
echo ========================================================
echo Test run complete. Press any key to exit.
echo ========================================================
pause >nul
endlocal
