@echo off
REM Script để push User Management Bug Fix lên GitHub

echo 🔧 Pushing User Management Bug Fix to GitHub...
echo.

cd /d "%~dp0"

REM Add changes
git add app/api/routes/user_management.py

REM Show what will be committed
echo 📝 Changes to be committed:
git diff --cached --stat
echo.

REM Commit
git commit -m "fix: Handle non-JSON responses in user management API calls - Fixed delete user JSON parsing error - Added content-type check before parsing response - Applied fix to toggleUserStatus and saveUser - Prevents Unexpected token error when server returns HTML"

REM Push to GitHub
echo.
echo 📤 Pushing to origin/main...
git push origin main

echo.
echo ✅ Done! Code pushed to GitHub
echo.
echo 📋 Next steps - Run on VPS:
echo cd /var/www/ads-automation ^&^& git pull origin main ^&^& sudo supervisorctl restart ads-automation-production
echo.
pause
