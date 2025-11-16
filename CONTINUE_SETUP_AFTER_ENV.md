# 🚀 TIẾP TỤC SETUP SAU KHI CẤU HÌNH .ENV

## ✅ ĐÃ HOÀN THÀNH

- [x] Update .env file
- [x] Set permissions
- [x] Reset PostgreSQL password

---

## 📋 BƯỚC TIẾP THEO

### **BƯỚC 1: TEST DATABASE CONNECTION**

```bash
cd ~/ads-automation

# Test connection
psql -U adsuser -d ads_automation -h localhost
# Nhập password: @Levandat0312
# Nếu vào được → OK
# Thoát: \q
```

### **BƯỚC 2: TEST SETTINGS VỚI PYTHON**

```bash
source venv/bin/activate

python -c "
from app.core.config import get_settings
settings = get_settings()
print('✅ Settings loaded!')
print(f'DATABASE_URL: {settings.DATABASE_URL[:50]}...')
print(f'TELEGRAM_CHAT_ID: {settings.TELEGRAM_CHAT_ID}')
print(f'WEBHOOK_URL: {settings.WEBHOOK_URL}')
"
```

**Kết quả mong đợi:**
```
✅ Settings loaded!
DATABASE_URL: postgresql://adsuser:%40Levandat0312@localhost:5432/ads_automation...
TELEGRAM_CHAT_ID: -1003433325208
WEBHOOK_URL: https://54.179.208.122/api/telegram/webhook
```

### **BƯỚC 3: INITIALIZE DATABASE**

```bash
source venv/bin/activate
python scripts/init_db.py
```

**Kết quả mong đợi:**
```
🚀 Initializing database...
📋 Database URL: postgresql://adsuser:%40Levandat0312@localhost:5432/ads_automation...
✅ Database initialized successfully!

📋 Created tables:
  - ads_metrics
  - logic_rules
  - system_settings
  - automation_status
  - telegram_updates
  - jobs
```

### **BƯỚC 4: VERIFY TABLES**

```bash
psql -U adsuser -d ads_automation -h localhost -c "\dt"
```

**Kết quả mong đợi:**
```
                  List of relations
 Schema |         Name          | Type  |  Owner   
--------+-----------------------+-------+----------
 public | ads_metrics           | table | adsuser
 public | automation_status     | table | adsuser
 public | jobs                  | table | adsuser
 public | logic_rules           | table | adsuser
 public | system_settings       | table | adsuser
 public | telegram_updates      | table | adsuser
(6 rows)
```

### **BƯỚC 5: TEST API SERVER**

```bash
source venv/bin/activate

# Test chạy server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Trong terminal/tab khác:**

```bash
# Test health check
curl http://localhost:8000/health
# Nên trả về: {"status":"healthy"}

# Test root
curl http://localhost:8000/
# Nên trả về JSON với message
```

**Dừng server:** `Ctrl+C`

---

## 🔧 BƯỚC 6: SETUP SUPERVISOR (PRODUCTION)

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

---

## 🌐 BƯỚC 7: SETUP NGINX

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

---

## 🔐 BƯỚC 8: SETUP TELEGRAM WEBHOOK

### **Sau khi API server đã chạy:**

```bash
curl -X POST "https://api.telegram.org/bot8597844822:AAGZav90dI9PjOKx9kQ2VQlkdmf90ytcG3k/setWebhook" \
  -d "url=https://54.179.208.122/api/telegram/webhook" \
  -d "secret_token=bac722f5ee22f178b4c1304e1a70293547706dbed02f7159e8fba75fba30791d"
```

### **Verify webhook:**

```bash
curl "https://api.telegram.org/bot8597844822:AAGZav90dI9PjOKx9kQ2VQlkdmf90ytcG3k/getWebhookInfo"
```

---

## ✅ CHECKLIST

- [ ] Test database connection
- [ ] Test settings với Python
- [ ] Initialize database: `python scripts/init_db.py`
- [ ] Verify tables: `psql -U adsuser -d ads_automation -h localhost -c "\dt"`
- [ ] Test API server: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [ ] Setup Supervisor
- [ ] Setup Nginx
- [ ] Setup Telegram webhook
- [ ] Test từ bên ngoài: `curl http://54.179.208.122/health`

---

**Bắt đầu với Bước 1: Test database connection! 🚀**


