#!/bin/bash
# Script nhanh để fix lỗi 502 Bad Gateway

echo "🔧 QUICK FIX 502 Bad Gateway"
echo "=============================="
echo ""

cd ~/ads-automation
source venv/bin/activate

# 1. Stop service
echo "1. Dừng service..."
sudo supervisorctl stop ads-automation-api

# 2. Check syntax
echo "2. Kiểm tra syntax..."
python -m py_compile app/api/routes/settings.py
if [ $? -ne 0 ]; then
    echo "❌ Có syntax errors! Vui lòng check logs."
    exit 1
fi

# 3. Check imports
echo "3. Kiểm tra imports..."
python -c "from app.api.routes.settings import router" 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Có import errors! Vui lòng check logs."
    exit 1
fi

# 4. Restart service
echo "4. Khởi động lại service..."
sudo supervisorctl start ads-automation-api

# 5. Wait a bit
sleep 3

# 6. Check status
echo "5. Kiểm tra trạng thái..."
sudo supervisorctl status ads-automation-api

echo ""
echo "✅ Hoàn tất! Kiểm tra lại website."

