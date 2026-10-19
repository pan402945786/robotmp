@echo off
setlocal
pushd "%~dp0" || exit /b 1
if exist "%~dp0.venv\python.exe" goto local_env
where conda >nul 2>nul
if errorlevel 1 goto missing_env
call conda run --no-capture-output -n py311 python %*
goto finished

:local_env
"%~dp0.venv\python.exe" %*
goto finished

:missing_env
echo Simulation environment missing. Create .venv from environment.yml or install Conda environment py311.
cmd /c exit 1

:finished
set "RUN_EXIT_CODE=%errorlevel%"
popd
exit /b %RUN_EXIT_CODE%
