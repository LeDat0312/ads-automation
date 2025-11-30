#!/bin/bash
# Simple script to fix git conflicts and pull latest code

echo "🔄 Fixing git conflicts and pulling latest code..."
echo ""

cd /home/adsuser/ads-automation

# Option 1: Stash changes
echo "💾 Stashing local changes..."
git stash

# Option 2: Pull latest
echo "📥 Pulling from GitHub..."
git pull origin main

echo ""
echo "✅ Done! Code updated."
echo ""
echo "📋 Available scripts:"
ls -1 VPS_*.sh 2>/dev/null || echo "Scripts will appear after pull"
