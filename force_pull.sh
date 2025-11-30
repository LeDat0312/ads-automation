#!/bin/bash
# Simple force pull - fix permission and pull latest code

echo "🔧 Force pulling latest code from GitHub..."
echo ""

cd /home/adsuser/ads-automation || exit 1

echo "Step 1: Stop nginx to release file locks..."
sudo systemctl stop nginx 2>/dev/null || echo "⚠️  Nginx not running"

echo ""
echo "Step 2: Force remove frontend/dist..."
sudo rm -rf frontend/dist/

echo ""
echo "Step 3: Fetch latest from GitHub..."
git fetch origin main

echo ""
echo "Step 4: Force reset to origin/main..."
git reset --hard origin/main

echo ""
echo "Step 5: Clean untracked files..."
git clean -fd

echo ""
echo "Step 6: Restart nginx..."
sudo systemctl start nginx

echo ""
echo "✅ Pull complete!"
echo ""
echo "📋 Current commit:"
git log -1 --oneline

echo ""
echo "📂 New scripts available:"
ls -1 VPS_*.sh 2>/dev/null
