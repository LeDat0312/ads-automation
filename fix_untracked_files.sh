#!/bin/bash
# Quick fix for untracked files blocking git pull
# Run on VPS: bash fix_untracked_files.sh

set -e

echo "🔧 Fixing untracked files blocking git pull..."

cd /home/adsuser/ads-automation
echo "✅ In directory: $(pwd)"

# Backup untracked files first
echo ""
echo "💾 Backing up untracked files..."
BACKUP_DIR="../backup_untracked_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

for file in VPS_DEPLOYMENT.md app/workers/ad_studio_publisher.py deploy_ad_studio.sh fix_permissions_deploy.sh fix_vps_conflicts.sh migrations/add_ad_studio_local_media_fields.py vps_commands.sh; do
    if [ -f "$file" ]; then
        mkdir -p "$BACKUP_DIR/$(dirname $file)"
        cp "$file" "$BACKUP_DIR/$file" 2>/dev/null && echo "  ✅ Backed up: $file" || echo "  ⚠️  Could not backup: $file"
    fi
done

echo "✅ Backup saved to $BACKUP_DIR"

# Remove untracked files
echo ""
echo "🗑️ Removing untracked files..."
for file in VPS_DEPLOYMENT.md app/workers/ad_studio_publisher.py deploy_ad_studio.sh fix_permissions_deploy.sh fix_vps_conflicts.sh migrations/add_ad_studio_local_media_fields.py vps_commands.sh; do
    if [ -f "$file" ]; then
        # Check if file is tracked by git
        if ! git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
            rm -f "$file" && echo "  ✅ Removed: $file" || echo "  ⚠️  Could not remove: $file"
        else
            echo "  ℹ️  Skipped (tracked): $file"
        fi
    fi
done

echo ""
echo "✅ Untracked files removed. You can now run:"
echo "   git pull origin main"
echo ""
echo "💾 Backup location: $BACKUP_DIR"



