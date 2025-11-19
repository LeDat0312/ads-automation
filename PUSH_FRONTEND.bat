@echo off
REM Script để push frontend code lên GitHub
REM Chạy script này từ thư mục project: C:\Users\Foxy\Downloads\File 5h_4_11\Code 18h 4-11 bản 3 sheet

echo ========================================
echo PUSH FRONTEND CODE LEN GITHUB
echo ========================================
echo.

REM Kiểm tra xem có phải đang ở đúng thư mục không
if not exist "frontend\src\components\LevelTabs.tsx" (
    echo ❌ ERROR: Khong tim thay thu muc frontend!
    echo Vui long chay script nay tu thu muc project:
    echo C:\Users\Foxy\Downloads\File 5h_4_11\Code 18h 4-11 ban 3 sheet
    pause
    exit /b 1
)

echo ✅ Tim thay thu muc frontend
echo.

echo 📝 Dang add cac file frontend...
git add frontend/src/components/LevelTabs.tsx
git add frontend/src/components/PaginationControls.tsx
git add frontend/src/components/BudgetEditor.tsx
git add frontend/src/components/FiltersBar.tsx
git add frontend/src/components/AdsetTable.tsx
git add frontend/src/components/SummaryCards.tsx
git add frontend/src/App.tsx
git add frontend/src/services/api.ts
git add frontend/src/types/dashboard.ts
git add frontend/src/utils/formatters.ts
git add frontend/package.json
git add frontend/vite.config.ts
git add frontend/tsconfig.json
git add frontend/index.html

echo.
echo 📋 Files da duoc staged:
git status --short | findstr frontend

echo.
echo 💾 Dang commit...
git commit -m "Add React+Vite frontend: LevelTabs, PaginationControls, BudgetEditor, Status toggle, Account filter, SummaryCards update"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ⚠️  WARNING: Commit failed. Co the file da duoc commit truoc do.
    echo Tiep tuc push...
)

echo.
echo 🚀 Dang push len GitHub...
git push origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Hoan tat! Frontend code da duoc push len GitHub.
) else (
    echo.
    echo ❌ ERROR: Push failed. Kiem tra lai git remote va quyen truy cap.
)

echo.
pause

