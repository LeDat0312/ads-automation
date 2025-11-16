#!/bin/bash
# Script để kiểm tra lỗi Dashboard chi tiết

echo "🔍 Kiểm tra lỗi Dashboard chi tiết..."
echo ""

# Xem logs đầy đủ (không grep)
echo "📋 Logs đầy đủ của ads-automation-api (100 dòng cuối):"
echo "----------------------------------------"
sudo supervisorctl tail -100 ads-automation-api
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
    print(f'❌ Lỗi import dashboard router: {e}')
    import traceback
    traceback.print_exc()
" 2>&1

# Kiểm tra import các dependencies
echo ""
echo "🧪 Kiểm tra import dependencies..."
python3 -c "
try:
    from app.models.account_prefix import Account, Prefix, AccountPrefix
    print('✅ Import Account, Prefix, AccountPrefix OK')
except Exception as e:
    print(f'❌ Lỗi import Account, Prefix: {e}')
    import traceback
    traceback.print_exc()

try:
    from app.api.routes.auth import get_current_user_optional
    print('✅ Import get_current_user_optional OK')
except Exception as e:
    print(f'❌ Lỗi import get_current_user_optional: {e}')
    import traceback
    traceback.print_exc()

try:
    from app.core.ui_helpers import get_user_dropdown_menu, get_account_locked_message
    print('✅ Import ui_helpers OK')
except Exception as e:
    print(f'❌ Lỗi import ui_helpers: {e}')
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
try:
    from app.main import app
    routes = [r.path for r in app.routes if 'dashboard' in r.path]
    print('Routes có chứa dashboard:')
    for r in routes:
        print(f'  - {r}')
    if not routes:
        print('  ⚠️  Không tìm thấy route nào có chứa dashboard')
except Exception as e:
    print(f'❌ Lỗi khi kiểm tra routes: {e}')
    import traceback
    traceback.print_exc()
" 2>&1


