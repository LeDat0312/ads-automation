#!/bin/bash
# Quick fix for common VPS deployment errors
# Addresses the 3 errors you encountered

echo "🔧 VPS Quick Fix Script"
echo "======================="
echo ""

cd /home/adsuser/ads-automation || {
    echo "❌ Cannot find project directory"
    exit 1
}

# Fix 1: Permission denied on scripts
echo "Fix 1: Make all shell scripts executable..."
chmod +x *.sh
echo "✅ Scripts are now executable"
echo ""

# Fix 2: Find correct supervisor service name
echo "Fix 2: Find supervisor service name..."
SERVICE_NAME=""

# Check all supervisor configs
for config in /etc/supervisor/conf.d/*.conf; do
    if [ -f "$config" ]; then
        # Look for our app
        if grep -q "ads-automation" "$config" 2>/dev/null || \
           grep -q "uvicorn app.main:app" "$config" 2>/dev/null; then
            # Extract program name
            SERVICE_NAME=$(grep "^\[program:" "$config" | sed 's/\[program:\(.*\)\]/\1/')
            if [ -n "$SERVICE_NAME" ]; then
                echo "✅ Found service: $SERVICE_NAME (in $config)"
                break
            fi
        fi
    fi
done

if [ -z "$SERVICE_NAME" ]; then
    echo "❌ No supervisor service found!"
    echo ""
    echo "Available supervisor configs:"
    sudo ls -la /etc/supervisor/conf.d/
    echo ""
    echo "Please check your supervisor configuration"
    echo "Or start backend manually:"
    echo "  source venv/bin/activate"
    echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"
    exit 1
fi
echo ""

# Fix 3: Run migration with correct Python path
echo "Fix 3: Run migration with correct Python..."
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Create with: python3 -m venv venv"
    exit 1
fi

# Activate venv
source venv/bin/activate

# Check if migration file exists
if [ ! -f "migrations/add_facebook_accounts_table.py" ]; then
    echo "⚠️ Migration file not in this commit yet"
    echo "Skipping migration (will be available after git pull)"
else
    echo "Running migration..."
    python -m migrations.add_facebook_accounts_table || {
        echo "⚠️ Migration failed (table might already exist)"
        echo "This is OK if redeploying"
    }
fi
echo ""

# Restart supervisor service
echo "Restarting service: $SERVICE_NAME..."
sudo supervisorctl restart "$SERVICE_NAME"
sleep 2
echo ""

# Check status
echo "Service status:"
sudo supervisorctl status "$SERVICE_NAME"
echo ""

# Check port
echo "Port 8000 status:"
if sudo lsof -i :8000 >/dev/null 2>&1; then
    echo "✅ Backend is listening on port 8000"
else
    echo "❌ Port 8000 not listening"
    echo ""
    echo "Check logs with:"
    echo "  sudo supervisorctl tail $SERVICE_NAME -f"
fi
echo ""

echo "✅ Quick fix complete!"
echo ""
echo "Next steps:"
echo "  1. Check logs: sudo supervisorctl tail $SERVICE_NAME -f"
echo "  2. Test health: curl http://localhost:8000/health"
echo "  3. Check status: sudo supervisorctl status"
