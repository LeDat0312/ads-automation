# 🚀 BƯỚC TIẾP THEO - SETUP PROJECT

Bạn đã kết nối được với server! Bây giờ tiếp tục setup project.

---

## ✅ KIỂM TRA MÔI TRƯỜNG

### **1. Kiểm tra Python:**

```bash
python3 --version
# Nên là Python 3.11+

python3.11 --version
# Nếu có Python 3.11
```

### **2. Kiểm tra PostgreSQL:**

```bash
sudo systemctl status postgresql
# Nên thấy "active (running)"

psql --version
```

### **3. Kiểm tra Redis:**

```bash
sudo systemctl status redis-server
# Nên thấy "active (running)"

redis-cli ping
# Nên trả về: PONG
```

---

## 📁 BƯỚC 1: TẠO THƯ MỤC PROJECT

```bash
# Tạo thư mục
mkdir -p ~/ads-automation
cd ~/ads-automation

# Kiểm tra
pwd
# Nên thấy: /home/adsuser/ads-automation
```

---

## 📤 BƯỚC 2: UPLOAD CODE

### **Option 1: Qua MobaXterm (Dễ nhất)**

1. **Mở MobaXterm File Manager:**
   - Click icon **"File manager"** ở sidebar bên trái
   - Navigate đến `/home/adsuser/ads-automation`

2. **Upload files:**
   - Kéo thả tất cả files từ máy local vào thư mục `ads-automation`
   - Hoặc right-click → Upload files

3. **Verify:**
   ```bash
   cd ~/ads-automation
   ls -la
   # Nên thấy các files: app/, requirements.txt, env.example, etc.
   ```

### **Option 2: Qua Git (nếu có repo)**

```bash
cd ~/ads-automation
git clone https://github.com/your-repo/ads-automation.git .
```

---

## 🐍 BƯỚC 3: SETUP PYTHON VENV

```bash
cd ~/ads-automation

# Tạo virtual environment
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Verify (prompt sẽ có (venv))
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
pip list
# Nên thấy: fastapi, uvicorn, sqlalchemy, etc.
```

---

## ⚙️ BƯỚC 5: CẤU HÌNH .ENV

```bash
cd ~/ads-automation

# Copy env.example
cp env.example .env

# Edit .env
nano .env
```

**Điền các giá trị:**

```bash
# Database
DATABASE_URL=postgresql://adsuser:your_password@localhost:5432/ads_automation

# Redis
REDIS_URL=redis://localhost:6379/0

# Facebook API
ACCESS_TOKEN=your_facebook_token_here
AD_ACCOUNT_IDS=act_123456789,act_987654321

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
DATA_DATE_PRESET=yesterday

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

## 🗄️ BƯỚC 6: SETUP DATABASE

### **6.1. Tạo database và user:**

```bash
sudo -u postgres psql << EOF
CREATE DATABASE ads_automation;
CREATE USER adsuser WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE ads_automation TO adsuser;
ALTER USER adsuser CREATEDB;
\q
EOF
```

**Lưu ý:** Thay `your_secure_password` bằng password thực tế và update trong `.env`

### **6.2. Test connection:**

```bash
psql -U adsuser -d ads_automation -h localhost
# Nhập password khi hỏi
# Nếu vào được psql prompt → OK
# Thoát: \q
```

### **6.3. Initialize tables:**

```bash
cd ~/ads-automation
source venv/bin/activate

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

### **6.4. Verify tables:**

```bash
psql -U adsuser -d ads_automation -h localhost -c "\dt"
# Nên thấy danh sách các tables
```

---

## 🧪 BƯỚC 7: TEST API SERVER

```bash
cd ~/ads-automation
source venv/bin/activate

# Test chạy API server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Trong terminal khác (hoặc MobaXterm tab mới):**

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

## 🔧 BƯỚC 8: SETUP SUPERVISOR

### **8.1. Tạo config file:**

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

### **8.2. Tạo log directory:**

```bash
sudo mkdir -p /var/log/ads-automation
sudo chown adsuser:adsuser /var/log/ads-automation
```

### **8.3. Reload supervisor:**

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ads-automation-api
sudo supervisorctl start ads-automation-worker:*
```

### **8.4. Check status:**

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

## 🌐 BƯỚC 9: SETUP NGINX

### **9.1. Tạo config:**

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

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

### **9.2. Enable site:**

```bash
sudo ln -s /etc/nginx/sites-available/ads-automation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### **9.3. Test:**

```bash
# Từ máy local hoặc server
curl http://your-server-ip/health
# Nên trả về: {"status":"healthy"}
```

---

## 🔒 BƯỚC 10: SETUP FIREWALL

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## ✅ BƯỚC 11: VERIFY TẤT CẢ

### **11.1. Check services:**

```bash
# Supervisor
sudo supervisorctl status

# Nginx
sudo systemctl status nginx

# PostgreSQL
sudo systemctl status postgresql

# Redis
sudo systemctl status redis-server
```

### **11.2. Check logs:**

```bash
# API logs
tail -f /var/log/ads-automation/api.out.log

# Worker logs
tail -f /var/log/ads-automation/worker.out.log
```

### **11.3. Test API:**

```bash
# Health check
curl http://localhost:8000/health

# Root
curl http://localhost:8000/

# Rules API
curl http://localhost:8000/api/rules
```

---

## 📝 QUICK COMMANDS

```bash
# Restart services
sudo supervisorctl restart ads-automation-api
sudo supervisorctl restart ads-automation-worker:*

# View logs
tail -f /var/log/ads-automation/api.out.log
tail -f /var/log/ads-automation/worker.out.log

# Check status
sudo supervisorctl status

# Update code
cd ~/ads-automation
source venv/bin/activate
# Upload files mới hoặc git pull
pip install -r requirements.txt
sudo supervisorctl restart all
```

---

## 🎯 NEXT: SETUP TELEGRAM WEBHOOK

Sau khi setup xong, tiếp tục với:
- Setup Telegram webhook
- Test commands
- Monitor logs

**Xem tiếp:** `SETUP_LIGHTSAIL_SERVER.md` phần Telegram webhook

---

**Bạn đang ở bước nào? Hãy chạy các lệnh trên! 🚀**

