param(
    [string]$Message = "chore: update UKIS disaster platform telemetry and features"
)

Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host " UKIS 2026 P-011: Synchronizing to GitHub & Vercel Production" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan

Write-Host "`n[1/3] Staging all files..." -ForegroundColor Yellow
git add .

Write-Host "`n[2/3] Committing changes: $Message" -ForegroundColor Yellow
git commit -m $Message

Write-Host "`n[3/3] Pushing to GitHub repository..." -ForegroundColor Yellow
git push origin main

Write-Host "`n[4/4] Deploying directly to Vercel Production..." -ForegroundColor Yellow
Set-Location "$PSScriptRoot\..\frontend"
npx vercel --prod --yes
Set-Location "$PSScriptRoot\.."

Write-Host "`n====================================================================" -ForegroundColor Green
Write-Host " SUCCESS: Synchronized with GitHub and Vercel Production!" -ForegroundColor Green
Write-Host " GitHub Repo: https://github.com/adityajoshi202424-commits/ukis-mountain-disaster-early-warning" -ForegroundColor White
Write-Host " Live Vercel: https://frontend-rosy-phi-23.vercel.app" -ForegroundColor White
Write-Host "====================================================================" -ForegroundColor Green
