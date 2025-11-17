#!/bin/bash

# Script tạo file .env từ template
echo "📝 Tạo file .env từ template..."

# Kiểm tra xem .env đã tồn tại chưa
if [ -f ".env" ]; then
    echo "⚠️  File .env đã tồn tại!"
    read -p "Bạn có muốn ghi đè không? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Hủy bỏ."
        exit 1
    fi
    echo "📋 Backup file .env cũ thành .env.backup"
    cp .env .env.backup
fi

# Copy từ template
if [ -f ".env.template" ]; then
    cp .env.template .env
    echo "✅ Đã tạo file .env từ .env.template"
    echo ""
    echo "⚠️  QUAN TRỌNG: Vui lòng chỉnh sửa file .env và điền các giá trị thực tế:"
    echo "   - ACCESS_TOKEN"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - TELEGRAM_WEBHOOK_SECRET"
    echo "   - SECRET_KEY (ít nhất 32 ký tự)"
    echo "   - WEBHOOK_URL"
    echo "   - DATABASE_URL (nếu khác)"
    echo ""
    echo "Sau đó chạy: nano .env hoặc vi .env"
else
    echo "❌ Không tìm thấy file .env.template"
    exit 1
fi

