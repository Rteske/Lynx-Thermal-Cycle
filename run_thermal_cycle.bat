@echo off
setlocal

REM Simple wrapper to run the thermal cycle CLI
REM Usage:
REM   run_thermal_cycle.bat --profile configs\thermal_profile.json --path "HIGH_BAND_PATH1 (Vertical)" --sno DUT-1234

python "%~dp0run_thermal_cycle_cli.py" %*

endlocal
