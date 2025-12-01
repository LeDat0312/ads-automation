#!/bin/bash

echo "🔄 Rebuilding frontend với code mới..."

cd /root/ads-automation/frontend || exit 1

echo "📦 Installing dependencies..."
npm install

echo "🔨 Building production bundle..."
npm run build

echo "✅ Frontend rebuild complete!"
echo ""
echo "📊 Check build output:"
ls -lh dist/index.html
echo ""
echo "🌐 Frontend đã được update. Refresh browser (Ctrl+Shift+R) để thấy thay đổi."
