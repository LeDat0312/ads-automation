#!/bin/bash
# Script để kiểm tra code trên VPS

echo "🔍 Kiểm tra code trên VPS..."
echo ""

cd /home/adsuser/ads-automation || exit 1

echo "📋 Git status:"
git status
echo ""

echo "📋 Commit mới nhất trên VPS:"
git log --oneline -3
echo ""

echo "📋 Commit mới nhất trên GitHub:"
git fetch origin main 2>&1
git log origin/main --oneline -3
echo ""

echo "📋 So sánh local vs remote:"
git log HEAD..origin/main --oneline
if [ $? -eq 0 ] && [ -n "$(git log HEAD..origin/main --oneline)" ]; then
    echo "⚠️  Có commits mới trên GitHub chưa được pull!"
else
    echo "✅ Code đã đồng bộ với GitHub"
fi
echo ""

echo "📋 Kiểm tra file dashboard.py:"
if [ -f "app/api/routes/dashboard.py" ]; then
    echo "✅ File tồn tại"
    echo "   - Dòng đầu tiên:"
    head -n 1 app/api/routes/dashboard.py
    echo "   - Có import logging ở đầu file:"
    head -n 20 app/api/routes/dashboard.py | grep -n "import logging" || echo "   ❌ Không tìm thấy 'import logging' ở đầu file"
    echo "   - Có logger = logging.getLogger ở đầu file:"
    head -n 25 app/api/routes/dashboard.py | grep -n "logger = logging.getLogger" || echo "   ❌ Không tìm thấy 'logger = logging.getLogger' ở đầu file"
    echo "   - Có logger.info trong dashboard_page:"
    grep -n "logger.info" app/api/routes/dashboard.py | head -3 || echo "   ❌ Không tìm thấy 'logger.info'"
else
    echo "❌ File không tồn tại!"
fi
echo ""

echo "📋 Kiểm tra main.py:"
if [ -f "app/main.py" ]; then
    echo "✅ File tồn tại"
    echo "   - Có redirect /dashboard/ không:"
    grep -n "dashboard_redirect\|/dashboard/" app/main.py || echo "   ✅ Không có redirect (đã xóa)"
else
    echo "❌ File không tồn tại!"
fi


