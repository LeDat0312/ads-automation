#!/bin/bash
# Script để pull code mới nhất từ GitHub và restart services trên VPS
# Sử dụng: bash PULL_VPS_DASHBOARD_FIX.sh

echo "🚀 Bắt đầu pull code từ GitHub..."

# Di chuyển đến thư mục dự án
cd ~/ads-automation || exit 1

# Stash các thay đổi local (nếu có)
echo "📦 Stashing local changes..."
git stash

# Pull code mới nhất từ GitHub
echo "⬇️ Pulling code from GitHub..."
git pull origin main

# Kiểm tra syntax Python
echo "🔍 Checking Python syntax..."
python3 -m py_compile app/api/routes/dashboard.py app/core/ui_helpers.py app/api/routes/home.py app/main.py

if [ $? -eq 0 ]; then
    echo "✅ Python syntax check passed!"
    
    # Restart services
    echo "🔄 Restarting services..."
    sudo supervisorctl restart all
    
    # Kiểm tra status
    echo "📊 Checking service status..."
    sudo supervisorctl status
    
    echo ""
    echo "✅ Hoàn tất! Code đã được cập nhật và services đã được restart."
    echo "📝 Xem logs nếu cần:"
    echo "   sudo supervisorctl tail -200 ads-automation-api"
else
    echo "❌ Python syntax check failed! Vui lòng kiểm tra lại code."
    exit 1
fi
