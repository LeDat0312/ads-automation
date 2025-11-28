#!/bin/bash
# Fix file permissions and deploy
# Run on VPS: bash fix_permissions_deploy.sh

set -e

echo "🔧 Fixing file permissions and deploying..."

cd /home/adsuser/ads-automation
echo "✅ In directory: $(pwd)"

# Fix permissions on frontend/dist
echo ""
echo "🔑 Fixing file permissions..."
if [ -d "frontend/dist" ]; then
    echo "Changing permissions on frontend/dist..."
    chmod -R 755 frontend/dist 2>/dev/null || true
    
    echo "Removing old frontend/dist..."
    rm -rf frontend/dist
    echo "✅ Removed old frontend/dist"
fi

# Backup local changes
echo ""
echo "💾 Backing up local changes..."
BACKUP_DIR="../backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup modified files
for file in .gitignore app/api/routes/ad_studio.py app/core/config.py app/main.py app/models/ad_studio.py frontend/src/types/adStudio.ts; do
    if [ -f "$file" ]; then
        mkdir -p "$BACKUP_DIR/$(dirname $file)"
        cp "$file" "$BACKUP_DIR/$file" 2>/dev/null || true
    fi
done

# Backup untracked files
for file in app/workers/ad_studio_publisher.py migrations/add_ad_studio_local_media_fields.py VPS_DEPLOYMENT.md deploy_ad_studio.sh fix_vps_conflicts.sh vps_commands.sh; do
    if [ -f "$file" ]; then
        mkdir -p "$BACKUP_DIR/$(dirname $file)"
        cp "$file" "$BACKUP_DIR/$file" 2>/dev/null || true
    fi
done

echo "✅ Backup saved to $BACKUP_DIR"

# Clean git state
echo ""
echo "🧹 Cleaning git state..."
git reset --hard HEAD
git clean -fd

# Pull latest
echo ""
echo "📥 Pulling latest code..."
git pull origin main

echo "✅ Code updated successfully"

# Verify critical files
echo ""
echo "🔍 Verifying files..."
MISSING_FILES=0

if [ ! -f "migrations/add_ad_studio_local_media_fields.py" ]; then
    echo "❌ migrations/add_ad_studio_local_media_fields.py missing"
    MISSING_FILES=1
else
    echo "✅ Migration file OK"
fi

if [ ! -f "app/workers/ad_studio_publisher.py" ]; then
    echo "❌ app/workers/ad_studio_publisher.py missing"
    MISSING_FILES=1
else
    echo "✅ Worker file OK"
fi

if [ ! -f "deploy_ad_studio.sh" ]; then
    echo "❌ deploy_ad_studio.sh missing"
    MISSING_FILES=1
else
    echo "✅ Deploy script OK"
fi

if [ ! -d "frontend/dist" ]; then
    echo "❌ frontend/dist directory missing"
    MISSING_FILES=1
else
    echo "✅ Frontend dist OK"
fi

if [ $MISSING_FILES -eq 1 ]; then
    echo ""
    echo "❌ Some files are missing. Git pull may have failed."
    echo "Current git status:"
    git status
    exit 1
fi

# Run migration
echo ""
echo "🗄️ Running database migration..."
python3 -m migrations.add_ad_studio_local_media_fields

# Create media directory
echo ""
echo "📁 Creating media directory..."
mkdir -p media/ad_studio
chmod -R 755 media
echo "✅ Media directory ready"

# Stop old processes
echo ""
echo "🛑 Stopping old processes..."
pkill -f "uvicorn app.main:app" 2>/dev/null || echo "No uvicorn running"
pkill -f "app.workers.ad_studio_publisher" 2>/dev/null || echo "No worker running"
sleep 3

# Start uvicorn
echo ""
echo "🚀 Starting uvicorn..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
UVICORN_PID=$!
echo "Uvicorn PID: $UVICORN_PID"

sleep 5

# Check uvicorn
if ! ps -p $UVICORN_PID > /dev/null 2>&1; then
    echo ""
    echo "❌ Uvicorn failed to start!"
    echo ""
    echo "=== Last 30 lines of uvicorn.log ==="
    tail -30 uvicorn.log
    echo "===================================="
    exit 1
fi
echo "✅ Uvicorn running"

# Start worker
echo ""
echo "🤖 Starting publisher worker..."
nohup python3 -m app.workers.ad_studio_publisher > worker.log 2>&1 &
WORKER_PID=$!
echo "Worker PID: $WORKER_PID"

sleep 3

# Check worker
if ! ps -p $WORKER_PID > /dev/null 2>&1; then
    echo ""
    echo "❌ Worker failed to start!"
    echo ""
    echo "=== Last 30 lines of worker.log ==="
    tail -30 worker.log
    echo "===================================="
    exit 1
fi
echo "✅ Worker running"

# Success!
echo ""
echo "================================================"
echo "✅ DEPLOYMENT COMPLETED SUCCESSFULLY!"
echo "================================================"
echo ""
echo "📊 Running processes:"
ps aux | grep -E "uvicorn app.main|ad_studio_publisher" | grep -v grep || echo "No processes found (this shouldn't happen)"
echo ""
echo "📝 Logs (last 5 lines):"
echo ""
echo "--- uvicorn.log ---"
tail -5 uvicorn.log
echo ""
echo "--- worker.log ---"
tail -5 worker.log
echo ""
echo "🌐 Your application is ready:"
echo "  • Dashboard: https://your-domain/dashboard/"
echo "  • Health: https://your-domain/health"
echo "  • API: https://your-domain/api/"
echo ""
echo "💾 Backup location: $BACKUP_DIR"
echo ""
echo "📖 View full logs:"
echo "  tail -f uvicorn.log"
echo "  tail -f worker.log"
echo ""
echo "================================================"
