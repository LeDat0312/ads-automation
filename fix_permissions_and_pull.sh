#!/bin/bash
# Fix permissions and pull from GitHub
# Run on VPS: bash fix_permissions_and_pull.sh

set -e

echo "🔧 Fixing permissions and pulling from GitHub..."

cd /home/adsuser/ads-automation
echo "✅ In directory: $(pwd)"

# Fix permissions on frontend/dist
echo ""
echo "🔑 Fixing file permissions on frontend/dist..."
if [ -d "frontend/dist" ]; then
    echo "Removing old frontend/dist (may need sudo)..."
    
    # Try without sudo first
    rm -rf frontend/dist 2>/dev/null && echo "✅ Removed old frontend/dist" || {
        # If failed, try with sudo
        echo "Need elevated permissions, using sudo..."
        sudo rm -rf frontend/dist && echo "✅ Removed old frontend/dist with sudo" || {
            echo "❌ Failed to remove frontend/dist even with sudo"
            echo "Please run manually: sudo rm -rf frontend/dist"
            exit 1
        }
    }
fi

# Fix git index if corrupted
echo ""
echo "🧹 Cleaning git state..."
git reset --hard HEAD || true

# Backup and remove untracked files that might conflict
echo ""
echo "💾 Backing up untracked files..."
BACKUP_DIR="../backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

for file in VPS_DEPLOYMENT.md app/workers/ad_studio_publisher.py deploy_ad_studio.sh fix_permissions_deploy.sh fix_vps_conflicts.sh migrations/add_ad_studio_local_media_fields.py vps_commands.sh; do
    if [ -f "$file" ]; then
        mkdir -p "$BACKUP_DIR/$(dirname $file)"
        cp "$file" "$BACKUP_DIR/$file" 2>/dev/null || true
        # Remove untracked file if not in git
        if ! git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
            rm -f "$file" 2>/dev/null || sudo rm -f "$file" 2>/dev/null || true
        fi
    fi
done

echo "✅ Backup saved to $BACKUP_DIR"

# Clean git
echo ""
echo "🧹 Cleaning git..."
git clean -fd || true

# Pull latest code
echo ""
echo "📥 Pulling latest code from GitHub..."
git pull origin main

echo ""
echo "✅ Pull completed successfully!"
echo ""
echo "💾 Backup location: $BACKUP_DIR"

