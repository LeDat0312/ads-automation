#!/bin/bash
# Script để verify VPS đã update chưa

echo "=== Kiểm tra Git commit trên VPS ==="
cd /home/adsuser/ads-automation
echo "Current commit:"
git log --oneline -1

echo ""
echo "=== Kiểm tra code trong settings.py ==="
echo "Tìm loadApifyStatus trong initializePage:"
grep -n "loadApifyStatus" app/api/routes/settings.py | head -5

echo ""
echo "Tìm loadScrapeGraphAIStatus (không nên có):"
grep -n "loadScrapeGraphAIStatus" app/api/routes/settings.py | head -5 || echo "✅ Không tìm thấy (đúng rồi!)"

echo ""
echo "=== Kiểm tra process đang chạy ==="
ps aux | grep uvicorn | grep -v grep

echo ""
echo "=== Hướng dẫn update ==="
echo "1. git pull origin main"
echo "2. sudo systemctl restart ads-automation"
echo "   HOẶC: pkill -f uvicorn && cd /home/adsuser/ads-automation && source venv/bin/activate && nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 &"
