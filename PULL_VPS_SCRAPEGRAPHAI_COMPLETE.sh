#!/bin/bash
# 🔍 Script Pull ScrapeGraphAI Code về VPS - HOÀN CHỈNH

set -e  # Exit on error

echo "========================================"
echo "🚀 PULL SCRAPEGRAPHAI CODE VỀ VPS"
echo "========================================"
echo ""

cd ~/ads-automation

echo "📥 Bước 1: Pull code từ GitHub..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Lỗi khi pull code. Có thể có conflict."
    echo "💡 Thử reset về remote:"
    echo "   git fetch origin"
    echo "   git reset --hard origin/main"
    exit 1
fi

echo ""
echo "🔄 Bước 2: Chạy migration để thêm columns ScrapeGraphAI..."
source venv/bin/activate

# Set PYTHONPATH để có thể import app
export PYTHONPATH=/home/adsuser/ads-automation:$PYTHONPATH

python migrations/add_scrapegraphai_api_key.py

if [ $? -ne 0 ]; then
    echo "⚠️ Migration có lỗi, nhưng có thể columns đã tồn tại. Tiếp tục..."
fi

echo ""
echo "🔄 Bước 3: Restart services..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart ads-automation
sudo supervisorctl restart ads-worker

echo ""
echo "⏳ Đợi 3 giây để services khởi động..."
sleep 3

echo ""
echo "📊 Bước 4: Kiểm tra status services..."
sudo supervisorctl status

echo ""
echo "📝 Bước 5: Hiển thị logs (10 dòng cuối)..."
echo "----------------------------------------"
sudo tail -10 /var/log/ads-automation.log

echo ""
echo "========================================"
echo "✅ HOÀN TẤT!"
echo "========================================"
echo ""
echo "📝 Để xem logs real-time:"
echo "   sudo tail -f /var/log/ads-automation.log"
echo ""
echo "🔍 Kiểm tra sau khi deploy:"
echo "   1. Truy cập: https://updatemetaads.site/"
echo "      → Kiểm tra có card '🔍 Nghiên Cứu Đối Thủ' không"
echo ""
echo "   2. Truy cập: https://updatemetaads.site/settings"
echo "      → Kiểm tra có section 'ScrapeGraphAI API Key' không"
echo "      → Thử lưu API key và test"
echo ""
echo "   3. Truy cập: https://updatemetaads.site/competitor"
echo "      → Kiểm tra trang nghiên cứu đối thủ có hoạt động không"
echo ""
echo "🔄 Nếu cần restart lại:"
echo "   sudo supervisorctl restart ads-automation"
echo "   sudo supervisorctl restart ads-worker"
echo ""

