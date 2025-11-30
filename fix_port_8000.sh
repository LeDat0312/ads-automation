#!/bin/bash
# Fix port 8000 already in use - kill old process and restart

echo "🔧 Fixing 'Address already in use' error..."
echo ""

echo "Step 1: Find process using port 8000..."
echo "=================================================="
PROCESS_INFO=$(sudo lsof -i :8000 -t)

if [ -z "$PROCESS_INFO" ]; then
    echo "✅ Port 8000 is free"
else
    echo "Found processes on port 8000:"
    sudo lsof -i :8000
    
    echo ""
    echo "Step 2: Killing processes on port 8000..."
    echo "=================================================="
    sudo kill -9 $(sudo lsof -i :8000 -t) 2>/dev/null || true
    echo "✅ Killed processes"
    
    sleep 2
fi

echo ""
echo "Step 3: Find all uvicorn processes..."
echo "=================================================="
ps aux | grep "[u]vicorn" || echo "No uvicorn processes found"

echo ""
echo "Step 4: Kill all uvicorn processes..."
echo "=================================================="
sudo pkill -9 -f uvicorn || echo "No uvicorn to kill"

echo ""
echo "Step 5: Verify port 8000 is free..."
echo "=================================================="
if sudo lsof -i :8000 > /dev/null 2>&1; then
    echo "❌ Port 8000 still in use!"
    sudo lsof -i :8000
else
    echo "✅ Port 8000 is now free"
fi

echo ""
echo "Step 6: Stop supervisor services..."
echo "=================================================="
sudo supervisorctl stop ads-automation
sudo supervisorctl stop ads-worker

echo ""
echo "Step 7: Wait 2 seconds..."
sleep 2

echo ""
echo "Step 8: Start supervisor services..."
echo "=================================================="
sudo supervisorctl start ads-automation
sudo supervisorctl start ads-worker

echo ""
echo "Step 9: Check status..."
echo "=================================================="
sudo supervisorctl status

echo ""
echo "Step 10: Show recent logs..."
echo "=================================================="
sleep 2
sudo supervisorctl tail ads-automation stdout | tail -20

echo ""
echo "✅ Done!"
echo ""
echo "📝 Next commands:"
echo "  - Check logs: sudo supervisorctl tail ads-automation -f"
echo "  - Check status: sudo supervisorctl status"
echo "  - Test API: curl http://localhost:8000/health"
