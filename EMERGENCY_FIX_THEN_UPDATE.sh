#!/bin/bash
echo "🚀 EMERGENCY FIX + DASHBOARD REDESIGN"

cd /home/adsuser/ads-automation/

# 1. Emergency fix first
echo "1. Emergency fix - using backup dashboard..."
cp app/api/routes/dashboard_backup.py app/api/routes/dashboard.py

# 2. Test and restart
source venv/bin/activate
python3 -c "import app.main; print('✅ Import OK')"
sudo supervisorctl restart ads-automation
sleep 5
sudo supervisorctl status ads-automation

# 3. Test endpoints
curl -s http://localhost:8000/health && echo " ✅ Health OK"

echo ""
echo "✅ Emergency fix completed! Website is now working."
echo "🔄 Now pulling new dashboard design from GitHub..."

# 4. Pull new dashboard design
git fetch --all
git reset --hard origin/main
sudo supervisorctl restart ads-automation

echo "✅ COMPLETED!"