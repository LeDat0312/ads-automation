# 🚨 EMERGENCY VPS FIX

## Current Issues Analysis
1. ❌ Missing `python3-venv` package on Ubuntu system
2. ❌ Invalid .env configuration with missing required fields
3. ❌ Supervisor config pointing to broken virtual environment
4. ❌ Application failing to start due to validation errors

## Critical Commands to Run on VPS

### Step 1: Install System Dependencies
```bash
# Install python3-venv package (REQUIRED)
sudo apt update
sudo apt install python3.10-venv -y

# Verify installation
python3 -m venv --help
```

### Step 2: Complete Environment Setup
```bash
cd /home/adsuser/ads-automation/

# Remove broken venv and recreate
sudo rm -rf venv/
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Verify pydantic-settings is installed
python3 -c "import pydantic_settings; print('✅ pydantic-settings OK')"
```

### Step 3: Create Proper .env File
```bash
# Create complete .env with all required fields
cat > .env << 'EOF'
# Environment
ENVIRONMENT=production
DEBUG=False

# Security - MUST be at least 32 characters
SECRET_KEY=ads-automation-super-secret-key-for-production-2024-secure

# Database (update with your actual credentials)
DATABASE_URL=postgresql://adsuser:password@localhost:5432/ads_automation

# Redis
REDIS_URL=redis://localhost:6379/0

# Facebook API - REQUIRED fields
ACCESS_TOKEN=your_facebook_access_token_here
AD_ACCOUNT_IDS=act_123456789,act_987654321

# Telegram - REQUIRED fields  
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here
TELEGRAM_WEBHOOK_SECRET=telegram-webhook-secret-key-2024

# Server Configuration
ALLOWED_HOSTS=updatemetaads.site,www.updatemetaads.site,localhost,127.0.0.1
CORS_ORIGINS=https://updatemetaads.site,https://www.updatemetaads.site

# Logging
LOG_LEVEL=INFO
EOF
```

### Step 4: Test Application Import
```bash
cd /home/adsuser/ads-automation/
source venv/bin/activate

# Test if app can import without errors
python3 -c "
import sys
sys.path.append('/home/adsuser/ads-automation')
try:
    from app.core.config import get_settings
    settings = get_settings()
    print('✅ Configuration loaded successfully')
    print(f'Environment: {settings.ENVIRONMENT}')
    print(f'Database URL configured: {bool(settings.DATABASE_URL)}')
except Exception as e:
    print(f'❌ Import failed: {e}')
"
```

### Step 5: Fix Supervisor Configuration
```bash
# Update supervisor config to use correct path
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
EOF

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart ads-automation
```

### Step 6: Verify Everything Works
```bash
# Check supervisor status
sudo supervisorctl status ads-automation

# Check application logs
sudo tail -f /var/log/supervisor/ads-automation.out.log &
sudo tail -f /var/log/supervisor/ads-automation.err.log &

# Test health endpoints
sleep 5
curl http://localhost:8000/health
curl https://updatemetaads.site/health

# Check nginx status
sudo systemctl status nginx

# Check SSL certificate
curl -I https://updatemetaads.site/
```

## Important Notes

1. **DATABASE_URL**: You need to update this with your actual PostgreSQL credentials
2. **Facebook API**: Add your real ACCESS_TOKEN and AD_ACCOUNT_IDS
3. **Telegram**: Add your real TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID  
4. **Backup**: The .env file contains sensitive data - keep it secure

## If Still Having Issues

1. Check supervisor logs: `sudo tail -100 /var/log/supervisor/ads-automation.err.log`
2. Check nginx logs: `sudo tail -100 /var/log/nginx/error.log`
3. Test manual startup: `cd /home/adsuser/ads-automation && source venv/bin/activate && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000`

Run these commands IN ORDER on your VPS to completely restore the application.