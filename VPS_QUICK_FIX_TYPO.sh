#!/bin/bash

# Quick fix for typo and model update

echo "🔧 Applying quick fixes..."

# Pull latest
git pull origin main

# Build frontend
cd frontend
npm run build

# Check if build succeeded
if [ $? -eq 0 ]; then
    echo "✅ Frontend built successfully"
else
    echo "❌ Frontend build failed"
    exit 1
fi

cd ..

# Restart backend
sudo systemctl restart ads-automation

echo "✅ Fixes applied successfully!"
echo ""
echo "Changes:"
echo "  - Fixed setCta Type -> setCtaType typo"
echo "  - Added server_default to color_hex column"
echo ""
echo "Please test:"
echo "  1. Create channel group without color"
echo "  2. Build Ad Studio page"
