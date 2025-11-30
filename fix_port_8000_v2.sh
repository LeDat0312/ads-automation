#!/bin/bash
# Fix port 8000 with extended wait time and better checks

echo "🔧 Fixing port 8000 issue (extended version)..."
echo ""

echo "Step 1: Stop ALL supervisor processes first..."
echo "=================================================="
sudo supervisorctl stop all
echo "✅ All supervisor processes stopped"

echo ""
echo "Step 2: Wait 3 seconds for graceful shutdown..."
sleep 3

echo ""
echo "Step 3: Force kill any remaining uvicorn/python processes..."
echo "=================================================="
echo "Current uvicorn processes:"
ps aux | grep "[u]vicorn" || echo "None found"

echo ""
echo "Killing all uvicorn processes..."
sudo pkill -9 -f "uvicorn app.main" || echo "No uvicorn to kill"

echo ""
echo "Step 4: Force kill any process on port 8000..."
echo "=================================================="
if sudo lsof -i :8000 > /dev/null 2>&1; then
    echo "Processes on port 8000:"
    sudo lsof -i :8000
    echo ""
    echo "Killing..."
    sudo kill -9 $(sudo lsof -i :8000 -t) 2>/dev/null || true
    sleep 2
fi

echo ""
echo "Step 5: Verify port 8000 is completely free..."
echo "=================================================="
for i in {1..5}; do
    if sudo lsof -i :8000 > /dev/null 2>&1; then
        echo "Attempt $i: Port still in use, waiting..."
        sudo lsof -i :8000
        sleep 2
    else
        echo "✅ Port 8000 is free"
        break
    fi
done

if sudo lsof -i :8000 > /dev/null 2>&1; then
    echo ""
    echo "❌ ERROR: Port 8000 still in use after cleanup!"
    echo "Please check what's using it:"
    sudo lsof -i :8000
    exit 1
fi

echo ""
echo "Step 6: Check if there are multiple supervisor configs..."
echo "=================================================="
echo "Supervisor configs:"
sudo find /etc/supervisor -name "*.conf" -exec echo "  - {}" \;

echo ""
echo "Step 7: Reload supervisor configuration..."
echo "=================================================="
sudo supervisorctl reread
sudo supervisorctl update

echo ""
echo "Step 8: Wait 5 seconds before starting..."
sleep 5

echo ""
echo "Step 9: Start ads-automation only (not all)..."
echo "=================================================="
sudo supervisorctl start ads-automation

echo ""
echo "Step 10: Wait 3 seconds for startup..."
sleep 3

echo ""
echo "Step 11: Check status..."
echo "=================================================="
sudo supervisorctl status

echo ""
echo "Step 12: Test if port 8000 is listening..."
echo "=================================================="
if sudo lsof -i :8000 > /dev/null 2>&1; then
    echo "✅ Port 8000 is now listening:"
    sudo lsof -i :8000
else
    echo "❌ Port 8000 is not listening yet"
    echo "Checking logs..."
    sudo supervisorctl tail ads-automation stdout | tail -30
fi

echo ""
echo "Step 13: Test API..."
echo "=================================================="
sleep 2
curl -s http://localhost:8000/health || echo "API not responding yet"

echo ""
echo "✅ Done!"
echo ""
echo "📝 Manual checks:"
echo "  - View logs: sudo supervisorctl tail ads-automation -f"
echo "  - Check port: sudo lsof -i :8000"
echo "  - Restart: sudo supervisorctl restart ads-automation"
