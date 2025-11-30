#!/bin/bash
# ==============================================================================
# VPS Pull Script - Phase 1 Ad Studio Complete (Tasks 1.1-1.5)
# ==============================================================================
# Đồng bộ tất cả code mới nhất từ GitHub về VPS
# Bao gồm: Ad Studio improvements và ScrapeGraphAI cleanup
# ==============================================================================

set -e  # Exit on error

echo "🚀 Bắt đầu đồng bộ code mới từ GitHub..."
echo "=================================================="

# 1. Navigate to project directory
cd ~/ads-automation || { echo "❌ Không tìm thấy thư mục ~/ads-automation"; exit 1; }

echo ""
echo "📁 Thư mục hiện tại: $(pwd)"

# 2. Stash any local changes
echo ""
echo "💾 Lưu tạm các thay đổi local (nếu có)..."
git stash

# 3. Fetch latest from GitHub
echo ""
echo "📥 Tải code mới từ GitHub..."
git fetch origin main

# 4. Reset to match remote exactly
echo ""
echo "🔄 Đồng bộ với origin/main..."
git reset --hard origin/main

# 5. Clean untracked files
echo ""
echo "🧹 Xóa các file không cần thiết..."
git clean -fd

# 6. Verify current commit
echo ""
echo "✅ Commit hiện tại:"
git log -1 --oneline

# 7. Stop backend service
echo ""
echo "⏸️  Dừng backend service..."
sudo systemctl stop metaupdate-backend || echo "⚠️  Service chưa chạy hoặc không tồn tại"

# 8. Activate Python virtual environment
echo ""
echo "🐍 Kích hoạt Python virtual environment..."
source venv/bin/activate || { echo "❌ Không tìm thấy venv"; exit 1; }

# 9. Install/update Python dependencies
echo ""
echo "📦 Cài đặt Python dependencies..."
pip install -r requirements.txt --quiet

# 10. Run database migrations (if any)
echo ""
echo "🗄️  Chạy database migrations..."
# Uncomment if you have migration scripts:
# python scripts/init_db.py

# 11. Build frontend
echo ""
echo "🎨 Build frontend..."
cd frontend
npm install --silent
npm run build
cd ..

# 12. Restart backend service
echo ""
echo "🔄 Khởi động lại backend service..."
sudo systemctl start metaupdate-backend

# 13. Check service status
echo ""
echo "🔍 Kiểm tra trạng thái service..."
sudo systemctl status metaupdate-backend --no-pager -l

# 14. Show recent logs
echo ""
echo "📋 Logs gần đây:"
sudo journalctl -u metaupdate-backend -n 20 --no-pager

echo ""
echo "=================================================="
echo "✅ HOÀN TẤT! Code đã được cập nhật lên VPS"
echo "=================================================="
echo ""
echo "📝 Thay đổi mới nhất (Phase 1 Complete):"
echo "  ✅ Task 1.1: UI merge (2-step → 1 screen)"
echo "  ✅ Task 1.2: Video Title + CTA fields"
echo "  ✅ Task 1.3: Size badge + download button"
echo "  ✅ Task 1.4: Error handling with /settings links"
echo "  ✅ Task 1.5: Remove ScrapeGraphAI references"
echo ""
echo "🌐 Truy cập: http://YOUR_VPS_IP:3000"
echo ""
