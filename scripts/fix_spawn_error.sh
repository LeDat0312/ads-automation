#!/bin/bash
# Script để fix spawn error khi restart service

echo "=========================================="
echo "🔧 FIX SPAWN ERROR"
echo "=========================================="
echo ""

cd ~/ads-automation
source venv/bin/activate

# 1. Kiểm tra syntax
echo "1️⃣ Kiểm tra syntax Python..."
echo "-----------------------------------"
python -m py_compile app/core/ui_helpers.py 2>&1
if [ $? -eq 0 ]; then
    echo "✅ ui_helpers.py: OK"
else
    echo "❌ ui_helpers.py: Syntax error"
    exit 1
fi

python -m py_compile app/api/routes/home.py 2>&1
if [ $? -eq 0 ]; then
    echo "✅ home.py: OK"
else
    echo "❌ home.py: Syntax error"
    exit 1
fi

python -m py_compile app/api/routes/dashboard.py 2>&1
if [ $? -eq 0 ]; then
    echo "✅ dashboard.py: OK"
else
    echo "❌ dashboard.py: Syntax error"
    exit 1
fi

python -m py_compile app/api/routes/auth.py 2>&1
if [ $? -eq 0 ]; then
    echo "✅ auth.py: OK"
else
    echo "❌ auth.py: Syntax error"
    exit 1
fi

echo ""

# 2. Kiểm tra import
echo "2️⃣ Kiểm tra import..."
echo "-----------------------------------"
python -c "from app.core.ui_helpers import get_user_dropdown_menu, get_account_locked_message; print('✅ ui_helpers import OK')" 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Import error in ui_helpers"
    exit 1
fi

python -c "from app.main import app; print('✅ main.py import OK')" 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Import error in main.py"
    echo ""
    echo "Chi tiết lỗi:"
    python -c "from app.main import app" 2>&1
    exit 1
fi

echo ""

# 3. Kiểm tra dependencies
echo "3️⃣ Kiểm tra dependencies..."
echo "-----------------------------------"
python -c "import email_validator; print('✅ email-validator installed')" 2>&1
if [ $? -ne 0 ]; then
    echo "⚠️  email-validator chưa được cài đặt, đang cài..."
    pip install email-validator==2.1.0
fi

echo ""

# 4. Kiểm tra logs
echo "4️⃣ Kiểm tra logs (50 dòng cuối)..."
echo "-----------------------------------"
sudo supervisorctl tail -50 ads-automation-api 2>&1 | tail -20

echo ""

# 5. Thử start lại
echo "5️⃣ Thử start lại service..."
echo "-----------------------------------"
sudo supervisorctl stop ads-automation-api
sleep 2
sudo supervisorctl start ads-automation-api
sleep 3
sudo supervisorctl status ads-automation-api

echo ""

# 6. Kiểm tra logs sau khi start
echo "6️⃣ Kiểm tra logs sau khi start..."
echo "-----------------------------------"
sudo supervisorctl tail -30 ads-automation-api 2>&1

echo ""
echo "=========================================="
echo "✅ Hoàn thành!"
echo "=========================================="

