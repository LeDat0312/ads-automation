#!/bin/bash
# AdStudio Deployment Script for VPS
# Run this on VPS: bash deploy_ad_studio.sh

set -e  # Exit on error

echo "🚀 Starting AdStudio deployment..."

# 1. Navigate to project directory
cd /home/adsuser/ads-automation
echo "✅ Changed to project directory: $(pwd)"

# 2. Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# 3. Run database migration
echo "🗄️ Running database migration..."
python3 -m migrations.add_ad_studio_local_media_fields

# 4. Create media directory if not exists
echo "📁 Creating media directory..."
mkdir -p media/ad_studio
chmod 755 media
chmod 755 media/ad_studio

# 5. Stop existing processes
echo "🛑 Stopping existing uvicorn and worker processes..."
pkill -f "uvicorn app.main:app" || echo "No uvicorn process found"
pkill -f "app.workers.ad_studio_publisher" || echo "No worker process found"
sleep 2

# 6. Start backend
echo "🚀 Starting uvicorn backend..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
UVICORN_PID=$!
echo "✅ Uvicorn started with PID: $UVICORN_PID"

# Wait for backend to start
sleep 3

# 7. Start publisher worker
echo "🤖 Starting AdStudio publisher worker..."
nohup python3 -m app.workers.ad_studio_publisher > worker.log 2>&1 &
WORKER_PID=$!
echo "✅ Worker started with PID: $WORKER_PID"

# 8. Check if processes are running
sleep 2
if ps -p $UVICORN_PID > /dev/null; then
   echo "✅ Uvicorn is running (PID: $UVICORN_PID)"
else
   echo "❌ Uvicorn failed to start. Check uvicorn.log:"
   tail -20 uvicorn.log
   exit 1
fi

if ps -p $WORKER_PID > /dev/null; then
   echo "✅ Worker is running (PID: $WORKER_PID)"
else
   echo "❌ Worker failed to start. Check worker.log:"
   tail -20 worker.log
   exit 1
fi

echo ""
echo "✨ Deployment completed successfully!"
echo ""
echo "📊 Process Status:"
echo "  - Uvicorn PID: $UVICORN_PID"
echo "  - Worker PID: $WORKER_PID"
echo ""
echo "📝 Log files:"
echo "  - Backend: tail -f uvicorn.log"
echo "  - Worker: tail -f worker.log"
echo ""
echo "🌐 Access your application at:"
echo "  - Dashboard: https://your-domain/dashboard/"
echo "  - Health check: https://your-domain/health"
echo "  - Media files: https://your-domain/media/"
echo ""
echo "🧪 Test AdStudio:"
echo "  1. Go to https://your-domain/dashboard/"
echo "  2. Click 'Ad Studio' tab"
echo "  3. Scrape a TikTok video"
echo "  4. Schedule a post to Facebook"
echo ""
