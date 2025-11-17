#!/bin/bash
echo "🚀 FIXING SUPERVISOR SPAWN ERROR"

cd /home/adsuser/ads-automation/

# 1. Stop all processes
echo "1. Stopping services..."
sudo supervisorctl stop ads-automation
sudo pkill -f uvicorn

# 2. Update from GitHub
echo "2. Pulling latest files..."
git fetch --all
git reset --hard origin/main

# 3. Fix supervisor config
echo "3. Creating correct supervisor config..."
sudo tee /etc/supervisor/conf.d/ads-automation.conf << 'EOF'
[program:ads-automation]
command=/home/adsuser/ads-automation/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
directory=/home/adsuser/ads-automation
user=adsuser
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/ads-automation.err.log
stdout_logfile=/var/log/supervisor/ads-automation.out.log
environment=PATH="/home/adsuser/ads-automation/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
redirect_stderr=true
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
killasgroup=true
stopasgroup=true
EOF

# 4. Test manual startup first
echo "4. Testing manual startup..."
source venv/bin/activate

# Test imports
echo "Testing Python imports..."
python3 -c "
try:
    import app.main
    print('✅ App import successful')
except Exception as e:
    print('❌ App import failed:', e)
    exit(1)
"

# Test uvicorn
echo "Testing uvicorn path..."
which uvicorn
uvicorn --version

# 5. Fix permissions
echo "5. Fixing permissions..."
chmod +x venv/bin/*
chown -R adsuser:adsuser /home/adsuser/ads-automation/
chmod 755 /home/adsuser/ads-automation/

# 6. Reload supervisor
echo "6. Reloading supervisor..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ads-automation

# 7. Check status
echo "7. Checking status..."
sleep 5
sudo supervisorctl status ads-automation

echo ""
echo "8. Testing endpoints..."
curl -s http://localhost:8000/health || echo "❌ Health check failed"
curl -s https://updatemetaads.site/health || echo "❌ Domain health check failed"

echo ""
echo "9. Recent logs..."
sudo tail -10 /var/log/supervisor/ads-automation.out.log

echo ""
echo "✅ Fix completed! Check results above."