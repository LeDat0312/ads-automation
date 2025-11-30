#!/bin/bash
# Quick restart script - handles different service managers

PROJECT_DIR="/home/adsuser/ads-automation"

echo "🔍 Detecting service manager..."

# Check if systemd service exists
if sudo systemctl status metaupdate &>/dev/null; then
    echo "✅ Found systemd service: metaupdate"
    echo "🔄 Restarting..."
    sudo systemctl restart metaupdate
    echo "📊 Status:"
    sudo systemctl status metaupdate --no-pager
    echo ""
    echo "📝 View logs with: sudo journalctl -u metaupdate -f"
    exit 0
fi

# Check for other systemd service names
for service in uvicorn fastapi ads-automation facebook-ads; do
    if sudo systemctl status $service &>/dev/null; then
        echo "✅ Found systemd service: $service"
        echo "🔄 Restarting..."
        sudo systemctl restart $service
        echo "📊 Status:"
        sudo systemctl status $service --no-pager
        exit 0
    fi
done

# Check if supervisor is used
if command -v supervisorctl &>/dev/null; then
    echo "✅ Found Supervisor"
    echo "🔄 Restarting all processes..."
    sudo supervisorctl restart all
    echo "📊 Status:"
    sudo supervisorctl status
    exit 0
fi

# Check for manual uvicorn process
UVICORN_PID=$(ps aux | grep "[u]vicorn app.main:app" | awk '{print $2}')
if [ ! -z "$UVICORN_PID" ]; then
    echo "✅ Found manual uvicorn process (PID: $UVICORN_PID)"
    echo "⚠️  Killing process..."
    sudo kill $UVICORN_PID
    sleep 2
    echo "🚀 Starting uvicorn..."
    cd $PROJECT_DIR
    source venv/bin/activate
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 > /tmp/uvicorn.log 2>&1 &
    echo "✅ Started with PID: $!"
    echo "📝 Logs: tail -f /tmp/uvicorn.log"
    exit 0
fi

# No service found
echo "❌ No service found!"
echo ""
echo "💡 Options:"
echo "1. Create systemd service: bash VPS_CREATE_SERVICE.sh"
echo "2. Start manually: cd $PROJECT_DIR && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo "3. Check processes: bash VPS_CHECK_AND_FIX_SERVICE.sh"
exit 1
