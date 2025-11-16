#!/bin/bash

# Script kiểm tra thông tin services trên server Ubuntu
# Chạy trên server: bash check-services.sh

echo "================================"
echo "🔍 KIỂM TRA THÔNG TIN SERVICES"
echo "================================"
echo ""

echo "📋 1. Processes đang chạy (gunicorn, supervisor, uvicorn, nginx):"
echo "---"
ps aux | grep -E 'gunicorn|supervisor|uvicorn|nginx|python' | grep -v grep
echo ""

echo "📋 2. Status Supervisor services:"
echo "---"
sudo supervisorctl status 2>/dev/null || echo "⚠️  Supervisor không cài đặt hoặc không có quyền"
echo ""

echo "📋 3. Systemd services:"
echo "---"
systemctl list-units --type=service --state=active | grep -E 'ads|app|automation|gunicorn' || echo "Không tìm thấy service liên quan"
echo ""

echo "📋 4. Nginx status:"
echo "---"
sudo systemctl status nginx 2>/dev/null | head -5 || echo "⚠️  Nginx không cài đặt hoặc không chạy"
echo ""

echo "📋 5. Python processes:"
echo "---"
ps aux | grep python | grep -v grep
echo ""

echo "📋 6. Port đang listen:"
echo "---"
sudo netstat -tlnp 2>/dev/null | grep -E 'LISTEN|Proto' || sudo ss -tlnp 2>/dev/null || echo "⚠️  Không thể kiểm tra port"
echo ""

echo "📋 7. Environment file (.env):"
echo "---"
if [ -f /home/adsuser/ads-automation/.env ]; then
    echo "✅ File .env tồn tại"
else
    echo "⚠️  File .env không tồn tại"
fi
echo ""

echo "📋 8. Project structure:"
echo "---"
ls -la /home/adsuser/ads-automation/ | head -15
echo ""

echo "================================"
echo "✅ Kiểm tra hoàn tất!"
echo "================================"
