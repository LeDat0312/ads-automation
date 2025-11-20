#!/bin/bash
# Script để kiểm tra import fetch_campaign_budgets_batch trên VPS

echo "🔍 Kiểm tra import fetch_campaign_budgets_batch trên VPS..."
echo ""

cd ~/ads-automation

echo "1. Kiểm tra xem function có tồn tại trong file không:"
grep -n "def fetch_campaign_budgets_batch" app/services/facebook_api.py || echo "❌ KHÔNG TÌM THẤY function"

echo ""
echo "2. Kiểm tra xem function có được định nghĩa ở top-level (không có indentation) không:"
grep -n "^def fetch_campaign_budgets_batch" app/services/facebook_api.py || echo "❌ Function có thể bị nested (có indentation)"

echo ""
echo "3. Test import trực tiếp:"
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from app.services.facebook_api import fetch_campaign_budgets_batch
    print('✅ SUCCESS: fetch_campaign_budgets_batch imported successfully')
    print(f'   Function: {fetch_campaign_budgets_batch}')
except ImportError as e:
    print(f'❌ ERROR: Cannot import fetch_campaign_budgets_batch')
    print(f'   Error: {e}')
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f'❌ ERROR: Unexpected error')
    print(f'   Error: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "4. Kiểm tra syntax của file:"
python3 -m py_compile app/services/facebook_api.py && echo "✅ Syntax OK" || echo "❌ Syntax ERROR"

echo ""
echo "5. Kiểm tra git status:"
git log --oneline -1 app/services/facebook_api.py

