@echo off
REM Script để push AI Login Interface lên GitHub

echo 🚀 Pushing AI Login Interface to GitHub...
echo.

cd /d "%~dp0"

REM Add changes
git add app/api/routes/auth.py

REM Show what will be committed
echo 📝 Changes to be committed:
git diff --cached --stat
echo.

REM Commit
git commit -m "feat: Add AI-powered login interface with mouse tracking - Added interactive AI robot character with gradient design - Implemented mouse tracking for AI eyes - Added password protection animation (AI covers eyes) - Enhanced with floating particles background - Improved responsive design for mobile"

REM Push to GitHub
echo.
echo 📤 Pushing to origin/main...
git push origin main

echo.
echo ✅ Done! Code pushed to GitHub
echo.
echo 📋 Next steps - Run on VPS:
echo cd /var/www/ads-automation
echo git pull origin main
echo sudo supervisorctl restart ads-automation-production
echo.
pause
