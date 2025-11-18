#!/bin/bash
# Script để cài đặt pydantic-settings trên VPS

echo "🔧 Đang cài đặt pydantic-settings..."

# Kích hoạt virtual environment
source /var/www/ads-automation/venv/bin/activate

# Cài đặt pydantic-settings
pip install pydantic-settings==2.1.0

# Kiểm tra xem đã cài đặt thành công chưa
python3 -c "import pydantic_settings; print('✅ pydantic-settings đã được cài đặt thành công')" || echo "❌ Lỗi: Không thể import pydantic_settings"

# Kiểm tra syntax Python
echo ""
echo "🔍 Kiểm tra syntax Python..."
python3 -m py_compile app/api/routes/dashboard.py && echo "✅ Syntax OK" || echo "❌ Syntax Error"

# Restart service
echo ""
echo "🔄 Đang restart service..."
sudo supervisorctl restart ads-automation
sleep 3
sudo supervisorctl status

echo ""
echo "✅ Hoàn tất!"



