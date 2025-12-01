#!/bin/bash

# Script để fix lỗi database: column channel_groups.color_hex does not exist
# Chạy trên VPS

echo "=========================================="
echo "🔧 FIX DATABASE: Add color_hex column"
echo "=========================================="
echo ""

# Màu sắc
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Thư mục project
PROJECT_DIR="/home/adsuser/ads-automation"

echo "📂 Di chuyển vào thư mục project..."
cd $PROJECT_DIR || { echo -e "${RED}❌ Không tìm thấy thư mục project${NC}"; exit 1; }

echo ""
echo "🔍 Kích hoạt virtual environment..."
source venv/bin/activate

echo ""
echo "🗃️ Chạy migration để thêm column color_hex..."
python -m migrations.add_color_hex_to_channel_groups

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Migration thất bại${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Migration thành công!${NC}"

echo ""
echo "🔄 Restart backend..."
sudo systemctl restart ads-automation

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend restarted${NC}"
else
    echo -e "${RED}❌ Lỗi khi restart backend${NC}"
fi

echo ""
echo "=========================================="
echo "✅ HOÀN TẤT!"
echo "=========================================="
echo ""
echo "📋 Đã thêm column color_hex vào bảng channel_groups"
echo ""
echo "🧪 Kiểm tra:"
echo "  1. Vào Settings → Channel Groups"
echo "  2. Tạo hoặc xem channel group"
echo "  3. Không còn lỗi 500 nữa"
echo ""
