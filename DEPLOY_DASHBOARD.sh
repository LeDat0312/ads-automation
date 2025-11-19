#!/bin/bash
# Deploy Dashboard to VPS
# Run this on VPS as adsuser

set -e

echo "🚀 Starting dashboard deployment..."

# Navigate to project
cd /home/adsuser/ads-automation

# Pull latest changes
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Navigate to frontend
cd frontend

# Install dependencies (if package.json changed)
echo "📦 Installing dependencies..."
npm install

# Build React app
echo "🔨 Building React app..."
npm run build

# Copy to Nginx directory
echo "📂 Deploying to Nginx..."
sudo rm -rf /var/www/ads-dashboard/*
sudo cp -r dist/* /var/www/ads-dashboard/

# Set proper permissions
sudo chown -R www-data:www-data /var/www/ads-dashboard
sudo chmod -R 755 /var/www/ads-dashboard

# Restart Nginx (optional, usually not needed for static files)
# sudo systemctl restart nginx

echo "✅ Deployment complete!"
echo "🌐 Dashboard available at: https://updatemetaads.site/dashboard/"
echo ""
echo "To verify deployment:"
echo "1. Check build: ls -la /var/www/ads-dashboard/"
echo "2. Check Nginx: sudo nginx -t"
echo "3. Open browser: https://updatemetaads.site/dashboard/"
