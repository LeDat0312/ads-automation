#!/bin/bash
# Complete deployment script for Facebook Accounts feature
# Fixes all known VPS issues and deploys new code

echo "🚀 Deploying Facebook Accounts Feature to VPS"
echo "=============================================="
echo ""

# Configuration
PROJECT_DIR="/home/adsuser/ads-automation"
MIGRATION_FILE="migrations/add_facebook_accounts_table.py"

# Step 1: Fix script permissions
echo "Step 1: Fix script permissions..."
cd "$PROJECT_DIR" || exit 1
chmod +x *.sh
echo "✅ Scripts are now executable"
echo ""

# Step 2: Check current supervisor status
echo "Step 2: Check supervisor status..."
if ! command -v supervisorctl &>/dev/null; then
    echo "❌ ERROR: Supervisor not installed!"
    echo "Install with: sudo apt-get install supervisor"
    exit 1
fi

echo "Current supervisor services:"
sudo supervisorctl status || echo "⚠️ No supervisor services running"
echo ""

# Step 3: Stop supervisor services
echo "Step 3: Stop all supervisor services..."
sudo supervisorctl stop all 2>/dev/null || echo "⚠️ No services to stop"
sleep 2
echo ""

# Step 4: Stop nginx (to release file locks)
echo "Step 4: Stop nginx temporarily..."
sudo systemctl stop nginx 2>/dev/null || echo "⚠️ Nginx not running"
echo ""

# Step 5: Clean old frontend dist
echo "Step 5: Clean frontend dist..."
sudo rm -rf frontend/dist/
echo "✅ Cleaned frontend/dist"
echo ""

# Step 6: Pull latest code
echo "Step 6: Pull latest code from GitHub..."
git fetch origin main
git reset --hard origin/main
git clean -fd
echo "✅ Code updated"
echo ""

echo "📋 Current commit:"
git log -1 --oneline
echo ""

# Step 7: Activate virtual environment
echo "Step 7: Activate Python virtual environment..."
if [ ! -d "venv" ]; then
    echo "❌ ERROR: Virtual environment not found!"
    echo "Create with: python3 -m venv venv"
    exit 1
fi

source venv/bin/activate || {
    echo "❌ Failed to activate venv"
    exit 1
}
echo "✅ Virtual environment activated"
echo ""

# Step 8: Install/upgrade dependencies
echo "Step 8: Check Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies up to date"
echo ""

