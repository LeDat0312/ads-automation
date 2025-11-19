# Sửa lỗi Dashboard trên VPS

## Vấn đề:
- `ads-automation: ERROR (spawn error)`
- `ERROR: [Errno 98] Address already in use`
- Website chưa thay đổi, tính năng mới chưa hoạt động

## Bước 1: Kiểm tra và kill process đang chiếm port

```bash
# Kiểm tra port nào đang được sử dụng (thường là 8000 hoặc 8080)
sudo netstat -tlnp | grep :8000
# hoặc
sudo lsof -i :8000

# Tìm process Python đang chạy
ps aux | grep python | grep uvicorn
ps aux | grep python | grep main.py

# Kill process nếu cần
sudo pkill -f uvicorn
sudo pkill -f "python.*main.py"
```

## Bước 2: Kiểm tra supervisor config

```bash
# Xem config hiện tại
sudo cat /etc/supervisor/conf.d/ads-automation.conf

# Kiểm tra log file path trong config
# Đảm bảo log file có quyền ghi
sudo touch /var/log/ads-automation.log
sudo chown adsuser:adsuser /var/log/ads-automation.log
sudo chmod 644 /var/log/ads-automation.log
```

## Bước 3: Kiểm tra và sửa supervisor config (nếu cần)

```bash
# Backup config cũ
sudo cp /etc/supervisor/conf.d/ads-automation.conf /etc/supervisor/conf.d/ads-automation.conf.backup

# Sửa config (thay đổi theo setup của bạn)
sudo nano /etc/supervisor/conf.d/ads-automation.conf
```

Config mẫu:
```ini
[program:ads-automation]
command=/home/adsuser/ads-automation/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
directory=/home/adsuser/ads-automation
user=adsuser
autostart=true
autorestart=true
stderr_logfile=/var/log/ads-automation.log
stdout_logfile=/var/log/ads-automation.log
environment=PATH="/home/adsuser/ads-automation/venv/bin"
```

## Bước 4: Restart supervisor

```bash
# Reread và update config
sudo supervisorctl reread
sudo supervisorctl update

# Stop tất cả services
sudo supervisorctl stop all

# Start lại
sudo supervisorctl start ads-automation
sudo supervisorctl start ads-worker

# Kiểm tra status
sudo supervisorctl status
```

## Bước 5: Kiểm tra log mới

### Backend logs (FastAPI):
```bash
# Log từ supervisor
sudo tail -f /var/log/ads-automation.log

# Hoặc log trực tiếp từ app (nếu có)
tail -f ~/ads-automation/logs/*.log
```

### Frontend logs (React/Vite):
```bash
# Kiểm tra build output
ls -la ~/ads-automation/frontend/dist/

# Kiểm tra nginx logs (nếu serve frontend qua nginx)
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Kiểm tra browser console (F12 trong browser)
```

## Bước 6: Đảm bảo frontend đã được build

```bash
cd ~/ads-automation/frontend

# Kiểm tra xem đã build chưa
ls -la dist/

# Nếu chưa có dist/, build lại
npm install
npm run build

# Kiểm tra build output
ls -la dist/
```

## Bước 7: Kiểm tra nginx config (nếu dùng nginx)

```bash
# Xem nginx config
sudo cat /etc/nginx/sites-available/ads-automation
# hoặc
sudo cat /etc/nginx/sites-enabled/ads-automation

# Test nginx config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

Nginx config mẫu cho React frontend:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend (React build)
    location / {
        root /home/adsuser/ads-automation/frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Dashboard route (nếu cần)
    location /dashboard {
        root /home/adsuser/ads-automation/frontend/dist;
        try_files $uri $uri/ /dashboard/index.html;
    }
}
```

## Bước 8: Debug chi tiết

```bash
# 1. Kiểm tra process đang chạy
ps aux | grep -E "uvicorn|python|node"

# 2. Kiểm tra port
sudo netstat -tlnp | grep -E "8000|8080|3000"

# 3. Test backend API trực tiếp
curl http://localhost:8000/api/health
# hoặc
curl http://localhost:8000/dashboard/data

# 4. Kiểm tra file permissions
ls -la ~/ads-automation/
ls -la ~/ads-automation/frontend/dist/

# 5. Xem supervisor logs
sudo tail -f /var/log/supervisor/supervisord.log
```

## Bước 9: Nếu vẫn lỗi, restart toàn bộ

```bash
# Stop tất cả
sudo supervisorctl stop all
sudo pkill -f uvicorn
sudo pkill -f python

# Đợi 2 giây
sleep 2

# Start lại
sudo supervisorctl start ads-automation
sudo supervisorctl start ads-worker

# Kiểm tra
sudo supervisorctl status
```

## Cách check log mới cho Dashboard React:

### 1. Browser Console (F12):
- Mở browser → F12 → Console tab
- Xem JavaScript errors và network requests

### 2. Network Tab (F12):
- Xem API calls đến `/api/dashboard/data`
- Kiểm tra response và status codes

### 3. Backend logs:
```bash
# Real-time log
sudo tail -f /var/log/ads-automation.log

# Hoặc nếu log ở chỗ khác
tail -f ~/ads-automation/logs/app.log
```

### 4. Frontend build logs:
```bash
# Khi build, xem output
cd ~/ads-automation/frontend
npm run build 2>&1 | tee build.log
```

### 5. Nginx logs (nếu dùng):
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log | grep dashboard
```

