@echo off
REM Script để push code dashboard refactor lên GitHub (Windows)

echo 📦 Đang kiểm tra git status...
git status --short

echo.
echo 📝 Đang add các file đã thay đổi...
git add app/api/routes/dashboard.py
git add frontend/src
git add .gitignore

echo.
echo 📋 Files đã được staged:
git status --short

echo.
echo 💾 Đang commit...
git commit -m "Refactor dashboard: Separate frontend (React+Vite) and backend (FastAPI) - Add LevelTabs, PaginationControls, BudgetEditor, Status toggle, Account filter"

echo.
echo 🚀 Đang push lên GitHub...
git push origin main

echo.
echo ✅ Hoàn tất! Code đã được push lên GitHub.
pause

