# ✅ TIẾP TỤC SETUP - USER UBUNTU

## 📋 TÌNH TRẠNG HIỆN TẠI

- ✅ User: `ubuntu` (thay vì `adsuser`)
- ✅ Thư mục đã tạo: `/home/ubuntu/ads-automation`
- ✅ Permissions OK: `drwxr-xr-x`

**Lưu ý:** Dùng user `ubuntu` cũng được, chỉ cần consistent trong toàn bộ setup.

---

## 📤 BƯỚC 1: UPLOAD FILES

### **Qua MobaXterm File Manager:**

1. **Mở File Manager** (icon bên trái)
2. **Navigate đến:** `/home/ubuntu/ads-automation`
3. **Upload files:**
   - Kéo thả tất cả files từ máy local
   - Hoặc right-click → Upload files

### **Verify sau khi upload:**

```bash
cd ~/ads-automation
ls -la
```

**Nên thấy:**
```
app/
requirements.txt
env.example
scripts/
...
```

---

## 🐍 BƯỚC 2: SETUP PYTHON VENV

```bash
cd ~/ads-automation

# Tạo venv
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Verify
which python
# Nên thấy: /home/ubuntu/ads-automation/venv/bin/python

# Upgrade pip
pip install --upgrade pip
```

---

## 📦 BƯỚC 3: INSTALL DEPENDENCIES

```bash
# Đảm bảo đang trong venv
source venv/bin/activate

# Install
pip install -r requirements.txt

# Verify
pip list | head -20
```

---

## ⚙️ BƯỚC 4: CẤU HÌNH .ENV

```bash
cd ~/ads-automation

# Copy env.example
cp env.example .env

# Edit
nano .env
```

**Update DATABASE_URL:**
```bash
# Thay password @Levandat0312 (URL encode @ thành %40)
DATABASE_URL=postgresql://adsuser:%40Levandat0312@localhost:5432/ads_automation
```

**Điền các giá trị khác:**
- `ACCESS_TOKEN` - Facebook token
- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `TELEGRAM_CHAT_ID` - Chat ID
- `TELEGRAM_WEBHOOK_SECRET` - Secret key (min 32 chars)
- `SECRET_KEY` - Secret key (min 32 chars)

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

**Set permissions:**
```bash
chmod 600 .env
```

---

## 🗄️ BƯỚC 5: INITIALIZE DATABASE

```bash
cd ~/ads-automation
source venv/bin/activate

# Initialize tables
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
```

**Dừng server:** `Ctrl+C`

---

## 🔧 BƯỚC 7: SETUP SUPERVISOR

### **Tạo config file:**

```bash
sudo nano /etc/supervisor/conf.d/ads-automation.conf
```

**Nội dung (update paths cho user ubuntu):**

```ini
[program:ads-automation-api]
command=/home/ubuntu/ads-automation/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
directory=/home/ubuntu/ads-automation
user=ubuntu
autostart=true
autorestart=true
stderr_logfile=/var/log/ads-automation/api.err.log
stdout_logfile=/var/log/ads-automation/api.out.log
environment=PATH="/home/ubuntu/ads-automation/venv/bin"

[program:ads-automation-worker]
command=/home/ubuntu/ads-automation/venv/bin/python -m app.workers.telegram_worker
directory=/home/ubuntu/ads-automation
user=ubuntu
autostart=true
autorestart=true
stderr_logfile=/var/log/ads-automation/worker.err.log
stdout_logfile=/var/log/ads-automation/worker.out.log
environment=PATH="/home/ubuntu/ads-automation/venv/bin"
numprocs=2
process_name=%(program_name)s_%(process_num)02d
```

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

### **Tạo log directory:**

```bash
sudo mkdir -p /var/log/ads-automation
sudo chown ubuntu:ubuntu /var/log/ads-automation
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

- [ ] Upload files vào `/home/ubuntu/ads-automation`
- [ ] Setup venv và install dependencies
- [ ] Configure `.env` file
- [ ] Initialize database: `python scripts/init_db.py`
- [ ] Test API server
- [ ] Setup Supervisor
- [ ] Setup Nginx
- [ ] Test từ bên ngoài: `curl http://your-server-ip/health`

---

**Bây giờ hãy upload files và tiếp tục setup! 🚀**

