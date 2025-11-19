#!/bin/bash
# Script to fix 502 Bad Gateway error
# Run this on VPS: /home/adsuser/ads-automation/FIX_502.sh

echo "🔧 Starting Fix 502 Process..."

# 1. Go to project directory
cd /home/adsuser/ads-automation || exit

# 2. Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# 3. Install dependencies (Crucial for Pillow/CAPTCHA)
echo "📦 Installing dependencies..."
/usr/bin/python3 -m pip install -r requirements.txt

# 4. Check logs for errors
echo "📋 Checking last 20 lines of error log..."
tail -n 20 /var/log/supervisor/ads-automation-stderr.log

# 5. Restart application
echo "🔄 Restarting application..."
sudo supervisorctl restart ads-automation-production

# 6. Check status
echo "✅ Status:"
sudo supervisorctl status ads-automation-production

echo "🎉 Fix process completed! Please try accessing the website again."
