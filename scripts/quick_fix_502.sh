#!/bin/bash
# Script để fix nhanh lỗi 502

echo "=========================================="
echo "🔧 FIX NHANH LỖI 502 BAD GATEWAY"
echo "=========================================="
echo ""

cd ~/ads-automation
source venv/bin/activate

# 1. Pull code mới nhất
echo "1️⃣ Pull code mới nhất..."
git pull origin main
echo ""

# 2. Check syntax
echo "2️⃣ Kiểm tra syntax..."
python -m py_compile app/api/routes/profile.py
python -m py_compile app/api/routes/user_management.py
python -m py_compile app/api/routes/settings.py
python -m py_compile app/main.py
echo "✅ Syntax OK"
echo ""

# 3. Restart services
echo "3️⃣ Restart services..."
sudo supervisorctl restart ads-automation-api
sleep 2
sudo supervisorctl status ads-automation-api
echo ""

# 4. Check logs
echo "4️⃣ Kiểm tra logs (10 dòng cuối)..."
sudo supervisorctl tail -10 ads-automation-api
echo ""

echo "=========================================="
echo "✅ Hoàn thành!"
echo "=========================================="
