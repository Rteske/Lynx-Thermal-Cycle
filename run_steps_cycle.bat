@echo off
setlocal

REM Entry wrapper to run the steps-based thermal cycle (temp_new-style profiles)
REM Usage example:
REM   run_steps_cycle.bat --profile data\profiles\dummy_thermal_cycle_1.json --sno ABC123

set SCRIPT_DIR=%~dp0
set PYTHON=python

%PYTHON% "%SCRIPT_DIR%run_steps_cycle_cli.py" %*

endlocal
