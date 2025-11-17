#!/bin/bash

# Script cài đặt dependencies và fix lỗi 502
echo "🔧 Cài đặt dependencies và fix lỗi 502..."

cd /var/www/ads-automation

# 1. Activate virtual environment
source venv/bin/activate

# 2. Cài đặt pydantic-settings (package bị thiếu)
echo ""
echo "1️⃣ Cài đặt pydantic-settings:"
pip install pydantic-settings==2.1.0

# 3. Cài đặt tất cả dependencies từ requirements.txt
echo ""
echo "2️⃣ Cài đặt tất cả dependencies từ requirements.txt:"
pip install -r requirements.txt

# 4. Kiểm tra import
echo ""
echo "3️⃣ Kiểm tra import:"
python3 -c "from pydantic_settings import BaseSettings; print('✅ pydantic-settings OK')" || echo "❌ Lỗi import pydantic-settings"

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
curl -s http://localhost:8000/health && echo "" || echo "⚠️ Chưa kết nối được"

# 10. Xem logs nếu vẫn lỗi
echo ""
echo "9️⃣ Logs (20 dòng cuối):"
sudo tail -20 /var/log/ads-automation.log

echo ""
echo "✅ Hoàn tất!"


