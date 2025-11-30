#!/bin/bash
# Debug supervisor service errors

echo "🔍 Debugging Supervisor service errors..."
echo ""

echo "Step 1: Check supervisor logs for ads-automation..."
echo "=================================================="
sudo supervisorctl tail ads-automation stderr | tail -50

echo ""
echo ""
echo "Step 2: Check stdout logs..."
echo "=================================================="
sudo supervisorctl tail ads-automation stdout | tail -50

echo ""
echo ""
echo "Step 3: Check supervisor config..."
echo "=================================================="
if [ -f /etc/supervisor/conf.d/ads-automation.conf ]; then
    echo "Config file: /etc/supervisor/conf.d/ads-automation.conf"
    cat /etc/supervisor/conf.d/ads-automation.conf
else
    echo "Looking for config files..."
    sudo find /etc/supervisor -name "*.conf" -exec echo "Found: {}" \; -exec cat {} \;
fi

echo ""
echo ""
echo "Step 4: Check if .env file exists..."
echo "=================================================="
if [ -f /home/adsuser/ads-automation/.env ]; then
    echo "✅ .env file exists"
    echo "Variables count: $(wc -l < /home/adsuser/ads-automation/.env)"
else
    echo "❌ .env file NOT found!"
fi

echo ""
echo ""
echo "Step 5: Test Python imports..."
echo "=================================================="
cd /home/adsuser/ads-automation
source venv/bin/activate
python -c "from app.main import app; print('✅ Import successful')" 2>&1

echo ""
echo ""
echo "Step 6: Check database connection..."
echo "=================================================="
python -c "from app.core.database import engine; engine.connect(); print('✅ Database OK')" 2>&1

echo ""
echo ""
echo "💡 Next steps:"
echo "1. Fix the error shown above"
echo "2. Update .env if needed"
echo "3. Restart: sudo supervisorctl restart ads-automation"
