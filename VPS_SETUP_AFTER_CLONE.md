# 🚀 VPS SETUP SAU KHI CLONE

## ✅ CLONE THÀNH CÔNG!

- ✅ **47 objects** đã được clone
- ✅ **44.16 KiB** code
- ✅ Repository: `~/ads-automation`

---

## 📋 BƯỚC 1: VERIFY FILES

```bash
# Navigate vào thư mục
cd ~/ads-automation

# Verify files
ls -la
```

**Kết quả mong đợi:**
```
app/
scripts/
requirements.txt
env.example
.gitignore
```

---

## ⚙️ BƯỚC 2: CẤU HÌNH .ENV

```bash
# Tạo .env từ env.example
cp env.example .env

# Edit .env
nano .env
```

**Điền các giá trị:**

```bash
# Database
DATABASE_URL=postgresql://adsuser:%40Levandat0312@localhost:5432/ads_automation

# Redis (optional)
REDIS_URL=redis://localhost:6379/0

# Facebook API
ACCESS_TOKEN=your_facebook_access_token
AD_ACCOUNT_IDS=act_123456789,act_987654321
DATA_DATE_PRESET=yesterday

# Telegram
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_WEBHOOK_SECRET=your_webhook_secret_min_32_chars
WEBHOOK_URL=https://your-domain.com/api/telegram/webhook

# Server
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=your_secret_key_min_32_chars_required

# Automation
RUN_WINDOW_START_HOUR=6
RUN_WINDOW_END_HOUR=23
DELAY_KHI_TAT_BATCH=1000
NOTIFY_NO_VIOLATION_MINUTES=30

# Job Queue
JOB_QUEUE_WORKERS=2
JOB_RATE_LIMIT_SECONDS=30
JOB_MAX_ATTEMPTS=3
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

**Set permissions:**
```bash
chmod 600 .env
```

---

## 🐍 BƯỚC 3: SETUP PYTHON VENV

```bash
# Tạo venv
python3.11 -m venv venv

# Activate venv
source venv/bin/activate

# Verify
which python
# Nên thấy: /home/adsuser/ads-automation/venv/bin/python

# Upgrade pip
pip install --upgrade pip
```

---

## 📦 BƯỚC 4: INSTALL DEPENDENCIES

```bash
# Đảm bảo đang trong venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify
pip list | head -20
```

**Kết quả mong đợi:**
```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
...
```

---

## 🗄️ BƯỚC 5: INITIALIZE DATABASE

```bash
# Đảm bảo đang trong venv
source venv/bin/activate

# Initialize database tables
python scripts/init_db.py
```

**Kết quả mong đợi:**
```
🚀 Initializing database...
✅ Database initialized successfully!

📋 Created tables:
  - ads_metrics
  - logic_rules
  - system_settings
  - automation_status
  - telegram_updates
  - jobs
```

### **Verify tables:**

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

---

## 🧪 BƯỚC 6: TEST API SERVER

```bash
cd ~/ads-automation
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

## 🔧 BƯỚC 7: SETUP SUPERVISOR (PRODUCTION)

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

## 🌐 BƯỚC 8: SETUP NGINX

```bash
sudo nano /etc/nginx/sites-available/ads-automation
```

**Nội dung:**

```nginx
server {
    listen 80;
    server_name your-server-ip;  # Hoặc domain nếu có

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

## ✅ CHECKLIST

- [ ] Verify files: `ls -la ~/ads-automation`
- [ ] Tạo .env: `cp env.example .env`
- [ ] Configure .env: `nano .env`
- [ ] Tạo venv: `python3.11 -m venv venv`
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Initialize database: `python scripts/init_db.py`
- [ ] Test API server: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [ ] Setup Supervisor (production)
- [ ] Setup Nginx (production)

---

**Bây giờ hãy bắt đầu với Bước 1: Verify files! 🚀**


