@echo off
chcp 65001 >nul
echo Đang push code lên GitHub...
cd /d "%~dp0"
git add app/services/facebook_api.py app/api/routes/dashboard.py
git commit -m "Optimize: Global cache cho objectives/budgets/status, fix filter adset_id, tối ưu tốc độ load"
git push origin main
echo Hoàn tất!
pause