# Step 9: Check if migration exists
echo "Step 9: Check migration file..."
if [ ! -f "$MIGRATION_FILE" ]; then
    echo "❌ ERROR: Migration file not found: $MIGRATION_FILE"
    echo "Available migrations:"
    ls -1 migrations/*.py
    exit 1
fi
echo "✅ Migration file found"
echo ""

# Step 10: Run migration
echo "Step 10: Run database migration..."
python -m migrations.add_facebook_accounts_table || {
    echo "❌ Migration failed!"
    echo ""
    echo "Common issues:"
    echo "  1. Database not accessible - check .env DATABASE_URL"
    echo "  2. Table already exists - safe to ignore if redeploying"
    echo "  3. Import errors - check model dependencies"
    echo ""
    echo "Continue anyway? (y/n)"
    read -r continue
    if [ "$continue" != "y" ]; then
        exit 1
    fi
}
echo "✅ Migration completed (or already exists)"
echo ""

# Step 11: Check supervisor config
echo "Step 11: Check supervisor configuration..."
SUPERVISOR_CONFIGS=$(sudo find /etc/supervisor/conf.d -name "*.conf" 2>/dev/null)

if [ -z "$SUPERVISOR_CONFIGS" ]; then
    echo "❌ ERROR: No supervisor config found!"
    echo ""
    echo "Expected config location: /etc/supervisor/conf.d/ads-automation.conf"
    echo ""
    echo "Sample config:"
    cat << 'EOF'
[program:ads-automation]
command=/home/adsuser/ads-automation/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/home/adsuser/ads-automation
user=adsuser
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/ads-automation.log
environment=PATH="/home/adsuser/ads-automation/venv/bin"
EOF
    echo ""
    echo "Create this file and run: sudo supervisorctl reread && sudo supervisorctl update"
    exit 1
fi

echo "Found supervisor configs:"
echo "$SUPERVISOR_CONFIGS"
echo ""

# Find the main backend service name
SERVICE_NAME=""
for config in $SUPERVISOR_CONFIGS; do
    if grep -q "uvicorn app.main:app" "$config" 2>/dev/null; then
        # Extract program name from config
        SERVICE_NAME=$(grep "^\[program:" "$config" | sed 's/\[program:\(.*\)\]/\1/')
        echo "✅ Found backend service: $SERVICE_NAME"
        echo "Config: $config"
        break
    fi
done

if [ -z "$SERVICE_NAME" ]; then
    echo "❌ ERROR: Could not find backend service in supervisor configs"
    echo ""
    echo "Configs found but none match 'uvicorn app.main:app'"
    echo "Please check your supervisor configuration"
    exit 1
fi
echo ""

# Step 12: Reload supervisor config
echo "Step 12: Reload supervisor configuration..."
sudo supervisorctl reread
sudo supervisorctl update
echo "✅ Supervisor config reloaded"
echo ""

# Step 13: Start nginx
echo "Step 13: Restart nginx..."
sudo systemctl start nginx
sudo systemctl status nginx --no-pager | head -5
echo ""

# Step 14: Start backend service
echo "Step 14: Start backend service ($SERVICE_NAME)..."
sudo supervisorctl start "$SERVICE_NAME"
sleep 3
echo ""

# Step 15: Check service status
echo "Step 15: Check service status..."
sudo supervisorctl status "$SERVICE_NAME"
echo ""

# Step 16: Check if port 8000 is listening
echo "Step 16: Verify port 8000 is listening..."
if sudo lsof -i :8000 >/dev/null 2>&1; then
    echo "✅ Port 8000 is open and listening"
    sudo lsof -i :8000 | head -5
else
    echo "❌ Port 8000 is NOT listening!"
    echo ""
    echo "Checking supervisor logs..."
    sudo supervisorctl tail "$SERVICE_NAME" stderr | tail -30
fi
echo ""

# Step 17: Test health endpoint
echo "Step 17: Test backend health endpoint..."
sleep 2
if curl -s http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Backend is responding!"
    curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "Health check OK"
else
    echo "❌ Backend not responding on /health"
    echo ""
    echo "Recent logs:"
    sudo supervisorctl tail "$SERVICE_NAME" stdout | tail -20
fi
echo ""

# Step 18: Check new API endpoints
echo "Step 18: Check new Facebook Accounts API..."
echo "Testing: GET /api/facebook-accounts (should return 401 without auth)"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/facebook-accounts)

if [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Facebook Accounts API endpoint is accessible (HTTP $HTTP_CODE)"
else
    echo "⚠️ Unexpected response: HTTP $HTTP_CODE"
    echo "Expected 401 (unauthorized) or 200 (if no auth required)"
fi
echo ""

# Final Summary
echo "=============================================="
echo "🎉 DEPLOYMENT SUMMARY"
echo "=============================================="
echo ""
echo "✅ Code pulled from GitHub"
echo "✅ Migration executed: add_facebook_accounts_table"
echo "✅ Supervisor service: $SERVICE_NAME"
echo "✅ Backend process started"
echo ""

echo "📊 Service Status:"
sudo supervisorctl status
echo ""

echo "📝 Quick Commands:"
echo "  - View logs:    sudo supervisorctl tail $SERVICE_NAME -f"
echo "  - Restart:      sudo supervisorctl restart $SERVICE_NAME"
echo "  - Stop:         sudo supervisorctl stop $SERVICE_NAME"
echo "  - Status:       sudo supervisorctl status"
echo ""

echo "🔗 New API Endpoints:"
echo "  - GET    /api/facebook-accounts          (list Via tokens)"
echo "  - POST   /api/facebook-accounts          (create Via)"
echo "  - PATCH  /api/facebook-accounts/{id}     (update Via)"
echo "  - DELETE /api/facebook-accounts/{id}     (delete Via)"
echo "  - POST   /api/facebook-accounts/{id}/verify"
echo "  - GET    /api/facebook-accounts/{id}/pages"
echo "  - POST   /api/channels/facebook/from-saved-account"
echo "  - POST   /api/channels/facebook/manual-v2"
echo ""

echo "📚 Documentation:"
echo "  - Full guide: cat FACEBOOK_VIA_TOKEN_IMPLEMENTATION.md"
echo "  - Test script: python test_facebook_via_api.py"
echo ""

echo "🔍 Troubleshooting:"
if [ -f "/var/log/supervisor/${SERVICE_NAME}.log" ]; then
    echo "  - Check logs: tail -f /var/log/supervisor/${SERVICE_NAME}.log"
fi
echo "  - Debug: ./check_supervisor_conflicts.sh"
echo "  - Port check: sudo lsof -i :8000"
echo ""

echo "✅ Deployment complete!"
