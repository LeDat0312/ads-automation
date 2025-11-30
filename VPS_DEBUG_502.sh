#!/bin/bash
# ==============================================================================
# VPS Debug Script - 502 Bad Gateway Error
# ==============================================================================
# Kiểm tra và khắc phục lỗi 502 Bad Gateway trên VPS
# ==============================================================================

echo "🔍 KIỂM TRA LỖI 502 BAD GATEWAY"
echo "=============================================="

# 1. Kiểm tra Nginx status
echo ""
echo "📋 1. NGINX STATUS:"
sudo systemctl status nginx --no-pager -l

# 2. Kiểm tra Backend service status
echo ""
echo "📋 2. BACKEND SERVICE STATUS:"
sudo systemctl status metaupdate-backend --no-pager -l

# 3. Kiểm tra process đang chạy
echo ""
echo "📋 3. PYTHON PROCESSES:"
ps aux | grep python | grep -v grep

# 4. Kiểm tra port backend đang lắng nghe
echo ""
echo "📋 4. PORTS LISTENING:"
sudo netstat -tlnp | grep -E ':(8000|3000|80|443)'
# Hoặc nếu không có netstat:
# sudo ss -tlnp | grep -E ':(8000|3000|80|443)'

# 5. Kiểm tra Nginx error logs
echo ""
echo "📋 5. NGINX ERROR LOGS (50 dòng cuối):"
sudo tail -50 /var/log/nginx/error.log

# 6. Kiểm tra Backend logs
echo ""
echo "📋 6. BACKEND LOGS (50 dòng cuối):"
if [ -f ~/ads-automation/uvicorn.log ]; then
    tail -50 ~/ads-automation/uvicorn.log
else
    sudo journalctl -u metaupdate-backend -n 50 --no-pager
fi

# 7. Kiểm tra Nginx config
echo ""
echo "📋 7. NGINX CONFIG TEST:"
sudo nginx -t

# 8. Kiểm tra disk space
echo ""
echo "📋 8. DISK SPACE:"
df -h

# 9. Kiểm tra memory
echo ""
echo "📋 9. MEMORY USAGE:"
free -h

# 10. Test kết nối localhost
echo ""
echo "📋 10. TEST BACKEND CONNECTION:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8000/health || echo "❌ Backend không phản hồi"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:8000/api/docs || echo "❌ API docs không phản hồi"

echo ""
echo "=============================================="
echo "✅ KIỂM TRA HOÀN TẤT"
echo "=============================================="
