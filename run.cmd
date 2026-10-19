@echo off
setlocal
set "PYTHON=%~dp0.venv\python.exe"
if not exist "%PYTHON%" (
  echo Simulation environment missing: %PYTHON%
  echo Create it from environment.yml first.
  exit /b 1
)
"%PYTHON%" %*
exit /b %errorlevel%
