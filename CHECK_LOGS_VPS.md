# Hướng dẫn Check Logs Dashboard trên VPS

## 🔍 Các cách check logs:

### 1. Backend Logs (FastAPI) - QUAN TRỌNG NHẤT

```bash
# Real-time log (theo dõi liên tục)
sudo tail -f /var/log/ads-automation.log

# Xem 100 dòng cuối
sudo tail -n 100 /var/log/ads-automation.log

# Xem log và filter theo keyword
sudo tail -f /var/log/ads-automation.log | grep -i "error"
sudo tail -f /var/log/ads-automation.log | grep -i "dashboard"
```

### 2. Worker Logs

```bash
sudo tail -f /var/log/ads-worker.log
```

### 3. Supervisor Logs

```bash
# Supervisor daemon log
sudo tail -f /var/log/supervisor/supervisord.log

# Supervisor status
sudo supervisorctl status

# Xem chi tiết process
sudo supervisorctl tail -f ads-automation
sudo supervisorctl tail -f ads-worker
```

### 4. Nginx Logs (nếu dùng nginx)

```bash
# Access log (tất cả requests)
sudo tail -f /var/log/nginx/access.log

# Error log
sudo tail -f /var/log/nginx/error.log

# Filter theo dashboard
sudo tail -f /var/log/nginx/access.log | grep dashboard
```

### 5. Browser Console (Frontend)

**Cách check:**
1. Mở website dashboard trong browser
2. Nhấn **F12** (hoặc Right-click → Inspect)
3. Chọn tab **Console** để xem JavaScript errors
4. Chọn tab **Network** để xem API calls:
   - Xem request đến `/api/dashboard/data`
   - Kiểm tra status code (200, 404, 500...)
   - Xem response data

### 6. Test API trực tiếp

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test dashboard data endpoint
curl "http://localhost:8000/dashboard/data?view_mode=lead&level=adset&page=1&pageSize=50"

# Test với authentication (nếu cần)
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/dashboard/data
```

### 7. Kiểm tra process đang chạy

```bash
# Xem tất cả Python processes
ps aux | grep python

# Xem uvicorn processes
ps aux | grep uvicorn

# Xem port đang được sử dụng
sudo netstat -tlnp | grep 8000
sudo lsof -i :8000
```

### 8. Kiểm tra frontend build

```bash
# Kiểm tra build output
ls -la ~/ads-automation/frontend/dist/

# Kiểm tra file index.html
cat ~/ads-automation/frontend/dist/index.html | head -20

# Kiểm tra assets
ls -la ~/ads-automation/frontend/dist/assets/
```

## 🚨 Debug khi có lỗi:

### Lỗi "Address already in use":
```bash
# Tìm và kill process
sudo lsof -ti:8000 | xargs sudo kill -9
sudo pkill -f uvicorn
```

### Lỗi "spawn error":
```bash
# Kiểm tra supervisor config
sudo cat /etc/supervisor/conf.d/ads-automation.conf

# Kiểm tra quyền
ls -la ~/ads-automation/venv/bin/uvicorn

# Restart supervisor
sudo supervisorctl stop all
sudo supervisorctl start ads-automation
```

### Website không thay đổi:
```bash
# 1. Kiểm tra frontend đã build chưa
ls -la ~/ads-automation/frontend/dist/

# 2. Build lại frontend
cd ~/ads-automation/frontend
npm run build

# 3. Kiểm tra nginx config (nếu dùng nginx)
sudo cat /etc/nginx/sites-available/ads-automation | grep -A 10 "location /"

# 4. Reload nginx
sudo systemctl reload nginx

# 5. Clear browser cache (Ctrl+Shift+R hoặc Ctrl+F5)
```

## 📝 Log Commands nhanh (copy toàn bộ):

```bash
# Backend log real-time
sudo tail -f /var/log/ads-automation.log

# Backend log với filter error
sudo tail -f /var/log/ads-automation.log | grep -i error

# Supervisor status
sudo supervisorctl status

# Nginx error log
sudo tail -f /var/log/nginx/error.log

# Test API
curl http://localhost:8000/api/health
```

## 🔄 Restart services:

```bash
# Restart tất cả
sudo supervisorctl stop all
sleep 2
sudo supervisorctl start ads-automation
sudo supervisorctl start ads-worker

# Hoặc restart từng service
sudo supervisorctl restart ads-automation
sudo supervisorctl restart ads-worker
```

