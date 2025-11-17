#!/bin/bash

# Script sửa lỗi 502 Bad Gateway
# Chạy với: bash FIX_VPS_502_ERROR.sh

echo "🔧 Bắt đầu sửa lỗi 502 Bad Gateway..."

cd ~/ads-automation

# 1. Pull code mới nhất
echo ""
echo "1️⃣ Pull code mới nhất từ GitHub:"
git pull origin main

# 2. Kiểm tra syntax
echo ""
echo "2️⃣ Kiểm tra syntax Python:"
python3 -m py_compile app/api/routes/dashboard.py
if [ $? -ne 0 ]; then
    echo "❌ Lỗi syntax trong dashboard.py!"
    exit 1
fi

python3 -m py_compile app/main.py
if [ $? -ne 0 ]; then
    echo "❌ Lỗi syntax trong main.py!"
    exit 1
fi

echo "✅ Syntax OK!"

# 3. Restart service
echo ""
echo "3️⃣ Restart service:"
sudo supervisorctl stop ads-automation-api
sleep 2
sudo supervisorctl start ads-automation-api
sleep 3

# 4. Kiểm tra status
echo ""
echo "4️⃣ Kiểm tra status:"
sudo supervisorctl status

# 5. Kiểm tra port
echo ""
echo "5️⃣ Kiểm tra port 8000:"
sleep 2
if sudo netstat -tlnp | grep 8000; then
    echo "✅ Port 8000 đang chạy!"
else
    echo "❌ Port 8000 không chạy! Kiểm tra logs:"
    sudo tail -20 /var/log/supervisor/ads-automation-api-stderr.log
fi

# 6. Test nginx
echo ""
echo "6️⃣ Test nginx config:"
sudo nginx -t

# 7. Reload nginx
echo ""
echo "7️⃣ Reload nginx:"
sudo systemctl reload nginx

echo ""
echo "✅ Hoàn tất! Kiểm tra website: https://updatemetaads.site/"


