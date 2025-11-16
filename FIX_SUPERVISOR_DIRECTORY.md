# 🔧 FIX SUPERVISOR DIRECTORY

## 🔍 VẤN ĐỀ

Lỗi: "No such file or directory" khi tạo file `/etc/supervisor/conf.d/ads-automation.conf`

**Nguyên nhân:** Thư mục `/etc/supervisor/conf.d/` có thể không tồn tại.

---

## ✅ CÁCH SỬA

### **BƯỚC 1: Check Supervisor đã được cài chưa:**

```bash
# Check supervisor đã cài chưa
which supervisorctl
supervisorctl --version
```

### **BƯỚC 2: Install Supervisor (nếu chưa có):**

```bash
sudo apt update
sudo apt install supervisor -y
```

### **BƯỚC 3: Tạo thư mục conf.d (nếu chưa có):**

```bash
# Check thư mục có tồn tại không
ls -la /etc/supervisor/

# Tạo thư mục conf.d nếu chưa có
sudo mkdir -p /etc/supervisor/conf.d
```

### **BƯỚC 4: Tạo config file:**

```bash
sudo nano /etc/supervisor/conf.d/ads-automation.conf
```

**Paste config:**

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

---

## ⚡ QUICK FIX

```bash
# Install supervisor (nếu chưa có)
sudo apt update
sudo apt install supervisor -y

# Tạo thư mục
sudo mkdir -p /etc/supervisor/conf.d

# Tạo config file
sudo nano /etc/supervisor/conf.d/ads-automation.conf
# Paste config và lưu

# Verify
ls -la /etc/supervisor/conf.d/ads-automation.conf
```

---

## ✅ SAU KHI TẠO FILE

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

---

**Chạy Quick Fix ở trên để tạo thư mục và file! 🚀**


