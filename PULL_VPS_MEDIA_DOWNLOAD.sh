#!/bin/bash
# Pull và deploy Media Download feature lên VPS
# Run: bash PULL_VPS_MEDIA_DOWNLOAD.sh

echo "=========================================="
echo "🚀 DEPLOYING MEDIA DOWNLOAD FEATURE"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Navigate to project directory
cd /root/ads-automation || { echo -e "${RED}❌ Failed to navigate to project directory${NC}"; exit 1; }

echo -e "${YELLOW}📥 Step 1: Pulling latest changes from GitHub...${NC}"
git fetch origin
git pull origin main || { echo -e "${RED}❌ Git pull failed${NC}"; exit 1; }

echo -e "${GREEN}✅ Git pull completed${NC}"

echo -e "${YELLOW}📦 Step 2: Checking Python dependencies...${NC}"
# No new dependencies needed, httpx and pathlib are already in requirements

echo -e "${YELLOW}🔧 Step 3: Creating storage directory...${NC}"
mkdir -p ./storage/competitor_media/images
mkdir -p ./storage/competitor_media/videos
mkdir -p ./storage/competitor_media/thumbnails
chmod -R 755 ./storage

echo -e "${GREEN}✅ Storage directories created${NC}"

echo -e "${YELLOW}🏗️  Step 4: Building frontend...${NC}"
cd frontend
npm install || { echo -e "${RED}❌ npm install failed${NC}"; exit 1; }
npm run build || { echo -e "${RED}❌ Frontend build failed${NC}"; exit 1; }
cd ..

echo -e "${GREEN}✅ Frontend built successfully${NC}"

echo -e "${YELLOW}🔄 Step 5: Restarting backend service...${NC}"
systemctl restart ads-automation || { echo -e "${RED}❌ Failed to restart service${NC}"; exit 1; }

echo -e "${GREEN}✅ Service restarted${NC}"

echo -e "${YELLOW}⏳ Step 6: Waiting for service to be ready...${NC}"
sleep 5

echo -e "${YELLOW}🔍 Step 7: Checking service status...${NC}"
systemctl status ads-automation --no-pager

echo ""
echo "=========================================="
echo -e "${GREEN}✅ DEPLOYMENT COMPLETED!${NC}"
echo "=========================================="
echo ""
echo "📋 New Features:"
echo "   - High-quality media download from Facebook Ads"
echo "   - Batch download support"
echo "   - Auto URL optimization (_s → _o, _sd → _hd)"
echo "   - Storage management & cleanup"
echo ""
echo "📁 Storage location: ./storage/competitor_media/"
echo ""
echo "🌐 Access: https://updatemetaads.site/competitor/"
echo ""
echo "🧪 To test:"
echo "   1. Go to Competitor Research page"
echo "   2. Scrape some ads"
echo "   3. Click 'Download Media' button"
echo ""
echo "📊 Check storage stats:"
echo "   GET /competitor/media/storage-stats"
echo ""
echo -e "${YELLOW}⚠️  Note: Make sure SCRAPEGRAPHAI_API_KEY is set in .env${NC}"
echo ""
