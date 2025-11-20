#!/bin/bash
# Script để build frontend trên VPS

echo "🔨 Đang build frontend..."

# Di chuyển vào thư mục frontend
cd ~/ads-automation/frontend

# Kiểm tra xem có package.json không
if [ ! -f "package.json" ]; then
    echo "❌ Không tìm thấy package.json trong thư mục frontend"
    echo "📁 Thư mục hiện tại: $(pwd)"
    exit 1
fi

# Kiểm tra xem có node_modules không, nếu không thì install
if [ ! -d "node_modules" ]; then
    echo "📦 Đang cài đặt dependencies..."
    npm install
fi

# Xóa dist folder cũ (nếu có)
echo "🗑️  Đang xóa dist folder cũ..."
sudo rm -rf dist

# Build frontend
echo "🔨 Đang build frontend (có thể mất vài phút)..."
npm run build

# Kiểm tra xem build có thành công không
if [ ! -d "dist" ]; then
    echo "❌ Build thất bại! Không tìm thấy thư mục dist"
    exit 1
fi

# Set ownership cho nginx
echo "🔐 Đang set ownership cho nginx..."
sudo chown -R www-data:www-data dist
sudo chmod -R 755 dist

echo "✅ Build frontend thành công!"
echo "📁 Thư mục dist: $(pwd)/dist"
echo ""
echo "🔄 Để reload nginx, chạy: sudo systemctl reload nginx"

