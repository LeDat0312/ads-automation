#!/bin/bash
# Script để fix lỗi import fetch_campaign_budgets_batch trên VPS

echo "🔧 Đang fix lỗi import fetch_campaign_budgets_batch..."
echo ""

cd ~/ads-automation

# 1. Dừng service
echo "1. Dừng service..."
sudo supervisorctl stop ads-automation 2>/dev/null || echo "   Service đã dừng"
sudo supervisorctl stop ads-worker 2>/dev/null || echo "   Worker đã dừng"

# 2. Kill process trên port 8000
echo "2. Kill process trên port 8000..."
sudo lsof -ti:8000 | xargs sudo kill -9 2>/dev/null || echo "   Không có process nào đang dùng port 8000"

# 3. Clear Python cache
echo "3. Clear Python cache..."
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo "   ✅ Đã clear cache"

# 4. Kiểm tra lại function
echo "4. Kiểm tra function..."
if grep -q "^def fetch_campaign_budgets_batch" app/services/facebook_api.py; then
    echo "   ✅ Function tồn tại"
    LINE=$(grep -n "^def fetch_campaign_budgets_batch" app/services/facebook_api.py | cut -d: -f1)
    echo "   📍 Dòng: $LINE"
else
    echo "   ❌ KHÔNG TÌM THẤY function!"
    exit 1
fi

# 5. Test import lại
echo "5. Test import..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from app.services.facebook_api import fetch_campaign_budgets_batch
    print('   ✅ Import thành công')
except Exception as e:
    print(f'   ❌ Import thất bại: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
" || exit 1

# 6. Kiểm tra syntax
echo "6. Kiểm tra syntax..."
python3 -m py_compile app/services/facebook_api.py && echo "   ✅ Syntax OK" || {
    echo "   ❌ Syntax ERROR!"
    exit 1
}

# 7. Restart service
echo "7. Restart service..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart ads-automation
sudo supervisorctl restart ads-worker

# 8. Đợi và kiểm tra status
echo "8. Đợi 5 giây và kiểm tra status..."
sleep 5
sudo supervisorctl status

# 9. Xem log
echo ""
echo "9. Log mới nhất (20 dòng):"
echo "=================================="
sudo tail -20 /var/log/ads-automation.log 2>/dev/null || echo "⚠️ Không tìm thấy log file"

echo ""
echo "✅ Hoàn tất! Kiểm tra status ở trên."

