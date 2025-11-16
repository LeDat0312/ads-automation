#!/bin/bash
# Script để kiểm tra lỗi Dashboard trên VPS

echo "🔍 Kiểm tra lỗi Dashboard..."
echo ""

# Kiểm tra logs của API service
echo "📋 Logs của ads-automation-api (100 dòng cuối):"
echo "----------------------------------------"
sudo supervisorctl tail -100 ads-automation-api | tail -50
echo ""

# Kiểm tra syntax Python
echo "🔍 Kiểm tra syntax Python..."
cd /home/adsuser/ads-automation
python3 -m py_compile app/api/routes/dashboard.py 2>&1 || echo "❌ Có lỗi syntax!"

# Kiểm tra import
echo ""
echo "🧪 Kiểm tra import..."
python3 -c "
try:
    from app.api.routes.dashboard import router
    print('✅ Import dashboard router OK')
except Exception as e:
    print(f'❌ Lỗi import: {e}')
    import traceback
    traceback.print_exc()
" 2>&1

# Kiểm tra route có được đăng ký không
echo ""
echo "📝 Kiểm tra route trong main.py..."
grep -n "dashboard" app/main.py || echo "⚠️  Không tìm thấy dashboard router trong main.py"

# Kiểm tra xem có route /dashboard/ không
echo ""
echo "🌐 Kiểm tra routes có sẵn..."
python3 -c "
from app.main import app
routes = [r.path for r in app.routes]
dashboard_routes = [r for r in routes if 'dashboard' in r]
print('Routes có chứa dashboard:')
for r in dashboard_routes:
    print(f'  - {r}')
" 2>&1 || echo "⚠️  Không thể kiểm tra routes"


