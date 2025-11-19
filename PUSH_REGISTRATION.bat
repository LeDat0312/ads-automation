@echo off
REM Script để push Registration Feature lên GitHub

echo 🚀 Pushing Registration Feature to GitHub...
echo.

cd /d "%~dp0"

REM Add changes
git add app/core/captcha.py
git add app/api/routes/auth.py

REM Show what will be committed
echo 📝 Changes to be committed:
git diff --cached --stat
echo.

REM Commit
git commit -m "feat: Implement User Registration with CAPTCHA - Added app/core/captcha.py - Added Register page and endpoints - Added CAPTCHA verification - Updated Login page"

REM Push to GitHub
echo.
echo 📤 Pushing to origin/main...
git push origin main

echo.
echo ✅ Done! Code pushed to GitHub
echo.
echo 📋 Next steps - Run on VPS:
echo cd /home/adsuser/ads-automation ^&^& git pull origin main ^&^& sudo supervisorctl restart ads-automation-production
echo.
pause
