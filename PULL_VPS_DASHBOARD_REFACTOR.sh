#!/bin/bash

# Script để pull code mới nhất lên VPS và restart dịch vụ
# Dashboard Refactor Complete

REPO_DIR="~/ads-automation"
DASHBOARD_FILE="app/api/routes/dashboard.py"
MAIN_FILE="app/main.py"
SERVICE_NAME="ads-automation-api"

echo "🚀 Bắt đầu quá trình cập nhật Dashboard Refactor..."

# 1. Di chuyển vào thư mục dự án
echo "📁 Di chuyển vào thư mục dự án: $REPO_DIR"
cd "$REPO_DIR" || { echo "❌ Lỗi: Không thể di chuyển vào thư mục $REPO_DIR. Đảm bảo đường dẫn chính xác."; exit 1; }

# 2. Stash các thay đổi cục bộ (nếu có) và pull code mới nhất
echo "📥 Kiểm tra và stash các thay đổi cục bộ..."
git stash push --include-untracked -m "Stash before pull on $(date +'%Y-%m-%d %H:%M:%S')"
if [ $? -ne 0 ]; then
    echo "⚠️  Cảnh báo: Không thể stash các thay đổi. Có thể không có thay đổi nào hoặc có lỗi."
fi

echo "⬇️  Pull code mới nhất từ origin/main..."
git pull origin main || { echo "❌ Lỗi: Không thể pull code từ GitHub. Kiểm tra kết nối mạng hoặc quyền truy cập."; exit 1; }

# 3. Kiểm tra cú pháp Python của các file quan trọng
echo "🔍 Kiểm tra cú pháp Python của $DASHBOARD_FILE và $MAIN_FILE..."
python3 -m py_compile "$DASHBOARD_FILE" || { echo "❌ Lỗi: Lỗi cú pháp trong $DASHBOARD_FILE. Vui lòng kiểm tra code."; exit 1; }
python3 -m py_compile "$MAIN_FILE" || { echo "❌ Lỗi: Lỗi cú pháp trong $MAIN_FILE. Vui lòng kiểm tra code."; exit 1; }
echo "✅ Kiểm tra cú pháp Python thành công."

# 4. Restart dịch vụ FastAPI
echo "🔄 Restart dịch vụ Supervisor: $SERVICE_NAME..."
sudo supervisorctl restart "$SERVICE_NAME" || { echo "❌ Lỗi: Không thể restart dịch vụ $SERVICE_NAME. Kiểm tra cấu hình Supervisor."; exit 1; }
echo "✅ Dịch vụ $SERVICE_NAME đã được restart."

# 5. Kiểm tra trạng thái dịch vụ
echo "📊 Kiểm tra trạng thái tất cả các dịch vụ Supervisor..."
sudo supervisorctl status

echo ""
echo "✅ Quá trình cập nhật Dashboard Refactor hoàn tất thành công!"
echo "📋 Các tính năng mới:"
echo "   - Header: Nút Trang chủ, chỉ 1 nút Làm mới"
echo "   - Layout: Chi Tiết Quảng Cáo lên trước Tổng Quan Theo Prefix"
echo "   - View Type Tabs: Campaign / Adset / Ad"
echo "   - Multi-select checkboxes và batch actions"
echo "   - Timezone fix: Asia/Ho_Chi_Minh"
echo "   - Filter persistence: localStorage"
echo "   - Debounce search: 300ms"
echo ""
echo "🌐 Vui lòng kiểm tra dashboard trên trình duyệt để xác nhận."

