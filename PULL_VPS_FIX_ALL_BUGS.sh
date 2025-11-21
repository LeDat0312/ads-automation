#!/bin/bash

# ============================================================================
# PULL VPS - FIX ALL DASHBOARD BUGS
# ============================================================================
# Script này pull code mới nhất từ GitHub về VPS
# Bao gồm tất cả các fix cho dashboard bugs
# ============================================================================

set -e  # Exit on error

echo "🚀 ===== PULL CODE TỪ GITHUB - FIX ALL BUGS ====="
echo "📅 Thời gian: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Màu sắc cho output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Xác định thư mục project
PROJECT_DIR="/root/ads-automation"

# Kiểm tra thư mục project có tồn tại không
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ Thư mục project không tồn tại: $PROJECT_DIR${NC}"
    echo -e "${YELLOW}💡 Hãy clone project trước:${NC}"
    echo "   cd /root"
    echo "   git clone https://github.com/LeDat0312/ads-automation.git"
    exit 1
fi

cd "$PROJECT_DIR"

echo -e "${BLUE}📂 Thư mục hiện tại: $(pwd)${NC}"
echo ""

# ============================================================================
# BƯỚC 1: Kiểm tra trạng thái Git
# ============================================================================
echo -e "${YELLOW}🔍 BƯỚC 1: Kiểm tra trạng thái Git...${NC}"

# Kiểm tra có thay đổi chưa commit không
if [[ -n $(git status -s) ]]; then
    echo -e "${YELLOW}⚠️  Có thay đổi chưa commit. Đang stash...${NC}"
    git stash save "Auto-stash before pull $(date '+%Y%m%d_%H%M%S')"
    STASHED=true
else
    echo -e "${GREEN}✅ Working directory clean${NC}"
    STASHED=false
fi

# Hiển thị branch hiện tại
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${BLUE}📌 Branch hiện tại: $CURRENT_BRANCH${NC}"
echo ""

# ============================================================================
# BƯỚC 2: Pull code mới từ GitHub
# ============================================================================
echo -e "${YELLOW}📥 BƯỚC 2: Pull code mới từ GitHub...${NC}"

# Fetch tất cả updates
git fetch origin

# Pull code từ main branch
echo -e "${BLUE}⬇️  Đang pull từ origin/main...${NC}"
git pull origin main --rebase

echo -e "${GREEN}✅ Pull code thành công!${NC}"
echo ""

# ============================================================================
# BƯỚC 3: Hiển thị các thay đổi mới
# ============================================================================
echo -e "${YELLOW}📋 BƯỚC 3: Các thay đổi mới nhất:${NC}"
echo ""
git log --oneline --graph --decorate -5
echo ""

# ============================================================================
# BƯỚC 4: Khôi phục stash nếu có
# ============================================================================
if [ "$STASHED" = true ]; then
    echo -e "${YELLOW}📦 BƯỚC 4: Khôi phục stash...${NC}"
    if git stash pop; then
        echo -e "${GREEN}✅ Stash đã được khôi phục${NC}"
    else
        echo -e "${RED}⚠️  Có conflict khi khôi phục stash. Vui lòng kiểm tra thủ công.${NC}"
        echo -e "${YELLOW}💡 Dùng lệnh: git status để xem conflicts${NC}"
    fi
    echo ""
fi

# ============================================================================
# BƯỚC 5: Kiểm tra dependencies (tùy chọn)
# ============================================================================
echo -e "${YELLOW}🔧 BƯỚC 5: Kiểm tra dependencies...${NC}"

# Backend - Python dependencies
if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}🐍 Kiểm tra Python dependencies...${NC}"
    # Không tự động install, chỉ hiển thị gợi ý
    echo -e "${YELLOW}💡 Nếu có dependencies mới, chạy:${NC}"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
fi

# Frontend - Node dependencies
if [ -f "frontend/package.json" ]; then
    echo -e "${BLUE}📦 Kiểm tra Node dependencies...${NC}"
    echo -e "${YELLOW}💡 Nếu có dependencies mới, chạy:${NC}"
    echo "   cd frontend"
    echo "   npm install"
    echo "   npm run build"
fi

echo ""

# ============================================================================
# BƯỚC 6: Restart services (tùy chọn)
# ============================================================================
echo -e "${YELLOW}🔄 BƯỚC 6: Restart services...${NC}"
echo ""
echo -e "${YELLOW}💡 CHỌN MỘT TRONG CÁC OPTION SAU:${NC}"
echo ""
echo "1️⃣  Restart chỉ Backend (FastAPI):"
echo "   sudo systemctl restart ads-automation"
echo ""
echo "2️⃣  Rebuild Frontend và restart Backend:"
echo "   cd frontend"
echo "   npm run build"
echo "   sudo systemctl restart ads-automation"
echo ""
echo "3️⃣  Restart toàn bộ (Backend + Nginx):"
echo "   cd frontend && npm run build"
echo "   sudo systemctl restart ads-automation"
echo "   sudo systemctl restart nginx"
echo ""

# ============================================================================
# BƯỚC 7: Tóm tắt
# ============================================================================
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ HOÀN THÀNH PULL CODE!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📊 CÁC FIX ĐÃ ĐƯỢC ÁP DỤNG:${NC}"
echo "   ✅ Fix campaign toggle ON/OFF (configured_status)"
echo "   ✅ Fix budget column display (CBO vs ABO)"
echo "   ✅ Fix budget adjustment modal"
echo "   ✅ Fix E-Commerce metrics (% ADS, Giá DATA, TLC, Frequency)"
echo "   ✅ Fix Lead Generation empty table"
echo ""
echo -e "${YELLOW}📝 Xem chi tiết tại: FIX_SUMMARY_BUGS.md${NC}"
echo ""
echo -e "${BLUE}🔗 Kiểm tra dashboard:${NC}"
echo "   http://your-vps-ip/dashboard"
echo ""
echo -e "${GREEN}🎉 Chúc mừng! Code đã được cập nhật thành công!${NC}"
echo ""
