#!/bin/bash
# Script pull Ad Studio redesign về VPS và rebuild frontend
# Chạy trên VPS với user adsuser

set -e  # Exit on error

echo "=========================================="
echo "🚀 PULL AD STUDIO REDESIGN TO VPS"
echo "=========================================="
echo ""

# 1. Navigate to project directory
echo "📁 Navigating to project directory..."
cd /home/adsuser/ads-automation

# 2. Stash any local changes
echo "💾 Stashing local changes..."
git stash

# 3. Pull latest code from GitHub
echo "⬇️  Pulling latest code from GitHub..."
git pull origin main

# 4. Navigate to frontend directory
echo "📂 Navigating to frontend directory..."
cd frontend

# 5. Install dependencies (if package.json changed)
echo "📦 Installing dependencies..."
npm install

# 6. Build frontend
echo "🔨 Building frontend..."
npm run build

# 7. Restart services
echo "🔄 Restarting services..."
cd ..
sudo supervisorctl restart ads_automation

echo ""
echo "=========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "🌐 Ad Studio đã được cập nhật với giao diện mới!"
echo "📱 Truy cập: http://your-vps-ip/ad-studio"
echo ""
echo "Kiểm tra logs:"
echo "  sudo supervisorctl tail -f ads_automation"
echo ""
