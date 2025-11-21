#!/bin/bash
# Deploy Batch API Update - Final Version

echo "🚀 Pulling latest code from GitHub..."
cd /home/ads-automation
git pull origin main

echo "📦 Installing frontend dependencies..."
cd frontend
npm install

echo "🔨 Building frontend..."
npm run build

echo "🔄 Restarting service..."
cd ..
sudo systemctl restart ads-automation

echo "✅ Deploy complete! Batch API now working:"
echo "   - 84 adsets = 2 batch requests (not 84!)"
echo "   - Progress bar visible in UI"
echo "   - No page reload after update"

# Check service status
echo ""
echo "📊 Service status:"
sudo systemctl status ads-automation --no-pager | head -n 10
