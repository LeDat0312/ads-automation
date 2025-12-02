#!/bin/bash
# VPS Deployment Script for Ad Studio Refactor
# Run this on VPS after pulling code

set -e  # Exit on error

echo "========================================="
echo "🚀 Deploying Ad Studio Refactor"
echo "========================================="

# 1. Check current directory
echo "📁 Current directory:"
pwd

# 2. Check Python syntax errors
echo ""
echo "🔍 Checking Python syntax errors..."
cd /home/adsuser/ads-automation
python3 -m py_compile app/api/routes/ad_studio.py
python3 -m py_compile app/schemas/ad_studio.py
echo "✅ Python syntax OK"

# 3. Check supervisor logs
echo ""
echo "📋 Checking supervisor error logs..."
sudo tail -n 50 /var/log/supervisor/ads-automation-stderr*.log

# 4. Build frontend
echo ""
echo "🔨 Building frontend..."
cd /home/adsuser/ads-automation/frontend
npm run build
echo "✅ Frontend built"

# 5. Restart services
echo ""
echo "♻️  Restarting services..."
sudo supervisorctl restart ads-automation
sudo supervisorctl restart ads-worker

# 6. Wait and check status
echo ""
echo "⏳ Waiting 3 seconds..."
sleep 3

echo ""
echo "📊 Services status:"
sudo supervisorctl status

# 7. Show recent logs
echo ""
echo "📜 Recent backend logs:"
sudo supervisorctl tail ads-automation stderr | tail -n 20

echo ""
echo "========================================="
echo "✅ Deployment complete!"
echo "========================================="
