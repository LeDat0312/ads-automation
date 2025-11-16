# 🧪 TEST API SERVER

## ✅ SERVER ĐÃ CHẠY THÀNH CÔNG

Từ log, tôi thấy:
- ✅ Server started: `Started server process [72981]`
- ✅ Database initialized: `✅ Database initialized successfully`
- ✅ Server running: `Uvicorn running on http://0.0.0.0:8000`

**Vấn đề:** Bạn đã dừng server (`Ctrl+C`) nên không thể test được.

---

## 🚀 CÁCH TEST

### **CÁCH 1: Test trong khi server đang chạy (2 terminals)**

#### **Terminal 1: Chạy server**

```bash
cd ~/ads-automation
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Giữ server chạy, KHÔNG dừng!**

#### **Terminal 2: Test API (MobaXterm tab mới)**

```bash
# Test health check
curl http://localhost:8000/health

# Test root
curl http://localhost:8000/

# Test API endpoints
curl http://localhost:8000/api/rules
```

**Sau khi test xong, quay lại Terminal 1 và dừng server:** `Ctrl+C`

---

### **CÁCH 2: Setup Supervisor (Production - KHUYẾN NGHỊ)**

**Server sẽ chạy tự động, không cần giữ terminal.**

```bash
# Tạo config
sudo nano /etc/supervisor/conf.d/ads-automation.conf
```

**Paste:**

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

```bash
# Tạo log directory
sudo mkdir -p /var/log/ads-automation
sudo chown adsuser:adsuser /var/log/ads-automation

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ads-automation-api
sudo supervisorctl start ads-automation-worker:*

# Check status
sudo supervisorctl status
```

**Sau đó test:**
```bash
curl http://localhost:8000/health
```

---

## 🧪 TEST CÁC ENDPOINTS

### **Khi server đang chạy:**

```bash
# Health check
curl http://localhost:8000/health

# Root
curl http://localhost:8000/

# Rules API
curl http://localhost:8000/api/rules

# Dashboard API
curl http://localhost:8000/api/dashboard/stats
```

---

## ✅ CHECKLIST

- [x] Server đã chạy thành công
- [x] Database initialized
- [ ] Test API endpoints (khi server đang chạy)
- [ ] Setup Supervisor (production)
- [ ] Setup Nginx
- [ ] Test từ bên ngoài

---

**Bây giờ hãy setup Supervisor để server chạy tự động! 🚀**


