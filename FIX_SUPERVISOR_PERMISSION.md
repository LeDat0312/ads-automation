# 🔧 FIX SUPERVISOR PERMISSION

## ❌ VẤN ĐỀ

```
Error #3 (/etc/supervisor/supervisord.conf): Permission denied
```

**Nguyên nhân:** File Supervisor config cần quyền root để sửa.

---

## ✅ GIẢI PHÁP

### **BƯỚC 1: Sửa file với sudo:**

```bash
sudo nano /etc/supervisor/conf.d/ads-automation.conf
```

**Hoặc dùng `sudo tee` (không cần editor):**

```bash
sudo tee /etc/supervisor/conf.d/ads-automation.conf > /dev/null << 'EOF'
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
command=/home/adsuser/ads-automation/venv/bin/python -m app.workers.telegram_worker %(process_num)02d
directory=/home/adsuser/ads-automation
user=adsuser
autostart=true
autorestart=true
stderr_logfile=/var/log/ads-automation/worker.err.log
stdout_logfile=/var/log/ads-automation/worker.out.log
environment=PATH="/home/adsuser/ads-automation/venv/bin"
numprocs=2
process_name=%(program_name)s_%(process_num)02d
EOF
```

**Lưu ý:** Thêm `%(process_num)02d` vào cuối command của worker để truyền worker ID (00, 01).

### **BƯỚC 2: Reload Supervisor:**

```bash
# Test config
sudo supervisorctl reread

# Update
sudo supervisorctl update

# Restart workers
sudo supervisorctl restart ads-automation-worker:*

# Check status
sudo supervisorctl status
```

---

## 🔍 THAY ĐỔI QUAN TRỌNG

**Trước:**
```ini
command=/home/adsuser/ads-automation/venv/bin/python -m app.workers.telegram_worker
```

**Sau:**
```ini
command=/home/adsuser/ads-automation/venv/bin/python -m app.workers.telegram_worker %(process_num)02d
```

**Lý do:** Thêm `%(process_num)02d` để worker nhận được ID (00, 01) từ Supervisor.

---

## ✅ VERIFY

```bash
# Check config
cat /etc/supervisor/conf.d/ads-automation.conf | grep "command.*worker"

# Phải thấy:
# command=/home/adsuser/ads-automation/venv/bin/python -m app.workers.telegram_worker %(process_num)02d

# Check status
sudo supervisorctl status

# Check logs
sudo tail -50 /var/log/ads-automation/worker.out.log
```

---

**Bây giờ hãy sửa file với sudo! 🚀**


