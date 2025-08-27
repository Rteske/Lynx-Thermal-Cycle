@echo off
setlocal

REM Activate venv if present
if exist "%~dp0..\.venv\Scripts\activate.bat" (
  call "%~dp0..\.venv\Scripts\activate.bat"
)

set PROFILE=%~dp0..\profiles\dummy_thermal_cycle_1.json

python "%~dp0run_quick_profile.py" --profile "%PROFILE%" %*

endlocal
