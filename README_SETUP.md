# 🚀 HƯỚNG DẪN SETUP - TÓM TẮT NHANH

## 📋 BƯỚC 1: SETUP SERVER

**Xem chi tiết:** `SETUP_LIGHTSAIL_SERVER.md`

### Quick steps:
1. Tạo instance trên Lightsail (Singapore, 2 vCPU, 2GB RAM)
2. Kết nối với MobaXterm (SSH)
3. Update hệ thống: `sudo apt update && sudo apt upgrade -y`
4. Cài Python 3.11, PostgreSQL, Redis, Nginx, Supervisor

---

## 📋 BƯỚC 2: SETUP PROJECT

```bash
# Tạo thư mục
mkdir -p ~/ads-automation
cd ~/ads-automation

# Upload code (qua MobaXterm file manager)

# Tạo venv
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 📋 BƯỚC 3: CẤU HÌNH

```bash
# Copy env.example
cp env.example .env

# Edit .env
nano .env
# Điền các giá trị:
# - DATABASE_URL
# - ACCESS_TOKEN
# - TELEGRAM_BOT_TOKEN
# - TELEGRAM_CHAT_ID
# - TELEGRAM_WEBHOOK_SECRET
# - SECRET_KEY (min 32 chars)
```

---

## 📋 BƯỚC 4: INITIALIZE DATABASE

```bash
# Tạo database
sudo -u postgres psql << EOF
CREATE DATABASE ads_automation;
CREATE USER adsuser WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ads_automation TO adsuser;
\q
EOF

# Update DATABASE_URL trong .env
# DATABASE_URL=postgresql://adsuser:your_password@localhost:5432/ads_automation

# Initialize tables
python scripts/init_db.py
```

---

## 📋 BƯỚC 5: START SERVICES

### **Option 1: Manual (test):**

```bash
# Terminal 1: API server
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Worker 1
source venv/bin/activate
python -m app.workers.telegram_worker worker-1

# Terminal 3: Worker 2
source venv/bin/activate
python -m app.workers.telegram_worker worker-2
```

### **Option 2: Supervisor (production):**

```bash
# Tạo config
sudo nano /etc/supervisor/conf.d/ads-automation.conf
# (Copy từ SETUP_LIGHTSAIL_SERVER.md)

# Reload
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all

# Check status
sudo supervisorctl status
```

---

## 📋 BƯỚC 6: SETUP NGINX

```bash
# Tạo config
sudo nano /etc/nginx/sites-available/ads-automation
# (Copy từ SETUP_LIGHTSAIL_SERVER.md)

# Enable
sudo ln -s /etc/nginx/sites-available/ads-automation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 📋 BƯỚC 7: SETUP TELEGRAM WEBHOOK

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -d "url=https://your-domain.com/api/telegram/webhook" \
  -d "secret_token=<YOUR_WEBHOOK_SECRET>"
```

---

## 📋 BƯỚC 8: TEST

```bash
# Health check
curl http://localhost:8000/health

# Test Telegram webhook
curl -X POST http://localhost:8000/api/telegram/webhook \
  -H "Content-Type: application/json" \
  -H "X-Telegram-Bot-Api-Secret-Token: <WEBHOOK_SECRET>" \
  -d '{"update_id": 123, "message": {"text": "/help", "chat": {"id": -123}, "from": {"id": 456}}}'

# Check logs
tail -f /var/log/ads-automation/api.out.log
tail -f /var/log/ads-automation/worker.out.log
```

---

## ✅ CHECKLIST

- [ ] Server setup hoàn tất
- [ ] Python 3.11, PostgreSQL, Redis installed
- [ ] Code uploaded
- [ ] .env configured
- [ ] Database initialized
- [ ] Services running
- [ ] Nginx configured
- [ ] Telegram webhook setup
- [ ] Test thành công

---

**Xem chi tiết trong `SETUP_LIGHTSAIL_SERVER.md`! 🚀**

