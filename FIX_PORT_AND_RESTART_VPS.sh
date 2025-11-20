#!/bin/bash
# Script để fix port 8000 bị chiếm và restart service

echo "🔄 Đang kill tất cả process trên port 8000..."

# Kill tất cả process đang dùng port 8000
sudo lsof -ti:8000 | xargs sudo kill -9 2>/dev/null || echo "✅ Không có process nào đang dùng port 8000"

# Đợi 2 giây
sleep 2

# Kiểm tra lại xem port 8000 còn bị chiếm không
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 vẫn còn bị chiếm, đang force kill..."
    sudo fuser -k 8000/tcp 2>/dev/null || true
    sleep 2
fi

echo "🧹 Đang clear Python cache..."
cd ~/ads-automation
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo "✅ Đã clear cache"

echo "🔨 Đang build frontend..."
cd frontend
npm run build
if [ -d "dist" ]; then
    sudo chown -R www-data:www-data dist
    sudo chmod -R 755 dist
    echo "✅ Frontend đã được build thành công"
else
    echo "❌ Build frontend thất bại!"
    exit 1
fi
cd ..

echo "🔄 Đang restart services..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl stop ads-automation 2>/dev/null || true
sudo supervisorctl stop ads-worker 2>/dev/null || true
sleep 2
sudo supervisorctl start ads-automation
sudo supervisorctl start ads-worker

echo "⏳ Đợi 5 giây để service khởi động..."
sleep 5

echo "📊 Kiểm tra status services..."
sudo supervisorctl status

echo ""
echo "📋 Logs mới nhất (30 dòng cuối):"
echo "=================================="
sudo tail -30 /var/log/ads-automation.log 2>/dev/null || echo "⚠️ Không tìm thấy log file"

echo ""
echo "✅ Hoàn tất! Kiểm tra status ở trên để đảm bảo services đang chạy."

