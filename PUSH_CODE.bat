@echo off
chcp 65001 >nul
echo Đang push code lên GitHub...
cd /d "%~dp0"
git add app/api/routes/dashboard.py app/services/facebook_api.py
git commit -m "fix: Thêm lại import dataclass bị thiếu, sửa logic filter status với normalize, thêm debug logs"
git push origin main
echo Hoàn tất!
pause
