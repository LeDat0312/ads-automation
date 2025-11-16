#!/bin/bash

# Script để pull code Dashboard mới nhất từ GitHub và restart services trên VPS
# Sử dụng: bash PULL_DASHBOARD_VPS.sh

set -e  # Exit on error

echo "🚀 Bắt đầu pull code Dashboard từ GitHub..."

# Màu sắc cho output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Thông tin GitHub
GITHUB_USER="LeDat0312"
GITHUB_TOKEN="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"
REPO_URL="https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/${GITHUB_USER}/PythonUpdateMetaAds.git"

# Đường dẫn project trên VPS
PROJECT_DIR="/home/adsuser/ads-automation"

# Kiểm tra xem thư mục project có tồn tại không
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ Thư mục project không tồn tại: $PROJECT_DIR${NC}"
    echo "Vui lòng kiểm tra lại đường dẫn PROJECT_DIR trong script"
    exit 1
fi

# Di chuyển vào thư mục project
cd "$PROJECT_DIR"

echo -e "${YELLOW}📂 Đang ở thư mục: $(pwd)${NC}"

# Stash các thay đổi local (nếu có)
echo -e "${YELLOW}💾 Đang stash các thay đổi local...${NC}"
git stash || true

# Pull code mới nhất từ GitHub
echo -e "${YELLOW}⬇️  Đang pull code từ GitHub...${NC}"
git pull origin main || {
    echo -e "${RED}❌ Lỗi khi pull code. Đang thử fetch và reset...${NC}"
    git fetch origin main
    git reset --hard origin/main
}

echo -e "${GREEN}✅ Đã pull code thành công!${NC}"

# Kiểm tra syntax Python
echo -e "${YELLOW}🔍 Đang kiểm tra syntax Python...${NC}"
python3 -m py_compile app/api/routes/dashboard.py app/core/ui_helpers.py app/api/routes/home.py 2>&1 || {
    echo -e "${RED}❌ Có lỗi syntax Python!${NC}"
    exit 1
}

echo -e "${GREEN}✅ Syntax Python hợp lệ!${NC}"

# Cài đặt dependencies nếu cần (uncomment nếu cần)
# echo -e "${YELLOW}📦 Đang cài đặt dependencies...${NC}"
# pip3 install -r requirements.txt --quiet

# Restart services với supervisor
echo -e "${YELLOW}🔄 Đang restart services...${NC}"

# Restart API service
if sudo supervisorctl status api | grep -q "RUNNING\|STOPPED"; then
    echo -e "${YELLOW}   - Restarting API service...${NC}"
    sudo supervisorctl restart api
    sleep 2
    if sudo supervisorctl status api | grep -q "RUNNING"; then
        echo -e "${GREEN}   ✅ API service đã restart thành công${NC}"
    else
        echo -e "${RED}   ❌ API service có vấn đề sau khi restart${NC}"
        sudo supervisorctl status api
    fi
else
    echo -e "${YELLOW}   ⚠️  API service không tìm thấy trong supervisor${NC}"
fi

# Restart Worker service (nếu có)
if sudo supervisorctl status worker | grep -q "RUNNING\|STOPPED"; then
    echo -e "${YELLOW}   - Restarting Worker service...${NC}"
    sudo supervisorctl restart worker
    sleep 2
    if sudo supervisorctl status worker | grep -q "RUNNING"; then
        echo -e "${GREEN}   ✅ Worker service đã restart thành công${NC}"
    else
        echo -e "${RED}   ❌ Worker service có vấn đề sau khi restart${NC}"
        sudo supervisorctl status worker
    fi
else
    echo -e "${YELLOW}   ⚠️  Worker service không tìm thấy trong supervisor${NC}"
fi

# Kiểm tra status tất cả services
echo -e "\n${YELLOW}📊 Trạng thái services:${NC}"
sudo supervisorctl status

echo -e "\n${GREEN}✅ Hoàn tất! Code Dashboard đã được cập nhật và services đã được restart.${NC}"
echo -e "${GREEN}🌐 Truy cập: https://updatemetaads.site/dashboard/${NC}"

