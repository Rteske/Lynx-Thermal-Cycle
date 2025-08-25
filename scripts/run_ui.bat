@echo off
setlocal ENABLEEXTENSIONS

REM Change to this script's directory (repo root)
cd /d "%~dp0"

REM Select a Python interpreter: prefer .venv if present, else use py launcher, else python
set "PYEXE="
if exist ".venv\Scripts\python.exe" set "PYEXE=.venv\Scripts\python.exe"
if not defined PYEXE (
  where py >nul 2>nul && set "PYEXE=py -3"
)
if not defined PYEXE (
  where python >nul 2>nul && set "PYEXE=python"
)
if not defined PYEXE (
  echo [ERROR] Python not found. Please install Python 3.10+ and re-run.
  echo Download: https://www.python.org/downloads/windows/
  pause
  exit /b 1
)

echo Launching Lynx Thermal Cycle Live View...
%PYEXE% -m src.ui.live_view
set EXITCODE=%ERRORLEVEL%
if %EXITCODE% NEQ 0 (
  echo.
  echo The program exited with error code %EXITCODE%.
  echo If you see missing module errors, install GUI dependencies:
  echo   %PYEXE% -m pip install PyQt5 pyqtgraph
  echo.
  pause
)

endlocal
