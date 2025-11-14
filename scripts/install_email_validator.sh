#!/bin/bash
# Script để cài đặt email-validator và restart service

echo "=========================================="
echo "🔧 CÀI ĐẶT EMAIL-VALIDATOR"
echo "=========================================="
echo ""

cd ~/ads-automation
source venv/bin/activate

# 1. Pull code mới nhất
echo "1️⃣ Pull code mới nhất..."
git pull origin main
echo ""

# 2. Cài đặt email-validator
echo "2️⃣ Cài đặt email-validator..."
pip install email-validator==2.1.0
echo ""

# 3. Hoặc cài từ requirements.txt
echo "3️⃣ Cài đặt từ requirements.txt..."
pip install -r requirements.txt
echo ""

# 4. Kiểm tra import
echo "4️⃣ Kiểm tra import..."
python -c "import email_validator; print('✅ email-validator installed successfully')" 2>&1
python -c "from app.main import app; print('✅ Main import OK')" 2>&1
echo ""

# 5. Restart service
echo "5️⃣ Restart service..."
sudo supervisorctl restart ads-automation-api
sleep 3
sudo supervisorctl status ads-automation-api
echo ""

# 6. Check logs
echo "6️⃣ Kiểm tra logs (20 dòng cuối)..."
sudo supervisorctl tail -20 ads-automation-api
echo ""

echo "=========================================="
echo "✅ Hoàn thành!"
echo "=========================================="

