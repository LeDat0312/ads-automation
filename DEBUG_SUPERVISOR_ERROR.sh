#!/bin/bash
echo "🔧 DEBUGGING SUPERVISOR SPAWN ERROR"

cd /home/adsuser/ads-automation/

echo "1. Checking supervisor logs..."
sudo tail -20 /var/log/supervisor/ads-automation.err.log

echo ""
echo "2. Checking supervisor config..."
cat /etc/supervisor/conf.d/ads-automation.conf

echo ""
echo "3. Testing manual start..."
source venv/bin/activate
python3 -c "import app.main; print('✅ App import OK')"

echo ""
echo "4. Testing uvicorn directly..."
timeout 10s uvicorn app.main:app --host 0.0.0.0 --port 8000 || echo "Uvicorn test completed"

echo ""
echo "5. Checking port 8000..."
netstat -tulpn | grep :8000

echo ""
echo "6. Checking permissions..."
ls -la /home/adsuser/ads-automation/venv/bin/uvicorn
ls -la /home/adsuser/ads-automation/

echo ""
echo "7. Current supervisor status..."
sudo supervisorctl status