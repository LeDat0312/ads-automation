# 🔧 FIX WORKER PYTHON PATH

## ❌ VẤN ĐỀ

```
timeout: failed to run command 'python': No such file or directory
ads-automation-worker:ads-automation-worker_00: ERROR (spawn error)
```

**Nguyên nhân:**
- Không có lệnh `python` (chỉ có `python3`)
- Supervisor config có thể đang dùng `python` thay vì đường dẫn venv

---

## ✅ GIẢI PHÁP

### **BƯỚC 1: Test worker với python3 hoặc venv:**

```bash
cd ~/ads-automation
source venv/bin/activate

# Test với venv
python -m app.workers.telegram_worker worker-test &
sleep 5
kill %1 2>/dev/null || true
```

**Hoặc:**

```bash
cd ~/ads-automation

# Test với python3 trực tiếp
timeout 5 ~/ads-automation/venv/bin/python -m app.workers.telegram_worker worker-test 2>&1 || true
```

### **BƯỚC 2: Check Supervisor config:**

```bash
cat /etc/supervisor/conf.d/ads-automation.conf
```

**Phải thấy:**
```ini
[program:ads-automation-worker]
command=/home/adsuser/ads-automation/venv/bin/python -m app.workers.telegram_worker
```

**Nếu thấy `python` thay vì đường dẫn đầy đủ, cần sửa!**

### **BƯỚC 3: Sửa Supervisor config:**

```bash
sudo nano /etc/supervisor/conf.d/ads-automation.conf
```

**Tìm và sửa:**

```ini
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
```

**Lưu ý:**
- `command` phải dùng đường dẫn đầy đủ: `/home/adsuser/ads-automation/venv/bin/python`
- `%(process_num)02d` để truyền worker ID (00, 01)

### **BƯỚC 4: Reload Supervisor:**

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

### **BƯỚC 5: Check logs:**

```bash
# Check error logs
sudo tail -50 /var/log/ads-automation/worker.err.log

# Check output logs
sudo tail -50 /var/log/ads-automation/worker.out.log
```

---

## 🚀 QUICK FIX

### **Sửa Supervisor config nhanh:**

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

# Reload
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart ads-automation-worker:*
sudo supervisorctl status
```

---

## ✅ KẾT QUẢ MONG ĐỢI

### **Status:**

```
ads-automation-api                  RUNNING   pid ..., uptime ...
ads-automation-worker:ads-automation-worker_00   RUNNING   pid ..., uptime ...
ads-automation-worker:ads-automation-worker_01   RUNNING   pid ..., uptime ...
```

### **Logs:**

```
🚀 Starting Telegram worker: worker-00
🚀 Starting Telegram worker: worker-01
```

---

## 🔍 VERIFY

### **Test worker manually:**

```bash
cd ~/ads-automation
source venv/bin/activate

# Test import
python -c "from app.workers.telegram_worker import worker_loop; print('✅ OK')"

# Test chạy (dừng sau 5 giây)
timeout 5 python -m app.workers.telegram_worker worker-test 2>&1 || true
```

---

## 📋 CHECKLIST

- [ ] Test worker với venv hoặc python3
- [ ] Check Supervisor config
- [ ] Sửa Supervisor config (dùng đường dẫn đầy đủ)
- [ ] Reload Supervisor
- [ ] Restart workers
- [ ] Check status và logs
- [ ] Verify workers đang chạy

---

**Bây giờ hãy sửa Supervisor config! 🚀**


