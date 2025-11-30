#!/bin/bash
# Script to check and fix service on VPS

echo "🔍 Step 1: Check existing services..."
sudo systemctl list-units --type=service | grep -E "uvicorn|fastapi|ads|meta|automation"

echo ""
echo "🔍 Step 2: Check for running Python processes..."
ps aux | grep -E "uvicorn|fastapi|main.py" | grep -v grep

echo ""
echo "🔍 Step 3: Check if service file exists..."
ls -la /etc/systemd/system/ | grep -E "uvicorn|fastapi|ads|meta|automation"

echo ""
echo "📝 Step 4: Check common service names..."
for service in uvicorn fastapi metaupdate ads-automation facebook-ads; do
    if sudo systemctl status $service &>/dev/null; then
        echo "✅ Found service: $service"
        sudo systemctl status $service --no-pager
    fi
done

echo ""
echo "🔍 Step 5: Check for old service configurations..."
if [ -f /etc/supervisor/conf.d/fastapi.conf ]; then
    echo "Found supervisor config: /etc/supervisor/conf.d/fastapi.conf"
    cat /etc/supervisor/conf.d/fastapi.conf
fi

echo ""
echo "💡 Suggested fixes:"
echo "1. If no service found, create new systemd service"
echo "2. If supervisor is used, restart with: sudo supervisorctl restart all"
echo "3. If manual uvicorn, kill and restart"
