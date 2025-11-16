# ✅ DATABASE INIT THÀNH CÔNG - BƯỚC TIẾP THEO

## 🎉 KẾT QUẢ

- ✅ **6 tables** đã được tạo:
  - `telegram_updates`
  - `jobs`
  - `logic_rules`
  - `ads_metrics`
  - `system_settings`
  - `automation_status`

---

## 📋 BƯỚC TIẾP THEO

### **BƯỚC 1: TEST API SERVER**

```bash
cd ~/ads-automation
source venv/bin/activate

# Test chạy server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Trong terminal/tab khác (hoặc MobaXterm tab mới):**

```bash
# Test health check
curl http://localhost:8000/health
# Nên trả về: {"status":"healthy"}

# Test root
curl http://localhost:8000/
# Nên trả về JSON với message

# Test API endpoints
curl http://localhost:8000/api/rules
```

**Dừng server:** `Ctrl+C`

---

## 🔧 BƯỚC 2: SETUP SUPERVISOR (PRODUCTION)

### **Tạo config file:**

```bash
sudo nano /etc/supervisor/conf.d/ads-automation.conf
```

**Nội dung:**

```ini
[program:ads-automation-api]
command=/home/adsuser/ads-automation/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
directory=/home/adsuser/ads-automation
user=adsuser
autostart=true
autorestart=true
stderr_logfile=/var/log/ads-automation/api.err.log
stdout_logfile=/var/log/ads-automation/api.out.log
environment=PATH="/home/adsuser/ads-automation/venv/bin"

[program:ads-automation-worker]
command=/home/adsuser/ads-automation/venv/bin/python -m app.workers.telegram_worker
directory=/home/adsuser/ads-automation
user=adsuser
autostart=true
autorestart=true
stderr_logfile=/var/log/ads-automation/worker.err.log
stdout_logfile=/var/log/ads-automation/worker.out.log
environment=PATH="/home/adsuser/ads-automation/venv/bin"
numprocs=2
process_name=%(program_name)s_%(process_num)02d
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

### **Tạo log directory:**

```bash
sudo mkdir -p /var/log/ads-automation
sudo chown adsuser:adsuser /var/log/ads-automation
```

### **Reload supervisor:**

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ads-automation-api
sudo supervisorctl start ads-automation-worker:*
```

### **Check status:**

```bash
sudo supervisorctl status
```

**Kết quả mong đợi:**
```
ads-automation-api                  RUNNING   pid 12345, uptime 0:00:05
ads-automation-worker:ads-automation-worker_00   RUNNING   pid 12346, uptime 0:00:05
ads-automation-worker:ads-automation-worker_01   RUNNING   pid 12347, uptime 0:00:05
```

---

## 🌐 BƯỚC 3: SETUP NGINX

### **Tạo config:**

```bash
sudo nano /etc/nginx/sites-available/ads-automation
```

**Nội dung:**

```nginx
server {
    listen 80;
    server_name 54.179.208.122;  # Public IP

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
```

**Enable:**

```bash
sudo ln -s /etc/nginx/sites-available/ads-automation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### **Test từ bên ngoài:**

```bash
# Từ máy local hoặc browser
curl http://54.179.208.122/health
# Nên trả về: {"status":"healthy"}
```

---

## 🔐 BƯỚC 4: SETUP TELEGRAM WEBHOOK

### **Sau khi API server đã chạy (qua Supervisor):**

```bash
curl -X POST "https://api.telegram.org/bot8597844822:AAGZav90dI9PjOKx9kQ2VQlkdmf90ytcG3k/setWebhook" \
  -d "url=https://54.179.208.122/api/telegram/webhook" \
  -d "secret_token=bac722f5ee22f178b4c1304e1a70293547706dbed02f7159e8fba75fba30791d"
```

### **Verify webhook:**

```bash
curl "https://api.telegram.org/bot8597844822:AAGZav90dI9PjOKx9kQ2VQlkdmf90ytcG3k/getWebhookInfo"
```

**Kết quả mong đợi:**
```json
{
  "ok": true,
  "result": {
    "url": "https://54.179.208.122/api/telegram/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0
  }
}
```

---

## 🧪 BƯỚC 5: TEST TELEGRAM BOT

### **Gửi message cho bot:**

1. **Mở Telegram**
2. **Tìm bot của bạn**
3. **Gửi:** `/help`
4. **Nên nhận được response**

---

## ✅ CHECKLIST

- [x] Database initialized (6 tables)
- [ ] Test API server: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [ ] Setup Supervisor
- [ ] Setup Nginx
- [ ] Test từ bên ngoài: `curl http://54.179.208.122/health`
- [ ] Setup Telegram webhook
- [ ] Test Telegram bot: `/help`

---

## 🚀 QUICK COMMANDS

### **Start services:**

```bash
# Start API
sudo supervisorctl start ads-automation-api

# Start workers
sudo supervisorctl start ads-automation-worker:*

# Check status
sudo supervisorctl status

# View logs
tail -f /var/log/ads-automation/api.out.log
tail -f /var/log/ads-automation/worker.out.log
```

### **Restart services:**

```bash
sudo supervisorctl restart ads-automation-api
sudo supervisorctl restart ads-automation-worker:*
```

---

**Bây giờ hãy test API server và setup Supervisor! 🚀**


