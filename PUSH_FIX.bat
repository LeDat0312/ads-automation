@echo off
REM Script to push the FIX_502.sh script to GitHub

echo 🚀 Pushing Fix Script to GitHub...
echo.

cd /d "%~dp0"

REM Add changes
git add FIX_502.sh

REM Commit
git commit -m "chore: Add FIX_502.sh script to resolve deployment issues"

REM Push to GitHub
echo.
echo 📤 Pushing to origin/main...
git push origin main

echo.
echo ✅ Done! Script pushed.
echo.
echo 📋 INSTRUCTIONS FOR USER:
echo 1. SSH into your VPS
echo 2. Run: cd /home/adsuser/ads-automation ^&^& git pull origin main
echo 3. Run: chmod +x FIX_502.sh
echo 4. Run: ./FIX_502.sh
echo.
pause
