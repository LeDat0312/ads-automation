#!/bin/bash

# Script to fix Facebook Via permissions detection and rebuild frontend
# Date: 2025-12-01

echo "🔧 Fixing Facebook Via permissions detection..."

# Navigate to project directory
cd /root/ads-automation || exit 1

echo "📥 Step 1: Pull latest code from GitHub..."
git fetch origin
git reset --hard origin/main
git pull origin main

echo "🔄 Step 2: Restart backend to apply permission fixes..."
sudo supervisorctl restart adstudio

echo "⏳ Waiting for backend to start..."
sleep 5

echo "📦 Step 3: Rebuild frontend with updated permission UI..."
cd frontend

# Install dependencies if needed
npm install

# Build production frontend
echo "🔨 Building frontend..."
npm run build

echo "✅ Build complete!"

echo ""
echo "📋 Changes applied:"
echo "  ✅ Backend now checks both 'perms' (ADMINISTER) and 'tasks' (MANAGE/CREATE_CONTENT/MODERATE)"
echo "  ✅ UI displays 3 badge states:"
echo "     🟢 QTV - Full admin with app permissions"
echo "     🟡 QTV nhưng app chưa đủ quyền - Admin but token lacks permissions"
echo "     🟡 Không phải QTV - Not admin"
echo "  ✅ Added debug logging for connect pages endpoint"
echo ""
echo "🔍 Test the changes:"
echo "  1. Go to Settings > Facebook Via"
echo "  2. Click 'Tải danh sách Fanpage' on a Via"
echo "  3. Check badges display correctly based on permissions"
echo "  4. Try connecting pages - should not get 400 error"
echo ""
echo "📊 Check backend logs:"
echo "  sudo tail -f /var/log/supervisor/adstudio-stderr.log | grep 'PAGE ROLES\\|Connect pages'"
