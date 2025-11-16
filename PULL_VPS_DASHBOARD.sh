#!/bin/bash
# Script để pull code Dashboard mới nhất từ GitHub và restart services trên VPS

set -e

echo "🚀 Bắt đầu pull code Dashboard từ GitHub..."

# Đường dẫn project trên VPS
PROJECT_DIR="/home/adsuser/ads-automation"

# Di chuyển vào thư mục project
cd "$PROJECT_DIR" || {
    echo "❌ Không tìm thấy thư mục: $PROJECT_DIR"
    echo "Vui lòng sửa PROJECT_DIR trong script"
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

# Restart services
echo "🔄 Đang restart services..."

# Restart API
if sudo supervisorctl status api 2>/dev/null | grep -q "RUNNING\|STOPPED"; then
    echo "   - Restarting API service..."
    sudo supervisorctl restart api
    sleep 2
    if sudo supervisorctl status api | grep -q "RUNNING"; then
        echo "   ✅ API service đã restart thành công"
    else
        echo "   ❌ API service có vấn đề"
        sudo supervisorctl status api
    fi
fi

# Restart Worker (nếu có)
if sudo supervisorctl status worker 2>/dev/null | grep -q "RUNNING\|STOPPED"; then
    echo "   - Restarting Worker service..."
    sudo supervisorctl restart worker
    sleep 2
    if sudo supervisorctl status worker | grep -q "RUNNING"; then
        echo "   ✅ Worker service đã restart thành công"
    fi
fi

# Kiểm tra status
echo ""
echo "📊 Trạng thái services:"
sudo supervisorctl status

echo ""
echo "✅ Hoàn tất! Dashboard đã được cập nhật."
echo "🌐 Truy cập: https://updatemetaads.site/dashboard/"

