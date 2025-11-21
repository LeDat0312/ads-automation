#!/bin/bash

# Script pull code về VPS - Batch Operations Fix
# Commit: 5e1c00f - FIX: Batch operations + no reload + proper filtering

echo "=========================================="
echo "PULL CODE VPS - BATCH OPERATIONS FIX"
echo "=========================================="
echo ""

# Bước 1: Dừng service
echo "🛑 [1/6] Dừng service backend..."
sudo systemctl stop ads-automation
sleep 2

# Bước 2: Backup code hiện tại
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
echo "   ✅ Code updated to commit: 5e1c00f"

# Bước 4: Cài đặt dependencies Python (nếu có)
echo "📦 [4/6] Kiểm tra Python dependencies..."
if [ -f "requirements.txt" ]; then
    source /home/ads-automation/venv/bin/activate
    pip install -r requirements.txt --quiet
    echo "   ✅ Dependencies checked"
else
    echo "   ⚠️  requirements.txt not found, skipping"
fi

# Bước 5: Build frontend
echo "🏗️  [5/6] Build frontend..."
cd /home/ads-automation/frontend || exit 1
npm install
npm run build
echo "   ✅ Frontend built"

# Bước 6: Khởi động lại service
echo "🚀 [6/6] Khởi động service..."
cd /home/ads-automation
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
echo "📋 CÁC VẤN ĐỀ ĐÃ FIX:"
echo ""
echo "✅ VẤN ĐỀ 1 - Batch status update (gom request):"
echo "   Backend:"
echo "   - Gom tất cả IDs cùng status thành 1 lần gọi batch API"
echo "   - ADSET/AD: Gọi pause_adsets()/resume_adsets() với toàn bộ mảng"
echo "   - Response: total, success_count, failed_count, success_ids"
echo "   - Log: 'Thực thi Batch BẬT LẠI hoàn tất. Thành công: 84, Thất bại: 0'"
echo ""
echo "   Frontend:"
echo "   - Gửi 1 request duy nhất với tất cả selectedIds"
echo "   - Giảm từ 84 requests xuống 1 request"
echo ""
echo "✅ VẤN ĐỀ 2 - Không reload toàn bộ trang:"
echo "   - handleConfirmStatusUpdate: Cập nhật state trực tiếp"
echo "   - handleStatusToggle: Không gọi fetchData()"
echo "   - Map qua rows và update status mới cho IDs thành công"
echo ""
echo "✅ VẤN ĐỀ 3 - Progress indicator:"
echo "   - Hiển thị progress ngay khi bắt đầu"
echo "   - Cập nhật từ response.success_count"
echo "   - UI: 'Đang xử lý 84/84 (100%)'"
echo ""
echo "✅ VẤN ĐỀ 4 - adset_id filter:"
echo "   - Chỉ gửi adset_id khi level === 'ad'"
echo "   - Không còn log spam khi level=campaign"
echo ""
echo "🔒 KHÔNG ĐỘNG VÀO:"
echo "   - Summary card logic (đang hoạt động tốt)"
echo "   - get_dashboard_dataset() core"
echo "   - Budget update (đã fix từ trước)"
echo ""
echo "🌐 Dashboard URL: http://YOUR_VPS_IP:8000/dashboard/"
echo ""
echo "📊 KẾT QUẢ MONG ĐỢI:"
echo "   - Chọn 84 adset → 1 request thay vì 84 requests"
echo "   - Bật/tắt không reload trang"
echo "   - Progress bar hiển thị tiến độ"
echo "   - Log sạch, không spam"
echo ""
