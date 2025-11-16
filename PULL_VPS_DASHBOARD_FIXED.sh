#!/bin/bash
# Script để pull code Dashboard - Tự động phát hiện tên service

set -e

echo "🚀 Bắt đầu pull code Dashboard từ GitHub..."

# Đường dẫn project trên VPS
PROJECT_DIR="/home/adsuser/ads-automation"

# Di chuyển vào thư mục project
cd "$PROJECT_DIR" || {
    echo "❌ Không tìm thấy thư mục: $PROJECT_DIR"
    exit 1
}

echo "📂 Đang ở thư mục: $(pwd)"

# Stash các thay đổi local
echo "💾 Đang stash các thay đổi local..."
git stash || true

# Pull code mới nhất
echo "⬇️  Đang pull code từ GitHub..."
git pull origin main || {
    echo "⚠️  Pull thất bại, đang thử fetch và reset..."
    git fetch origin main
    git reset --hard origin/main
}

echo "✅ Đã pull code thành công!"

# Kiểm tra syntax Python
echo "🔍 Đang kiểm tra syntax Python..."
python3 -m py_compile app/api/routes/dashboard.py app/core/ui_helpers.py app/api/routes/home.py 2>&1 || {
    echo "❌ Có lỗi syntax Python!"
    exit 1
}

echo "✅ Syntax Python hợp lệ!"

# Tự động phát hiện và restart services
echo "🔄 Đang restart services..."

# Lấy danh sách tất cả services
SERVICES=$(sudo supervisorctl status | awk '{print $1}' | grep -v "^$")

if [ -z "$SERVICES" ]; then
    echo "⚠️  Không tìm thấy services nào trong supervisor"
    echo "📊 Trạng thái supervisor:"
    sudo supervisorctl status
else
    echo "📋 Tìm thấy các services: $SERVICES"
    
    # Restart từng service
    for service in $SERVICES; do
        echo "   - Restarting $service..."
        sudo supervisorctl restart "$service" || echo "   ⚠️  Không thể restart $service"
        sleep 1
    done
fi

# Kiểm tra status
echo ""
echo "📊 Trạng thái services sau khi restart:"
sudo supervisorctl status

echo ""
echo "✅ Hoàn tất! Dashboard đã được cập nhật."
echo "🌐 Truy cập: https://updatemetaads.site/dashboard/"


