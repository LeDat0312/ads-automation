#!/bin/bash

# Script debug chi tiết port 8000
echo "🔍 Debug chi tiết port 8000 và logs..."

# 1. Kiểm tra logs thực tế (theo config supervisor)
echo ""
echo "1️⃣ Logs từ /var/log/ads-automation.log (50 dòng cuối):"
sudo tail -50 /var/log/ads-automation.log 2>/dev/null || echo "Không có log file"

# 2. Kiểm tra port 8000 với nhiều cách
echo ""
echo "2️⃣ Kiểm tra port 8000:"
echo "   - ss:"
sudo ss -tlnp | grep 8000 || echo "   ⚠️ Không thấy port 8000"
echo "   - lsof:"
sudo lsof -i :8000 2>/dev/null || echo "   ⚠️ Không thấy port 8000"
echo "   - netstat (nếu có):"
sudo netstat -tlnp 2>/dev/null | grep 8000 || echo "   ⚠️ netstat không có hoặc không thấy port"

# 3. Kiểm tra process đang chạy
echo ""
echo "3️⃣ Process uvicorn đang chạy:"
ps aux | grep uvicorn | grep -v grep

# 4. Kiểm tra xem process có thể bind port không
echo ""
echo "4️⃣ Kiểm tra quyền bind port:"
sudo -u adsuser ss -tlnp 2>/dev/null | grep 8000 || echo "   User adsuser không thấy port"

# 5. Test kết nối trực tiếp
echo ""
echo "5️⃣ Test kết nối localhost:8000:"
curl -v http://localhost:8000/health 2>&1 | head -20 || echo "   ⚠️ Không kết nối được"

# 6. Kiểm tra xem có firewall block không
echo ""
echo "6️⃣ Kiểm tra firewall:"
sudo ufw status 2>/dev/null || echo "   ufw không chạy hoặc không có"

# 7. Kiểm tra logs real-time khi restart
echo ""
echo "7️⃣ Restart và xem logs real-time:"
sudo supervisorctl stop ads-automation
sleep 2
sudo tail -f /var/log/ads-automation.log &
TAIL_PID=$!
sudo supervisorctl start ads-automation
sleep 5
kill $TAIL_PID 2>/dev/null

# 8. Kiểm tra lại port sau restart
echo ""
echo "8️⃣ Kiểm tra lại port sau restart:"
sleep 2
sudo ss -tlnp | grep 8000 || echo "   ⚠️ Port 8000 vẫn không có"

echo ""
echo "✅ Hoàn tất debug!"


