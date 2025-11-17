#!/bin/bash

# Script cài đặt pydantic-settings và fix lỗi 502
echo "🔧 Cài đặt pydantic-settings và fix lỗi 502..."

cd /var/www/ads-automation

# 1. Activate virtual environment
source venv/bin/activate

# 2. Cài đặt pydantic-settings
echo ""
echo "1️⃣ Cài đặt pydantic-settings:"
pip install pydantic-settings

# 3. Kiểm tra xem có requirements.txt không
echo ""
echo "2️⃣ Kiểm tra requirements.txt:"
if [ -f "requirements.txt" ]; then
    echo "   ✅ Tìm thấy requirements.txt"
    echo "   Cài đặt tất cả dependencies:"
    pip install -r requirements.txt
else
    echo "   ⚠️ Không tìm thấy requirements.txt"
    echo "   Cài đặt các package cần thiết:"
    pip install pydantic-settings fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv
fi

# 4. Kiểm tra import
echo ""
echo "3️⃣ Kiểm tra import:"
python3 -c "from pydantic_settings import BaseSettings; print('✅ pydantic-settings OK')" || echo "❌ Lỗi import"

# 5. Test import app
echo ""
echo "4️⃣ Test import app:"
python3 -c "from app.main import app; print('✅ App import OK')" || echo "❌ Lỗi import app"

# 6. Restart service
echo ""
echo "5️⃣ Restart service:"
sudo supervisorctl stop ads-automation
sleep 2
sudo supervisorctl start ads-automation
sleep 5

# 7. Kiểm tra status
echo ""
echo "6️⃣ Kiểm tra status:"
sudo supervisorctl status

# 8. Kiểm tra port
echo ""
echo "7️⃣ Kiểm tra port 8000:"
sudo ss -tlnp | grep 8000 || echo "⚠️ Port 8000 chưa chạy, đợi thêm..."

# 9. Test kết nối
echo ""
echo "8️⃣ Test kết nối:"
sleep 3
curl -s http://localhost:8000/health || echo "⚠️ Chưa kết nối được, kiểm tra logs:"
sudo tail -20 /var/log/ads-automation.log

echo ""
echo "✅ Hoàn tất!"


