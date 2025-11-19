#!/bin/bash
# Script để push frontend code lên GitHub
# Chạy script này từ thư mục project

echo "========================================"
echo "PUSH FRONTEND CODE LEN GITHUB"
echo "========================================"
echo ""

# Kiểm tra xem có phải đang ở đúng thư mục không
if [ ! -f "frontend/src/components/LevelTabs.tsx" ]; then
    echo "❌ ERROR: Không tìm thấy thư mục frontend!"
    echo "Vui lòng chạy script này từ thư mục project"
    exit 1
fi

echo "✅ Tìm thấy thư mục frontend"
echo ""

echo "📝 Đang add các file frontend..."
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

echo ""
echo "📋 Files đã được staged:"
git status --short | grep frontend

echo ""
echo "💾 Đang commit..."
git commit -m "Add React+Vite frontend: LevelTabs, PaginationControls, BudgetEditor, Status toggle, Account filter, SummaryCards update" || echo "⚠️  WARNING: Commit failed. Có thể file đã được commit trước đó."

echo ""
echo "🚀 Đang push lên GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Hoàn tất! Frontend code đã được push lên GitHub."
else
    echo ""
    echo "❌ ERROR: Push failed. Kiểm tra lại git remote và quyền truy cập."
fi

