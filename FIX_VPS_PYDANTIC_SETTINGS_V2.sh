#!/bin/bash
# Script để cài đặt pydantic-settings vào đúng Python environment mà supervisor đang dùng

echo "🔍 Kiểm tra supervisor config..."
sudo cat /etc/supervisor/conf.d/ads-automation.conf | grep -E "command|directory|user"

echo ""
echo "🔍 Kiểm tra Python path mà supervisor đang dùng..."
# Lấy Python path từ supervisor config
PYTHON_PATH=$(sudo cat /etc/supervisor/conf.d/ads-automation.conf | grep "command=" | sed 's/.*command=//' | awk '{print $1}' | sed 's|/uvicorn.*||' | sed 's|/bin/python.*||')
echo "Python path từ config: $PYTHON_PATH"

# Kiểm tra xem có venv không
if [ -d "$PYTHON_PATH/bin" ]; then
    echo "✅ Tìm thấy venv tại: $PYTHON_PATH"
    echo "🔧 Đang cài đặt pydantic-settings vào venv này..."
    $PYTHON_PATH/bin/pip install pydantic-settings==2.1.0
    echo "✅ Đã cài đặt vào venv"
else
    echo "⚠️ Không tìm thấy venv, đang kiểm tra system Python..."
    # Thử với system Python
    sudo python3 -m pip install pydantic-settings==2.1.0
    echo "✅ Đã cài đặt vào system Python"
fi

echo ""
echo "🔍 Kiểm tra process đang chạy..."
ps aux | grep uvicorn | grep -v grep

echo ""
echo "🔍 Kiểm tra Python path của process đang chạy..."
PID=$(ps aux | grep uvicorn | grep -v grep | awk '{print $2}' | head -1)
if [ ! -z "$PID" ]; then
    echo "Process ID: $PID"
    sudo ls -la /proc/$PID/exe
fi

echo ""
echo "🔄 Đang restart service..."
sudo supervisorctl restart ads-automation
sleep 5
sudo supervisorctl status

echo ""
echo "📋 Kiểm tra logs..."
sudo tail -20 /var/log/ads-automation.log



