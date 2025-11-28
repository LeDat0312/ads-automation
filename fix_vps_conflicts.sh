#!/bin/bash
# Fix VPS conflicts and deploy
# Run this on VPS: bash fix_vps_conflicts.sh

set -e

echo "🔧 Fixing VPS conflicts and deploying AdStudio..."

# Navigate to project directory
cd /home/adsuser/ads-automation
echo "✅ In directory: $(pwd)"

# Show current status
echo ""
echo "📊 Current git status:"
git status

# Backup any local changes
echo ""
echo "💾 Backing up local changes..."
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "../$BACKUP_DIR"

# Backup modified files if they exist
for file in .gitignore app/api/routes/ad_studio.py app/core/config.py app/main.py app/models/ad_studio.py frontend/src/types/adStudio.ts; do
    if [ -f "$file" ]; then
        cp --parents "$file" "../$BACKUP_DIR/" 2>/dev/null || true
    fi
done

# Backup untracked files
for file in app/workers/ad_studio_publisher.py migrations/add_ad_studio_local_media_fields.py; do
    if [ -f "$file" ]; then
        cp --parents "$file" "../$BACKUP_DIR/" 2>/dev/null || true
    fi
done

echo "✅ Backup saved to ../$BACKUP_DIR"

# Reset to clean state
echo ""
echo "🧹 Resetting to clean state..."
git reset --hard HEAD
git clean -fd

# Pull latest code
echo ""
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Verify migration file exists
echo ""
echo "🔍 Verifying files..."
if [ ! -f "migrations/add_ad_studio_local_media_fields.py" ]; then
    echo "❌ Migration file not found!"
    exit 1
fi
echo "✅ Migration file found"

if [ ! -f "app/workers/ad_studio_publisher.py" ]; then
    echo "❌ Worker file not found!"
    exit 1
fi
echo "✅ Worker file found"

if [ ! -f "deploy_ad_studio.sh" ]; then
    echo "❌ Deployment script not found!"
    exit 1
fi
echo "✅ Deployment script found"

# Run migration
echo ""
echo "🗄️ Running database migration..."
python3 -m migrations.add_ad_studio_local_media_fields

# Create media directory
echo ""
echo "📁 Creating media directory..."
mkdir -p media/ad_studio
chmod -R 755 media

# Stop old processes
echo ""
echo "🛑 Stopping old processes..."
pkill -f "uvicorn app.main:app" || echo "No uvicorn running"
pkill -f "app.workers.ad_studio_publisher" || echo "No worker running"
sleep 3

# Start uvicorn
echo ""
echo "🚀 Starting uvicorn..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
UVICORN_PID=$!
echo "Uvicorn PID: $UVICORN_PID"

# Wait for backend
sleep 5

# Check if uvicorn started successfully
if ! ps -p $UVICORN_PID > /dev/null 2>&1; then
    echo "❌ Uvicorn failed to start!"
    echo ""
    echo "Last 30 lines of uvicorn.log:"
    tail -30 uvicorn.log
    exit 1
fi
echo "✅ Uvicorn running"

# Start worker
echo ""
echo "🤖 Starting publisher worker..."
nohup python3 -m app.workers.ad_studio_publisher > worker.log 2>&1 &
WORKER_PID=$!
echo "Worker PID: $WORKER_PID"

# Wait for worker
sleep 3

# Check if worker started successfully
if ! ps -p $WORKER_PID > /dev/null 2>&1; then
    echo "❌ Worker failed to start!"
    echo ""
    echo "Last 30 lines of worker.log:"
    tail -30 worker.log
    exit 1
fi
echo "✅ Worker running"

# Final verification
echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "📊 Running processes:"
ps aux | grep -E "uvicorn app.main|ad_studio_publisher" | grep -v grep
echo ""
echo "📝 Recent logs:"
echo "--- uvicorn.log (last 10 lines) ---"
tail -10 uvicorn.log
echo ""
echo "--- worker.log (last 10 lines) ---"
tail -10 worker.log
echo ""
echo "🌐 Test your application:"
echo "  Dashboard: https://your-domain/dashboard/"
echo "  Health: https://your-domain/health"
echo ""
echo "💾 Backup location: ../$BACKUP_DIR"
