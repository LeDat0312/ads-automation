#!/bin/bash
# Fix circular import issue

cd ~/ads-automation || exit 1

echo "🧹 Step 1: Cleaning Python cache..."
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "✅ Cache cleaned"

echo ""
echo "📥 Step 2: Pulling latest code from GitHub..."
git stash 2>/dev/null || true
git pull origin main
echo "✅ Code updated"

echo ""
echo "🔍 Step 3: Verifying database.py has no top-level Job import..."
if grep -n "^from app.models.job import" app/core/database.py 2>/dev/null; then
    echo "❌ ERROR: Found top-level Job import in database.py!"
    echo "Please check the file manually."
    exit 1
else
    echo "✅ No top-level Job import found (correct!)"
fi

echo ""
echo "🔍 Step 4: Verifying Job import is inside init_db()..."
if grep -A 10 "def init_db" app/core/database.py | grep -q "from app.models.job import"; then
    echo "✅ Job import found inside init_db() (correct!)"
else
    echo "⚠️  WARNING: Job import not found in init_db()"
fi

echo ""
echo "🧪 Step 5: Testing import..."
source venv/bin/activate
if python -c "from app.workers.telegram_worker import worker_loop; print('✅ Import OK')" 2>&1; then
    echo "✅ Import test passed!"
else
    echo "❌ Import test failed! Check errors above."
    exit 1
fi

echo ""
echo "🔄 Step 6: Restarting workers..."
sudo supervisorctl restart ads-automation-worker:*
sleep 2
sudo supervisorctl status

echo ""
echo "✅ Fix complete! Check worker status above."


