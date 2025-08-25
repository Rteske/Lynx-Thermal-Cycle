@echo off
setlocal

REM Validate a temp_new-style profile JSON
REM Usage:
REM   validate_profile.bat data\profiles\dummy_thermal_cycle_1.json

set SCRIPT_DIR=%~dp0
set PYTHON=python

if "%~1"=="" (
  echo Usage: %~nx0 ^<profile.json^>
  exit /b 2
)

%PYTHON% "%SCRIPT_DIR%scripts\validate_profile.py" --profile "%~1"

endlocal
