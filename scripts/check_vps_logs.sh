#!/bin/bash
# Script để check logs trên VPS khi bị lỗi 502 Bad Gateway

echo "=========================================="
echo "🔍 KIỂM TRA LOGS VPS - 502 Bad Gateway"
echo "=========================================="
echo ""

# 1. Check service status
echo "1️⃣  Kiểm tra trạng thái services:"
echo "-----------------------------------"
sudo supervisorctl status
echo ""

# 2. Check supervisor logs (ads-automation-api)
echo "2️⃣  Logs của ads-automation-api (50 dòng cuối):"
echo "-----------------------------------"
sudo supervisorctl tail -50 ads-automation-api
echo ""

# 3. Check nginx error logs
echo "3️⃣  Nginx error logs (50 dòng cuối):"
echo "-----------------------------------"
sudo tail -50 /var/log/nginx/error.log
echo ""

# 4. Check nginx access logs
echo "4️⃣  Nginx access logs (20 dòng cuối):"
echo "-----------------------------------"
sudo tail -20 /var/log/nginx/access.log
echo ""

# 5. Check Python syntax errors
echo "5️⃣  Kiểm tra syntax errors trong settings.py:"
echo "-----------------------------------"
cd ~/ads-automation
source venv/bin/activate
python -m py_compile app/api/routes/settings.py 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Không có syntax errors trong settings.py"
else
    echo "❌ Có syntax errors trong settings.py"
fi
echo ""

# 6. Check import errors
echo "6️⃣  Kiểm tra import errors:"
echo "-----------------------------------"
python -c "from app.api.routes.settings import router" 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Import thành công"
else
    echo "❌ Có lỗi khi import"
fi
echo ""

# 7. Check database connection
echo "7️⃣  Kiểm tra kết nối database:"
echo "-----------------------------------"
python -c "from app.core.database import engine; print('✅ Database connection OK' if engine else '❌ Database connection FAILED')" 2>&1
echo ""

# 8. Check recent git changes
echo "8️⃣  Git log (5 commits gần nhất):"
echo "-----------------------------------"
cd ~/ads-automation
git log --oneline -5
echo ""

# 9. Check if port is listening
echo "9️⃣  Kiểm tra port 8000 (FastAPI):"
echo "-----------------------------------"
sudo netstat -tlnp | grep 8000 || sudo ss -tlnp | grep 8000
echo ""

# 10. Check disk space
echo "🔟 Kiểm tra dung lượng disk:"
echo "-----------------------------------"
df -h
echo ""

echo "=========================================="
echo "✅ Hoàn tất kiểm tra!"
echo "=========================================="
echo ""
echo "💡 Gợi ý sửa lỗi:"
echo "1. Nếu service không chạy: sudo supervisorctl start ads-automation-api"
echo "2. Nếu có syntax errors: sửa code và restart service"
echo "3. Nếu có import errors: kiểm tra dependencies (pip install -r requirements.txt)"
echo "4. Nếu database lỗi: kiểm tra DATABASE_URL trong .env"
echo "5. Restart service: sudo supervisorctl restart ads-automation-api"

