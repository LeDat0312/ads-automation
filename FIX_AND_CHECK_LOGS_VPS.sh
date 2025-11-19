#!/bin/bash
# Script để sửa lỗi và check logs cho Dashboard trên VPS

echo "=========================================="
echo "🔧 FIX DASHBOARD VPS - CHECK LOGS"
echo "=========================================="

cd ~/ads-automation

# Bước 1: Kill process đang chiếm port 8000
echo ""
echo "📋 Bước 1: Kiểm tra và kill process đang chiếm port 8000..."
sudo lsof -ti:8000 | xargs sudo kill -9 2>/dev/null || echo "Không có process nào trên port 8000"
sudo pkill -f uvicorn 2>/dev/null || echo "Không có uvicorn process"
sleep 2

# Bước 2: Kiểm tra supervisor config
echo ""
echo "📋 Bước 2: Kiểm tra supervisor config..."
sudo cat /etc/supervisor/conf.d/ads-automation.conf

# Bước 3: Đảm bảo log file có quyền ghi
echo ""
echo "📋 Bước 3: Sửa quyền log files..."
sudo touch /var/log/ads-automation.log
sudo chown adsuser:adsuser /var/log/ads-automation.log
sudo chmod 644 /var/log/ads-automation.log

# Bước 4: Build frontend
echo ""
echo "📋 Bước 4: Build frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Đang cài đặt dependencies..."
    npm install
fi
echo "Đang build frontend..."
npm run build
cd ..

# Bước 5: Kiểm tra build output
echo ""
echo "📋 Bước 5: Kiểm tra build output..."
ls -la frontend/dist/ | head -10

# Bước 6: Restart supervisor
echo ""
echo "📋 Bước 6: Restart supervisor services..."
sudo supervisorctl stop all
sleep 2
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ads-automation
sudo supervisorctl start ads-worker
sleep 3

# Bước 7: Kiểm tra status
echo ""
echo "📋 Bước 7: Kiểm tra status..."
sudo supervisorctl status

# Bước 8: Hiển thị cách check logs
echo ""
echo "=========================================="
echo "📊 CÁCH CHECK LOGS MỚI:"
echo "=========================================="
echo ""
echo "1. Backend logs (FastAPI):"
echo "   sudo tail -f /var/log/ads-automation.log"
echo ""
echo "2. Worker logs:"
echo "   sudo tail -f /var/log/ads-worker.log"
echo ""
echo "3. Supervisor logs:"
echo "   sudo tail -f /var/log/supervisor/supervisord.log"
echo ""
echo "4. Nginx logs (nếu dùng nginx):"
echo "   sudo tail -f /var/log/nginx/access.log"
echo "   sudo tail -f /var/log/nginx/error.log"
echo ""
echo "5. Browser Console (F12 trong browser):"
echo "   - Mở browser → F12 → Console tab"
echo "   - Xem JavaScript errors"
echo "   - Network tab để xem API calls"
echo ""
echo "6. Test API trực tiếp:"
echo "   curl http://localhost:8000/api/health"
echo "   curl http://localhost:8000/dashboard/data"
echo ""
echo "=========================================="
echo "✅ Hoàn tất!"
echo "=========================================="

