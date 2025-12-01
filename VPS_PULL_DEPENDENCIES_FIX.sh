#!/bin/bash

# VPS Pull Script - Fix Frontend Dependencies
# Cập nhật code mới nhất với frontend dependencies đã được fix

echo "🚀 Starting VPS deployment - Frontend Dependencies Fix..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Change to project directory
cd /home/adsuser/ads-automation || exit 1

echo "📂 Current directory: $(pwd)"
echo ""

# Step 1: Stash any local changes
echo "💾 Stashing local changes..."
git stash
echo ""

# Step 2: Pull latest code
echo "⬇️  Pulling latest code from GitHub..."
git pull origin main
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Git pull failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Code pulled successfully${NC}"
echo ""

# Step 3: Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend || exit 1
npm install
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ npm install failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
echo ""

# Step 4: Build frontend
echo "🔨 Building frontend..."
npm run build
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Frontend build failed!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Frontend built successfully${NC}"
echo ""

# Step 5: Go back to root
cd ..

# Step 6: Run migrations (if needed)
echo "🗄️  Running database migrations..."
source venv/bin/activate

echo "  → Running add_last_error_to_facebook_accounts migration..."
python3 -m migrations.add_last_error_to_facebook_accounts
echo ""

echo "  → Running add_color_hex_to_channel_groups migration..."
python3 -m migrations.add_color_hex_to_channel_groups
echo ""

deactivate

# Step 7: Restart backend service
echo "🔄 Restarting backend service..."
sudo systemctl restart ads-automation
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}⚠️  Service restart failed, trying supervisor...${NC}"
    sudo supervisorctl restart backend
fi
echo ""

# Step 8: Check service status
echo "🔍 Checking service status..."
sleep 2
sudo systemctl status ads-automation --no-pager -l | head -20
echo ""

# Step 9: Check if backend is responding
echo "🌐 Testing backend API..."
sleep 2
curl -s http://localhost:8000/api/health > /dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Backend is responding${NC}"
else
    echo -e "${YELLOW}⚠️  Backend might not be ready yet, check logs${NC}"
fi
echo ""

# Step 10: Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Deployment completed!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 What was updated:"
echo "  ✅ Frontend dependencies added:"
echo "     - @headlessui/react ^1.7.17"
echo "     - react-toastify ^9.1.3"
echo "     - dayjs ^1.11.10"
echo "  ✅ Frontend rebuilt successfully"
echo "  ✅ Database migrations executed"
echo "  ✅ Backend service restarted"
echo ""
echo "🔍 Next steps:"
echo "  1. Check logs: sudo journalctl -u ads-automation -f"
echo "  2. Test frontend: Open browser and check pages"
echo "  3. Test Facebook Via connection"
echo "  4. Test Fanpage connection with permission check"
echo ""
echo "📝 New features available:"
echo "  - Token expiry tracking with last_error field"
echo "  - Custom colors for channel groups"
echo "  - Improved permission checking for Facebook pages"
echo "  - Better error messages in Vietnamese"
echo ""
