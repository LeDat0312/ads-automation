#!/bin/bash

# Script cài đặt Node.js và npm trên Ubuntu
# Chạy với quyền sudo: sudo bash INSTALL_REACT_DEPENDENCIES_UBUNTU.sh

echo "Bắt đầu cài đặt Node.js và npm..."

# Cập nhật package list
sudo apt update

# Cài đặt Node.js và npm (version 18.x LTS)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Kiểm tra phiên bản
echo "Node.js version:"
node --version
echo "npm version:"
npm --version

# Cài đặt dependencies cho React components (nếu có package.json)
if [ -f "package.json" ]; then
    echo "Đang cài đặt npm dependencies..."
    npm install
    echo "✅ Đã cài đặt dependencies thành công!"
else
    echo "⚠️  Không tìm thấy package.json. Các React components cần được tích hợp vào frontend app riêng."
fi

echo "Hoàn tất!"

