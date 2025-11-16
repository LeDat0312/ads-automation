# 🔧 FIX SUPERVISOR CONFIG - XÓA MARKDOWN

## 🔍 VẤN ĐỀ

Lỗi: "File contains no section headers" và có `'```ini\n'` ở đầu file.

**Nguyên nhân:** File config có chứa markdown code block markers (```ini) thay vì chỉ có nội dung config.

---

## ✅ CÁCH SỬA

### **BƯỚC 1: Xem file hiện tại:**

```bash
cat /etc/supervisor/conf.d/ads-automation.conf
```

**Sẽ thấy có ````ini` ở đầu file.**

### **BƯỚC 2: Xóa file và tạo lại:**

```bash
# Xóa file cũ
sudo rm /etc/supervisor/conf.d/ads-automation.conf

# Tạo file mới
sudo nano /etc/supervisor/conf.d/ads-automation.conf
```

### **BƯỚC 3: Paste config (KHÔNG có markdown markers):**

**Chỉ paste phần này (KHÔNG có ```ini và ```):**

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

**⚠️ QUAN TRỌNG:** 
- KHÔNG paste ````ini` ở đầu
- KHÔNG paste ``` ở cuối
- CHỈ paste nội dung config (từ `[program:ads-automation-api]` đến hết)

**Lưu:** `Ctrl+O`, `Enter`, `Ctrl+X`

### **BƯỚC 4: Verify file:**

```bash
cat /etc/supervisor/conf.d/ads-automation.conf
```

**Phải thấy:**
```
[program:ads-automation-api]
command=/home/adsuser/ads-automation/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
...
```

**KHÔNG được có:**
```
```ini
...
```
```

---

## ⚡ QUICK FIX - TẠO FILE TRỰC TIẾP

### **Tạo file bằng cat (không qua nano):**

```bash
# Xóa file cũ
sudo rm /etc/supervisor/conf.d/ads-automation.conf

# Tạo file mới
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
EOF

# Verify
cat /etc/supervisor/conf.d/ads-automation.conf
```

---

## ✅ SAU KHI FIX

```bash
# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ads-automation-api
sudo supervisorctl start ads-automation-worker:*

# Check status
sudo supervisorctl status
```

---

**Chạy Quick Fix ở trên để tạo file đúng! 🚀**


