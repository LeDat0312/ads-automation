#!/bin/bash
# 🔧 Fix 502 Backend Error - Auto Diagnostic & Repair

echo "========================================="
echo "🔍 Backend 502 Error Diagnostic & Fix"
echo "========================================="
echo ""

# Change to project directory
cd /path/to/ads-automation || { echo "❌ Project directory not found!"; exit 1; }

echo "📁 Working directory: $(pwd)"
echo ""

# Step 1: Check if virtualenv exists
echo "1️⃣ Checking Python environment..."
if [ -d "venv" ]; then
    echo "✅ Virtual environment found"
    source venv/bin/activate
else
    echo "⚠️  No virtualenv found, using system Python"
fi
echo ""

# Step 2: Install Pillow if not exists
echo "2️⃣ Checking Pillow installation..."
if python3 -c "import PIL" 2>/dev/null; then
    echo "✅ Pillow already installed"
else
    echo "📦 Installing Pillow..."
    pip install Pillow
fi
echo ""

# Step 3: Check SECRET_KEY in .env
echo "3️⃣ Checking SECRET_KEY..."
if grep -q "SECRET_KEY" .env 2>/dev/null; then
    echo "✅ SECRET_KEY exists in .env"
else
    echo "🔑 Adding SECRET_KEY to .env..."
    echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env
    echo "✅ SECRET_KEY added"
fi
echo ""

# Step 4: Test Python imports
echo "4️⃣ Testing Python imports..."
python3 << 'EOF'
import sys
import traceback

tests = [
    ("Pillow", "from PIL import Image"),
    ("captcha.py", "from app.core.captcha import generate_captcha_text, generate_captcha_image"),
    ("auth.py", "from app.api.routes.auth import router"),
    ("main.py", "from app.main import app"),
]

failed = []
for name, code in tests:
    try:
        exec(code)
        print(f"  ✅ {name}")
    except Exception as e:
        print(f"  ❌ {name}: {str(e)}")
        failed.append((name, str(e)))

if failed:
    print("\n❌ Import errors found:")
    for name, error in failed:
        print(f"  - {name}: {error}")
    sys.exit(1)
else:
    print("\n✅ All imports successful")
EOF

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Import test failed! Check error messages above."
    echo "💡 Common fixes:"
    echo "  - pip install -r requirements.txt"
    echo "  - Check Python syntax errors"
    exit 1
fi
echo ""

# Step 5: Check backend service status
echo "5️⃣ Checking backend service..."
SERVICE_NAME="your-backend-service"  # CHANGE THIS to your actual service name

if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Backend service is running"
else
    echo "⚠️  Backend service is NOT running"
fi
echo ""

# Step 6: Check port 8000
echo "6️⃣ Checking port 8000..."
if netstat -tuln | grep -q ":8000 "; then
    echo "✅ Port 8000 is listening"
else
    echo "❌ Port 8000 is NOT listening"
fi
echo ""

# Step 7: Test CAPTCHA endpoint
echo "7️⃣ Testing CAPTCHA endpoint..."
if curl -s http://localhost:8000/auth/captcha -o /tmp/test_captcha.png 2>/dev/null; then
    if file /tmp/test_captcha.png | grep -q "PNG"; then
        echo "✅ CAPTCHA endpoint works! (PNG image generated)"
        rm /tmp/test_captcha.png
    else
        echo "❌ CAPTCHA endpoint returns invalid data"
    fi
else
    echo "❌ Cannot reach CAPTCHA endpoint"
fi
echo ""

# Step 8: Restart backend service
echo "8️⃣ Restarting backend service..."
sudo systemctl restart $SERVICE_NAME
sleep 3

if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Backend service restarted successfully"
else
    echo "❌ Backend service failed to start"
    echo ""
    echo "📋 Last 20 lines of service log:"
    sudo journalctl -u $SERVICE_NAME -n 20 --no-pager
    exit 1
fi
echo ""

# Step 9: Final health check
echo "9️⃣ Final health check..."
sleep 2

# Test API health endpoint
if curl -s http://localhost:8000/api/health 2>/dev/null | grep -q "healthy"; then
    echo "✅ API health check passed"
else
    echo "⚠️  API health check failed (may still be starting)"
fi

# Test CAPTCHA again
if curl -s http://localhost:8000/auth/captcha -o /tmp/final_test.png 2>/dev/null; then
    if file /tmp/final_test.png | grep -q "PNG"; then
        echo "✅ CAPTCHA endpoint works!"
        rm /tmp/final_test.png
    fi
fi
echo ""

echo "========================================="
echo "✅ Fix completed!"
echo "========================================="
echo ""
echo "📊 Next steps:"
echo "  1. Test website: http://your-domain.com"
echo "  2. If still 502, check logs:"
echo "     sudo journalctl -u $SERVICE_NAME -n 50 --no-pager"
echo "  3. Check Nginx logs:"
echo "     sudo tail -50 /var/log/nginx/error.log"
echo ""
