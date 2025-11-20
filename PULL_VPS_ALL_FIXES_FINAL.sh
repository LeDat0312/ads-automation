#!/bin/bash
# Script để pull code mới và restart service sau khi fix tất cả bugs

echo "🔄 Đang dừng service và kill process trên port 8000..."

# Kill process đang dùng port 8000
sudo lsof -ti:8000 | xargs sudo kill -9 2>/dev/null || echo "✅ Không có process nào đang dùng port 8000"

# Dừng supervisor services
sudo supervisorctl stop ads-automation 2>/dev/null || echo "✅ Service đã dừng"
sudo supervisorctl stop ads-worker 2>/dev/null || echo "✅ Worker đã dừng"

# Đợi 2 giây
sleep 2

echo "📥 Đang pull code mới từ GitHub..."
cd ~/ads-automation
git pull origin main

echo "🧹 Đang clear Python cache..."
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo "✅ Đã clear cache"

echo "🔨 Đang build frontend (nếu có thay đổi)..."
# Chỉ build nếu có thay đổi trong frontend hoặc lần đầu
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo "📦 Đang cài đặt dependencies..."
        npm install
    fi
    echo "🔨 Đang build frontend..."
    npm run build
    if [ -d "dist" ]; then
        sudo chown -R www-data:www-data dist
        sudo chmod -R 755 dist
        echo "✅ Frontend đã được build thành công"
    else
        echo "⚠️  Build frontend thất bại, nhưng vẫn tiếp tục restart service"
    fi
    cd ..
fi

echo "🔄 Đang restart services..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart ads-automation
sudo supervisorctl restart ads-worker

echo "⏳ Đợi 5 giây để service khởi động..."
sleep 5

echo "📊 Kiểm tra status services..."
sudo supervisorctl status

echo ""
echo "📋 Logs mới nhất (20 dòng cuối):"
echo "=================================="
sudo tail -20 /var/log/ads-automation.log 2>/dev/null || echo "⚠️ Không tìm thấy log file"

echo ""
echo "✅ Hoàn tất! Kiểm tra status ở trên để đảm bảo services đang chạy."
echo ""
echo "📝 Thay đổi chính trong lần update này:"
echo "   ✅ Summary chỉ tính từ adsets có spend > 0 và impressions > 0"
echo "   ✅ Lead Gen: Hiển thị đúng cột 'Lượt Mua' và 'Chi phí / LM'"
echo "   ✅ Bulk actions: Thêm confirm popup và progress bar"
echo "   ✅ Layout: Cải thiện thanh bulk action (sticky, đẹp hơn)"
echo "   ✅ Totals: cost_per_purchase tính từ tổng spend/purchases (Lead Gen)"

