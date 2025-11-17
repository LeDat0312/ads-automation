#!/bin/bash

# Script kiểm tra và sửa lỗi 502 Bad Gateway trên VPS Ubuntu
# Chạy với: bash CHECK_VPS_502_ERROR.sh

echo "🔍 Bắt đầu kiểm tra lỗi 502 Bad Gateway..."

# 1. Kiểm tra trạng thái supervisor
echo ""
echo "1️⃣ Kiểm tra trạng thái supervisor:"
sudo supervisorctl status

# 2. Kiểm tra logs của app
echo ""
echo "2️⃣ Kiểm tra logs của app (50 dòng cuối):"
sudo tail -50 /var/log/supervisor/ads-automation-api-stdout.log
echo ""
echo "--- Logs lỗi (nếu có): ---"
sudo tail -50 /var/log/supervisor/ads-automation-api-stderr.log

# 3. Kiểm tra nginx logs
echo ""
echo "3️⃣ Kiểm tra nginx error logs:"
sudo tail -50 /var/log/nginx/error.log

# 4. Kiểm tra nginx status
echo ""
echo "4️⃣ Kiểm tra nginx status:"
sudo systemctl status nginx --no-pager -l

# 5. Kiểm tra port 8000 (FastAPI)
echo ""
echo "5️⃣ Kiểm tra port 8000:"
sudo netstat -tlnp | grep 8000 || echo "⚠️ Port 8000 không có process nào đang chạy!"

# 6. Kiểm tra syntax Python
echo ""
echo "6️⃣ Kiểm tra syntax Python:"
cd ~/ads-automation
python3 -m py_compile app/api/routes/dashboard.py 2>&1
python3 -m py_compile app/main.py 2>&1

# 7. Thử restart service
echo ""
echo "7️⃣ Thử restart service:"
sudo supervisorctl restart ads-automation-api
sleep 3
sudo supervisorctl status

# 8. Kiểm tra lại port sau restart
echo ""
echo "8️⃣ Kiểm tra lại port 8000 sau restart:"
sleep 2
sudo netstat -tlnp | grep 8000 || echo "⚠️ Port 8000 vẫn không có process!"

echo ""
echo "✅ Hoàn tất kiểm tra!"
echo ""
echo "📝 Nếu vẫn lỗi, hãy kiểm tra:"
echo "   - File config supervisor: /etc/supervisor/conf.d/ads-automation-api.conf"
echo "   - File config nginx: /etc/nginx/sites-available/updatemetaads.site"
echo "   - Database connection trong app/core/config.py"


