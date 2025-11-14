#!/bin/bash
# Script để check lỗi 502 Bad Gateway

echo "=========================================="
echo "🔍 KIỂM TRA LỖI 502 BAD GATEWAY"
echo "=========================================="
echo ""

# 1. Check supervisor status
echo "1️⃣ Kiểm tra trạng thái Supervisor:"
echo "-----------------------------------"
sudo supervisorctl status
echo ""

# 2. Check API service logs
echo "2️⃣ Kiểm tra logs của API service (50 dòng cuối):"
echo "-----------------------------------"
sudo supervisorctl tail -50 ads-automation-api
echo ""

# 3. Check nginx error logs
echo "3️⃣ Kiểm tra logs của Nginx (50 dòng cuối):"
echo "-----------------------------------"
sudo tail -50 /var/log/nginx/error.log
echo ""

# 4. Check nginx access logs
echo "4️⃣ Kiểm tra access logs của Nginx (20 dòng cuối):"
echo "-----------------------------------"
sudo tail -20 /var/log/nginx/access.log
echo ""

# 5. Check Python syntax
echo "5️⃣ Kiểm tra Python syntax:"
echo "-----------------------------------"
cd ~/ads-automation
source venv/bin/activate

echo "Checking profile.py..."
python -m py_compile app/api/routes/profile.py 2>&1 || echo "❌ Syntax error in profile.py"

echo "Checking user_management.py..."
python -m py_compile app/api/routes/user_management.py 2>&1 || echo "❌ Syntax error in user_management.py"

echo "Checking settings.py..."
python -m py_compile app/api/routes/settings.py 2>&1 || echo "❌ Syntax error in settings.py"

echo "Checking main.py..."
python -m py_compile app/main.py 2>&1 || echo "❌ Syntax error in main.py"
echo ""

# 6. Check imports
echo "6️⃣ Kiểm tra imports:"
echo "-----------------------------------"
python -c "from app.main import app; print('✅ Main import OK')" 2>&1 || echo "❌ Import error in main.py"
python -c "from app.api.routes.profile import router; print('✅ Profile import OK')" 2>&1 || echo "❌ Import error in profile.py"
python -c "from app.api.routes.user_management import router; print('✅ User management import OK')" 2>&1 || echo "❌ Import error in user_management.py"
echo ""

# 7. Check if port 8000 is listening
echo "7️⃣ Kiểm tra port 8000:"
echo "-----------------------------------"
sudo netstat -tlnp | grep :8000 || echo "❌ Port 8000 không có process nào đang listen"
echo ""

# 8. Check process
echo "8️⃣ Kiểm tra process Python:"
echo "-----------------------------------"
ps aux | grep "uvicorn\|python.*main" | grep -v grep || echo "❌ Không tìm thấy Python process"
echo ""

# 9. Check database connection
echo "9️⃣ Kiểm tra kết nối database:"
echo "-----------------------------------"
python -c "
from app.core.database import get_db_session
from sqlalchemy import text
try:
    db = get_db_session()
    db.execute(text('SELECT 1'))
    print('✅ Database connection OK')
    db.close()
except Exception as e:
    print(f'❌ Database connection error: {e}')
" 2>&1
echo ""

echo "=========================================="
echo "✅ Hoàn thành kiểm tra!"
echo "=========================================="

