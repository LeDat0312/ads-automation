#!/bin/bash
# 🔧 Script Fix và Restart Service trên VPS

set -e

echo "========================================"
echo "🔧 FIX VÀ RESTART SERVICE"
echo "========================================"
echo ""

cd ~/ads-automation

echo "📥 Bước 1: Pull code mới nhất..."
git pull origin main

echo ""
echo "🔄 Bước 2: Kill processes trên port 8000..."
sudo lsof -ti:8000 | xargs sudo kill -9 2>/dev/null || echo "Không có process nào trên port 8000"

echo ""
echo "🔄 Bước 3: Fix log file permissions..."
sudo touch /var/log/ads-automation.log
sudo touch /var/log/ads-worker.log
sudo chown adsuser:adsuser /var/log/ads-automation.log /var/log/ads-worker.log 2>/dev/null || true

echo ""
echo "🔄 Bước 4: Restart supervisor services..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart ads-automation
sudo supervisorctl restart ads-worker

echo ""
echo "⏳ Đợi 5 giây để services khởi động..."
sleep 5

echo ""
echo "📊 Bước 5: Kiểm tra status..."
sudo supervisorctl status

echo ""
echo "📝 Bước 6: Hiển thị logs (20 dòng cuối)..."
echo "----------------------------------------"
sudo tail -20 /var/log/ads-automation.log

echo ""
echo "========================================"
echo "✅ HOÀN TẤT!"
echo "========================================"
echo ""
echo "📝 Để xem logs real-time:"
echo "   sudo tail -f /var/log/ads-automation.log"
echo ""
echo "🔍 Kiểm tra Settings page:"
echo "   https://updatemetaads.site/settings"
echo "   → Scroll xuống để tìm section 'ScrapeGraphAI API Key'"
echo ""

