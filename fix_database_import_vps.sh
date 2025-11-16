#!/bin/bash
# Fix database.py import issue on VPS

cd ~/ads-automation || exit 1

echo "🔍 Checking database.py for top-level Job import..."

# Check if line 19 has the import
if sed -n '19p' app/core/database.py | grep -q "from app.models.job import"; then
    echo "❌ Found top-level Job import at line 19!"
    echo "🔧 Removing it..."
    
    # Create backup
    cp app/core/database.py app/core/database.py.backup
    
    # Remove the import line (line 19)
    sed -i '19d' app/core/database.py
    
    echo "✅ Removed top-level import"
else
    echo "✅ No top-level import found (already fixed)"
fi

# Verify import is only in init_db()
echo ""
echo "🔍 Verifying Job import is only in init_db()..."
if grep -A 10 "def init_db" app/core/database.py | grep -q "from app.models.job import"; then
    echo "✅ Job import found in init_db() (correct!)"
else
    echo "⚠️  WARNING: Job import not found in init_db()"
    echo "   Adding it..."
    
    # Find init_db function and add import after the comment
    sed -i '/def init_db():/a\    # Import models ở đây để tránh circular import\n    from app.models.telegram_update import TelegramUpdate\n    from app.models.job import Job\n    from app.models.logic_rule import LogicRule' app/core/database.py
fi

echo ""
echo "🧪 Testing import..."
source venv/bin/activate
if python -c "from app.workers.telegram_worker import worker_loop; print('✅ Import OK')" 2>&1; then
    echo "✅ Import test passed!"
    echo ""
    echo "🔄 Restarting workers..."
    sudo supervisorctl restart ads-automation-worker:*
    sleep 2
    sudo supervisorctl status
else
    echo "❌ Import test failed!"
    echo "Showing first 30 lines of database.py:"
    head -30 app/core/database.py
    exit 1
fi


