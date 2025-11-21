#!/bin/bash

# Script pull code mới nhất về VPS - Budget Optimization (4 fixes)
# Commit: d676069 - FIX: Optimize budget update - Batch processing, no reload, progress indicator

echo "=========================================="
echo "PULL CODE VPS - BUDGET OPTIMIZATION"
echo "=========================================="
echo ""

# Bước 1: Dừng service
echo "🛑 [1/6] Dừng service backend..."
sudo systemctl stop ads-automation
sleep 2

# Bước 2: Backup code hiện tại (nếu cần rollback)
echo "💾 [2/6] Backup code hiện tại..."
BACKUP_DIR="/home/backup/ads-automation-$(date +%Y%m%d_%H%M%S)"
mkdir -p /home/backup
cp -r /home/ads-automation "$BACKUP_DIR"
echo "   ✅ Backup saved to: $BACKUP_DIR"

# Bước 3: Pull code mới từ GitHub
echo "📥 [3/6] Pull code từ GitHub..."
cd /home/ads-automation || exit 1
git fetch origin
git reset --hard origin/main
echo "   ✅ Code updated to commit: d676069"

# Bước 4: Cài đặt dependencies Python (nếu có thay đổi)
echo "📦 [4/6] Kiểm tra dependencies..."
source /home/ads-automation/venv/bin/activate
pip install -r requirements.txt --quiet
echo "   ✅ Dependencies checked"

# Bước 5: Build frontend
echo "🏗️  [5/6] Build frontend..."
cd /home/ads-automation/frontend || exit 1
npm install
npm run build
echo "   ✅ Frontend built"

# Bước 6: Khởi động lại service
echo "🚀 [6/6] Khởi động service..."
sudo systemctl start ads-automation
sleep 3

# Kiểm tra status
echo ""
echo "=========================================="
echo "KIỂM TRA STATUS"
echo "=========================================="
sudo systemctl status ads-automation --no-pager -l

echo ""
echo "=========================================="
echo "✅ HOÀN THÀNH!"
echo "=========================================="
echo ""
echo "📋 THAY ĐỔI TRONG BẢN CẬP NHẬT NÀY:"
echo ""
echo "✅ LỖI 1 - Batch update budget:"
echo "   - Backend xử lý batch với asyncio.gather() + semaphore(3)"
echo "   - Giảm API spam, tối ưu performance"
echo "   - Response format: total, success_count, failed_count"
echo ""
echo "✅ LỖI 2 - Không reload toàn bộ:"
echo "   - Loại bỏ fetchData() sau budget update"
echo "   - Update state trực tiếp từ API response"
echo "   - UX mượt mà hơn, không bị giật"
echo ""
echo "✅ LỖI 3 - Progress indicator:"
echo "   - Hiển thị tiến độ batch operation"
echo "   - Progress bar trong BudgetModal"
echo "   - User biết được trạng thái xử lý"
echo ""
echo "✅ LỖI 4 - Loại bỏ adset_id filter:"
echo "   - Backend: adset_id = None khi level != ad"
echo "   - Frontend: chỉ gửi khi level === 'ad'"
echo "   - Giảm log spam không cần thiết"
echo ""
echo "🌐 Dashboard URL: http://YOUR_VPS_IP:8000/dashboard/"
echo ""
