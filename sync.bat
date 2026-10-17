@echo off
setlocal enabledelayedexpansion

REM ==============================================================================
REM UKIS Mountain Disaster Intelligence — 1-Click Dual Sync (GitHub + Vercel)
REM Pushes all updates to GitHub and deploys live to Vercel in one step
REM ==============================================================================

set MSG=%~1
if "%MSG%"=="" set MSG="chore: update UKIS disaster platform telemetry and features"

echo ====================================================================
echo  UKIS 2026 P-011: Synchronizing to GitHub and Vercel Production
echo ====================================================================
echo.

echo [1/3] Staging all modified files to Git...
git add .

echo [2/3] Committing with message: %MSG%
git commit -m %MSG%

echo [3/3] Pushing to GitHub repository...
git push origin main

echo.
echo [4/4] Deploying latest updates directly to Vercel Production...
cd frontend
call npx vercel --prod --yes
cd ..

echo.
echo ====================================================================
echo  SYNC COMPLETE!
echo  GitHub Repo: https://github.com/adityajoshi202424-commits/ukis-mountain-disaster-early-warning
echo  Live Vercel: https://frontend-rosy-phi-23.vercel.app
echo ====================================================================
