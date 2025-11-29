#!/bin/bash
# Script to pull Channel Management backend updates on VPS
# This script handles permissions and pulls latest code safely

set -e  # Exit on error

cd /home/adsuser/ads-automation || exit 1

echo "🔄 Starting pull process for Channel Management backend..."

# Step 1: Backup any local changes
echo "📦 Backing up any local changes..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Warning: You have uncommitted changes. Stashing them..."
    git stash save "Backup before pull - $(date '+%Y-%m-%d %H:%M:%S')"
fi

# Step 2: Handle frontend/dist permissions if needed
if [ -d "frontend/dist" ]; then
    echo "🔧 Fixing frontend/dist permissions..."
    sudo chown -R adsuser:adsuser frontend/dist 2>/dev/null || true
    sudo rm -rf frontend/dist 2>/dev/null || true
fi

# Step 3: Pull latest code
echo "⬇️  Pulling latest code from GitHub..."
git fetch origin main
git reset --hard origin/main
git clean -fd

# Step 4: Rebuild frontend (new components were added)
echo "🔨 Rebuilding frontend..."
cd frontend
npm install
npm run build
cd ..

# Step 5: Run database migration for new Channel Management tables
echo "🗄️  Running database migration for Channel Management..."
python3 -m migrations.add_channels_management_tables

# Step 6: Restart services (if using systemd/supervisor)
echo "🔄 Checking if services need restart..."
if systemctl is-active --quiet ads-automation.service 2>/dev/null; then
    echo "♻️  Restarting ads-automation service..."
    sudo systemctl restart ads-automation.service
elif systemctl is-active --quiet uwsgi.service 2>/dev/null; then
    echo "♻️  Restarting uwsgi service..."
    sudo systemctl restart uwsgi.service
else
    echo "ℹ️  No service found to restart. You may need to restart manually."
fi

echo ""
echo "✅ Pull completed successfully!"
echo ""
echo "📋 Summary:"
echo "   - Code pulled from GitHub"
echo "   - Frontend rebuilt"
echo "   - Database migration run"
echo ""
echo "📝 Next steps:"
echo "   1. Verify API endpoints are working: /api/channels, /api/channel-groups, /api/posting/settings"
echo "   2. Test frontend pages: /settings/channels, /settings/channel-groups, /settings/posting"
echo "   3. Check logs if any issues occur"

