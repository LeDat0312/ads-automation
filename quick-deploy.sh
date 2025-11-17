#!/bin/bash

# =============================================================================
# 📦 Quick Deploy Script for VPS
# =============================================================================
# Rapid deployment script for Facebook Ads Automation
# Usage: curl -sSL https://raw.githubusercontent.com/LeDat0312/ads-automation/main/quick-deploy.sh | bash
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}
╔═══════════════════════════════════════════════════════════════════════════════╗
║                     🚀 Facebook Ads Automation - Quick Deploy                ║
║                                                                               ║
║  This script will automatically deploy the latest version                    ║
║  from GitHub to your VPS server.                                             ║
╚═══════════════════════════════════════════════════════════════════════════════╝
${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run as root: sudo bash quick-deploy.sh${NC}"
    exit 1
fi

# Download and run main deploy script
echo -e "${BLUE}📥 Downloading deployment script...${NC}"
curl -sSL https://raw.githubusercontent.com/LeDat0312/ads-automation/main/deploy.sh -o /tmp/deploy.sh
chmod +x /tmp/deploy.sh

echo -e "${BLUE}🚀 Starting deployment...${NC}"
bash /tmp/deploy.sh

echo -e "${GREEN}✅ Quick deploy completed!${NC}"