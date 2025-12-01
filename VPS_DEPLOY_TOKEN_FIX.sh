#!/bin/bash

# Script để deploy fix hoàn chỉnh: Token hết hạn + Database
# Chạy trên VPS

echo "=========================================="
echo "🚀 DEPLOY FIX HOÀN CHỈNH"
echo "=========================================="
echo ""

# Màu sắc
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Thư mục project
PROJECT_DIR="/home/adsuser/ads-automation"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "📂 Di chuyển vào thư mục project..."
cd $PROJECT_DIR || { echo -e "${RED}❌ Không tìm thấy thư mục project${NC}"; exit 1; }

echo ""
echo "🔍 Stash thay đổi local (nếu có)..."
git stash

echo ""
echo "📥 Pull code mới từ GitHub..."
git pull origin main

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Lỗi khi pull code${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Pull code thành công!${NC}"

echo ""
echo "=========================================="
echo "🗃️ CHẠY MIGRATIONS"
echo "=========================================="
echo ""

echo "🔍 Kích hoạt virtual environment..."
source venv/bin/activate

echo ""
echo "📝 Migration 1: Thêm column color_hex vào channel_groups..."
python -m migrations.add_color_hex_to_channel_groups

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Migration 1 thất bại${NC}"
    exit 1
fi

echo ""
echo "📝 Migration 2: Thêm column last_error vào facebook_accounts..."
python -m migrations.add_last_error_to_facebook_accounts

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Migration 2 thất bại${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Tất cả migrations thành công!${NC}"

echo ""
echo "=========================================="
echo "🔨 REBUILD FRONTEND"
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

echo "🔄 Restart Backend..."
sudo systemctl restart ads-automation

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend restarted${NC}"
else
    echo -e "${RED}❌ Lỗi khi restart backend${NC}"
fi

echo ""
echo "🔄 Restart Nginx..."
sudo systemctl restart nginx

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Nginx restarted${NC}"
else
    echo -e "${RED}❌ Lỗi khi restart nginx${NC}"
fi

echo ""
echo "=========================================="
echo "✅ HOÀN TẤT!"
echo "=========================================="
echo ""
echo "📋 Các thay đổi đã được áp dụng:"
echo ""
echo "  ✅ Database:"
echo "     - Thêm column color_hex vào channel_groups"
echo "     - Thêm column last_error vào facebook_accounts"
echo ""
echo "  ✅ Backend:"
echo "     - Xử lý token hết hạn (code 190) → set is_active=False"
echo "     - Lưu last_error vào DB"
echo "     - Trả message tiếng Việt rõ ràng"
echo "     - Clear error khi token hoạt động lại"
echo ""
echo "  ✅ Frontend:"
echo "     - Hiển thị trạng thái Via (Token hết hạn)"
echo "     - Hiển thị last_error nếu có"
echo "     - Cảnh báo khi chọn Via không hoạt động"
echo "     - Hiển thị error detail từ backend"
echo ""
echo "🧪 Kiểm tra:"
echo "  1. Vào Settings → Facebook Via"
echo "  2. Chọn Via có token hết hạn → Bấm 'Tải danh sách Fanpage'"
echo "  3. Xem toast hiển thị: 'Token Facebook của Via này đã hết hạn...'"
echo "  4. Via sẽ được đánh dấu 'Token hết hạn' trong dropdown"
echo ""
echo "📊 Xem logs nếu cần:"
echo "  sudo journalctl -u ads-automation -f"
echo ""
