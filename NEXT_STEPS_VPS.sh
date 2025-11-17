#!/bin/bash
# 🚀 NEXT STEPS FOR VPS RESTORATION

echo "=============================================="
echo "🔧 VPS RESTORATION - NEXT STEPS"
echo "=============================================="

cd /home/adsuser/ads-automation/

# Step 1: Ensure python3-venv is installed
echo "📦 Step 1: Installing python3-venv..."
sudo apt update
sudo apt install python3.10-venv -y

# Step 2: Recreate virtual environment
echo "🐍 Step 2: Creating virtual environment..."
sudo rm -rf venv/
python3 -m venv venv
source venv/bin/activate

# Step 3: Install dependencies
echo "📚 Step 3: Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 4: Test configuration import
echo "⚙️ Step 4: Testing configuration..."
python3 -c "
try:
    from app.core.config import get_settings
    settings = get_settings()
    print('✅ Configuration loaded successfully!')
    print(f'Environment: {settings.ENVIRONMENT}')
    print(f'Database URL: {settings.DATABASE_URL[:20]}...')
    print(f'Access Token: {settings.ACCESS_TOKEN[:20]}...')
    print(f'Telegram Bot Token: {settings.TELEGRAM_BOT_TOKEN[:20]}...')
    print(f'Ad Account IDs: {settings.AD_ACCOUNT_IDS}')
except Exception as e:
    print(f'❌ Configuration failed: {e}')
    exit(1)
"

# Step 5: Test application import
echo "🧪 Step 5: Testing application import..."
python3 -c "
try:
    import app.main
    print('✅ Application imports successfully!')
except Exception as e:
    print(f'❌ Application import failed: {e}')
    exit(1)
"

# Step 6: Update supervisor configuration
echo "👮 Step 6: Updating supervisor configuration..."
sudo tee /etc/supervisor/conf.d/ads-automation.conf << 'EOF'
[program:ads-automation]
command=/home/adsuser/ads-automation/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
directory=/home/adsuser/ads-automation
user=adsuser
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/ads-automation.err.log
stdout_logfile=/var/log/supervisor/ads-automation.out.log
environment=PATH="/home/adsuser/ads-automation/venv/bin"
redirect_stderr=true
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
EOF

# Step 7: Reload supervisor
echo "🔄 Step 7: Reloading supervisor..."
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl stop ads-automation || true
sleep 2
sudo supervisorctl start ads-automation

# Step 8: Check status
echo "📊 Step 8: Checking status..."
sleep 3
sudo supervisorctl status ads-automation

# Step 9: Test health endpoints
echo "🏥 Step 9: Testing health endpoints..."
sleep 5

echo "Testing local endpoint..."
curl -s http://localhost:8000/health || echo "❌ Local health check failed"

echo "Testing domain endpoint..."
curl -s https://updatemetaads.site/health || echo "❌ Domain health check failed"

# Step 10: Show logs
echo "📋 Step 10: Recent logs..."
echo "=== STDOUT LOGS ==="
sudo tail -20 /var/log/supervisor/ads-automation.out.log || echo "No stdout logs found"

echo "=== ERROR LOGS ==="
sudo tail -20 /var/log/supervisor/ads-automation.err.log || echo "No error logs found"

echo "=============================================="
echo "✅ RESTORATION COMPLETE!"
echo "=============================================="
echo "If you see any errors above, run the following to debug:"
echo "  sudo supervisorctl tail -f ads-automation"
echo "  sudo tail -f /var/log/supervisor/ads-automation.err.log"
echo "  curl -v https://updatemetaads.site/health"
echo "=============================================="