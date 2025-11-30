#!/bin/bash
# Check for duplicate or conflicting supervisor configs

echo "🔍 Checking for supervisor configuration issues..."
echo ""

echo "1. All supervisor config files:"
echo "=================================================="
sudo find /etc/supervisor -name "*.conf" -type f -exec echo "--- File: {} ---" \; -exec cat {} \; -exec echo "" \;

echo ""
echo "2. Check for processes trying to use port 8000:"
echo "=================================================="
grep -r "port.*8000" /etc/supervisor/ 2>/dev/null || echo "No port 8000 references found in supervisor configs"

echo ""
echo "3. Check systemd services that might conflict:"
echo "=================================================="
sudo systemctl list-units --all --type=service | grep -E "uvicorn|fastapi|ads|meta" || echo "No conflicting systemd services"

echo ""
echo "4. Current processes on port 8000:"
echo "=================================================="
sudo lsof -i :8000 2>/dev/null || echo "Port 8000 is free"

echo ""
echo "5. All Python/uvicorn processes:"
echo "=================================================="
ps aux | grep -E "[p]ython|[u]vicorn" | grep -v grep

echo ""
echo "6. Supervisor status:"
echo "=================================================="
sudo supervisorctl status

echo ""
echo "💡 Analysis:"
echo "If multiple configs reference port 8000, you need to:"
echo "  1. Choose which config to keep"
echo "  2. Remove or disable the others"
echo "  3. Run: sudo supervisorctl reread && sudo supervisorctl update"
