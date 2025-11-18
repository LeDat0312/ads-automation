#!/bin/bash
# Script debug 502 Bad Gateway

echo "=== Kiểm tra Supervisor Status ==="
sudo supervisorctl status

echo ""
echo "=== Kiểm tra logs backend ==="
sudo tail -50 /var/log/ads-automation.log

echo ""
echo "=== Kiểm tra stderr logs ==="
sudo tail -50 /var/log/ads-automation-stderr.log 2>/dev/null || echo "Không có stderr log"

echo ""
echo "=== Kiểm tra Python syntax ==="
cd ~/ads-automation
python3 -m py_compile app/api/routes/dashboard.py app/services/facebook_api.py 2>&1

echo ""
echo "=== Kiểm tra port 8000 ==="
sudo netstat -tlnp | grep 8000 || sudo ss -tlnp | grep 8000

echo ""
echo "=== Kiểm tra nginx error log ==="
sudo tail -20 /var/log/nginx/error.log

echo ""
echo "=== Kiểm tra nginx config ==="
sudo nginx -t

