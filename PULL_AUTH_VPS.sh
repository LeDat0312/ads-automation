#!/bin/bash
# Script để pull authentication files lên VPS

set -e  # Exit on error

echo "🚀 Pulling authentication files to VPS..."
echo ""

# Vào thư mục project
cd ~/ads-automation || exit 1

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Pull code mới nhất
echo "⬇️  Pulling latest code from GitHub..."
git stash
git pull origin main

# Kiểm tra các file mới
echo ""
echo "📁 Checking new files..."
if [ -f "app/models/user.py" ]; then
    echo "✅ app/models/user.py"
else
    echo "❌ app/models/user.py not found"
    exit 1
fi

if [ -f "app/core/security.py" ]; then
    echo "✅ app/core/security.py"
else
    echo "❌ app/core/security.py not found"
    exit 1
fi

if [ -f "scripts/create_admin_user.py" ]; then
    echo "✅ scripts/create_admin_user.py"
else
    echo "❌ scripts/create_admin_user.py not found"
    exit 1
fi

# Cài đặt dependencies
echo ""
echo "📦 Installing new dependencies..."
pip install -q python-jose[cryptography] passlib[bcrypt]

# Kiểm tra import
echo ""
echo "🧪 Testing imports..."
python -c "from app.models.user import User; from app.core.security import get_password_hash; print('✅ Import OK')" || {
    echo "❌ Import failed"
    exit 1
}

echo ""
echo "✅ All files pulled and dependencies installed!"
echo ""
echo "📝 Next step: Run the following command to create an admin user:"
echo "   python scripts/create_admin_user.py"
echo ""

