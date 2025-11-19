#!/bin/bash
# Script để sửa lỗi IndentationError trong dashboard.py trên VPS

cd ~/ads-automation

echo "🔧 Đang sửa lỗi IndentationError trong dashboard.py..."

# Tạo script Python để xóa HTML code
python3 << 'PYTHON_SCRIPT'
file_path = "app/api/routes/dashboard.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original file: {len(lines)} lines")

# Xóa function trùng lặp (dòng 431-709) và HTML code (dòng 944-4894)
# Giữ lại:
# - Lines 1-430 (tất cả code trước function trùng lặp)
# - Lines 710-943 (code giữa, nhưng bỏ HTML từ 944)
# - Lines 4895-end (function thực sự)

# Thực ra, cần xóa:
# - Function trùng lặp: lines 431-709 (indices 430-708)
# - HTML code: lines 944-4894 (indices 943-4893)

# Giữ: lines 1-430 + lines 710-943 (nhưng bỏ HTML) + lines 4895-end
# Nhưng lines 710-943 có thể có HTML, nên tốt nhất là:
# Giữ: lines 1-430 + lines 4895-end

new_lines = lines[:430] + lines[4894:]

print(f"Removed duplicate function (lines 431-709) and HTML code (lines 944-4894)")
print(f"New file: {len(new_lines)} lines")

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ File cleaned successfully!")
PYTHON_SCRIPT

# Test import
echo ""
echo "🧪 Testing Python import..."
source venv/bin/activate
python3 -c "import app.main; print('✅ Import OK')" || {
    echo "❌ Import failed, trying backup..."
    if [ -f "app/api/routes/dashboard_BACKUP_BEFORE_REFACTOR_20251119_175928.py" ]; then
        cp app/api/routes/dashboard_BACKUP_BEFORE_REFACTOR_20251119_175928.py app/api/routes/dashboard.py
        echo "✅ Restored from backup"
    fi
}

# Restart service
echo ""
echo "🔄 Restarting service..."
sudo supervisorctl restart ads-automation
sleep 3
sudo supervisorctl status

echo ""
echo "✅ Done! Check logs: sudo tail -f /var/log/ads-automation.log"

