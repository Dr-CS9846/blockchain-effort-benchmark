@echo off
setlocal
REM ============================================================
REM  One-time bootstrap: publish this complete folder to GitHub.
REM
REM  Sets a REPO-LOCAL git identity (does not change your global
REM  git config) so the commit succeeds. The previous failure
REM  ("src refspec main does not match any") meant no commit
REM  existed because git had no name/email configured.
REM
REM  Plain --force is used ONCE here: this brand-new repo is
REM  solely yours and we intentionally supersede the 4 browser
REM  files with the full set. Later pushes use normal/lease.
REM
REM  Requires Git (https://git-scm.com/download/win). First push
REM  opens a GitHub login in your browser (secure).
REM ============================================================
cd /d "%~dp0"

where git >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Git is not installed. Install from https://git-scm.com/download/win then re-run.
  pause & exit /b 1
)

if not exist ".git" git init

REM repo-local identity (only affects THIS repo; change if you prefer)
git config user.name  "Dr-CS9846"
git config user.email "Dr-CS9846@users.noreply.github.com"

git add -A
git commit -m "Layered reproducibility backbone: full pipeline, provenance, datasheet"
git branch -M main

REM confirm a commit actually exists before trying to push
git rev-parse --verify HEAD >nul 2>nul
if errorlevel 1 (
  echo.
  echo [ERROR] No commit was created - cannot push. See git output above.
  pause & exit /b 1
)

git remote add origin https://github.com/Dr-CS9846/blockchain-effort-benchmark.git 2>nul
git remote set-url origin https://github.com/Dr-CS9846/blockchain-effort-benchmark.git

git push -u origin main --force
if errorlevel 1 (
  echo.
  echo ============================================================
  echo  PUSH FAILED. Nothing was changed on GitHub.
  echo  Copy the lines ABOVE this box ^(the actual git error^) and
  echo  send them back so we can diagnose.
  echo ============================================================
  pause & exit /b 1
)

echo.
echo ============================================================
echo  SUCCESS - the full repo is now on GitHub. Watch Actions:
echo  https://github.com/Dr-CS9846/blockchain-effort-benchmark/actions
echo ============================================================
pause
