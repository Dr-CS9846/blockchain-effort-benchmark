@echo off
setlocal
REM ============================================================
REM  Routine update to GitHub (normal push - NO force).
REM  Use this for every change AFTER the one-time bootstrap.
REM  It commits your local changes and pushes them to main the
REM  safe way (fast-forward). It does NOT touch the CI 'rolling'
REM  branch or use --force.
REM ============================================================
cd /d "%~dp0"

where git >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Git is not installed.
  pause & exit /b 1
)

git add -A

set /p MSG="Describe what changed (commit message): "
if "%MSG%"=="" set MSG=Update repository content
git commit -m "%MSG%"

REM pull any remote changes first (safety; CI only touches 'rolling', so usually a no-op)
git pull --rebase origin main

git push origin main
if errorlevel 1 (
  echo.
  echo ============================================================
  echo  PUSH FAILED. Copy the lines ABOVE this box and send them.
  echo ============================================================
  pause & exit /b 1
)

echo.
echo ============================================================
echo  SUCCESS - your changes are now on GitHub ^(main^).
echo ============================================================
pause
