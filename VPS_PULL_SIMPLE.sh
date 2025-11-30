#!/bin/bash
# Script đơn giản để pull code và chạy migration trên VPS

cd /home/adsuser/ads-automation

echo "📥 Pulling latest code..."
git pull origin main

echo "🗄️ Running database migration..."
python3 -m migrations.add_channels_management_tables

echo "🔄 Restarting service..."
sudo systemctl restart ads-automation.service

echo "✅ Done!"

