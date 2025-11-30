# VPS Service Setup - Hướng dẫn chi tiết

## Vấn đề hiện tại
```bash
Failed to restart metaupdate.service: Unit metaupdate.service not found.
```

Service chưa được tạo trên VPS. Cần setup service để quản lý backend.

---

## Giải pháp - 3 Options

### **Option 1: Kiểm tra service hiện tại (RECOMMENDED - Chạy đầu tiên)**

```bash
cd /home/adsuser/ads-automation
bash VPS_CHECK_AND_FIX_SERVICE.sh
```

Script này sẽ:
- ✅ Tìm tất cả services liên quan (uvicorn, fastapi, metaupdate, etc.)
- ✅ Kiểm tra Python processes đang chạy
- ✅ Kiểm tra Supervisor config (nếu có)
- ✅ Gợi ý cách fix

### **Option 2: Tạo systemd service mới**

Nếu không có service nào, tạo mới:

```bash
cd /home/adsuser/ads-automation
bash VPS_CREATE_SERVICE.sh
```

Script này sẽ:
1. Tạo file `/etc/systemd/system/metaupdate.service`
2. Cấu hình:
   - User: adsuser
   - WorkingDirectory: /home/adsuser/ads-automation
   - ExecStart: venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   - Auto-restart on failure
   - Load .env file
3. Enable service (auto-start on boot)
4. Start service

**Sau khi tạo, kiểm tra:**
```bash
sudo systemctl status metaupdate
sudo journalctl -u metaupdate -f
```

### **Option 3: Restart thông minh (Auto-detect)**

Script tự động detect và restart service:

```bash
cd /home/adsuser/ads-automation
bash VPS_RESTART.sh
```

Script này sẽ:
- Tự động tìm systemd service (metaupdate, uvicorn, fastapi, etc.)
- Hoặc tìm Supervisor
- Hoặc tìm manual uvicorn process
- Restart tự động

---

## Quy trình đầy đủ để deploy code mới

### **Bước 1: Pull code mới**
```bash
cd /home/adsuser/ads-automation
git pull origin main
```

### **Bước 2: Cài đặt dependencies (nếu có thay đổi)**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### **Bước 3: Chạy migrations (nếu có DB changes)**
```bash
source venv/bin/activate
python migrations/add_ad_studio_tables.py  # Nếu cần
```

### **Bước 4: Kiểm tra service hiện tại**
```bash
bash VPS_CHECK_AND_FIX_SERVICE.sh
```

### **Bước 5a: Nếu có service - Restart**
```bash
# Nếu tìm thấy service tên "metaupdate"
sudo systemctl restart metaupdate
sudo journalctl -u metaupdate -f

# Hoặc dùng script tự động
bash VPS_RESTART.sh
```

### **Bước 5b: Nếu không có service - Tạo mới**
```bash
bash VPS_CREATE_SERVICE.sh
```

### **Bước 6: Verify backend đang chạy**
```bash
# Check process
ps aux | grep uvicorn

# Check port 8000
sudo netstat -tlnp | grep :8000

# Test API
curl http://localhost:8000/health
```

### **Bước 7: Restart nginx (nếu cần)**
```bash
sudo systemctl restart nginx
sudo systemctl status nginx
```

### **Bước 8: Test từ browser**
```
https://updatemetaads.site/health
https://updatemetaads.site/dashboard
```

---

## Service Management Commands

### Systemd (nếu dùng metaupdate.service)

```bash
# Check status
sudo systemctl status metaupdate

# Start
sudo systemctl start metaupdate

# Stop
sudo systemctl stop metaupdate

# Restart
sudo systemctl restart metaupdate

# Enable (auto-start on boot)
sudo systemctl enable metaupdate

# Disable
sudo systemctl disable metaupdate

# View logs (real-time)
sudo journalctl -u metaupdate -f

# View last 100 lines
sudo journalctl -u metaupdate -n 100

# View logs since boot
sudo journalctl -u metaupdate -b
```

### Supervisor (nếu dùng supervisor)

