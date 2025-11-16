#!/bin/bash
# Script để kiểm tra lỗi Dashboard

echo "🔍 Kiểm tra lỗi Dashboard..."
echo ""

# Kiểm tra logs của API service
echo "📋 Logs của ads-automation-api (50 dòng cuối):"
echo "----------------------------------------"
sudo supervisorctl tail -50 ads-automation-api
echo ""

# Kiểm tra syntax Python
echo "🔍 Kiểm tra syntax Python..."
python3 -m py_compile app/api/routes/dashboard.py 2>&1 || echo "❌ Có lỗi syntax!"

# Kiểm tra import
echo ""
echo "🧪 Kiểm tra import..."
python3 -c "from app.api.routes.dashboard import router; print('✅ Import OK')" 2>&1 || echo "❌ Lỗi import!"

# Kiểm tra route có được đăng ký không
echo ""
echo "📝 Kiểm tra route trong main.py..."
grep -n "dashboard" app/main.py || echo "⚠️  Không tìm thấy dashboard router trong main.py"


