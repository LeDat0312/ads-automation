#!/bin/bash
# Script pull code mới nhất lên VPS
# Chạy: bash PULL_VPS_DASHBOARD_LATEST.sh

cd ~/ads-automation || exit 1

echo "🔄 Đang pull code mới nhất từ GitHub..."
git pull origin main

if [ $? -eq 0 ]; then
    echo "✅ Pull code thành công!"
    
    echo "🔍 Đang kiểm tra syntax Python..."
    python3 -m py_compile app/api/routes/dashboard.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Syntax OK!"
        
        echo "🔄 Đang restart service..."
        sudo supervisorctl restart ads-automation-api
        
        echo "📊 Trạng thái service:"
        sudo supervisorctl status
        
        echo ""
        echo "✅ Hoàn tất! Dashboard đã được cập nhật."
    else
        echo "❌ Lỗi syntax! Vui lòng kiểm tra lại."
        exit 1
    fi
else
    echo "❌ Lỗi khi pull code! Vui lòng kiểm tra lại."
    exit 1
fi

