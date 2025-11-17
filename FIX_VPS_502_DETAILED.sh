#!/bin/bash

# Script sửa lỗi 502 chi tiết
echo "🔧 Sửa lỗi 502 Bad Gateway..."

cd ~/ads-automation

# 1. Kiểm tra supervisor config
echo ""
echo "1️⃣ Kiểm tra supervisor config:"
sudo cat /etc/supervisor/conf.d/ads-automation.conf | grep -A 5 "\[program:"

# 2. Kiểm tra port 8000 (dùng ss thay vì netstat)
echo ""
echo "2️⃣ Kiểm tra port 8000:"
sudo ss -tlnp | grep 8000 || echo "⚠️ Port 8000 không có process nào!"

# 3. Kiểm tra logs của ads-automation
echo ""
echo "3️⃣ Logs của ads-automation (stdout):"
sudo tail -30 /var/log/supervisor/ads-automation-stdout.log 2>/dev/null || echo "Không có stdout log"

echo ""
echo "4️⃣ Logs của ads-automation (stderr):"
sudo tail -30 /var/log/supervisor/ads-automation-stderr.log 2>/dev/null || echo "Không có stderr log"

# 4. Kiểm tra process đang chạy
echo ""
echo "5️⃣ Process đang chạy:"
ps aux | grep -E "(uvicorn|python.*main|ads-automation)" | grep -v grep

# 5. Kiểm tra syntax Python
echo ""
echo "6️⃣ Kiểm tra syntax Python:"
python3 -m py_compile app/api/routes/dashboard.py 2>&1
python3 -m py_compile app/main.py 2>&1

# 6. Restart đúng service
echo ""
echo "7️⃣ Restart service ads-automation:"
sudo supervisorctl stop ads-automation
sleep 2
sudo supervisorctl start ads-automation
sleep 3

# 7. Kiểm tra lại
echo ""
echo "8️⃣ Kiểm tra lại status:"
sudo supervisorctl status

echo ""
echo "9️⃣ Kiểm tra lại port 8000:"
sleep 2
sudo ss -tlnp | grep 8000 || echo "⚠️ Port 8000 vẫn không chạy!"

# 8. Test nginx
echo ""
echo "🔟 Test và reload nginx:"
sudo nginx -t
sudo systemctl reload nginx

echo ""
echo "✅ Hoàn tất!"


