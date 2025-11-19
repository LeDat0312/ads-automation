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

# Xóa HTML code từ dòng 944 đến 4894 (indices 943-4893)
# Giữ: lines 1-943 + lines 4895-end
new_lines = lines[:943] + lines[4894:]

print(f"Removed HTML/CSS/JS code (lines 944-4894)")
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
    echo "❌ Import failed!"
    exit 1
}

# Restart service
echo ""
echo "🔄 Restarting service..."
sudo supervisorctl restart ads-automation
sleep 3
sudo supervisorctl status

echo ""
echo "✅ Done! Check logs: sudo tail -f /var/log/ads-automation.log"

