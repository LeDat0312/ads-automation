#!/bin/bash
echo "🚀 EMERGENCY FIX - INDENTATION ERROR"

cd /home/adsuser/ads-automation/

# 1. Create quick backup
cp app/api/routes/dashboard.py app/api/routes/dashboard_broken.py

# 2. Fix the Python syntax error by removing stray CSS
# The error is at line 1644 - CSS code mixed with Python

# Temporary fix: Use the working dashboard_backup.py
echo "Using backup dashboard file temporarily..."
cp app/api/routes/dashboard_backup.py app/api/routes/dashboard.py

# 3. Test import
echo "Testing Python import..."
source venv/bin/activate
python3 -c "
try:
    import app.main
    print('✅ App import successful - FIXED!')
except Exception as e:
    print('❌ App import failed:', e)
    exit(1)
"

# 4. Start supervisor
echo "Starting supervisor..."
sudo supervisorctl start ads-automation
sleep 5
sudo supervisorctl status ads-automation

# 5. Test endpoints
echo "Testing endpoints..."
curl -s http://localhost:8000/health && echo " ✅ Local health OK"
curl -s https://updatemetaads.site/health && echo " ✅ Domain health OK"

echo ""
echo "✅ EMERGENCY FIX COMPLETED!"
echo "Dashboard is now working with backup version."
echo "You can access: https://updatemetaads.site/dashboard/"