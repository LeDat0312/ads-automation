#!/bin/bash

# Script để pull fix kết nối Fanpage Facebook về VPS
# Chạy trên VPS với quyền root hoặc user có quyền

echo "=========================================="
echo "🔄 PULL FIX KẾT NỐI FANPAGE FACEBOOK"
echo "=========================================="
echo ""

# Màu sắc
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Thư mục project
PROJECT_DIR="/root/ads-automation"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "📂 Di chuyển vào thư mục project..."
cd $PROJECT_DIR || { echo -e "${RED}❌ Không tìm thấy thư mục project${NC}"; exit 1; }

echo ""
echo "🔍 Kiểm tra trạng thái Git..."
git status

echo ""
echo "⚠️  Stash các thay đổi local (nếu có)..."
git stash

echo ""
echo "📥 Pull code mới từ GitHub..."
git pull origin main

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Lỗi khi pull code. Vui lòng kiểm tra lại.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Pull code thành công!${NC}"

echo ""
echo "=========================================="
echo "🔄 REBUILD FRONTEND"
echo "=========================================="
echo ""

echo "📂 Di chuyển vào thư mục frontend..."
cd $FRONTEND_DIR || { echo -e "${RED}❌ Không tìm thấy thư mục frontend${NC}"; exit 1; }

echo ""
echo "🔨 Build frontend mới..."
npm run build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Lỗi khi build frontend${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Build frontend thành công!${NC}"

echo ""
echo "=========================================="
echo "🔄 RESTART SERVICES"
echo "=========================================="
echo ""

echo "🔄 Restart Gunicorn (Backend)..."
sudo systemctl restart ads-automation

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Gunicorn restarted${NC}"
else
    echo -e "${RED}❌ Lỗi khi restart Gunicorn${NC}"
fi

echo ""
echo "🔄 Restart Nginx..."
sudo systemctl restart nginx

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Nginx restarted${NC}"
else
    echo -e "${RED}❌ Lỗi khi restart Nginx${NC}"
fi

echo ""
echo "=========================================="
echo "✅ HOÀN TẤT!"
echo "=========================================="
echo ""
echo "📋 Các thay đổi đã được áp dụng:"
echo "  ✅ Sửa lỗi GET /api/facebook-accounts/{id}/pages (400 → 200)"
echo "  ✅ Lưu đúng Page Access Token khi kết nối"
echo "  ✅ Hiển thị thông báo lỗi tiếng Việt rõ ràng"
echo "  ✅ Cảnh báo khi thiếu quyền QTV"
echo ""
echo "🧪 Kiểm tra:"
echo "  1. Vào Settings → Facebook Via"
echo "  2. Chọn Via → Bấm 'Tải danh sách Fanpage'"
echo "  3. Kiểm tra tab 'Chọn từ danh sách' có hiển thị pages không"
echo "  4. Kết nối 1 page và kiểm tra toast message"
echo ""
echo "📊 Kiểm tra logs nếu cần:"
echo "  sudo journalctl -u ads-automation -f"
echo ""
