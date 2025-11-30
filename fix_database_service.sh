#!/bin/bash
# Script tự động kiểm tra và sửa database + service

set -e

cd /home/adsuser/ads-automation

echo "🔍 Step 1: Checking DATABASE_URL..."
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    exit 1
fi

if ! grep -q "DATABASE_URL" .env; then
    echo "❌ DATABASE_URL not found in .env"
    exit 1
fi

DB_URL=$(grep DATABASE_URL .env | cut -d'=' -f2- | tr -d '"' | tr -d "'" | xargs)
if [ -z "$DB_URL" ]; then
    echo "❌ DATABASE_URL is empty"
    exit 1
fi

echo "✅ DATABASE_URL found"

# Extract database name from URL
# Format: postgresql://user:pass@host:port/dbname
DB_NAME=$(echo $DB_URL | sed -n 's|.*/\([^?]*\).*|\1|p')
DB_USER=$(echo $DB_URL | sed -n 's|postgresql://\([^:]*\):.*|\1|p')

echo "📋 Database: $DB_NAME"
echo "📋 User: $DB_USER"

echo ""
echo "🔍 Step 2: Checking PostgreSQL service..."
if ! systemctl is-active --quiet postgresql; then
    echo "⚠️  PostgreSQL not running, starting..."
    sudo systemctl start postgresql
    sleep 2
fi
echo "✅ PostgreSQL is running"

echo ""
echo "🔍 Step 3: Checking if database exists..."
DB_EXISTS=$(sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME" && echo "yes" || echo "no")

if [ "$DB_EXISTS" = "no" ]; then
    echo "📦 Creating database $DB_NAME..."
    sudo -u postgres createdb -O $DB_USER $DB_NAME 2>/dev/null || {
        echo "⚠️  Failed to create database, trying with postgres user..."
        sudo -u postgres createdb $DB_NAME
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null || true
    }
    echo "✅ Database created"
else
    echo "✅ Database already exists"
fi

echo ""
echo "🧪 Step 4: Testing database connection..."
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
fi

python3 -c "
import sys
sys.path.insert(0, '/home/adsuser/ads-automation')
from app.core.config import get_settings
from app.core.database import init_db
try:
    settings = get_settings()
    print('✅ Config loaded')
    init_db()
    print('✅ Database connection successful!')
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
" || {
    echo "❌ Database connection test failed!"
    exit 1
}

echo ""
echo "🔄 Step 5: Restarting service..."
sudo systemctl restart ads-automation.service
sleep 3

echo ""
echo "📊 Service status:"
if sudo systemctl is-active --quiet ads-automation.service; then
    echo "✅ Service is running"
else
    echo "❌ Service is not running. Check logs:"
    echo "   sudo journalctl -u ads-automation.service -n 50"
    exit 1
fi

echo ""
echo "✅ All checks passed!"

