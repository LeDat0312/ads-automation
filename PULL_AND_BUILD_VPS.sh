#!/bin/bash
# Script để pull code mới và build lại frontend trên VPS

echo "🔄 Đang dừng service và kill process trên port 8000..."

# Kill process đang dùng port 8000
sudo lsof -ti:8000 | xargs sudo kill -9 2>/dev/null || echo "✅ Không có process nào đang dùng port 8000"

# Dừng supervisor services
sudo supervisorctl stop ads-automation 2>/dev/null || echo "✅ Service đã dừng"
sudo supervisorctl stop ads-worker 2>/dev/null || echo "✅ Worker đã dừng"

# Đợi 2 giây
sleep 2

echo "📥 Đang pull code mới từ GitHub..."
cd ~/ads-automation
git pull origin main

echo "📦 Đang build lại frontend..."
# Chạy script build frontend
cd ~/ads-automation
chmod +x BUILD_FRONTEND_VPS.sh
./BUILD_FRONTEND_VPS.sh

echo "🔄 Đang restart services..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart ads-automation
sudo supervisorctl restart ads-worker

echo "⏳ Đợi 5 giây để service khởi động..."
sleep 5

echo "📊 Kiểm tra status services..."
sudo supervisorctl status

echo ""
echo "📋 Logs mới nhất (20 dòng cuối):"
echo "=================================="
sudo tail -20 /var/log/ads-automation.log 2>/dev/null || echo "⚠️ Không tìm thấy log file"

echo ""
echo "✅ Hoàn tất! Kiểm tra status ở trên để đảm bảo services đang chạy."