```bash
# Check status
sudo supervisorctl status

# Restart all
sudo supervisorctl restart all

# Restart specific
sudo supervisorctl restart fastapi

# View logs
sudo supervisorctl tail -f fastapi
```

---

## Troubleshooting

### ❌ Lỗi: Port 8000 already in use

```bash
# Tìm process đang dùng port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Hoặc kill all uvicorn
sudo pkill -f uvicorn
```

### ❌ Lỗi: Module not found

```bash
cd /home/adsuser/ads-automation
source venv/bin/activate
pip install -r requirements.txt
```

### ❌ Lỗi: Database connection failed

```bash
# Check PostgreSQL running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Check .env file có đúng DB credentials
cat .env | grep DATABASE_URL
```

### ❌ Lỗi: Permission denied

```bash
# Fix ownership
sudo chown -R adsuser:adsuser /home/adsuser/ads-automation

# Fix venv permissions
sudo chown -R adsuser:adsuser /home/adsuser/ads-automation/venv
```

### ❌ Service fails to start

```bash
# Check detailed logs
sudo journalctl -u metaupdate -xe

# Check service file syntax
sudo systemd-analyze verify /etc/systemd/system/metaupdate.service

# Reload daemon
sudo systemctl daemon-reload
```

---

## Quick Reference - One-liner deploy

**Nếu service đã tồn tại:**
```bash
cd /home/adsuser/ads-automation && git pull origin main && bash VPS_RESTART.sh
```

**Nếu cần tạo service mới:**
```bash
cd /home/adsuser/ads-automation && git pull origin main && bash VPS_CREATE_SERVICE.sh
```

---

## Service File Template

Nếu muốn tạo manual, file `/etc/systemd/system/metaupdate.service`:

```ini
[Unit]
Description=MetaUpdate FastAPI Backend (Facebook Ads Automation)
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=adsuser
Group=adsuser
WorkingDirectory=/home/adsuser/ads-automation

Environment="PATH=/home/adsuser/ads-automation/venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/home/adsuser/ads-automation/.env

ExecStart=/home/adsuser/ads-automation/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

NoNewPrivileges=true
PrivateTmp=true
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

**Sau khi tạo file:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable metaupdate
sudo systemctl start metaupdate
sudo systemctl status metaupdate
```

---

## Environment Variables cần thiết cho Facebook OAuth

Đảm bảo file `.env` có các biến sau:

```bash
# Facebook OAuth - Fanpage Connection
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here
FACEBOOK_REDIRECT_URI=https://updatemetaads.site/api/facebook/callback
FACEBOOK_API_VERSION=v20.0
FACEBOOK_VERIFY_TOKEN=your_random_verify_token_here
FRONTEND_BASE_URL=https://updatemetaads.site

# Database
DATABASE_URL=postgresql://user:password@localhost/dbname

# Security
SECRET_KEY=your_secret_key_here
ENCRYPTION_KEY=your_encryption_key_here

# Other settings...
```

---

## Next Steps - Test Facebook OAuth

Sau khi service chạy thành công:

1. **Deploy frontend:**
```bash
cd /home/adsuser/ads-automation/frontend
npm run build
sudo cp -r dist/* /var/www/html/
```

2. **Test OAuth flow:**
- Truy cập: https://updatemetaads.site/settings/channels
- Click "➕ Thêm kênh"
- Authorize Facebook
- Kiểm tra callback redirect
- Xem logs: `sudo journalctl -u metaupdate -f`

3. **Configure Facebook App:**
- Valid OAuth Redirect URIs: `https://updatemetaads.site/api/facebook/callback`
- Webhook Callback URL: `https://updatemetaads.site/api/facebook/webhook`
- Verify Token: Same as `FACEBOOK_VERIFY_TOKEN` in .env

---

## Support

Nếu gặp vấn đề, chạy:
```bash
bash VPS_CHECK_AND_FIX_SERVICE.sh > service_check.log 2>&1
cat service_check.log
```

Gửi log để debug.
