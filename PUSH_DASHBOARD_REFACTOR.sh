#!/bin/bash
# Script để push code dashboard refactor lên GitHub

cd "$(dirname "$0")"

echo "📦 Đang kiểm tra git status..."
git status --short | head -20

echo ""
echo "📝 Đang add các file đã thay đổi..."
git add app/api/routes/dashboard.py
git add frontend/src
git add .gitignore

echo ""
echo "📋 Files đã được staged:"
git status --short | grep "^A" | head -20

echo ""
echo "💾 Đang commit..."
git commit -m "Refactor dashboard: Separate frontend (React+Vite) and backend (FastAPI)

- Add LevelTabs component với drill-down/up
- Add PaginationControls component  
- Add BudgetEditor component với +/- buttons
- Add Status toggle switch trong AdsetTable
- Add Account filter dropdown trong FiltersBar
- Update SummaryCards để match backend response
- Update backend để thêm account_name vào response
- Fix field names để match giữa frontend và backend"

echo ""
echo "🚀 Đang push lên GitHub..."
git push origin main

echo ""
echo "✅ Hoàn tất! Code đã được push lên GitHub."

